from __future__ import annotations

from pathlib import Path

import pytesseract
from PIL import Image

from app.core.config import settings
from app.ocr.preprocess import preprocess_for_tesseract


def ocr_plain(img: Image.Image) -> str:
    # OCR "grezzo" (senza preprocessing)
    config = "--psm 6"
    return pytesseract.image_to_string(img, lang=settings.tesseract_lang, config=config)


def main() -> None:
    # Se serve il path a tesseract.exe
    if settings.tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd

    samples_dir = Path("scripts") / "samples"
    paths = sorted(samples_dir.glob("*.*"))

    if not paths:
        print("Nessun sample trovato. Metti 3-5 immagini in backend/scripts/samples/")
        return

    for p in paths:
        img = Image.open(p)

        before = ocr_plain(img)
        after = ocr_plain(preprocess_for_tesseract(img))

        before_words = len(before.split())
        after_words = len(after.split())

        print("=" * 80)
        print(f"FILE: {p.name}")
        print(f"WORDS before={before_words} after={after_words}")

        # Mostriamo i primi 300 caratteri per confronto rapido
        print("--- BEFORE (first 300 chars) ---")
        print(before[:300].replace("\n", "\\n"))
        print("--- AFTER  (first 300 chars) ---")
        print(after[:300].replace("\n", "\\n"))


if __name__ == "__main__":
    main()
