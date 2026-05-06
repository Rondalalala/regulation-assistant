from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from services.data_store import (
    write_json, read_json, write_regulation_text,
)
from services.ai_parser import normalize_regulations, normalize_authority
from services import debug_log
import time
import io
import json
import pandas as pd
import pdfplumber

try:
    from docx import Document
    HAS_DOCX = True
except Exception:
    HAS_DOCX = False

router = APIRouter()
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

# 进程内临时缓存(重启丢失,够用)
_upload_cache: dict = {}


def _df_to_rows(df: pd.DataFrame) -> list[dict]:
    rows = []
    for _, row in df.iterrows():
        rows.append({k: (None if pd.isna(v) else v) for k, v in row.to_dict().items()})
    return rows


def _parse_excel(content: bytes) -> list[dict]:
    df = pd.read_excel(io.BytesIO(content))
    return _df_to_rows(df)


def _parse_flow(flow_str: str) -> list[dict]:
    """字符串 'A→B→C' → [{role, org, step, is_final}]。AI 不可用时的兜底。"""
    if not flow_str or not isinstance(flow_str, str):
        return []
    raw = flow_str.replace("->", "→").replace("→→", "→")
    steps = [s.strip() for s in raw.split("→") if s.strip()]
    out = []
    for i, s in enumerate(steps):
        is_last = i == len(steps) - 1
        out.append({
            "role": s,
            "org": s,
            "step": "发起申请" if i == 0 else ("终审批准" if is_last else "审核审批"),
            "is_final": is_last,
        })
    return out


# ─────────────────────────────────────────────────────────────
# 智能导入(推荐流程):一次请求完成"解析 → AI 标准化 → 保存"
# ─────────────────────────────────────────────────────────────

@router.post("/smart-import")
async def smart_import(
    file: UploadFile = File(...),
    kind: str = Form(...),
    base_url: str = Form(""),
    api_key: str = Form(""),
    model: str = Form(""),
):
    """
    通用智能导入:接收任意格式 Excel,后台 AI 静默标准化为系统 schema 后直接保存。
    kind: regulations | authority
    base_url/api_key/model: 用户在前端"AI 设置"里配置的 LLM 凭证
    """
    started = time.time()
    if not file.filename:
        raise HTTPException(400, "Missing filename")
    if kind not in ("regulations", "authority"):
        raise HTTPException(400, "kind must be 'regulations' or 'authority'")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(413, "File too large (max 50MB)")

    debug_log.info("upload", f"smart-import 开始 kind={kind} file={file.filename} size={len(content)}")

    # 1. 解析 Excel
    try:
        rows = _parse_excel(content)
    except Exception as e:
        debug_log.error("upload", f"Excel 解析失败:{e}", filename=file.filename)
        raise HTTPException(422, f"Excel 解析失败:{e}")

    if not rows:
        raise HTTPException(422, "文件为空,没有可导入的数据")

    raw_columns = list(rows[0].keys()) if rows else []
    debug_log.info(
        "upload",
        f"Excel 解析完成,共 {len(rows)} 行,字段:{raw_columns}",
    )

    # 2. AI 标准化
    llm_config = {"base_url": base_url, "api_key": api_key, "model": model}
    if not base_url or not api_key:
        raise HTTPException(
            400,
            "缺少 AI 配置(base_url 或 api_key)。请先去【设置】填写并测试连接,再上传文件。"
        )

    try:
        if kind == "regulations":
            normalized = await normalize_regulations(rows, llm_config)
        else:
            normalized = await normalize_authority(rows, llm_config)
    except Exception as e:
        debug_log.error("ai_parser", f"AI 标准化失败:{type(e).__name__}: {e}", kind=kind)
        # 降级:用本地启发式
        normalized = _fallback_normalize(rows, kind)
        if not normalized:
            raise HTTPException(502, f"AI 标准化失败,且本地兜底也未能识别字段:{e}")
        debug_log.warn("ai_parser", f"AI 失败,降级为本地兜底,共 {len(normalized)} 条")

    if not normalized:
        raise HTTPException(422, "AI 处理后为空,可能是表格内容无法识别")

    # 3. 保存到 data/
    if kind == "regulations":
        write_json("regulations.json", normalized)
    else:
        write_json("authority.json", normalized)

    elapsed_ms = int((time.time() - started) * 1000)
    debug_log.info(
        "upload",
        f"smart-import 完成 kind={kind} count={len(normalized)} 耗时={elapsed_ms}ms",
    )

    return {
        "saved": True,
        "kind": kind,
        "count": len(normalized),
        "preview": normalized[:3],
        "raw_columns": raw_columns,
        "duration_ms": elapsed_ms,
    }


def _fallback_normalize(rows: list[dict], kind: str) -> list[dict]:
    """AI 不可用时的兜底:尽量按列名常见关键词做映射。质量低,只为不丢数据。"""
    if not rows:
        return []
    cols = list(rows[0].keys())

    def _find(*keys, exclude=()):
        """优先返回完全等于关键词的列;其次返回包含关键词且不含 exclude 词的列。"""
        cl_map = {c: str(c).lower() for c in cols}
        # 1. 完全相等
        for c, cl in cl_map.items():
            for k in keys:
                if cl == k.lower() or str(c) == k:
                    return c
        # 2. 包含但排除指定词
        for c, cl in cl_map.items():
            if any(e in str(c) for e in exclude):
                continue
            for k in keys:
                if k.lower() in cl or k in str(c):
                    return c
        return None

    if kind == "regulations":
        col_id = _find("id", "编号", "序号", exclude=("名称",))
        col_name = _find("name", "名称", "标题")
        col_module = _find("module", "类别", "类型", "大类", "分类", exclude=("二级", "子"))
        col_item = _find("item", "二级", "子类", "子项")
        col_dept = _find("dept", "主责部门", "部门")
        col_doc_no = _find("doc_no", "文号", "doc")
        col_status = _find("status", "状态")
        out = []
        for i, r in enumerate(rows, 1):
            name = str(r.get(col_name, "") if col_name else "").strip()
            if not name:
                continue
            module = str(r.get(col_module, "") if col_module else "未分类").strip() or "未分类"
            item = str(r.get(col_item, "") if col_item else module).strip() or module
            out.append({
                "id": str(r.get(col_id, "") if col_id else "").strip() or f"1-1-{i}",
                "name": name,
                "module": module,
                "item": item,
                "dept": str(r.get(col_dept, "") if col_dept else "").strip(),
                "doc_no": str(r.get(col_doc_no, "") if col_doc_no else "").strip(),
                "status": str(r.get(col_status, "") if col_status else "施行").strip() or "施行",
            })
        return out

    # authority
    col_key = _find("key", "流程编号", "编号", exclude=("名称",))
    col_name = _find("name", "流程名称", "名称", "事项")
    col_cat = _find("category", "业务类别", "类别", "业务", "类型")
    col_sys = _find("system", "关联制度", "制度", "关联")
    col_init = _find("initiator", "发起人", "发起")
    col_final = _find("final_approver", "最终审批人", "终审", "审批人")
    col_flow = _find("flow", "审批流程", exclude=("编号", "名称", "类别", "人")) \
        or _find("flow", "流程", exclude=("编号", "名称"))
    out = []
    for i, r in enumerate(rows, 1):
        name = str(r.get(col_name, "") if col_name else "").strip()
        if not name:
            continue
        out.append({
            "key": str(r.get(col_key, "") if col_key else "").strip() or f"X{i:03d}",
            "name": name,
            "category": str(r.get(col_cat, "") if col_cat else "").strip(),
            "system": str(r.get(col_sys, "") if col_sys else "").strip(),
            "initiator": str(r.get(col_init, "") if col_init else "").strip(),
            "final_approver": str(r.get(col_final, "") if col_final else "").strip(),
            "flow": _parse_flow(str(r.get(col_flow, "") if col_flow else "")),
        })
    return out


# ─────────────────────────────────────────────────────────────
# 旧版分步流程(预览 → 确认):为兼容历史前端保留
# ─────────────────────────────────────────────────────────────

@router.post("/regulations-excel")
async def upload_regulations_excel(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(400, "Missing filename")
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(413, "File too large")

    try:
        all_rows = _parse_excel(content)
    except Exception as e:
        raise HTTPException(422, f"Excel parse error: {e}")

    _upload_cache["regulations"] = all_rows

    return {
        "preview": all_rows[:5],
        "total_rows": len(all_rows),
        "preview_count": min(5, len(all_rows)),
        "warnings": [],
    }


@router.post("/authority-excel")
async def upload_authority_excel(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(400, "Missing filename")
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(413, "File too large")

    try:
        all_rows = _parse_excel(content)
    except Exception as e:
        raise HTTPException(422, f"Excel parse error: {e}")

    for row in all_rows:
        if "flow" in row and isinstance(row["flow"], str):
            row["flow"] = _parse_flow(row["flow"])

    _upload_cache["authority"] = all_rows

    return {
        "preview": all_rows[:5],
        "total_rows": len(all_rows),
        "preview_count": min(5, len(all_rows)),
        "warnings": [],
    }


@router.post("/regulation-pdf")
async def upload_regulation_pdf(file: UploadFile = File(...), reg_id: str = ""):
    if not file.filename:
        raise HTTPException(400, "Missing filename")
    if not reg_id:
        raise HTTPException(400, "Missing reg_id query parameter")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(413, "File too large")

    text = ""
    filename = file.filename.lower()
    try:
        if filename.endswith(".pdf"):
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        elif filename.endswith(".docx") and HAS_DOCX:
            doc = Document(io.BytesIO(content))
            text = "\n".join(p.text for p in doc.paragraphs if p.text)
        else:
            raise HTTPException(422, "Unsupported file format. Use .pdf or .docx")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(422, f"Text extraction failed: {e}")

    return {
        "reg_id": reg_id,
        "text_preview": text[:1000],
        "text_length": len(text),
        "warnings": [],
    }


@router.post("/confirm-regulations")
async def confirm_regulations(data: dict):
    regs = _upload_cache.get("regulations") or data.get("data")
    if not isinstance(regs, list):
        raise HTTPException(400, "No regulation data to save. Please re-upload the file.")
    write_json("regulations.json", regs)
    _upload_cache.pop("regulations", None)
    return {"saved": True, "count": len(regs)}


@router.post("/confirm-authority")
async def confirm_authority(data: dict):
    auths = _upload_cache.get("authority") or data.get("data")
    if not isinstance(auths, list):
        raise HTTPException(400, "No authority data to save. Please re-upload the file.")
    write_json("authority.json", auths)
    _upload_cache.pop("authority", None)
    return {"saved": True, "count": len(auths)}


@router.post("/confirm-pdf")
async def confirm_pdf(data: dict):
    reg_id = data.get("reg_id")
    text = data.get("text", "")
    blocks = data.get("blocks", [])
    if not reg_id:
        raise HTTPException(400, "Missing reg_id")
    write_regulation_text(reg_id, {"id": reg_id, "text": text, "blocks": blocks})
    return {"saved": True}
