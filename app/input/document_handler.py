import os
from typing import Dict, Optional

import fitz  # PyMuPDF
import docx
from app.input.preprocessing import clean_text

DOCUMENT_EXTENSIONS = {".pdf", ".docx", ".txt"}

# PDF Extraction
def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    try:
        with fitz.open(file_path) as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        print(f"[PDF Extraction Error] {e}")
    return text


# DOCX Extraction
def extract_text_from_docx(file_path: str) -> str:
    text = ""
    try:
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"[DOCX Extraction Error] {e}")
    return text


# TXT Extraction
def extract_text_from_txt(file_path: str) -> str:
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception as e:
        print(f"[TXT Extraction Error] {e}")
        return ""


# Main Document Handler
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

    return {
        "raw_text": raw_text,
        "cleaned_text": cleaned_text,
        "prompt_found": cleaned_text,
        "has_text": bool(cleaned_text.strip()),
    }