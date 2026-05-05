from fastapi import APIRouter, UploadFile, File, HTTPException
from services.data_store import (
    write_json, read_json, write_regulation_text,
)
import io
import pandas as pd
import pdfplumber

try:
    from docx import Document
    HAS_DOCX = True
except Exception:
    HAS_DOCX = False

router = APIRouter()
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


def _preview_df(df: pd.DataFrame, max_rows: int = 5):
    rows = []
    for _, row in df.head(max_rows).iterrows():
        rows.append({k: (v if pd.notna(v) else None) for k, v in row.to_dict().items()})
    return rows


@router.post("/regulations-excel")
async def upload_regulations_excel(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(400, "Missing filename")
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(413, "File too large")

    try:
        df = pd.read_excel(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(422, f"Excel parse error: {e}")

    preview = _preview_df(df)
    return {
        "preview": preview,
        "total_rows": len(df),
        "preview_count": len(preview),
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
        df = pd.read_excel(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(422, f"Excel parse error: {e}")

    preview = _preview_df(df)
    return {
        "preview": preview,
        "total_rows": len(df),
        "preview_count": len(preview),
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
    regs = data.get("data")
    if not isinstance(regs, list):
        raise HTTPException(400, "data must be an array")
    write_json("regulations.json", regs)
    return {"saved": True, "count": len(regs)}


@router.post("/confirm-authority")
async def confirm_authority(data: dict):
    auths = data.get("data")
    if not isinstance(auths, list):
        raise HTTPException(400, "data must be an array")
    write_json("authority.json", auths)
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
