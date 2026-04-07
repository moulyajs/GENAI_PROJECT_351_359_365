import os
import uuid
from datetime import datetime
from typing import Any, Dict

from app.input.image_handler import extract_text_from_image_path

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff", ".tif"}

def _is_image_path(value: Any) -> bool:
    return (
        isinstance(value, str)
        and os.path.isfile(value)
        and os.path.splitext(value)[1].lower() in IMAGE_EXTENSIONS
    )

def handle_input(user_input: Any) -> Dict:
    image_data = None
    if isinstance(user_input, dict) and "image_path" in user_input:
        image_path = user_input["image_path"]
        image_data = extract_text_from_image_path(image_path)
        prompt = image_data.get("prompt_found", "") if image_data else ""
        mode = "image"
    elif _is_image_path(user_input):
        image_data = extract_text_from_image_path(user_input)
        prompt = image_data.get("prompt_found", "") if image_data else ""
        mode = "image"
    else:
        prompt = str(user_input)
        mode = "text"

    return {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "prompt": prompt,
        "mode": mode,
        "image_data": image_data,
    }