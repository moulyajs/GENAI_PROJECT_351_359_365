import os
from typing import Dict, Optional

import fitz  # PyMuPDF
import docx
from app.input.preprocessing import clean_text

DOCUMENT_EXTENSIONS = {".pdf", ".docx", ".txt"}


def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    try:
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        print(f"[PDF Extraction Error] {e}")
    return text


def extract_text_from_docx(file_path: str) -> str:
    text = ""
    try:
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"[DOCX Extraction Error] {e}")
    return text


def extract_text_from_txt(file_path: str) -> str:
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        print(f"[TXT Extraction Error] {e}")
        return ""


def detect_prompt_injection(text: str) -> Optional[str]:
    """
    Basic rule-based detection for indirect prompt injection patterns
    """
    suspicious_patterns = [
        "ignore previous instructions",
        "override system",
        "act as",
        "you are now",
        "execute this",
        "bypass",
        "system prompt",
        "do anything now",
    ]

    detected = []
    for pattern in suspicious_patterns:
        if pattern in text:
            detected.append(pattern)

    return ", ".join(detected) if detected else None


def extract_text_from_document(file_path: str) -> Optional[Dict]:
    if not os.path.isfile(file_path):
        print(f"[DocumentHandler] File not found: {file_path}")
        return None

    ext = os.path.splitext(file_path)[1].lower()
    raw_text = ""

    if ext == ".pdf":
        raw_text = extract_text_from_pdf(file_path)
    elif ext == ".docx":
        raw_text = extract_text_from_docx(file_path)
    elif ext == ".txt":
        raw_text = extract_text_from_txt(file_path)
    else:
        print(f"[DocumentHandler] Unsupported file type: {ext}")
        return None

    cleaned_text = clean_text(raw_text)

    prompt_injection = detect_prompt_injection(cleaned_text)

    return {
        "raw_text": raw_text,
        "cleaned_text": cleaned_text,
        "prompt_found": cleaned_text,
        "injection_detected": prompt_injection,
        "has_text": bool(cleaned_text.strip()),
    }