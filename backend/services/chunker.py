from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from uuid import uuid4

import fitz

from backend.config import get_settings


@dataclass(slots=True)
class Chunk:
    text: str
    metadata: dict


HEADER_FOOTER_PATTERNS = [
    re.compile(r"^page\s+\d+\s*$", re.IGNORECASE),
    re.compile(r"^\d+$"),
]


def _clean_page_text(text: str) -> str:
    lines = [line.strip() for line in text.splitlines()]
    filtered: list[str] = []
    for line in lines:
        if not line:
            continue
        if any(pattern.match(line) for pattern in HEADER_FOOTER_PATTERNS):
            continue
        if len(line) <= 3:
            continue
        filtered.append(line)
    normalized = re.sub(r"\s+", " ", " ".join(filtered))
    return normalized.strip()


def _split_text(text: str, max_words: int) -> list[str]:
    words = text.split()
    if len(words) <= max_words:
        return [text]
    chunks: list[str] = []
    for index in range(0, len(words), max_words):
        chunks.append(" ".join(words[index : index + max_words]))
    return chunks


def _infer_section(page_text: str, page_number: int) -> str:
    headings = re.findall(r"(^[A-Z][A-Za-z0-9 ,\-/:]{8,80}$)", page_text, flags=re.MULTILINE)
    if headings:
        return headings[0].strip()
    return f"Page {page_number}"


def chunk_pdf(pdf_path: str | Path, doc_name: str | None = None, doc_id: str | None = None) -> list[Chunk]:
    settings = get_settings()
    document_id = doc_id or str(uuid4())
    file_path = Path(pdf_path)
    document_name = doc_name or file_path.name
    ingested_at = datetime.now(timezone.utc).isoformat()
    chunks: list[Chunk] = []

    with fitz.open(file_path) as pdf:
        for page_index in range(pdf.page_count):
            page = pdf.load_page(page_index)
            cleaned = _clean_page_text(page.get_text("text"))
            if not cleaned:
                continue
            sections = _split_text(cleaned, settings.chunk_token_limit * 2)
            for split_index, split_text in enumerate(sections, start=1):
                metadata = {
                    "doc_id": document_id,
                    "doc_name": document_name,
                    "page_number": page_index + 1,
                    "section": _infer_section(split_text, page_index + 1),
                    "char_count": len(split_text),
                    "ingested_at": ingested_at,
                    "chunk_index": split_index,
                }
                chunks.append(Chunk(text=split_text, metadata=metadata))

    return chunks


def chunk_text_blocks(blocks: Iterable[dict], doc_name: str, doc_id: str | None = None) -> list[Chunk]:
    document_id = doc_id or str(uuid4())
    ingested_at = datetime.now(timezone.utc).isoformat()
    chunks: list[Chunk] = []
    for block in blocks:
        text = _clean_page_text(block.get("text", ""))
        if not text:
            continue
        page_number = int(block.get("page_number", 1))
        metadata = {
            "doc_id": document_id,
            "doc_name": doc_name,
            "page_number": page_number,
            "section": block.get("section") or _infer_section(text, page_number),
            "char_count": len(text),
            "ingested_at": ingested_at,
            "chunk_index": 1,
        }
        chunks.extend(Chunk(text=piece, metadata={**metadata, "chunk_index": idx}) for idx, piece in enumerate(_split_text(text, get_settings().chunk_token_limit * 2), start=1))
    return chunks
