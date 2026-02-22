from __future__ import annotations

from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    document_id: str
    original_filename: str
    mime_type: str
    size_bytes: int
    sha256: str
    stored_relative_path: str
    created_at: str


class DocumentRead(DocumentUploadResponse):
    status: str
    ocr_text_plain: str | None = None
    ocr_json_path: str | None = None
    error_message: str | None = None
