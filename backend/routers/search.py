from fastapi import APIRouter
from services.data_store import list_regulations, list_authority
from utils.bigram import bigram_score

router = APIRouter()

STOP_WORDS = {"需要", "什么", "怎么", "如何", "是否", "可以", "应该", "流程", "走", "的", "了", "吗", "呢", "啊", "我", "要", "去", "在", "和", "与", "或", "有", "是", "一下", "哪些", "怎样", "能", "请", "问", "想", "规定", "要求", "内容", "相关"}


def match_search(item, kw, fields):
    for f in fields:
        fl = f.lower()
        if kw in fl:
            return True
        if bigram_score(kw, fl) >= 0.4:
            return True
    return False


@router.get("")
@router.get("/")
def search(q: str = "", limit: int = 30):
    if not q or not q.strip():
        return {"regulations": [], "authority": []}

    ql = q.lower().strip()
    regs = list_regulations()
    auths = list_authority()

    reg_results = []
    for r in regs:
        fields = [
            r.get("name", ""),
            r.get("module", ""),
            r.get("item", ""),
            r.get("dept", ""),
            r.get("id", ""),
        ]
        exact = any(ql in f.lower() for f in fields)
        score = max(
            bigram_score(ql, f.lower()) for f in fields
        )
        if exact or score >= 0.4:
            reg_results.append({
                "id": r["id"],
                "name": r.get("name", ""),
                "score": 1.0 if exact else score,
                "snippet": f"{r.get('module', '')} - {r.get('item', '')} | {r.get('dept', '')}",
            })

    auth_results = []
    for a in auths:
        if not a.get("flow") or not a["flow"]:
            continue
        fields = [
            a.get("name", ""),
            a.get("initiator", ""),
            a.get("category", ""),
            a.get("key", ""),
        ]
        exact = any(ql in f.lower() for f in fields)
        score = max(
            bigram_score(ql, f.lower()) for f in fields
        )
        if exact or score >= 0.4:
            auth_results.append({
                "key": a["key"],
                "name": a.get("name", ""),
                "score": 1.0 if exact else score,
                "snippet": f"发起：{a.get('initiator', '')} | 最终审批：{a.get('final_approver', '')}",
            })

    reg_results.sort(key=lambda x: x["score"], reverse=True)
    auth_results.sort(key=lambda x: x["score"], reverse=True)

    half = limit // 2
    return {
        "regulations": reg_results[:max(half, limit - len(auth_results))],
        "authority": auth_results[:max(half, limit - len(reg_results))],
    }
