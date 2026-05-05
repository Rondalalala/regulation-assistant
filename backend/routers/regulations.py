from fastapi import APIRouter, HTTPException
import json, re
from pathlib import Path

router = APIRouter()
DATA_DIR = Path(__file__).parent.parent.parent / 'data'

_authority_cache = None  # v2

def load_regulations():
    with open(DATA_DIR / 'regulations.json', encoding='utf-8') as f:
        data = json.load(f)
    return [r for r in data if r.get('id') and r['id'] != '制度序号' and r.get('name') != '制度名称']

def load_authority():
    with open(DATA_DIR / 'authority.json', encoding='utf-8') as f:
        return json.load(f)

_SUFFIXES = re.compile(r'(管理办法|实施细则|工作规则|管理规定|实施方案|操作规程|暂行规定|工作制度|管理制度|实施办法|管理规程|办法|规定|规则|细则|方案|制度)$')
_SKIP = {'中交西北投资发展有限公司', '西北投资', '中交投资', '有限公司', '公司'}

def extract_keywords(text: str) -> list[str]:
    """从制度名称中提取核心业务关键词"""
    # 去公司前缀
    text = re.sub(r'^中交西北投资发展有限公司', '', text).strip()
    # 按括号/空格切分段
    parts = re.split(r'[（）【】、，。\s]+', text)
    keywords = []
    for p in parts:
        if not p or p in _SKIP:
            continue
        # 去掉常见管理类后缀，保留业务核心词
        core = _SUFFIXES.sub('', p).strip()
        if len(core) >= 2:
            keywords.append(core)
        if len(p) >= 2:
            keywords.append(p)
    return list(dict.fromkeys(keywords))  # 去重保序

def match_authority(reg_id: str, reg_name: str, reg_module: str) -> list:
    """匹配相关权责事项：优先读 LLM 预计算映射，降级为关键词匹配"""
    authority = load_authority()
    auth_dict = {i['key']: i for i in authority}

    mapping_file = DATA_DIR / 'authority_mapping.json'
    if mapping_file.exists():
        mapping = json.loads(mapping_file.read_text(encoding='utf-8'))
        if reg_id in mapping:
            return [auth_dict[k] for k in mapping[reg_id] if k in auth_dict]

    # 降级：关键词匹配
    keywords = extract_keywords(reg_name)
    if not keywords:
        return []
    scored = []
    for item in authority:
        if not item.get('flow') or not item['flow']:
            continue
        item_name = item.get('name', '')
        score = sum(1 for kw in keywords if kw in item_name)
        if score > 0:
            scored.append((score, item))
    scored.sort(key=lambda x: -x[0])
    return [item for _, item in scored[:20]]


@router.get('/debug/authority-match')
def debug_authority_match(name: str = '中交西北投资发展有限公司采购管理办法'):
    auth = load_authority()
    kws = extract_keywords(name)
    with_flow = [i for i in auth if i.get('flow')]
    scored = []
    for item in with_flow:
        score = sum(1 for kw in kws if kw in item.get('name', ''))
        if score > 0:
            scored.append({'key': item['key'], 'name': item['name'], 'score': score})
    return {
        'data_dir': str(DATA_DIR),
        'authority_count': len(auth),
        'with_flow': len(with_flow),
        'keywords': kws,
        'matched': len(scored),
        'samples': scored[:5],
    }

@router.get('/')
def list_regulations():
    return load_regulations()


@router.get('/tree')
def get_tree():
    regs = load_regulations()
    tree = {}
    for r in regs:
        mod = r['module'] or '其他'
        item = r['item'] or '其他'
        tree.setdefault(mod, {}).setdefault(item, []).append(r)
    return tree


@router.get('/authority/list')
def list_authority_items():
    return load_authority()


@router.get('/{reg_id:path}')
def get_regulation(reg_id: str):
    regs = load_regulations()
    reg = next((r for r in regs if r['id'] == reg_id), None)
    if not reg:
        raise HTTPException(404, 'Not found')

    text_file = DATA_DIR / 'texts' / f'{reg_id}.json'
    reg['text'] = ''
    reg['blocks'] = []
    if text_file.exists():
        with open(text_file, encoding='utf-8') as f:
            tf = json.load(f)
            reg['text'] = tf.get('text', '')
            reg['blocks'] = tf.get('blocks', [])

    diagram_file = DATA_DIR / 'diagrams' / f'{reg_id}.json'
    reg['charts'] = []
    if diagram_file.exists():
        with open(diagram_file, encoding='utf-8') as f:
            reg['charts'] = json.load(f).get('charts', [])

    reg['authority_items'] = match_authority(reg_id, reg.get('name', ''), reg.get('module', ''))

    return reg
