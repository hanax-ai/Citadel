
"""
Tests for the TopicClassifier.
"""

import pytest
import asyncio
import json
from unittest.mock import MagicMock, patch

from citadel_llm.classifiers import TopicClassifier
from citadel_llm.models import LLMManager, GenerationResult


@pytest.fixture
def mock_llm_manager():
    """Create a mock LLMManager for testing."""
    manager = MagicMock(spec=LLMManager)
    
    async def mock_generate(*args, **kwargs):
        # Sample topic classification result
        result = {
            "primary_topic": "Technology",
            "topics": [
                {
                    "name": "Technology",
                    "confidence": 0.9,
                    "explanation": "The text discusses AI and machine learning technologies."
                },
                {
                    "name": "Business",
                    "confidence": 0.7,
                    "explanation": "The text mentions business applications of AI."
                }
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
async def test_topic_classifier(mock_llm_manager):
    """Test the TopicClassifier."""
    classifier = TopicClassifier(llm_manager=mock_llm_manager)
    result = await classifier.classify("AI and machine learning are transforming businesses.")
    
    # Check that the expected keys are present
    assert "primary_topic" in result
    assert "topics" in result
    
    # Check specific topics
    assert result["primary_topic"] == "Technology"
    assert len(result["topics"]) == 2
    assert result["topics"][0]["name"] == "Technology"
    assert result["topics"][1]["name"] == "Business"
    
    # Check that the LLM was called
    mock_llm_manager.generate.assert_called_once()


@pytest.mark.asyncio
async def test_topic_classifier_empty_text(mock_llm_manager):
    """Test the TopicClassifier with empty text."""
    classifier = TopicClassifier(llm_manager=mock_llm_manager)
    result = await classifier.classify("")
    
    # Check that the result has the expected structure
    assert "primary_topic" in result
    assert "topics" in result
    assert result["primary_topic"] is None
    assert result["topics"] == []
    
    # Check that the LLM was not called
    mock_llm_manager.generate.assert_not_called()


@pytest.mark.asyncio
async def test_topic_classifier_custom_topics(mock_llm_manager):
    """Test the TopicClassifier with custom topics."""
    custom_topics = ["Technology", "Business", "Science", "Health"]
    classifier = TopicClassifier(
        llm_manager=mock_llm_manager,
        topics=custom_topics
    )
    
    # Check that the topics are set correctly
    assert classifier.topics == custom_topics
    
    # Test classification with custom topics
    result = await classifier.classify("AI and machine learning are transforming healthcare.")
    
    # Check that the LLM was called with the custom topics
    mock_llm_manager.generate.assert_called_once()
    call_args = mock_llm_manager.generate.call_args[1]
    assert "prompt" in call_args
    assert "Technology" in call_args["prompt"]
    assert "Business" in call_args["prompt"]
    assert "Science" in call_args["prompt"]
    assert "Health" in call_args["prompt"]
