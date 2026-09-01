"""Recursive character text splitter for chunking cleaned document text.

Pipeline stage: cleaning -> chunking (docs/rag/RAG_SPEC.md). Reimplements the
well-known recursive-character-splitting behavior (try separators in order,
merge back up to chunk_size, carry a chunk_overlap tail forward) without
depending on the LangChain package, since Phase 08 is ingestion only —
LangChain orchestration is Phase 10 (docs/project/IMPLEMENTATION_PHASES.md).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.services.ingestion.config import (
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_SEPARATORS,
)


@dataclass
class RecursiveCharacterTextSplitter:
    chunk_size: int = DEFAULT_CHUNK_SIZE
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP
    separators: list[str] = field(default_factory=lambda: list(DEFAULT_SEPARATORS))

    def __post_init__(self) -> None:
        if self.chunk_size <= 0:
            raise ValueError("chunk_size must be positive.")
        if self.chunk_overlap < 0:
            raise ValueError("chunk_overlap must not be negative.")
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size.")

    def split_text(self, text: str) -> list[str]:
        text = text.strip()
        if not text:
            return []
        pieces = self._split(text, list(self.separators))
        return self._merge(pieces)

    def _split(self, text: str, separators: list[str]) -> list[str]:
        if not separators:
            return [text]

        separator, remaining = separators[0], separators[1:]

        if separator == "":
            parts = list(text)
        else:
            raw_parts = text.split(separator)
            parts = [
                part + separator if i < len(raw_parts) - 1 else part
                for i, part in enumerate(raw_parts)
            ]
            parts = [part for part in parts if part != ""]

        pieces: list[str] = []
        for part in parts:
            if len(part) <= self.chunk_size:
                pieces.append(part)
            else:
                pieces.extend(self._split(part, remaining))
        return pieces

    def _merge(self, pieces: list[str]) -> list[str]:
        chunks: list[str] = []
        current = ""
        for piece in pieces:
            candidate = current + piece
            if not current or len(candidate) <= self.chunk_size:
                current = candidate
                continue
            chunks.append(current.strip())
            overlap_tail = current[-self.chunk_overlap :] if self.chunk_overlap else ""
            current = overlap_tail + piece
        if current.strip():
            chunks.append(current.strip())
        return [chunk for chunk in chunks if chunk]
