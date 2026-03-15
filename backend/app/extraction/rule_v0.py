from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any

"""
Estrattore a regole: prende l'output OCR (che è un JSON con testo + bbox + confidence) 
e prova a tirare fuori 4 campi:
- merchant
- currency
- date
- total

Restituisce anche una confidence, una evidence (snippet di testo e, quando possibile, bbox e numero pagina) 
e una flag needs_review
"""

# --- Tipi interni -------------------------------------------------------------

@dataclass
class OcrToken:
    # Una parola o un token dell'OCR
    text: str
    confidence: float
    bbox: list[int] | None
    line_key: str | None


@dataclass
class OcrPage:
    # Una pagina del PDF
    page_index: int
    full_text: str
    tokens: list[OcrToken]


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def _safe_decimal(s: str) -> Decimal | None:
    # normalizza 1,60 -> 1.60
    norm = s.replace(",", ".")
    try:
        return Decimal(norm)
    except (InvalidOperation, ValueError):
        return None


def _normalize_currency(text: str) -> str | None:
    t = text.upper()
    if "EUR" in t or "€" in t:
        return "EUR"
    if "USD" in t or "$" in t:
        return "USD"
    if "GBP" in t or "£" in t:
        return "GBP"
    return None


def _parse_date_candidate(s: str) -> date | None:
    # supporto base: dd-mm-yyyy, dd/mm/yyyy, yyyy-mm-dd
    m = re.search(r"\b(\d{2})[/-](\d{2})[/-](\d{4})\b", s)
    if m:
        dd, mm, yyyy = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            return date(yyyy, mm, dd)
        except ValueError:
            return None

    m = re.search(r"\b(\d{4})[/-](\d{2})[/-](\d{2})\b", s)
    if m:
        yyyy, mm, dd = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            return date(yyyy, mm, dd)
        except ValueError:
            return None

    return None


def _union_bbox(b1: list[int] | None, b2: list[int] | None) -> list[int] | None:
    # Serve ad unire token che contengono parti dello stesso valore (es. "12" e ".25" deve diventare "12.25")
    if not b1:
        return b2
    if not b2:
        return b1
    return [min(b1[0], b2[0]), min(b1[1], b2[1]), max(b1[2], b2[2]), max(b1[3], b2[3])]


def _load_ocr_pages(ocr_json: dict[str, Any]) -> list[OcrPage]:
    """
    Trasforma il JSON OCR, che è un dizionario complesso, in una 
    lista di OcrPage con OcrToken.
    """
    pages_raw = ocr_json.get("pages") or []
    pages: list[OcrPage] = []

    for p in pages_raw:
        page_index = int(p.get("page_index", 1))
        full_text = str(p.get("full_text") or "")
        items = p.get("items") or []
        tokens: list[OcrToken] = []
        for it in items:
            tokens.append(
                OcrToken(
                    text=str(it.get("text") or ""),
                    confidence=float(it.get("confidence") or 0.0),
                    bbox=it.get("bbox"),
                    line_key=it.get("line_key"),
                )
            )
        pages.append(OcrPage(page_index=page_index, full_text=full_text, tokens=tokens))

    return pages


# --- Estrazione campi ---------------------------------------------------------

TOTAL_KEYWORDS = [
    "TOTALE",
    "TOT",
    "TOT.",
    "TOT.COMPLESSIVO",
    "IMPORTO",
    "TOTAL",
    "AMOUNT",
]

MERCHANT_STOP = {
    "DOCUMENTO",
    "DOCUMENTO COMMERCIALE",
    "RICEVUTA",
    "SCONTRINO",
    "FATTURA",
}


def extract_fields_rule_v0(ocr_json: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """
    Ritorna un dict "flat" con chiavi:
    - total, currency, date, merchant
    Ogni valore è un dict: {value, confidence, evidence{snippet,bbox,page_index}}
    """
    pages = _load_ocr_pages(ocr_json) # Carica pagine e token

    # --- Merchant: prima riga "sensata" del testo della prima pagina
    merchant_val: str | None = None
    merchant_conf = 0.3
    merchant_evidence = None

    if pages:
        lines = [ln.strip() for ln in pages[0].full_text.splitlines() if ln.strip()]
        for ln in lines[:10]: # Per cercare merchant che spesso sta all'inizio dello scontrino
            up = ln.upper()
            if up in MERCHANT_STOP:
                continue
            # evita righe troppo lunghe (di solito non sono merchant)
            if 2 <= len(ln) <= 40:
                merchant_val = ln
                merchant_conf = 0.6
                merchant_evidence = {"snippet": ln, "bbox": None, "page_index": pages[0].page_index}
                break

    # --- Currency: cerca EUR/€ ecc. nel testo aggregato
    currency_val: str | None = None
    currency_conf = 0.2
    currency_evidence = None

    for pg in pages:
        cur = _normalize_currency(pg.full_text)
        if cur:
            currency_val = cur
            currency_conf = 0.7
            currency_evidence = {"snippet": cur, "bbox": None, "page_index": pg.page_index}
            break

    # --- Date: prima data valida trovata nel testo (euristica v0)
    date_val: str | None = None
    date_conf = 0.2
    date_evidence = None

    for pg in pages:
        d = _parse_date_candidate(pg.full_text)
        if d:
            date_val = d.isoformat()
            date_conf = 0.75
            date_evidence = {"snippet": d.isoformat(), "bbox": None, "page_index": pg.page_index}
            break

    # --- Total: cerca righe con keyword + importo
    total_val: str | None = None
    total_conf = 0.2
    total_evidence = None

    amount_re = re.compile(r"\b(\d+[.,]\d{2})\b") # Numero "," o "." numero

    best_score = -1.0
    best_amount: Decimal | None = None
    best_snippet = None
    best_bbox = None
    best_page = None

    for pg in pages:
        lines = pg.full_text.splitlines()
        for ln in lines:
            ln_stripped = ln.strip()
            if not ln_stripped:
                continue
            up = ln_stripped.upper()

            has_kw = any(k in up for k in TOTAL_KEYWORDS)
            m = amount_re.search(ln_stripped)
            if not m:
                continue

            amt = _safe_decimal(m.group(1))
            if amt is None:
                continue

            # score semplice: keyword + importo grande (spesso totale è uno dei più grandi)
            score = 0.0
            if has_kw:
                score += 1.0
            # importo: leggero bias verso importi più grandi (cap per non esplodere)
            score += min(float(amt), 999.0) / 999.0 * 0.2

            # provo a trovare bbox del token importo nella pagina
            bbox = None
            ocr_conf = 0.0
            for tok in pg.tokens:
                if tok.text.strip() == m.group(1):
                    bbox = _union_bbox(bbox, tok.bbox)
                    ocr_conf = max(ocr_conf, tok.confidence)

            # integro conf OCR (se c'è)
            score += ocr_conf * 0.3

            if score > best_score:
                best_score = score
                best_amount = amt
                best_snippet = ln_stripped
                best_bbox = bbox
                best_page = pg.page_index

    if best_amount is not None:
        total_val = f"{best_amount:.2f}"
        # confidence: da score -> 0..1 (euristica)
        total_conf = _clamp01(0.5 + (best_score / 1.5) * 0.5)
        total_evidence = {"snippet": best_snippet, "bbox": best_bbox, "page_index": best_page}

    # needs_review: se manca total o date o confidence bassa
    needs_review = (
        total_val is None
        or date_val is None
        or total_conf < 0.7
        or date_conf < 0.7
    )

    return {
        "needs_review": needs_review,
        "fields": {
            "merchant": {"value": merchant_val, "confidence": _clamp01(merchant_conf), "evidence": merchant_evidence},
            "currency": {"value": currency_val, "confidence": _clamp01(currency_conf), "evidence": currency_evidence},
            "date": {"value": date_val, "confidence": _clamp01(date_conf), "evidence": date_evidence},
            "total": {"value": total_val, "confidence": _clamp01(total_conf), "evidence": total_evidence},
        },
    }
