from __future__ import annotations

import json
from pathlib import Path

import pytest


def _make_dummy_png(tmp_path: Path) -> Path:
    # File dummy: non serve che sia una PNG valida, perché nei test non facciamo OCR reale.
    # Però UploadFile salva bytes su disco: basta un contenuto qualsiasi.
    p = tmp_path / "dummy.png"
    p.write_bytes(b"not-a-real-png")
    return p


@pytest.fixture()
def temp_storage(tmp_path, monkeypatch):
    """
    Override della directory storage per non scrivere in backend/data.
    Usiamo una cartella temporanea pytest.
    """
    from app.core.config import settings

    monkeypatch.setattr(settings, "storage_dir", str(tmp_path.name), raising=False)
    # settings.storage_path usa BACKEND_DIR / storage_dir, quindi dobbiamo anche creare la cartella sotto backend/
    backend_dir = Path(__file__).resolve().parents[1]  # backend/
    storage_path = backend_dir / settings.storage_dir
    storage_path.mkdir(parents=True, exist_ok=True)
    return storage_path


@pytest.fixture()
def fake_ocr(monkeypatch):
    """
    Monkeypatch del Tesseract engine per rendere deterministico il risultato.
    """
    from app.ocr import tesseract_engine as te

    class FakeEngine:
        def extract_from_image(self, _path):
            return te.OcrResult(
                engine="fake",
                items=[
                    te.OcrItem(text="TOT", confidence=0.9, bbox=[0, 0, 10, 10], line_key="1:1:1:1"),
                    te.OcrItem(text="12.34", confidence=0.8, bbox=[12, 0, 30, 10], line_key="1:1:1:1"),
                ],
                full_text="TOT 12.34",
            )

        def extract_from_pil(self, _img, *, page_index=1):
            return self.extract_from_image(None)

    monkeypatch.setattr(te, "TesseractOcrEngine", FakeEngine)


def test_documents_upload_process_and_fetch_json(client, temp_storage, fake_ocr, tmp_path, monkeypatch):
    """
    Integration test API-first:
    upload -> process-ocr -> get ocr-json
    """
    # 1) upload
    dummy = _make_dummy_png(tmp_path)
    with dummy.open("rb") as f:
        resp = client.post(
            "/documents/upload",
            files={"file": ("dummy.png", f, "image/png")},
        )
    assert resp.status_code == 200
    data = resp.json()
    doc_id = data["document_id"]
    assert data["status"] == "uploaded"

    # 2) process-ocr
    resp = client.post(f"/documents/{doc_id}/process-ocr")
    assert resp.status_code == 200
    processed = resp.json()
    assert processed["status"] == "processed"
    assert processed["ocr_text_plain"] == "TOT 12.34"
    assert processed["ocr_json_path"] is not None

    # 3) fetch json
    resp = client.get(f"/documents/{doc_id}/ocr-json")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["engine"] in ("tesseract", "fake")  # nel nostro fake è "fake"
    assert "pages" in payload
    assert payload["pages"][0]["page_index"] == 1
    assert payload["pages"][0]["full_text"] == "TOT 12.34"
    assert len(payload["pages"][0]["items"]) == 2
