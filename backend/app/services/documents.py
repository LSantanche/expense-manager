from __future__ import annotations

from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.document import Document
from app.ocr.tesseract_engine import TesseractOcrEngine


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


def process_document_ocr(db: Session, document_id: str) -> Document | None:
    doc = db.get(Document, document_id)
    if doc is None:
        return None

    # In questo step supportiamo solo immagini
    if not doc.mime_type.startswith("image/"):
        doc.status = "failed"
        doc.error_message = "PDF non supportato ancora."
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc

    try:
        # storage_path è relativo a backend/ (es: data/documents/<id>/original.jpg)
        abs_input = settings.storage_path.parent / doc.storage_path

        engine = TesseractOcrEngine()
        result = engine.extract_from_image(abs_input)

        # Salviamo json nel folder del documento
        doc_dir = settings.storage_path / "documents" / doc.id
        ocr_path = doc_dir / "ocr_result.json"

        ocr_payload = {
            "engine": result.engine,
            "full_text": result.full_text,
            "items": [
                {
                    "text": it.text,
                    "confidence": it.confidence,
                    "bbox": it.bbox,
                    "line_key": it.line_key,
                }
                for it in result.items
            ],
        }
        ocr_path.write_text(
            __import__("json").dumps(ocr_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        # Path relativo coerente con storage_dir (tipicamente "data/...")
        rel_ocr_path = str(Path(settings.storage_dir) / "documents" / doc.id / "ocr_result.json")

        doc.ocr_text_plain = result.full_text
        doc.ocr_json_path = rel_ocr_path
        doc.error_message = None
        doc.status = "processed"

        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc

    except Exception as e:
        doc.status = "failed"
        doc.error_message = f"OCR failed: {type(e).__name__}: {e}"
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc
