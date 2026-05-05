import uuid
from datetime import datetime, timezone

tasks = {}


def create_task(total: int):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        "task_id": task_id,
        "status": "running",
        "progress": 0,
        "total": total,
        "current_item": None,
        "error": None,
        "result": None,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": 0,
    }
    return task_id


def update_progress(task_id: str, progress: int, current_item: str = None):
    if task_id not in tasks:
        return
    tasks[task_id]["progress"] = progress
    if current_item is not None:
        tasks[task_id]["current_item"] = current_item
    started = datetime.fromisoformat(tasks[task_id]["started_at"])
    now = datetime.now(timezone.utc)
    tasks[task_id]["elapsed_seconds"] = int((now - started).total_seconds())


def complete_task(task_id: str, result):
    if task_id not in tasks:
        return
    tasks[task_id]["status"] = "completed"
    tasks[task_id]["progress"] = tasks[task_id]["total"]
    tasks[task_id]["result"] = result
    started = datetime.fromisoformat(tasks[task_id]["started_at"])
    now = datetime.now(timezone.utc)
    tasks[task_id]["elapsed_seconds"] = int((now - started).total_seconds())


def fail_task(task_id: str, error: str):
    if task_id not in tasks:
        return
    tasks[task_id]["status"] = "failed"
    tasks[task_id]["error"] = str(error)
    started = datetime.fromisoformat(tasks[task_id]["started_at"])
    now = datetime.now(timezone.utc)
    tasks[task_id]["elapsed_seconds"] = int((now - started).total_seconds())


def get_task(task_id: str):
    return tasks.get(task_id)
