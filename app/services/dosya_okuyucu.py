from __future__ import annotations
from typing import List, Tuple
from io import BytesIO

from fastapi import UploadFile

from pypdf import PdfReader
from docx import Document


def _temizle(text: str) -> str:
    text = (text or "").replace("\x00", "").strip()
    # çok uzun whitespace'i düzelt
    return " ".join(text.split())


async def dosyadan_metin_cikar(file: UploadFile) -> Tuple[str, List[str]]:
    """
    Returns: (metin, warnings)
    """
    warnings: List[str] = []

    filename = (file.filename or "").lower()
    content = await file.read()

    if not content:
        raise ValueError("Dosya boş görünüyor.")

    if filename.endswith(".pdf"):
        try:
            reader = PdfReader(BytesIO(content))
            pages_text = []
            for i, page in enumerate(reader.pages):
                t = page.extract_text() or ""
                t = _temizle(t)
                if t:
                    pages_text.append(t)
            metin = "\n\n".join(pages_text).strip()
            if not metin:
                warnings.append("PDF içinden metin çıkarılamadı (tarama/ görüntü PDF olabilir).")
            return metin, warnings
        except Exception as e:
            raise ValueError(f"PDF okunamadı: {e}")

    if filename.endswith(".docx"):
        try:
            doc = Document(BytesIO(content))
            paras = [_temizle(p.text) for p in doc.paragraphs if _temizle(p.text)]
            metin = "\n".join(paras).strip()
            if not metin:
                warnings.append("DOCX içinden metin çıkarılamadı.")
            return metin, warnings
        except Exception as e:
            raise ValueError(f"DOCX okunamadı: {e}")

    raise ValueError("Desteklenmeyen dosya türü. Sadece .pdf ve .docx kabul.")