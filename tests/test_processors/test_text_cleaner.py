
"""
Tests for the TextCleaner processor.
"""

import pytest
import asyncio
from unittest.mock import MagicMock, patch

from citadel_llm.processors import TextCleaner, LLMTextCleaner
from citadel_llm.models import LLMManager, GenerationResult


@pytest.fixture
def text_cleaner():
    """Create a TextCleaner instance for testing."""
    return TextCleaner(
        remove_html=True,
        remove_urls=True,
        remove_emails=True,
        remove_extra_whitespace=True
    )


@pytest.mark.asyncio
async def test_text_cleaner_html_removal(text_cleaner):
    """Test that HTML tags are removed."""
    text = "<p>This is a <b>test</b> with <a href='#'>HTML</a> tags.</p>"
    result = await text_cleaner.process(text)
    assert "<p>" not in result
    assert "<b>" not in result
    assert "<a href='#'>" not in result
    assert "This is a test with HTML tags." in result


@pytest.mark.asyncio
async def test_text_cleaner_url_removal(text_cleaner):
    """Test that URLs are removed."""
    text = "Visit https://example.com or www.example.org for more information."
    result = await text_cleaner.process(text)
    assert "https://example.com" not in result
    assert "www.example.org" not in result
    assert "Visit or for more information." in result


@pytest.mark.asyncio
async def test_text_cleaner_email_removal(text_cleaner):
    """Test that email addresses are removed."""
    text = "Contact user@example.com for support."
    result = await text_cleaner.process(text)
    assert "user@example.com" not in result
    assert "Contact for support." in result


@pytest.mark.asyncio
async def test_text_cleaner_whitespace_normalization(text_cleaner):
    """Test that extra whitespace is normalized."""
    text = "This    has    extra    spaces    and\n\nmultiple\n\nline breaks."
    result = await text_cleaner.process(text)
    assert "This has extra spaces and multiple line breaks." == result


@pytest.fixture
def mock_llm_manager():
    """Create a mock LLMManager for testing."""
    manager = MagicMock(spec=LLMManager)
    
    async def mock_generate(*args, **kwargs):
        return GenerationResult(
            text="This is the cleaned text.",
            model="test-model",
            prompt_tokens=10,
            completion_tokens=5,
            total_tokens=15
        )
    
    manager.generate.side_effect = mock_generate
    return manager


@pytest.mark.asyncio
async def test_llm_text_cleaner(mock_llm_manager):
    """Test the LLMTextCleaner."""
    cleaner = LLMTextCleaner(llm_manager=mock_llm_manager)
    result = await cleaner.process("This is a test text with errors.")
    
    assert result == "This is the cleaned text."
    mock_llm_manager.generate.assert_called_once()
