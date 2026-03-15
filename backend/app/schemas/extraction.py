from __future__ import annotations

from pydantic import BaseModel


class Evidence(BaseModel):
    # da dove viene l'evidenza: per ora solo OCR
    source: str = "ocr"
    # testo "umano" che giustifica il valore (es: la riga dove compare totale)
    snippet: str | None = None
    # bbox in pixel [x1, y1, x2, y2]
    bbox: list[int] | None = None
    # pagina (1-based) se disponibile
    page_index: int | None = None


class ExtractedField(BaseModel):
    value: str | None
    confidence: float
    evidence: Evidence | None = None


class DocumentExtractionResponse(BaseModel):
    document_id: str
    extraction_version: str = "rule_v0"
    needs_review: bool
    fields: dict[str, ExtractedField]
