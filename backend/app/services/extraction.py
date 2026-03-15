from __future__ import annotations

import json
from pathlib import Path as SysPath

from sqlalchemy.orm import Session

from app.core.config import settings
from app.extraction.rule_v0 import extract_fields_rule_v0
from app.models.document import Document
from app.schemas.extraction import DocumentExtractionResponse, Evidence, ExtractedField


def extract_fields_for_document(db: Session, document_id: str) -> DocumentExtractionResponse | None:
    doc = db.get(Document, document_id)
    if doc is None:
        return None

    if doc.status != "processed" or not doc.ocr_json_path:
        # non pronto
        return DocumentExtractionResponse(
            document_id=doc.id,
            needs_review=True,
            fields={
                "total": ExtractedField(value=None, confidence=0.0),
                "currency": ExtractedField(value=None, confidence=0.0),
                "date": ExtractedField(value=None, confidence=0.0),
                "merchant": ExtractedField(value=None, confidence=0.0),
            },
        )

    # Path assoluto al JSON OCR (compatibilità: vecchi record con prefisso "data\\...")
    p = SysPath(doc.ocr_json_path)
    if str(p).lower().startswith("data\\") or str(p).lower().startswith("data/"):
        abs_json = settings.storage_path.parent / p
    else:
        abs_json = settings.storage_path / p

    ocr_json = json.loads(abs_json.read_text(encoding="utf-8"))
    out = extract_fields_rule_v0(ocr_json)

    fields: dict[str, ExtractedField] = {}
    for k, v in out["fields"].items():
        ev = v.get("evidence")
        fields[k] = ExtractedField(
            value=v.get("value"),
            confidence=float(v.get("confidence", 0.0)),
            evidence=Evidence(
                source="ocr",
                snippet=(ev or {}).get("snippet"),
                bbox=(ev or {}).get("bbox"),
                page_index=(ev or {}).get("page_index"),
            ) if ev else None,
        )

    return DocumentExtractionResponse(
        document_id=doc.id,
        needs_review=bool(out["needs_review"]),
        fields=fields,
    )
