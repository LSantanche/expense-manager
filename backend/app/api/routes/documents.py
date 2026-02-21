from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.core.config import settings
from app.schemas.document import DocumentUploadResponse
from app.storage import is_allowed_mime, save_uploaded_document

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentUploadResponse)
def upload_document(file: UploadFile = File(...)) -> DocumentUploadResponse:
    mime_type = file.content_type or ""
    if not is_allowed_mime(mime_type):
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported media type: {mime_type}. Allowed: images/*, application/pdf",
        )

    payload = save_uploaded_document(base_dir=settings.storage_path, upload=file)
    return DocumentUploadResponse(**payload)
