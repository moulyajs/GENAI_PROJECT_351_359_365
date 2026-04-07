import os
import uuid
from datetime import datetime
from typing import Any, Dict

from app.input.image_handler import extract_text_from_image_path
from app.input.document_handler import extract_text_from_document

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff", ".tif"}
DOCUMENT_EXTENSIONS = {".pdf", ".docx", ".txt"}


def _is_image_path(value: Any) -> bool:
    return (
        isinstance(value, str)
        and os.path.isfile(value)
        and os.path.splitext(value)[1].lower() in IMAGE_EXTENSIONS
    )


def _is_document_path(value: Any) -> bool:
    return (
        isinstance(value, str)
        and os.path.isfile(value)
        and os.path.splitext(value)[1].lower() in DOCUMENT_EXTENSIONS
    )


def handle_input(user_input: Any) -> Dict:
    image_data = None
    document_data = None

    # Case 1: Dictionary input
    if isinstance(user_input, dict):
        if "image_path" in user_input:
            image_path = user_input["image_path"]
            image_data = extract_text_from_image_path(image_path)
            prompt = image_data.get("prompt_found", "") if image_data else ""
            mode = "image"

        elif "document_path" in user_input:
            doc_path = user_input["document_path"]
            document_data = extract_text_from_document(doc_path)
            prompt = document_data.get("prompt_found", "") if document_data else ""
            mode = "document"

        else:
            prompt = str(user_input)
            mode = "text"

    # Case 2: Direct file path input
    elif _is_image_path(user_input):
        image_data = extract_text_from_image_path(user_input)
        prompt = image_data.get("prompt_found", "") if image_data else ""
        mode = "image"

    elif _is_document_path(user_input):
        document_data = extract_text_from_document(user_input)
        prompt = document_data.get("prompt_found", "") if document_data else ""
        mode = "document"

    # Case 3: Plain text input
    else:
        prompt = str(user_input)
        mode = "text"

    return {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now().isoformat(),
        "prompt": prompt,
        "mode": mode,
        "image_data": image_data,
        "document_data": document_data,
    }