"""Loading and cleaning of Markdown knowledge-base documents.

Pipeline stage: Document -> Loader -> text extraction -> cleaning
(docs/rag/RAG_SPEC.md).
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

import markdown
from bs4 import BeautifulSoup

_FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
_WHITESPACE_RE = re.compile(r"[ \t]+")
_BLANK_LINES_RE = re.compile(r"\n{3,}")
_REQUIRED_FRONTMATTER_FIELDS = ("title", "category", "version")


@dataclass(frozen=True)
class LoadedDocument:
    """A knowledge-base source document after loading and cleaning."""

    source_id: str
    title: str
    category: str
    version: str
    raw_markdown: str
    clean_text: str
    content_hash: str


def _parse_frontmatter(text: str, filename: str) -> tuple[dict[str, str], str]:
    match = _FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError(
            f"Document '{filename}' is missing required YAML frontmatter "
            "(title/category/version)."
        )

    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if not line.strip() or ":" not in line:
            continue
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip().strip('"').strip("'")

    for required in _REQUIRED_FRONTMATTER_FIELDS:
        if not fields.get(required):
            raise ValueError(f"Document '{filename}' is missing frontmatter field '{required}'.")

    return fields, text[match.end() :]


def _markdown_to_text(md_body: str) -> str:
    html = markdown.markdown(md_body, extensions=["tables"])
    text = BeautifulSoup(html, "html.parser").get_text(separator="\n")
    text = _WHITESPACE_RE.sub(" ", text)
    text = "\n".join(line.strip() for line in text.splitlines())
    text = _BLANK_LINES_RE.sub("\n\n", text)
    return text.strip()


def load_document(path: Path) -> LoadedDocument:
    """Load a single Markdown KB document: parse frontmatter and clean the body text."""
    raw = path.read_text(encoding="utf-8")
    fields, body = _parse_frontmatter(raw, path.name)
    clean_text = _markdown_to_text(body)
    content_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()

    return LoadedDocument(
        source_id=path.name,
        title=fields["title"],
        category=fields["category"],
        version=fields["version"],
        raw_markdown=raw,
        clean_text=clean_text,
        content_hash=content_hash,
    )


def load_knowledge_base(directory: Path) -> list[LoadedDocument]:
    """Load and clean every Markdown document in a knowledge-base directory."""
    return [load_document(path) for path in sorted(directory.glob("*.md"))]
