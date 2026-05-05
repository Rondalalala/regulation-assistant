"""
从制度汇编 Word 文档中提取每份制度的正文，保留表格结构
输出格式: data/texts/{id}.json
  { id, name, text(纯文本), blocks(结构化，含段落和表格) }
"""
import sys, zipfile, re, json
from xml.etree import ElementTree as ET
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

DOCX    = Path(r'D:\西北投资\制度助理\附件2：中交西北投资发展有限公司规章制度汇编（截至2026年1月）.docx')
OUT_DIR = Path(r'D:\西北投资\制度助理\data\texts')
NS      = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
W       = lambda tag: f'{{{NS}}}{tag}'

# ── 工具函数 ──────────────────────────────────────────────────────────

def para_text(p):
    return ''.join(t.text for t in p.findall(f'.//{W("t")}') if t.text).strip()

def cell_text(tc):
    lines = []
    for p in tc.findall(f'.//{W("p")}'):
        t = para_text(p)
        if t:
            lines.append(t)
    return '\n'.join(lines)

def get_colspan(tc):
    tcPr = tc.find(W('tcPr'))
    if tcPr is None:
        return 1
    gs = tcPr.find(W('gridSpan'))
    return int(gs.get(W('val'), 1)) if gs is not None else 1

def is_vmerge_continue(tc):
    """返回 True 表示该单元格是垂直合并的续行（不渲染）"""
    tcPr = tc.find(W('tcPr'))
    if tcPr is None:
        return False
    vm = tcPr.find(W('vMerge'))
    if vm is None:
        return False
    val = vm.get(W('val'), '')
    return val != 'restart'   # restart = 合并首行；空/其他 = 续行

def extract_table(tbl):
    """返回 rows: [[{text, colspan}, ...], ...]，跳过 vMerge 续行单元格"""
    rows = []
    for tr in tbl.findall(W('tr')):
        row = []
        for tc in tr.findall(W('tc')):
            if is_vmerge_continue(tc):
                continue          # 合并续行，跳过
            colspan = get_colspan(tc)
            text    = cell_text(tc)
            row.append({'text': text, 'colspan': colspan})
        if row:
            rows.append(row)
    return rows

# ── 读取文档 body 的直接子元素（保留段落与表格的顺序）────────────────

print('读取文档...')
with zipfile.ZipFile(DOCX) as z:
    xml = z.read('word/document.xml')
root = ET.fromstring(xml)
body = root.find(W('body'))

# body 直接子元素列表：p / tbl / sdt / sectPr
children = list(body)
print(f'body 子元素数: {len(children)}')

# ── 按制度 ID 拆分 ────────────────────────────────────────────────────
REG_HEADER = re.compile(r'^(\d+-\d+-\d+)\s{0,6}中交')
TOC_PARA_THRESHOLD = 50   # 目录区仅前50段，内容从para#68开始

# 先统计段落序号（只计 <w:p>，用于判断目录/正文边界）
para_idx   = 0
reg_blocks = {}   # {id: [block, ...]}
cur_id     = None
cur_blocks = []

for child in children:
    tag = child.tag.split('}')[-1]

    if tag == 'p':
        para_idx += 1
        text = para_text(child)
        m = REG_HEADER.match(text)
        if m and para_idx > TOC_PARA_THRESHOLD:
            # 新制度开始
            if cur_id and cur_blocks:
                reg_blocks[cur_id] = cur_blocks
            cur_id     = m.group(1)
            cur_blocks = [{'type': 'para', 'text': text}]
        elif cur_id:
            if text:
                cur_blocks.append({'type': 'para', 'text': text})
            # 空段落作段间距，不存储

    elif tag == 'tbl' and cur_id:
        rows = extract_table(child)
        if rows:
            cur_blocks.append({'type': 'table', 'rows': rows})

    elif tag == 'sdt' and cur_id:
        # 结构化文档标签，递归找段落和表格
        for sub in child.iter():
            stag = sub.tag.split('}')[-1]
            if stag == 'p':
                text = para_text(sub)
                if text:
                    cur_blocks.append({'type': 'para', 'text': text})
            elif stag == 'tbl':
                rows = extract_table(sub)
                if rows:
                    cur_blocks.append({'type': 'table', 'rows': rows})

# 末尾
if cur_id and cur_blocks:
    reg_blocks[cur_id] = cur_blocks

print(f'提取到制度: {len(reg_blocks)} 份')

# ── 生成纯文本（给 LLM 等用）────────────────────────────────────────

def blocks_to_text(blocks):
    lines = []
    for b in blocks:
        if b['type'] == 'para':
            lines.append(b['text'])
        elif b['type'] == 'table':
            for row in b['rows']:
                lines.append('  '.join(c['text'].replace('\n', ' ') for c in row if c['text']))
    return '\n'.join(lines)

# ── 写出文件 ────────────────────────────────────────────────────────
regs_meta = json.loads(Path(r'D:\西北投资\制度助理\data\regulations.json').read_text(encoding='utf-8'))
reg_names = {r['id']: r.get('name', '') for r in regs_meta if r.get('id') and r['id'] != '制度序号'}

saved = 0
for reg_id, blocks in reg_blocks.items():
    text = blocks_to_text(blocks)
    out  = {'id': reg_id, 'name': reg_names.get(reg_id, ''), 'text': text, 'blocks': blocks}
    (OUT_DIR / f'{reg_id}.json').write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
    saved += 1

print(f'写出: {saved} 份 → {OUT_DIR}')

# ── 样本验证 ─────────────────────────────────────────────────────────
for sid in ['1-1-1', '1-1-2', '17-3-1']:
    d = json.loads((OUT_DIR / f'{sid}.json').read_text(encoding='utf-8'))
    btypes = [b['type'] for b in d['blocks']]
    table_cnt = btypes.count('table')
    para_cnt  = btypes.count('para')
    preview   = d['text'][:80].replace('\n', ' / ')
    print(f'{sid}: {para_cnt}段落 {table_cnt}表格 | {preview}')
