"""
用公司 LLM 为每条制度匹配相关权责事项，结果写入 data/authority_mapping.json
格式: {"reg_id": ["KEY1", "KEY2", ...], ...}
支持断点续跑：已处理的制度自动跳过
"""
import json, os, time, sys
from pathlib import Path
import openai
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / 'backend' / '.env')
sys.stdout.reconfigure(encoding='utf-8')

client = openai.OpenAI(
    base_url=os.environ['COMPANY_LLM_BASE_URL'],
    api_key=os.environ['COMPANY_LLM_API_KEY'],
)
MODEL = os.environ.get('COMPANY_LLM_MODEL', 'jiaorong-deepseek-v4-pro')

DATA_DIR = Path(r"D:\西北投资\制度助理\data")
MAPPING_PATH = DATA_DIR / 'authority_mapping.json'

regs = json.loads((DATA_DIR / 'regulations.json').read_text(encoding='utf-8'))
auth = json.loads((DATA_DIR / 'authority.json').read_text(encoding='utf-8'))
auth_with_flow = [i for i in auth if i.get('flow') and len(i['flow']) > 0]

# 权责列表文本（一次性构建，每次请求复用）
auth_list_str = '\n'.join(f"{i['key']}: {i['name']}" for i in auth_with_flow)

SYSTEM_PROMPT = """你是企业制度与权责管理专家。给定一份企业制度的名称，以及一份权责事项清单（编号: 事项名称），判断该制度直接涉及哪些权责事项。

判断原则：
- 制度规范了该权责事项的审批流程、操作规范或管理要求，则认为相关
- 名称有明确业务主题重叠，则认为相关
- 仅因同属一个公司而相关，不算相关
- 党建、工会、纪检类制度通常不直接对应业务权责事项

输出格式（严格JSON，不要其他文字）：
{"matched_keys": ["编号1", "编号2"]}

如无相关项，返回：{"matched_keys": []}
最多返回20个，按相关度从高到低排列。"""

# 加载已有映射（支持断点续跑）
mapping = {}
if MAPPING_PATH.exists():
    mapping = json.loads(MAPPING_PATH.read_text(encoding='utf-8'))
    print(f'已有映射: {len(mapping)} 条，继续处理剩余...')

todo = [r for r in regs if r['id'] not in mapping]
print(f'待处理: {len(todo)} / {len(regs)} 条制度')
print()

success = 0
fail = 0

for i, reg in enumerate(todo):
    reg_id = reg['id']
    reg_name = reg.get('name', '')

    user_msg = f"制度名称：{reg_name}\n\n权责事项清单：\n{auth_list_str}"

    try:
        resp = client.chat.completions.create(
            model=MODEL,
            max_tokens=600,
            temperature=0,
            messages=[
                {'role': 'system', 'content': SYSTEM_PROMPT},
                {'role': 'user', 'content': user_msg},
            ]
        )
        content = resp.choices[0].message.content.strip()
        # 去掉可能的 markdown 代码块
        if '```json' in content:
            content = content.split('```json')[1].split('```')[0].strip()
        elif '```' in content:
            content = content.split('```')[1].split('```')[0].strip()
        result = json.loads(content)
        matched = result.get('matched_keys', [])
        # 过滤掉不存在的 key
        valid_keys = {a['key'] for a in auth_with_flow}
        matched = [k for k in matched if k in valid_keys]
    except json.JSONDecodeError as e:
        print(f'  [JSONError] {reg_id}: {e} | raw: {content[:80]}')
        matched = []
        fail += 1
    except Exception as e:
        print(f'  [APIError] {reg_id}: {e}')
        time.sleep(2)
        fail += 1
        continue

    mapping[reg_id] = matched
    MAPPING_PATH.write_text(json.dumps(mapping, ensure_ascii=False, indent=2), encoding='utf-8')
    success += 1

    tag = '✓' if matched else '○'
    print(f'[{i+1}/{len(todo)}] {tag} {reg_id} {reg_name[:25]} → {len(matched)} 条权责')
    time.sleep(0.4)

print(f'\n完成！成功 {success} 条，失败 {fail} 条')
print(f'映射文件: {MAPPING_PATH}')

# 统计覆盖率
total_with_match = sum(1 for v in mapping.values() if v)
print(f'有匹配权责的制度: {total_with_match} / {len(mapping)}')
