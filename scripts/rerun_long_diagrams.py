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

DIAG_DIR = Path(r"D:\西北投资\制度助理\data\diagrams")
TEXT_DIR = Path(r"D:\西北投资\制度助理\data\texts")

SYSTEM_PROMPT = """你是企业制度流程分析专家。给定一份制度原文，你需要：
1. 判断该制度是否包含可视化的审批流程、操作流程或管理流程
2. 如果有，生成对应的 Mermaid 图表代码
3. 一份制度可生成多个图表，每个对应一个独立流程

支持的图表类型：
- flowchart TD（审批流、操作步骤）
- 用 subgraph 划分泳道（不同部门/角色）

严格输出 JSON 格式（不要有任何其他文字）：
{"has_process":true,"charts":[{"title":"流程名称","type":"flowchart","mermaid":"flowchart TD\\n  A[节点] --> B[节点]"}]}
或：{"has_process":false,"charts":[]}

Mermaid 代码要求：
- 节点标签用中文，≤12字
- flowchart 用 TD 方向
- 用 subgraph 区分不同部门的泳道
- 节点 id 用英文字母，标签用中文方括号
- 不要出现特殊字符导致解析失败"""

# 找出 has_process=false 且文本>3000字的制度
todo = []
for f in sorted(DIAG_DIR.glob('*.json')):
    d = json.loads(f.read_text(encoding='utf-8'))
    if not d.get('has_process') and not d.get('charts'):
        reg_id = d['id']
        tf = TEXT_DIR / f'{reg_id}.json'
        if tf.exists():
            t = json.loads(tf.read_text(encoding='utf-8'))
            tlen = len(t.get('text', ''))
            if tlen > 3000:
                todo.append((reg_id, tlen, d['name']))

todo.sort(key=lambda x: -x[1])
print(f'待重新处理: {len(todo)} 条')

updated = 0
for i, (reg_id, tlen, name) in enumerate(todo):
    reg = json.loads((TEXT_DIR / f'{reg_id}.json').read_text(encoding='utf-8'))
    # 发送更多文本，最多10000字
    text_preview = reg['text'][:10000]

    try:
        resp = client.chat.completions.create(
            model=MODEL,
            max_tokens=3000,
            temperature=0.1,
            messages=[
                {'role': 'system', 'content': SYSTEM_PROMPT},
                {'role': 'user', 'content': f"制度名称：{reg['name']}\n\n原文：\n{text_preview}"}
            ]
        )
        content = resp.choices[0].message.content.strip()
        if '```json' in content:
            content = content.split('```json')[1].split('```')[0].strip()
        elif '```' in content:
            content = content.split('```')[1].split('```')[0].strip()
        result = json.loads(content)
    except json.JSONDecodeError as e:
        print(f'  JSON解析失败 {reg_id}: {e}')
        time.sleep(0.3)
        continue
    except Exception as e:
        print(f'  API错误 {reg_id}: {e}')
        time.sleep(0.3)
        continue

    charts_count = len(result.get('charts', []))
    if charts_count > 0:
        out = {'id': reg_id, 'name': reg['name'], **result}
        (DIAG_DIR / f'{reg_id}.json').write_text(
            json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8'
        )
        updated += 1
        print(f'[{i+1}/{len(todo)}] ✓ {reg_id} {name[:20]} → {charts_count} 张图表')
    else:
        print(f'[{i+1}/{len(todo)}]   {reg_id} {name[:20]} → 确认无流程图')

    time.sleep(0.3)

print(f'\n完成！新增图表 {updated} 份，确认无流程 {len(todo)-updated} 份')
