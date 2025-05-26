
"""
Tests for the ExtractiveSummarizer.
"""

import pytest
import asyncio
import json
from unittest.mock import MagicMock, patch

from citadel_llm.summarizers import ExtractiveSummarizer
from citadel_llm.models import LLMManager, GenerationResult


@pytest.fixture
def mock_llm_manager():
    """Create a mock LLMManager for testing."""
    manager = MagicMock(spec=LLMManager)
    
    async def mock_generate(*args, **kwargs):
        # Sample sentence indices
        return GenerationResult(
            text="```json\n[0, 2, 4]\n```",
            model="test-model",
            prompt_tokens=10,
            completion_tokens=5,
            total_tokens=15
        )
    
    manager.generate.side_effect = mock_generate
    return manager


@pytest.mark.asyncio
async def test_extractive_summarizer(mock_llm_manager):
    """Test the ExtractiveSummarizer."""
    summarizer = ExtractiveSummarizer(llm_manager=mock_llm_manager, num_sentences=3)
    
    # Create a text with multiple sentences
    sentences = []
    for i in range(5):
        sentences.append(f"This is sentence {i+1} of the test text.")
    
    text = " ".join(sentences)
    result = await summarizer.summarize(text)
    
    # Check that the summary contains the expected sentences
    assert "This is sentence 1 of the test text." in result
    assert "This is sentence 3 of the test text." in result
    assert "This is sentence 5 of the test text." in result
    
    # Check that the LLM was called
    mock_llm_manager.generate.assert_called_once()


@pytest.mark.asyncio
async def test_extractive_summarizer_empty_text(mock_llm_manager):
    """Test the ExtractiveSummarizer with empty text."""
    summarizer = ExtractiveSummarizer(llm_manager=mock_llm_manager)
    result = await summarizer.summarize("")
    
    assert result == ""
    mock_llm_manager.generate.assert_not_called()


@pytest.mark.asyncio
async def test_extractive_summarizer_short_text(mock_llm_manager):
    """Test the ExtractiveSummarizer with text shorter than requested sentences."""
    summarizer = ExtractiveSummarizer(llm_manager=mock_llm_manager, num_sentences=5)
    
    # Create a short text with fewer sentences than requested
    text = "This is a short text. It has only two sentences."
    result = await summarizer.summarize(text)
    
    # Should return the original text
    assert result == text
    mock_llm_manager.generate.assert_not_called()


@pytest.mark.asyncio
async def test_extractive_summarizer_fallback(mock_llm_manager):
    """Test the ExtractiveSummarizer fallback method."""
    # Mock a failure in the LLM response
    manager = MagicMock(spec=LLMManager)
    
    async def mock_generate(*args, **kwargs):
        # Invalid response that will trigger fallback
        return GenerationResult(
            text="Not a valid JSON response",
            model="test-model",
            prompt_tokens=10,
            completion_tokens=5,
            total_tokens=15
        )
    
    manager.generate.side_effect = mock_generate
    
    summarizer = ExtractiveSummarizer(llm_manager=manager, num_sentences=3)
    
    # Create a text with multiple sentences
    sentences = []
    for i in range(10):
        sentences.append(f"This is sentence {i+1} of the test text.")
    
    text = " ".join(sentences)
    result = await summarizer.summarize(text)
    
    # Check that we got a result despite the invalid LLM response
    assert result != ""
    assert isinstance(result, str)
    
    # Should include first and last sentences in fallback mode
    assert "This is sentence 1 of the test text." in result
    assert "This is sentence 10 of the test text." in result
