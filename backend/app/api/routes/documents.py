from __future__ import annotations

import json
from pathlib import Path as SysPath

from fastapi import APIRouter, Depends, File, HTTPException, Path, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db import get_db
from app.schemas.document import DocumentRead
from app.services.documents import create_document, get_document, process_document_ocr
from app.storage import is_allowed_mime, save_uploaded_document

router = APIRouter(prefix="/documents", tags=["documents"])
db_dep = Depends(get_db)

@router.post("/upload", response_model=DocumentRead)
def upload_document(file: UploadFile = File(...), db: Session = db_dep) -> DocumentRead:
    mime_type = file.content_type or ""
    if not is_allowed_mime(mime_type):
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported media type: {mime_type}. Allowed: images/*, application/pdf",
        )

    saved = save_uploaded_document(base_dir=settings.storage_path, upload=file)

    doc = create_document(
        db,
        document_id=saved["document_id"],
        original_filename=saved["original_filename"],
        mime_type=saved["mime_type"],
        storage_path=saved["stored_relative_path"],
        sha256=saved["sha256"],
        size_bytes=saved["size_bytes"],
    )

    return DocumentRead(**saved, status=doc.status)

@router.get("/{document_id}", response_model=DocumentRead)
def read_document(
    document_id: str = Path(..., min_length=36, max_length=36),
    db: Session = db_dep,
) -> DocumentRead:
    doc = get_document(db, document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")

    return DocumentRead(
        document_id=doc.id,
        original_filename=doc.original_filename,
        mime_type=doc.mime_type,
        size_bytes=doc.size_bytes,
        sha256=doc.sha256,
        stored_relative_path=doc.storage_path,
        created_at=doc.created_at.isoformat(),
        status=doc.status,
        ocr_text_plain=doc.ocr_text_plain,
        ocr_json_path=doc.ocr_json_path,
        error_message=doc.error_message,
    )


@router.post("/{document_id}/process-ocr", response_model=DocumentRead)
def process_ocr(
    document_id: str = Path(..., min_length=36, max_length=36),
    db: Session = db_dep,
) -> DocumentRead:
    doc = process_document_ocr(db, document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")

    return DocumentRead(
        document_id=doc.id,
        original_filename=doc.original_filename,
        mime_type=doc.mime_type,
        size_bytes=doc.size_bytes,
        sha256=doc.sha256,
        stored_relative_path=doc.storage_path,
        created_at=doc.created_at.isoformat(),
        status=doc.status,
        ocr_text_plain=doc.ocr_text_plain,
        ocr_json_path=doc.ocr_json_path,
        error_message=doc.error_message,
    )

@router.get("/{document_id}/ocr-json")
def get_ocr_json(
    document_id: str = Path(..., min_length=36, max_length=36),
    db: Session = db_dep,
) -> JSONResponse:
    doc = get_document(db, document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc.status != "processed" or not doc.ocr_json_path:
        raise HTTPException(
            status_code=409,
            detail="OCR not available for this document (status is not processed)",
        )

    abs_json = settings.storage_path.parent / SysPath(doc.ocr_json_path)
    if not abs_json.exists():
        raise HTTPException(status_code=404, detail="OCR JSON file not found on disk")

    payload = json.loads(abs_json.read_text(encoding="utf-8"))
    return JSONResponse(content=payload)


