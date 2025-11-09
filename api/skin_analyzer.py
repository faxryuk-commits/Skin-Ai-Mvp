import base64
import io
import json
import os
import uuid
from pathlib import Path
from typing import Any, Dict

import numpy as np
from dotenv import load_dotenv
from openai import AsyncOpenAI
from PIL import Image

from prompts import JSON_SCHEMA, SYSTEM_PROMPT

try:
    import cv2  # type: ignore
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("opencv-python-headless не установлен. Добавьте его в зависимости.") from exc


BASE_DIR = Path(__file__).resolve().parent
RULES_PATH = BASE_DIR / "rules" / "product_rules.json"


with RULES_PATH.open("r", encoding="utf-8") as fh:
    PRODUCT_RULES: Dict[str, Dict[str, Any]] = json.load(fh)


load_dotenv()

client = AsyncOpenAI()


def _ensure_quality(image: Image.Image) -> None:
    arr = np.array(image.convert("L"))
    mean_brightness = float(arr.mean())
    variance = float(arr.var())
    if mean_brightness < 35 or variance < 150:
        raise ValueError("bad_quality")


def _compute_metrics(image: Image.Image) -> Dict[str, float]:
    rgb = np.array(image.convert("RGB"))
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    laplace_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())

    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    h, s, v = cv2.split(hsv)

    redness_mask = (h < 10) | (h > 170)
    redness_proxy = float(np.mean(s[redness_mask])) if np.any(redness_mask) else float(np.mean(s))
    oil_proxy = float(np.mean(v > 220))

    contrast = float(np.std(v))

    return {
        "texture_laplacian_var": laplace_var,
        "redness_proxy": redness_proxy,
        "oil_proxy": oil_proxy,
        "luma_contrast": contrast,
    }


def _merge_with_rules(result: Dict[str, Any]) -> Dict[str, Any]:
    skin_type = (result.get("skin_type") or "").lower()
    mapping = PRODUCT_RULES.get(skin_type)
    if not mapping:
        return result

    result.setdefault("ingredients", [])
    result.setdefault("product_classes", [])

    for item in mapping.get("ingredients", []):
        if item not in result["ingredients"]:
            result["ingredients"].append(item)

    for item in mapping.get("product_classes", []):
        if item not in result["product_classes"]:
            result["product_classes"].append(item)

    return result


async def _call_gpt(metrics: Dict[str, float], image_bytes: bytes) -> Dict[str, Any]:
    b64_image = base64.b64encode(image_bytes).decode("utf-8")
    selected_model = os.getenv("OPENAI_MODEL_VISION", "gpt-4o-mini")

    response = await client.responses.create(
        model=selected_model,
        temperature=0.2,
        response_format={"type": "json_schema", "json_schema": JSON_SCHEMA},
        input=[
            {"role": "system", "content": [{"type": "input_text", "text": SYSTEM_PROMPT}]},
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "Analyze this face for skin profile."},
                    {
                        "type": "input_image",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"},
                    },
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": f"Reference metrics: {json.dumps(metrics, ensure_ascii=False)}",
                    }
                ],
            },
        ],
    )

    if hasattr(response, "output_text"):
        raw = response.output_text  # type: ignore[attr-defined]
    else:
        raw = response.output[0].content[0].text  # type: ignore[index]
    return json.loads(raw)


async def analyze_image(image_bytes: bytes, user_id: str) -> Dict[str, Any]:
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    _ensure_quality(image)

    metrics = _compute_metrics(image)
    ai_result = await _call_gpt(metrics, image_bytes)

    ai_result["id"] = str(uuid.uuid4())
    ai_result["metrics"] = metrics
    ai_result["user_id"] = user_id

    merged = _merge_with_rules(ai_result)
    return merged

