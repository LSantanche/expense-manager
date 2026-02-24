from __future__ import annotations

import math

import cv2
import numpy as np
from PIL import Image


def _pil_to_cv_gray(img: Image.Image) -> np.ndarray:
    """Converte PIL -> OpenCV grayscale (uint8)."""
    arr = np.array(img.convert("RGB"))
    bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    return gray


def _cv_gray_to_pil(gray: np.ndarray) -> Image.Image:
    """Converte OpenCV grayscale -> PIL."""
    return Image.fromarray(gray)


def _estimate_skew_angle(gray: np.ndarray) -> float:
    """
    Stima angolo di skew (in gradi) usando Hough su bordi.
    Ritorna un angolo piccolo tipo [-15, +15] se trova linee.
    """
    edges = cv2.Canny(gray, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, math.pi / 180.0, threshold=80, minLineLength=100, maxLineGap=10)
    if lines is None:
        return 0.0

    angles = []
    for x1, y1, x2, y2 in lines[:, 0]:
        dx = x2 - x1
        dy = y2 - y1
        if dx == 0:
            continue
        angle = math.degrees(math.atan2(dy, dx))
        # Filtra linee quasi verticali
        if -45 < angle < 45:
            angles.append(angle)

    if not angles:
        return 0.0

    # Mediana è più robusta di media
    return float(np.median(np.array(angles)))


def _deskew(gray: np.ndarray) -> np.ndarray:
    angle = _estimate_skew_angle(gray)
    if abs(angle) < 0.5:
        return gray

    (h, w) = gray.shape[:2]
    center = (w // 2, h // 2)

    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated


def preprocess_for_tesseract(img: Image.Image) -> Image.Image:
    """
    Preprocessing v1:
    - grayscale
    - denoise leggero
    - deskew (raddrizza)
    - threshold Otsu (automatico)
    - (opzionale) upscale se piccola
    """
    gray = _pil_to_cv_gray(img)

    # Upscale se l'immagine è piccola (testo più leggibile)
    h, w = gray.shape[:2]
    if w < 1000:
        gray = cv2.resize(gray, (w * 2, h * 2), interpolation=cv2.INTER_CUBIC)

    # Denoise leggero
    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    # Deskew
    gray = _deskew(gray)

    # Threshold automatico Otsu
    _, thr = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return _cv_gray_to_pil(thr)
