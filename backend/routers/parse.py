from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from services.task_manager import (
    create_task, update_progress, complete_task, fail_task, get_task,
)
from services.data_store import (
    list_regulations, read_regulation_text, write_regulation_text,
    write_regulation_diagrams, write_json, read_json,
)
from services.ai_parser import parse_structure, generate_diagram
import asyncio

router = APIRouter()


class ParseStartRequest(BaseModel):
    scope: str | List[str] = "all"
    tasks: List[str] = ["structure", "diagrams"]
    llm_config: dict = {}


@router.post("/start")
async def start_parsing(req: ParseStartRequest, background_tasks: BackgroundTasks):
    regulations = list_regulations()
    if req.scope != "all" and isinstance(req.scope, list):
        scope_ids = set(req.scope)
        regulations = [r for r in regulations if r["id"] in scope_ids]

    task_id = create_task(len(regulations))
    background_tasks.add_task(_run_parse_task, task_id, regulations, req.tasks, req.llm_config)
    return {
        "task_id": task_id,
        "total": len(regulations),
        "status": "running",
    }


async def _run_parse_task(task_id: str, regulations, tasks, llm_config):
    results = {"regulations": [], "diagrams": {}, "mapping": {}}

    try:
        for i, reg in enumerate(regulations):
            update_progress(task_id, i + 1, reg["id"])
            text_data = read_regulation_text(reg["id"])
            text = text_data.get("text", "") if text_data else ""

            if "structure" in tasks and text:
                blocks = await parse_structure(text, llm_config)
                results["regulations"].append({"id": reg["id"], "blocks": blocks})
                # 避免速率限制
                await asyncio.sleep(0.2)

            if "diagrams" in tasks and text:
                mermaid = await generate_diagram(text, llm_config)
                if mermaid:
                    results["diagrams"][reg["id"]] = {
                        "charts": [{
                            "title": f"{reg.get('name', reg['id'])} 流程图",
                            "mermaid": mermaid,
                        }]
                    }
                await asyncio.sleep(0.2)

        # Build mapping stub (placeholder for future keyword-based mapping)
        authority = read_json("authority.json") or []
        mapping = {}
        for reg in regulations:
            mapping[reg["id"]] = []
        results["mapping"] = mapping

        complete_task(task_id, results)
    except Exception as e:
        fail_task(task_id, str(e))


@router.get("/progress/{task_id}")
async def get_progress(task_id: str):
    task = get_task(task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    return task


@router.get("/result/{task_id}")
async def get_result(task_id: str):
    task = get_task(task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    if task["status"] != "completed":
        raise HTTPException(400, "Task not completed yet")
    return task["result"]


@router.post("/save/{task_id}")
async def save_result(task_id: str):
    task = get_task(task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    if task["status"] != "completed":
        raise HTTPException(400, "Task not completed yet")

    result = task["result"]
    for reg_data in result.get("regulations", []):
        reg_id = reg_data["id"]
        text_data = read_regulation_text(reg_id) or {"id": reg_id, "text": "", "blocks": []}
        text_data["blocks"] = reg_data.get("blocks", [])
        write_regulation_text(reg_id, text_data)

    for reg_id, diagram_data in result.get("diagrams", {}).items():
        write_regulation_diagrams(reg_id, diagram_data)

    mapping = result.get("mapping", {})
    if mapping:
        write_json("authority_mapping.json", mapping)

    return {"saved": True}
