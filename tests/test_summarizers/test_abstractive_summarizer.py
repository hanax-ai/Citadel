
"""
Tests for the AbstractiveSummarizer.
"""

import pytest
import asyncio
from unittest.mock import MagicMock, patch

from citadel_llm.summarizers import AbstractiveSummarizer
from citadel_llm.models import LLMManager, GenerationResult


@pytest.fixture
def mock_llm_manager():
    """Create a mock LLMManager for testing."""
    manager = MagicMock(spec=LLMManager)
    
    async def mock_generate(*args, **kwargs):
        # Sample summary
        return GenerationResult(
            text="This is a concise summary of the input text.",
            model="test-model",
            prompt_tokens=10,
            completion_tokens=5,
            total_tokens=15
        )
    
    manager.generate.side_effect = mock_generate
    return manager


@pytest.mark.asyncio
async def test_abstractive_summarizer(mock_llm_manager):
    """Test the AbstractiveSummarizer."""
    summarizer = AbstractiveSummarizer(llm_manager=mock_llm_manager)
    result = await summarizer.summarize("This is a long text that needs to be summarized.")
    
    assert result == "This is a concise summary of the input text."
    mock_llm_manager.generate.assert_called_once()


@pytest.mark.asyncio
async def test_abstractive_summarizer_empty_text(mock_llm_manager):
    """Test the AbstractiveSummarizer with empty text."""
    summarizer = AbstractiveSummarizer(llm_manager=mock_llm_manager)
    result = await summarizer.summarize("")
    
    assert result == ""
    mock_llm_manager.generate.assert_not_called()


@pytest.mark.asyncio
async def test_abstractive_summarizer_summary_types(mock_llm_manager):
    """Test the AbstractiveSummarizer with different summary types."""
    # Test short summary
    short_summarizer = AbstractiveSummarizer(
        llm_manager=mock_llm_manager,
        summary_type="short",
        max_words=50
    )
    assert short_summarizer.summary_type == "short"
    assert short_summarizer.max_words == 50
    
    # Test medium summary
    medium_summarizer = AbstractiveSummarizer(
        llm_manager=mock_llm_manager,
        summary_type="medium",
        max_words=200
    )
    assert medium_summarizer.summary_type == "medium"
    assert medium_summarizer.max_words == 200
    
    # Test long summary
    long_summarizer = AbstractiveSummarizer(
        llm_manager=mock_llm_manager,
        summary_type="long",
        max_words=500
    )
    assert long_summarizer.summary_type == "long"
    assert long_summarizer.max_words == 500


@pytest.mark.asyncio
async def test_summarize_chunks(mock_llm_manager):
    """Test summarizing multiple chunks."""
    summarizer = AbstractiveSummarizer(llm_manager=mock_llm_manager)
    
    chunks = [
        "This is the first chunk of text.",
        "This is the second chunk of text.",
        "This is the third chunk of text."
    ]
    
    result = await summarizer.summarize_chunks(chunks)
    assert result == "This is a concise summary of the input text."
    
    # Should be called multiple times for hierarchical summarization
    assert mock_llm_manager.generate.call_count > 1
