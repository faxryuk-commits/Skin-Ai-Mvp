"""
Вспомогательные функции для распознавания лица и ROI.

Пока что здесь заглушки — в v1.1 можно подключить Mediapipe Face Mesh.
"""

from typing import Tuple

import numpy as np


def detect_face_bbox(image: np.ndarray) -> Tuple[int, int, int, int]:
    """
    Возвращает приблизительную рамку лица.
    Сейчас метод — заглушка по центру кадра.
    """
    h, w, _ = image.shape
    box_w = int(w * 0.6)
    box_h = int(h * 0.6)
    x1 = (w - box_w) // 2
    y1 = (h - box_h) // 2
    return x1, y1, x1 + box_w, y1 + box_h

