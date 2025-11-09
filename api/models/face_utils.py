"""
Вспомогательные функции для поиска лица и работы с ROI.
"""

from typing import Optional, Tuple

import cv2
import mediapipe as mp
import numpy as np


_FACE_DETECTION = mp.solutions.face_detection.FaceDetection


def detect_face_bbox(
    image: np.ndarray,
    min_confidence: float = 0.5,
    padding_ratio: float = 0.25,
) -> Optional[Tuple[int, int, int, int]]:
    """
    Возвращает рамку лица в пикселях (x1, y1, x2, y2). Если лицо не найдено — None.
    padding_ratio добавляет поля вокруг лица, чтобы сохранить пропорции.
    """
    if image.ndim != 3:
        raise ValueError("Ожидалось цветное изображение для распознавания лица.")

    height, width, _ = image.shape

    with _FACE_DETECTION(model_selection=1, min_detection_confidence=min_confidence) as detector:
        rgb_to_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        results = detector.process(rgb_to_bgr)

    if not results.detections:
        return None

    detection = max(results.detections, key=lambda det: det.score[0] if det.score else 0.0)
    bbox = detection.location_data.relative_bounding_box

    x1 = max(int(bbox.xmin * width), 0)
    y1 = max(int(bbox.ymin * height), 0)
    x2 = min(int((bbox.xmin + bbox.width) * width), width)
    y2 = min(int((bbox.ymin + bbox.height) * height), height)

    # Добавляем поля вокруг лица
    face_w = x2 - x1
    face_h = y2 - y1
    pad_w = int(face_w * padding_ratio)
    pad_h = int(face_h * padding_ratio)

    x1 = max(x1 - pad_w, 0)
    y1 = max(y1 - pad_h, 0)
    x2 = min(x2 + pad_w, width)
    y2 = min(y2 + pad_h, height)

    if x2 - x1 <= 0 or y2 - y1 <= 0:
        return None

    return x1, y1, x2, y2

