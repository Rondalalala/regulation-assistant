from fastapi import APIRouter
import json
from pathlib import Path

router = APIRouter()
DATA_DIR = Path(__file__).parent.parent.parent / 'data'


@router.get('/')
def search(q: str = ''):
    if not q.strip():
        return []
    with open(DATA_DIR / 'regulations.json', encoding='utf-8') as f:
        regs = json.load(f)
    q_lower = q.lower()
    results = [
        r for r in regs
        if q_lower in r['name'].lower()
        or q_lower in r['module'].lower()
        or q_lower in r['item'].lower()
        or q_lower in r['dept'].lower()
        or q_lower in r['id'].lower()
    ]
    return results[:30]
