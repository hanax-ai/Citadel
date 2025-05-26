
"""
Tests for the SentimentClassifier.
"""

import pytest
import asyncio
import json
from unittest.mock import MagicMock, patch

from citadel_llm.classifiers import SentimentClassifier
from citadel_llm.models import LLMManager, GenerationResult


@pytest.fixture
def mock_llm_manager():
    """Create a mock LLMManager for testing."""
    manager = MagicMock(spec=LLMManager)
    
    async def mock_generate(*args, **kwargs):
        # Sample sentiment analysis result
        result = {
            "sentiment": "positive",
            "score": 0.8,
            "confidence": 0.9,
            "indicators": ["excellent", "impressive", "highly recommend"],
            "explanation": "The text expresses strong approval and satisfaction."
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
async def test_sentiment_classifier(mock_llm_manager):
    """Test the SentimentClassifier."""
    classifier = SentimentClassifier(llm_manager=mock_llm_manager)
    result = await classifier.classify("This product is excellent and impressive. I highly recommend it!")
    
    # Check that the expected keys are present
    assert "sentiment" in result
    assert "score" in result
    assert "confidence" in result
    assert "indicators" in result
    assert "explanation" in result
    
    # Check specific values
    assert result["sentiment"] == "positive"
    assert result["score"] == 0.8
    assert result["confidence"] == 0.9
    assert "excellent" in result["indicators"]
    assert "impressive" in result["indicators"]
    assert "highly recommend" in result["indicators"]
    
    # Check that the LLM was called
    mock_llm_manager.generate.assert_called_once()


@pytest.mark.asyncio
async def test_sentiment_classifier_empty_text(mock_llm_manager):
    """Test the SentimentClassifier with empty text."""
    classifier = SentimentClassifier(llm_manager=mock_llm_manager)
    result = await classifier.classify("")
    
    # Check that the result has the expected structure
    assert "sentiment" in result
    assert "score" in result
    assert "confidence" in result
    assert "indicators" in result
    assert "explanation" in result
    
    # Check default values for empty text
    assert result["sentiment"] == "neutral"
    assert result["score"] == 0.0
    assert result["confidence"] == 0.0
    assert result["indicators"] == []
    
    # Check that the LLM was not called
    mock_llm_manager.generate.assert_not_called()


@pytest.mark.asyncio
async def test_sentiment_classifier_negative_text(mock_llm_manager):
    """Test the SentimentClassifier with negative text."""
    # Override the mock to return a negative sentiment
    async def mock_generate_negative(*args, **kwargs):
        result = {
            "sentiment": "negative",
            "score": -0.7,
            "confidence": 0.85,
            "indicators": ["terrible", "disappointing", "waste of money"],
            "explanation": "The text expresses strong disapproval and dissatisfaction."
        }
        
        return GenerationResult(
            text=json.dumps(result),
            model="test-model",
            prompt_tokens=10,
            completion_tokens=5,
            total_tokens=15
        )
    
    mock_llm_manager.generate.side_effect = mock_generate_negative
    
    classifier = SentimentClassifier(llm_manager=mock_llm_manager)
    result = await classifier.classify("This product is terrible and disappointing. It was a waste of money!")
    
    # Check specific values
    assert result["sentiment"] == "negative"
    assert result["score"] == -0.7
    assert result["confidence"] == 0.85
    assert "terrible" in result["indicators"]
    assert "disappointing" in result["indicators"]
    assert "waste of money" in result["indicators"]
