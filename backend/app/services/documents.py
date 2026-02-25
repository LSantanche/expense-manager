from __future__ import annotations

from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.document import Document
from app.ocr.pdf_render import render_pdf_to_images
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

    try:
        abs_input = settings.storage_path / Path(doc.storage_path)
        engine = TesseractOcrEngine()

        pages_payload = []
        full_text_pages = []

        if doc.mime_type.startswith("image/"):
            result = engine.extract_from_image(abs_input)
            pages_payload.append(
                {
                    "page_index": 1,
                    "full_text": result.full_text,
                    "items": [
                        {"text": it.text, "confidence": it.confidence, "bbox": it.bbox, "line_key": it.line_key}
                        for it in result.items
                    ],
                }
            )
            full_text_pages.append(result.full_text)

        elif doc.mime_type == "application/pdf":
            pil_pages = render_pdf_to_images(abs_input, scale=2.0)

            for idx, pil_img in enumerate(pil_pages, start=1):
                page_res = engine.extract_from_pil(pil_img, page_index=idx)
                pages_payload.append(
                    {
                        "page_index": idx,
                        "full_text": page_res.full_text,
                        "items": [
                            {"text": it.text, "confidence": it.confidence, "bbox": it.bbox, "line_key": it.line_key}
                            for it in page_res.items
                        ],
                    }
                )
                full_text_pages.append(page_res.full_text)

        else:
            doc.status = "failed"
            doc.error_message = f"Unsupported mime_type for OCR: {doc.mime_type}"
            db.add(doc)
            db.commit()
            db.refresh(doc)
            return doc

        doc_dir = settings.storage_path / "documents" / doc.id
        ocr_path = doc_dir / "ocr_result.json"

        ocr_payload = {
            "engine": "tesseract",
            "pages": pages_payload,
        }

        ocr_path.write_text(
            __import__("json").dumps(ocr_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        rel_ocr_path = str(Path(settings.storage_dir) / "documents" / doc.id / "ocr_result.json")

        # Aggregazione testo: separatore tra pagine
        aggregated = "\n\n----- PAGE BREAK -----\n\n".join(full_text_pages)

        doc.ocr_text_plain = aggregated
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
