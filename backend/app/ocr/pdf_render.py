from __future__ import annotations

from pathlib import Path

import pypdfium2 as pdfium
from PIL import Image


def render_pdf_to_images(pdf_path: Path, *, scale: float = 2.0) -> list[Image.Image]:
    """Converte un PDF in una lista di immagini PIL (una per pagina)."""
    pdf = pdfium.PdfDocument(str(pdf_path))
    images: list[Image.Image] = []

    for i in range(len(pdf)):
        page = pdf[i]
        bitmap = page.render(scale=scale)
        images.append(bitmap.to_pil())

    return images
