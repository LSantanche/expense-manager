from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytesseract
from PIL import Image

from app.core.config import settings
from app.ocr.preprocess import preprocess_for_tesseract


@dataclass
class OcrItem:
    text: str
    confidence: float
    bbox: list[int]  # [x1, y1, x2, y2]
    line_key: str    # chiave utile per ricostruire righe (page/block/par/line)


@dataclass
class OcrResult:
    engine: str
    items: list[OcrItem]
    full_text: str


class TesseractOcrEngine:
    def __init__(self) -> None:
        # Se l'utente non ha messo tesseract nel PATH, può configurare TESSERACT_CMD
        # TESSERACT_CMD è il percorso a tesseract.exe. Tesseract è un wrapper quindi il vero 
        # OCR lo fa il programma esterno tesseract.exe
        if settings.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd
    
    def extract_from_pil(self, img: Image.Image, *, page_index: int = 1) -> OcrResult:
        img = preprocess_for_tesseract(img)

        config = "--psm 6"
        data: dict[str, Any] = pytesseract.image_to_data(
            img,
            lang=settings.tesseract_lang,
            config=config,
            output_type=pytesseract.Output.DICT,
        )

        items: list[OcrItem] = []
        lines: dict[str, list[tuple[int, str]]] = {}

        n = len(data.get("text", []))
        for i in range(n):
            txt = (data["text"][i] or "").strip()
            conf_raw = data["conf"][i]

            try:
                conf_int = int(float(conf_raw))
            except Exception:
                conf_int = -1

            if not txt or conf_int < 0:
                continue

            left = int(data["left"][i])
            top = int(data["top"][i])
            width = int(data["width"][i])
            height = int(data["height"][i])
            x1, y1, x2, y2 = left, top, left + width, top + height

            # Per PDF usiamo page_index passato dall'esterno
            block = data.get("block_num", [0])[i]
            par = data.get("par_num", [0])[i]
            line = data.get("line_num", [0])[i]
            word = data.get("word_num", [0])[i]

            line_key = f"{page_index}:{block}:{par}:{line}"

            items.append(
                OcrItem(
                    text=txt,
                    confidence=conf_int / 100.0,
                    bbox=[x1, y1, x2, y2],
                    line_key=line_key,
                )
            )
            lines.setdefault(line_key, []).append((int(word), txt))

        ordered_keys = sorted(lines.keys(), key=lambda k: [int(x) for x in k.split(":")])
        full_lines: list[str] = []
        for k in ordered_keys:
            words = [w for _, w in sorted(lines[k], key=lambda t: t[0])]
            full_lines.append(" ".join(words))

        return OcrResult(engine="tesseract", items=items, full_text="\n".join(full_lines))


    def extract_from_image(self, image_path: Path) -> OcrResult:
        img = Image.open(image_path)
        return self.extract_from_pil(img, page_index=1)
