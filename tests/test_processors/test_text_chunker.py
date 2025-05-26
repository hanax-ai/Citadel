
"""
Tests for the TextChunker processor.
"""

import pytest
import asyncio
from unittest.mock import MagicMock

from citadel_llm.processors import TextChunker


@pytest.fixture
def text_chunker():
    """Create a TextChunker instance for testing."""
    return TextChunker(
        chunk_size=100,
        chunk_overlap=20,
        respect_paragraphs=True,
        respect_sentences=True
    )


@pytest.mark.asyncio
async def test_text_chunker_short_text(text_chunker):
    """Test chunking with text shorter than chunk size."""
    text = "This is a short text that should fit in one chunk."
    chunks = await text_chunker.process(text)
    assert len(chunks) == 1
    assert chunks[0] == text


@pytest.mark.asyncio
async def test_text_chunker_long_text(text_chunker):
    """Test chunking with text longer than chunk size."""
    # Create a text with multiple sentences
    sentences = []
    for i in range(10):
        sentences.append(f"This is sentence {i+1} of the test text.")
    
    text = " ".join(sentences)
    chunks = await text_chunker.process(text)
    
    # Should be split into multiple chunks
    assert len(chunks) > 1
    
    # Check that all content is preserved
    combined = " ".join(chunks)
    for sentence in sentences:
        assert sentence in combined


@pytest.mark.asyncio
async def test_text_chunker_with_metadata(text_chunker):
    """Test chunking with metadata."""
    text = "This is a test text. It has multiple sentences. Each sentence should be preserved."
    chunks = await text_chunker.process(text, return_metadata=True)
    
    # Check that metadata is included
    assert isinstance(chunks, list)
    assert all(isinstance(chunk, dict) for chunk in chunks)
    assert all("text" in chunk for chunk in chunks)
    assert all("start" in chunk for chunk in chunks)
    assert all("end" in chunk for chunk in chunks)
    assert all("index" in chunk for chunk in chunks)


@pytest.mark.asyncio
async def test_text_chunker_respect_paragraphs(text_chunker):
    """Test that paragraph boundaries are respected."""
    text = "This is paragraph 1.\n\nThis is paragraph 2.\n\nThis is paragraph 3."
    chunks = await text_chunker.process(text)
    
    # Check that paragraphs are preserved
    for chunk in chunks:
        # A chunk should not contain partial paragraphs
        assert not chunk.startswith("paragraph")
        assert not chunk.endswith("This is")


@pytest.mark.asyncio
async def test_chunk_pdf_content(text_chunker):
    """Test chunking PDF content."""
    pdf_content = {
        "text": "This is the PDF content. It has multiple sentences. Each sentence should be preserved.",
        "metadata": {"title": "Test PDF"}
    }
    
    result = await text_chunker.chunk_pdf_content(pdf_content)
    
    # Check that the PDF content is preserved
    assert "text" in result
    assert "metadata" in result
    assert "chunks" in result
    assert isinstance(result["chunks"], list)
