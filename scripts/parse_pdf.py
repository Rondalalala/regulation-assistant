import pdfplumber, json, re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

PDF_PATH = r"D:\西北投资\2026-win\其他工作\制度\关于印发《中交西北投资发展有限公司规章制度汇编》的通知_32158520260324085552\附件2：中交西北投资发展有限公司规章制度汇编（截至2026年1月）.pdf"
INDEX_PATH = r"D:\西北投资\制度助理\data\regulations.json"
OUT_DIR = Path(r"D:\西北投资\制度助理\data\texts")
OUT_DIR.mkdir(exist_ok=True)

with open(INDEX_PATH, encoding='utf-8') as f:
    regulations = json.load(f)

reg_map = {r['id']: r['name'] for r in regulations}
reg_ids = sorted(reg_map.keys())

print(f'正在提取 PDF 文本（共 2290 页，请稍候）...')
with pdfplumber.open(PDF_PATH) as pdf:
    total = len(pdf.pages)
    page_texts = []
    for i, page in enumerate(pdf.pages):
        if i % 200 == 0:
            print(f'  进度: {i}/{total}')
        page_texts.append(page.extract_text() or '')

full_text = '\n'.join(page_texts)
print('文本提取完成，开始按制度编号分割...')

# 找每条制度在正文中的起始位置（跳过目录，找第二次出现）
boundaries = []
for reg_id in reg_ids:
    name_prefix = reg_map[reg_id][:6].replace('(', r'\(').replace(')', r'\)')
    pattern = re.compile(re.escape(reg_id) + r'[\s　]+' + name_prefix)
    matches = list(pattern.finditer(full_text))
    if len(matches) >= 2:
        boundaries.append((reg_id, matches[1].start()))
    elif matches:
        boundaries.append((reg_id, matches[0].start()))

boundaries.sort(key=lambda x: x[1])
print(f'找到 {len(boundaries)} 条制度边界')

for i, (reg_id, start) in enumerate(boundaries):
    end = boundaries[i + 1][1] if i + 1 < len(boundaries) else len(full_text)
    text_chunk = full_text[start:end].strip()
    safe_id = reg_id.replace('/', '_')
    out_file = OUT_DIR / f'{safe_id}.json'
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump({'id': reg_id, 'name': reg_map[reg_id], 'text': text_chunk},
                  f, ensure_ascii=False, indent=2)

print(f'解析完成：{len(boundaries)} 条制度原文 → {OUT_DIR}')
