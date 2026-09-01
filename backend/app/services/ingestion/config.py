"""Paths and constants for the Phase 08 RAG ingestion pipeline."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]

KNOWLEDGE_BASE_DIR = REPO_ROOT / "data" / "knowledge_base"

# Recursive text splitter defaults, per docs/rag/RAG_SPEC.md and
# docs/langchain/LANGCHAIN_SPEC.md ("configurable recursive text splitter").
DEFAULT_CHUNK_SIZE = 500
DEFAULT_CHUNK_OVERLAP = 50
DEFAULT_SEPARATORS: list[str] = ["\n\n", "\n", ". ", " ", ""]

DOCUMENT_STATUS_INDEXED = "indexed"
DOCUMENT_STATUS_PENDING = "pending"
