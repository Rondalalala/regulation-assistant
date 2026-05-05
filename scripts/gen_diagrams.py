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

TEXTS_DIR = Path(r"D:\西北投资\制度助理\data\texts")
OUT_DIR = Path(r"D:\西北投资\制度助理\data\diagrams")
OUT_DIR.mkdir(exist_ok=True)

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

text_files = sorted(TEXTS_DIR.glob('*.json'))
done = {f.stem for f in OUT_DIR.glob('*.json')}
todo = [f for f in text_files if f.stem not in done]

print(f'待处理: {len(todo)} 条 / 已完成: {len(done)} 条')

for i, text_file in enumerate(todo):
    reg_id = text_file.stem

    with open(text_file, encoding='utf-8') as f:
        reg = json.load(f)

    # 截取前3000字，避免超长
    text_preview = reg['text'][:3000]

    try:
        resp = client.chat.completions.create(
            model=MODEL,
            max_tokens=2000,
            temperature=0.1,
            messages=[
                {'role': 'system', 'content': SYSTEM_PROMPT},
                {'role': 'user', 'content': f"制度名称：{reg['name']}\n\n原文：\n{text_preview}"}
            ]
        )
        content = resp.choices[0].message.content.strip()
        # 提取 JSON（可能被 ```json 包裹）
        if '```json' in content:
            content = content.split('```json')[1].split('```')[0].strip()
        elif '```' in content:
            content = content.split('```')[1].split('```')[0].strip()
        result = json.loads(content)
    except json.JSONDecodeError as e:
        print(f'  JSON解析失败 {reg_id}: {e} | 原始: {content[:100]}')
        result = {'has_process': False, 'charts': []}
    except Exception as e:
        print(f'  API错误 {reg_id}: {e}')
        result = {'has_process': False, 'charts': []}

    out_file = OUT_DIR / f'{reg_id}.json'
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump({'id': reg_id, 'name': reg['name'], **result}, f,
                  ensure_ascii=False, indent=2)

    charts_count = len(result.get('charts', []))
    print(f'[{i+1}/{len(todo)}] {reg_id} {reg["name"][:18]} → {charts_count} 张图表')
    time.sleep(0.3)

print(f'\n全部完成！共生成 {len(list(OUT_DIR.glob("*.json")))} 个图表文件')
