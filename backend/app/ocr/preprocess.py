from __future__ import annotations

from PIL import Image, ImageEnhance, ImageOps


def preprocess_for_tesseract(img: Image.Image) -> Image.Image:
    """
    Preprocessing semplice per migliorare OCR su ricevute:
    - converte in grayscale
    - aumenta contrasto
    - binarizza (bianco/nero) con threshold fisso (v0)
    - upscale se l'immagine è piccola
    """
    # Converti in grayscale
    gray = img.convert("L")

    # Autocontrast aiuta su foto "spente"
    gray = ImageOps.autocontrast(gray)

    # Aumenta leggermente il contrasto
    gray = ImageEnhance.Contrast(gray).enhance(1.5)

    # Upscale se è piccola (testo più leggibile)
    w, h = gray.size
    if w < 1000:
        scale = 2
        gray = gray.resize((w * scale, h * scale))

    # Binarizzazione semplice (threshold)
    # 160 è un compromesso: lo renderemo configurabile/tunable dopo.
    bw = gray.point(lambda x: 255 if x > 160 else 0, mode="1")

    # Torniamo in "L" per compatibilità con pytesseract
    return bw.convert("L")
