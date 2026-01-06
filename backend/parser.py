from __future__ import annotations
import re
from typing import List

from pypdf import PdfReader
from docx import Document

def _normalize(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)          # cross-\nfunctional -> crossfunctional
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)          # join single newlines
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()

def extract_pdf(path: str) -> str:
    reader = PdfReader(path)
    parts: List[str] = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
    return _normalize("\n\n".join(parts))

def extract_docx(path: str) -> str:
    doc = Document(path)
    parts: List[str] = [p.text.strip() for p in doc.paragraphs if p.text and p.text.strip()]
    return _normalize("\n\n".join(parts))

def extract_txt_bytes(b: bytes) -> str:
    try:
        text = b.decode("utf-8")
    except UnicodeDecodeError:
        text = b.decode("latin-1", errors="ignore")
    return _normalize(text)
