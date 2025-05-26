
"""
Tests for the KeywordExtractor.
"""

import pytest
import asyncio
import json
from unittest.mock import MagicMock, patch

from citadel_llm.extractors import KeywordExtractor
from citadel_llm.models import LLMManager, GenerationResult


@pytest.fixture
def mock_llm_manager():
    """Create a mock LLMManager for testing."""
    manager = MagicMock(spec=LLMManager)
    
    async def mock_generate(*args, **kwargs):
        # Sample keyword extraction result
        result = {
            "keywords": [
                {"text": "AI", "relevance": 0.95},
                {"text": "machine learning", "relevance": 0.85}
            ],
            "keyphrases": [
                {"text": "natural language processing", "relevance": 0.9},
                {"text": "deep learning models", "relevance": 0.8}
            ],
            "topics": [
                {"text": "artificial intelligence", "relevance": 0.95},
                {"text": "technology trends", "relevance": 0.75}
            ]
        }
        
        return GenerationResult(
            text=json.dumps(result),
            model="test-model",
            prompt_tokens=10,
            completion_tokens=5,
            total_tokens=15
        )
    
    manager.generate.side_effect = mock_generate
    return manager


@pytest.mark.asyncio
async def test_keyword_extractor(mock_llm_manager):
    """Test the KeywordExtractor."""
    extractor = KeywordExtractor(llm_manager=mock_llm_manager)
    result = await extractor.extract("AI and machine learning are transforming natural language processing with deep learning models.")
    
    # Check that the expected keys are present
    assert "keywords" in result
    assert "keyphrases" in result
    assert "topics" in result
    
    # Check specific keywords
    assert any(kw["text"] == "AI" for kw in result["keywords"])
    assert any(kw["text"] == "machine learning" for kw in result["keywords"])
    assert any(kw["text"] == "natural language processing" for kw in result["keyphrases"])
    assert any(kw["text"] == "artificial intelligence" for kw in result["topics"])
    
    # Check that the LLM was called
    mock_llm_manager.generate.assert_called_once()


@pytest.mark.asyncio
async def test_keyword_extractor_empty_text(mock_llm_manager):
    """Test the KeywordExtractor with empty text."""
    extractor = KeywordExtractor(llm_manager=mock_llm_manager)
    result = await extractor.extract("")
    
    # Check that all keys are present but empty
    assert "keywords" in result
    assert "keyphrases" in result
    assert "topics" in result
    assert result["keywords"] == []
    assert result["keyphrases"] == []
    assert result["topics"] == []
    
    # Check that the LLM was not called
    mock_llm_manager.generate.assert_not_called()


@pytest.mark.asyncio
async def test_keyword_extractor_max_limits(mock_llm_manager):
    """Test the KeywordExtractor with custom max limits."""
    extractor = KeywordExtractor(
        llm_manager=mock_llm_manager,
        max_keywords=5,
        max_keyphrases=3,
        max_topics=2
    )
    
    # Check that the limits are set correctly
    assert extractor.max_keywords == 5
    assert extractor.max_keyphrases == 3
    assert extractor.max_topics == 2
