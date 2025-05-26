
"""
Tests for the EntityExtractor.
"""

import pytest
import asyncio
import json
from unittest.mock import MagicMock, patch

from citadel_llm.extractors import EntityExtractor
from citadel_llm.models import LLMManager, GenerationResult


@pytest.fixture
def mock_llm_manager():
    """Create a mock LLMManager for testing."""
    manager = MagicMock(spec=LLMManager)
    
    async def mock_generate(*args, **kwargs):
        # Sample entity extraction result
        result = {
            "PERSON": [
                {"text": "John Smith", "start": 10, "end": 20},
                {"text": "Jane Doe", "start": 45, "end": 53}
            ],
            "ORGANIZATION": [
                {"text": "Acme Corp", "start": 100, "end": 109}
            ],
            "LOCATION": [
                {"text": "New York", "start": 120, "end": 128}
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
async def test_entity_extractor(mock_llm_manager):
    """Test the EntityExtractor."""
    extractor = EntityExtractor(llm_manager=mock_llm_manager)
    result = await extractor.extract("John Smith works at Acme Corp in New York with Jane Doe.")
    
    # Check that the expected entities are extracted
    assert "PERSON" in result
    assert "ORGANIZATION" in result
    assert "LOCATION" in result
    
    # Check specific entities
    assert any(entity["text"] == "John Smith" for entity in result["PERSON"])
    assert any(entity["text"] == "Jane Doe" for entity in result["PERSON"])
    assert any(entity["text"] == "Acme Corp" for entity in result["ORGANIZATION"])
    assert any(entity["text"] == "New York" for entity in result["LOCATION"])
    
    # Check that the LLM was called
    mock_llm_manager.generate.assert_called_once()


@pytest.mark.asyncio
async def test_entity_extractor_empty_text(mock_llm_manager):
    """Test the EntityExtractor with empty text."""
    extractor = EntityExtractor(llm_manager=mock_llm_manager)
    result = await extractor.extract("")
    
    # Check that all entity types are present but empty
    for entity_type in extractor.entity_types:
        assert entity_type in result
        assert result[entity_type] == []
    
    # Check that the LLM was not called
    mock_llm_manager.generate.assert_not_called()


@pytest.mark.asyncio
async def test_entity_extractor_custom_entity_types(mock_llm_manager):
    """Test the EntityExtractor with custom entity types."""
    custom_entity_types = ["PERSON", "ORGANIZATION", "PRODUCT"]
    extractor = EntityExtractor(
        llm_manager=mock_llm_manager,
        entity_types=custom_entity_types
    )
    
    # Check that the entity types are set correctly
    assert extractor.entity_types == custom_entity_types
