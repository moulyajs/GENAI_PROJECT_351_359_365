import os
import tempfile
from typing import Dict, Optional

import cv2
import numpy as np
import pytesseract # type: ignore
import piexif # type: ignore
from PIL import Image
from stegano import lsb  # type: ignore

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff", ".tif"}

def _configure_tesseract() -> None:
    if os.name == "nt":
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    elif os.name == "posix":
        if os.path.exists("/usr/bin/tesseract"):
            pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
        elif os.path.exists("/usr/local/bin/tesseract"):
            pytesseract.pytesseract.tesseract_cmd = "/usr/local/bin/tesseract"

def preprocess_image_pil(pil_img: Image.Image) -> Image.Image:
    img = np.array(pil_img)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    img = cv2.convertScaleAbs(img, alpha=1.5, beta=0)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )

    kernel = np.ones((1, 1), np.uint8)
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

    return Image.fromarray(cleaned)

def extract_ocr_text(pil_image: Image.Image, lang: str = "eng") -> str:
    try:
        _configure_tesseract()
        processed_image = preprocess_image_pil(pil_image)
        extracted_text = pytesseract.image_to_string(processed_image, lang=lang).strip()
        return extracted_text if extracted_text else ""
    except Exception as e:
        print(f"[OCR Extraction Error] {e}")
        return ""

def extract_hidden_text(image_file_name: str, pil_image: Image.Image) -> str:
    ext = os.path.splitext(image_file_name)[1].lower()
    if ext != ".png":
        return ""

    try:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            pil_image.save(tmp.name, format="PNG")
            temp_path = tmp.name

        hidden = lsb.reveal(temp_path)

        try:
            os.unlink(temp_path)
        except Exception:
            pass

        return hidden if hidden else ""
    except Exception as e:
        print(f"[HiddenText Extraction Error] {e}")
        return ""

def extract_metadata(image_file_name: str, pil_image: Image.Image) -> str:
    ext = os.path.splitext(image_file_name)[1].lower()

    if ext == ".png":
        try:
            info = pil_image.info
            if info:
                return str(info.get("Description", "")).strip()
            return ""
        except Exception as e:
            print(f"[PNG Metadata Error] {e}")
            return ""

    elif ext in [".jpg", ".jpeg"]:
        try:
            exif_data = piexif.load(image_file_name)
            desc_bytes = exif_data["0th"].get(piexif.ImageIFD.ImageDescription, b"")
            if not desc_bytes:
                return ""
            desc = desc_bytes.decode("utf-8", errors="ignore").strip()
            return desc
        except Exception as e:
            print(f"[JPEG Metadata Error] {e}")
            return ""

    return ""

def run_all_retrievals(image_file_name: str, pil_image: Image.Image) -> Optional[Dict]:
    results = {
        "ocr_text": "",
        "hidden_text": "",
        "metadata_text": "",
        "prompt_found": None,
        "has_text": False,
    }

    try:
        ocr_text = extract_ocr_text(pil_image)
        if ocr_text:
            results["ocr_text"] = ocr_text
            results["has_text"] = True

        hidden_text = extract_hidden_text(image_file_name, pil_image)
        if hidden_text:
            results["hidden_text"] = hidden_text
            results["has_text"] = True

        metadata_text = extract_metadata(image_file_name, pil_image)
        if metadata_text:
            results["metadata_text"] = metadata_text
            results["has_text"] = True

        if results["has_text"]:
            all_texts = []
            if results["metadata_text"]:
                all_texts.append(results["metadata_text"])
            if results["hidden_text"]:
                all_texts.append(results["hidden_text"])
            if results["ocr_text"]:
                all_texts.append(results["ocr_text"])

            results["prompt_found"] = " ".join(all_texts)

        return results
    except Exception as e:
        print(f"[Error in run_all_retrievals] {e}")
        return None

def extract_text_from_image_path(image_file_name: str) -> Optional[Dict]:
    if not os.path.isfile(image_file_name):
        print(f"[ImageHandler] File not found: {image_file_name}")
        return None

    try:
        with Image.open(image_file_name) as pil_image:
            pil_image = pil_image.convert("RGB")
            return run_all_retrievals(image_file_name, pil_image)
    except Exception as e:
        print(f"[ImageHandler] Failed to open image {image_file_name}: {e}")
        return None
