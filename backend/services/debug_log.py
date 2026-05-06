"""轻量调试日志:写到内存环形缓冲区,前端可拉取查看。
不写到磁盘,避免越用越慢。重启进程即清空。
"""
from collections import deque
from datetime import datetime, timezone
from typing import Any
import threading

_BUFFER: deque = deque(maxlen=500)
_LOCK = threading.Lock()


def log(level: str, scope: str, message: str, **extra: Any) -> None:
    """level: info / warn / error;scope: 模块名(如 'upload', 'ai_parser')"""
    entry = {
        "ts": datetime.now(tz=timezone.utc).isoformat(),
        "level": level,
        "scope": scope,
        "message": message,
    }
    if extra:
        # 把不可 JSON 序列化的对象转字符串
        safe_extra = {}
        for k, v in extra.items():
            try:
                import json
                json.dumps(v, ensure_ascii=False)
                safe_extra[k] = v
            except Exception:
                safe_extra[k] = repr(v)[:500]
        entry["extra"] = safe_extra
    with _LOCK:
        _BUFFER.append(entry)


def info(scope: str, message: str, **extra: Any) -> None:
    log("info", scope, message, **extra)


def warn(scope: str, message: str, **extra: Any) -> None:
    log("warn", scope, message, **extra)


def error(scope: str, message: str, **extra: Any) -> None:
    log("error", scope, message, **extra)


def list_logs(limit: int = 200, level: str | None = None) -> list[dict]:
    with _LOCK:
        items = list(_BUFFER)
    if level:
        items = [x for x in items if x["level"] == level]
    return items[-limit:]


def clear() -> None:
    with _LOCK:
        _BUFFER.clear()
