from __future__ import annotations

from app.extraction.rule_v0 import extract_fields_rule_v0


def test_extract_rule_v0_happy_path():
    # OCR JSON minimale (una pagina)
    ocr_json = {
        "engine": "fake",
        "pages": [
            {
                "page_index": 1,
                "full_text": "COOP\nTOTALE 12,34 EUR\n27/06/2019 11:52\n",
                "items": [
                    {"text": "TOTALE", "confidence": 0.9, "bbox": [0, 0, 10, 10], "line_key": "1:1:1:1"},
                    {"text": "12,34", "confidence": 0.85, "bbox": [12, 0, 30, 10], "line_key": "1:1:1:1"},
                    {"text": "EUR", "confidence": 0.9, "bbox": [32, 0, 45, 10], "line_key": "1:1:1:1"},
                ],
            }
        ],
    }

    out = extract_fields_rule_v0(ocr_json)
    fields = out["fields"]

    assert fields["merchant"]["value"] == "COOP"
    assert fields["currency"]["value"] == "EUR"
    assert fields["date"]["value"] == "2019-06-27"
    assert fields["total"]["value"] == "12.34"
    assert fields["total"]["confidence"] >= 0.5
