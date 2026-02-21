from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.document import Document


def create_document(
    db: Session,
    *,
    document_id: str,
    original_filename: str,
    mime_type: str,
    storage_path: str,
    sha256: str,
    size_bytes: int,
) -> Document:
    doc = Document(
        id=document_id,
        original_filename=original_filename,
        mime_type=mime_type,
        storage_path=storage_path,
        sha256=sha256,
        size_bytes=size_bytes,
        status="uploaded",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def get_document(db: Session, document_id: str) -> Document | None:
    return db.get(Document, document_id)
