"""Extract plain text from an uploaded CV (PDF, DOCX or text)."""

import io

from docx import Document
from pypdf import PdfReader

MAX_BYTES = 5 * 1024 * 1024


def extract_text(filename: str, data: bytes) -> str:
    name = filename.lower()
    if name.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(data))
        return "\n".join(page.extract_text() or "" for page in reader.pages[:10])
    if name.endswith(".docx"):
        doc = Document(io.BytesIO(data))
        return "\n".join(p.text for p in doc.paragraphs)
    if name.endswith((".txt", ".md")):
        return data.decode("utf-8", errors="ignore")
    raise ValueError("Use PDF, DOCX or TXT")
