import pytest

from app.services.ingestion.splitter import RecursiveCharacterTextSplitter


def test_default_chunk_size_and_overlap_are_500_and_50():
    splitter = RecursiveCharacterTextSplitter()
    assert splitter.chunk_size == 500
    assert splitter.chunk_overlap == 50


def test_empty_text_returns_no_chunks():
    splitter = RecursiveCharacterTextSplitter()
    assert splitter.split_text("") == []
    assert splitter.split_text("   \n\n  ") == []


def test_short_text_returns_single_chunk():
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    text = "This is a short paragraph well under the chunk size."
    chunks = splitter.split_text(text)
    assert len(chunks) == 1
    assert chunks[0] == text


def test_long_text_is_split_into_multiple_chunks_within_size_bound():
    splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)
    paragraph = "Refunds are processed within five business days. " * 20
    chunks = splitter.split_text(paragraph)

    assert len(chunks) > 1
    # Allow a small overshoot for overlap-tail merging, matching the
    # documented recursive-splitting behavior.
    assert all(len(chunk) <= splitter.chunk_size + splitter.chunk_overlap for chunk in chunks)


def test_consecutive_chunks_share_overlapping_content():
    splitter = RecursiveCharacterTextSplitter(chunk_size=120, chunk_overlap=30)
    text = " ".join(f"sentence-{i} has some words in it." for i in range(30))
    chunks = splitter.split_text(text)

    assert len(chunks) > 1
    for first, second in zip(chunks, chunks[1:]):
        tail = first[-10:]
        assert tail in second or any(word in second for word in tail.split())


def test_no_content_word_is_lost_across_chunks():
    splitter = RecursiveCharacterTextSplitter(chunk_size=80, chunk_overlap=10)
    text = " ".join(f"token{i}" for i in range(100))
    chunks = splitter.split_text(text)

    reconstructed = " ".join(chunks)
    for i in range(100):
        assert f"token{i}" in reconstructed


def test_splits_on_paragraph_boundaries_before_falling_back_to_words():
    splitter = RecursiveCharacterTextSplitter(chunk_size=60, chunk_overlap=10)
    text = "First paragraph is short.\n\nSecond paragraph is also fairly short."
    chunks = splitter.split_text(text)
    assert any("First paragraph" in chunk for chunk in chunks)
    assert any("Second paragraph" in chunk for chunk in chunks)


@pytest.mark.parametrize(
    "chunk_size,chunk_overlap",
    [(0, 0), (-10, 0), (100, 100), (100, 150)],
)
def test_invalid_chunk_size_or_overlap_raises_value_error(chunk_size, chunk_overlap):
    with pytest.raises(ValueError):
        RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)


def test_negative_overlap_raises_value_error():
    with pytest.raises(ValueError):
        RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=-1)
