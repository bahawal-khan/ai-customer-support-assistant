import pytest

from app.services.ingestion.config import KNOWLEDGE_BASE_DIR
from app.services.ingestion.loader import load_document, load_knowledge_base

EXPECTED_SOURCE_IDS = {
    "refund_policy.md",
    "cancellation_policy.md",
    "payment_faq.md",
    "account_recovery.md",
    "delivery_faq.md",
    "technical_support.md",
    "router_troubleshooting.md",
    "escalation_policy.md",
    "general_faq.md",
}


def test_knowledge_base_dir_exists_and_has_nine_documents():
    assert KNOWLEDGE_BASE_DIR.is_dir()
    md_files = sorted(p.name for p in KNOWLEDGE_BASE_DIR.glob("*.md"))
    assert set(md_files) == EXPECTED_SOURCE_IDS


def test_load_knowledge_base_returns_one_entry_per_file():
    documents = load_knowledge_base(KNOWLEDGE_BASE_DIR)
    assert {doc.source_id for doc in documents} == EXPECTED_SOURCE_IDS
    assert len(documents) == 9


def test_loaded_document_has_required_frontmatter_fields():
    documents = load_knowledge_base(KNOWLEDGE_BASE_DIR)
    for doc in documents:
        assert doc.title
        assert doc.category
        assert doc.version
        assert doc.content_hash
        assert len(doc.content_hash) == 64  # sha256 hex digest


def test_clean_text_strips_markdown_syntax():
    doc = load_document(KNOWLEDGE_BASE_DIR / "refund_policy.md")
    assert "#" not in doc.clean_text
    assert "---" not in doc.clean_text
    assert "Refund Policy" in doc.clean_text
    # Frontmatter fields must not leak into the cleaned body text.
    assert "category: refund" not in doc.clean_text


def test_clean_text_mentions_fictional_disclaimer():
    for doc in load_knowledge_base(KNOWLEDGE_BASE_DIR):
        assert "fictional" in doc.clean_text.lower() or "demo" in doc.clean_text.lower()


def test_content_hash_is_stable_across_loads():
    first = load_document(KNOWLEDGE_BASE_DIR / "general_faq.md")
    second = load_document(KNOWLEDGE_BASE_DIR / "general_faq.md")
    assert first.content_hash == second.content_hash


def test_content_hash_changes_when_content_changes(tmp_path):
    doc_a = tmp_path / "a.md"
    doc_a.write_text(
        '---\ntitle: "A"\ncategory: test\nversion: v1\n---\n\n# A\n\nFirst version.\n',
        encoding="utf-8",
    )
    hash_v1 = load_document(doc_a).content_hash

    doc_a.write_text(
        '---\ntitle: "A"\ncategory: test\nversion: v1\n---\n\n# A\n\nSecond version.\n',
        encoding="utf-8",
    )
    hash_v2 = load_document(doc_a).content_hash

    assert hash_v1 != hash_v2


def test_missing_frontmatter_raises_value_error(tmp_path):
    bad_doc = tmp_path / "bad.md"
    bad_doc.write_text("# No frontmatter here\n\nJust content.\n", encoding="utf-8")

    with pytest.raises(ValueError, match="frontmatter"):
        load_document(bad_doc)


def test_missing_required_field_raises_value_error(tmp_path):
    bad_doc = tmp_path / "bad.md"
    bad_doc.write_text(
        '---\ntitle: "Missing category"\nversion: v1\n---\n\nBody text.\n',
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="category"):
        load_document(bad_doc)


def test_source_id_is_derived_from_filename():
    doc = load_document(KNOWLEDGE_BASE_DIR / "payment_faq.md")
    assert doc.source_id == "payment_faq.md"
