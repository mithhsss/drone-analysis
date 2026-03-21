"""
Upload route — POST /upload  (PDF or TXT file ingestion)
"""
import os
import time
import logging
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, Form
from api.models.responses import UploadResponse
from api.services.analytics_service import analytics

router = APIRouter()
logger = logging.getLogger("api.upload")
UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "uploads"

@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...), description: str = Form(None)):
    start = time.time()
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    ext = Path(file.filename).suffix.lower()
    if ext not in (".pdf", ".txt"):
        return UploadResponse(
            success=False, filename=file.filename,
            message="Only PDF and TXT files are supported.",
        )

    timestamp = int(time.time())
    saved_path = UPLOAD_DIR / f"{timestamp}_{file.filename}"
    content = await file.read()
    with open(saved_path, "wb") as f:
        f.write(content)

    vectors_added = 0
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

        if ext == ".pdf":
            from rag.ingest import ingest_pdfs
            ingest_pdfs(str(UPLOAD_DIR))
            vectors_added = -1  # can't easily count, mark as processed
        elif ext == ".txt":
            from rag.ingest import ingest_txt_chunks
            ingest_txt_chunks(saved_path)
            vectors_added = -1
    except Exception as e:
        logger.error(f"Ingestion error: {e}")
        return UploadResponse(
            success=False, filename=file.filename,
            message=f"File saved but ingestion failed: {str(e)}",
        )

    ms = round((time.time() - start) * 1000, 2)
    analytics.track("/upload", file.filename, ms)

    return UploadResponse(
        success=True, filename=file.filename,
        vectors_added=vectors_added,
        message=f"File '{file.filename}' uploaded and ingested successfully.",
    )
