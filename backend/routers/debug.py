from fastapi import APIRouter, Query
from services import debug_log

router = APIRouter()


@router.get("/logs")
def get_logs(
    limit: int = Query(200, ge=1, le=500),
    level: str | None = Query(None),
):
    if level and level not in ("info", "warn", "error"):
        level = None
    return {
        "logs": debug_log.list_logs(limit=limit, level=level),
        "total": len(debug_log.list_logs(limit=500)),
    }


@router.delete("/logs")
def clear_logs():
    debug_log.clear()
    return {"cleared": True}
