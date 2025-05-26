
"""
Integration tests for the Citadel LLM content processing components.
"""

import pytest
import asyncio
from unittest.mock import MagicMock, patch

from citadel_llm.processors import TextCleaner, TextChunker
from citadel_llm.extractors import EntityExtractor, KeywordExtractor
from citadel_llm.summarizers import AbstractiveSummarizer
from citadel_llm.classifiers import TopicClassifier, SentimentClassifier
from citadel_llm.models import LLMManager, GenerationResult
from citadel_core.pdf_processing import PDFProcessor
from citadel_core.crawlers.pdf_crawler import PDFCrawler


class MockLLMManager:
    """Mock LLM manager for testing."""
    
    async def generate(self, prompt, model_name, options=None, system_message=None, stream=False):
        """Mock generate method."""
        if "extract entities" in prompt.lower() or "extract all named entities" in prompt.lower():
            return GenerationResult(
                text='{"PERSON": [{"text": "John Smith", "start": 10, "end": 20}], "ORGANIZATION": [{"text": "Acme Corp", "start": 30, "end": 39}]}',
                model=model_name,
                prompt_tokens=10,
                completion_tokens=5,
                total_tokens=15
            )
        elif "extract keywords" in prompt.lower() or "extract the most important keywords" in prompt.lower():
            return GenerationResult(
                text='{"keywords": [{"text": "AI", "relevance": 0.9}], "keyphrases": [{"text": "machine learning", "relevance": 0.8}], "topics": [{"text": "technology", "relevance": 0.95}]}',
                model=model_name,
                prompt_tokens=10,
                completion_tokens=5,
                total_tokens=15
            )
        elif "summarize" in prompt.lower() or "summary" in prompt.lower():
            return GenerationResult(
                text="This is a summary of the text.",
                model=model_name,
                prompt_tokens=10,
                completion_tokens=5,
                total_tokens=15
            )
        elif "classify" in prompt.lower() or "topic" in prompt.lower():
            return GenerationResult(
                text='{"primary_topic": "Technology", "topics": [{"name": "Technology", "confidence": 0.9, "explanation": "The text discusses technology."}]}',
                model=model_name,
                prompt_tokens=10,
                completion_tokens=5,
                total_tokens=15
            )
        elif "sentiment" in prompt.lower():
            return GenerationResult(
                text='{"sentiment": "positive", "score": 0.8, "confidence": 0.9, "indicators": ["good"], "explanation": "The text is positive."}',
                model=model_name,
                prompt_tokens=10,
                completion_tokens=5,
                total_tokens=15
            )
        else:
            return GenerationResult(
                text="Generic response",
                model=model_name,
                prompt_tokens=10,
                completion_tokens=5,
                total_tokens=15
            )


@pytest.fixture
def mock_llm_manager():
    """Create a mock LLM manager for testing."""
    return MockLLMManager()


@pytest.mark.asyncio
async def test_web_content_processing_pipeline(mock_llm_manager):
    """Test the complete content processing pipeline for web content."""
    # Sample web content
    web_content = """
    <html>
    <body>
    <h1>Artificial Intelligence in Business</h1>
    <p>John Smith, CEO of Acme Corp, announced a new AI initiative yesterday. 
    The company will invest $10 million in machine learning research.</p>
    <p>This is a significant step for the technology sector.</p>
    </body>
    </html>
    """
    
    # 1. Clean the text
    cleaner = TextCleaner(remove_html=True, remove_extra_whitespace=True)
    cleaned_text = await cleaner.process(web_content)
    
    # 2. Chunk the text
    chunker = TextChunker(chunk_size=200, chunk_overlap=50)
    chunks = await chunker.process(cleaned_text)
    
    # 3. Extract entities
    entity_extractor = EntityExtractor(llm_manager=mock_llm_manager)
    entities = await entity_extractor.extract(cleaned_text)
    
    # 4. Extract keywords
    keyword_extractor = KeywordExtractor(llm_manager=mock_llm_manager)
    keywords = await keyword_extractor.extract(cleaned_text)
    
    # 5. Generate summary
    summarizer = AbstractiveSummarizer(llm_manager=mock_llm_manager)
    summary = await summarizer.summarize(cleaned_text)
    
    # 6. Classify content
    topic_classifier = TopicClassifier(llm_manager=mock_llm_manager)
    topics = await topic_classifier.classify(cleaned_text)
    
    sentiment_classifier = SentimentClassifier(llm_manager=mock_llm_manager)
    sentiment = await sentiment_classifier.classify(cleaned_text)
    
    # Verify results
    assert "Artificial Intelligence in Business" in cleaned_text
    assert "John Smith" in cleaned_text
    assert "Acme Corp" in cleaned_text
    
    assert len(chunks) >= 1
    
    assert "PERSON" in entities
    assert "ORGANIZATION" in entities
    
    assert "keywords" in keywords
    assert "keyphrases" in keywords
    assert "topics" in keywords
    
    assert summary == "This is a summary of the text."
    
    assert "primary_topic" in topics
    assert topics["primary_topic"] == "Technology"
    
    assert "sentiment" in sentiment
    assert sentiment["sentiment"] == "positive"


@pytest.mark.asyncio
async def test_pdf_content_processing_pipeline(mock_llm_manager, monkeypatch):
    """Test the complete content processing pipeline for PDF content."""
    # Mock the PDFProcessor and PDFCrawler
    class MockPDFProcessor:
        def process_pdf(self, pdf_path):
            return {
                "text": "This is a PDF about artificial intelligence. John Smith from Acme Corp wrote it.",
                "metadata": {
                    "title": "AI in Business",
                    "author": "John Smith",
                    "page_count": 5
                },
                "chunks": ["This is a PDF about artificial intelligence.", "John Smith from Acme Corp wrote it."]
            }
    
    class MockPDFCrawler:
        def __init__(self, *args, **kwargs):
            self.pdf_processor = MockPDFProcessor()
        
        async def process_local_pdf(self, pdf_path):
            return self.pdf_processor.process_pdf(pdf_path)
    
    # Apply the monkeypatches
    monkeypatch.setattr("citadel_core.pdf_processing.PDFProcessor", MockPDFProcessor)
    monkeypatch.setattr("citadel_core.crawlers.pdf_crawler.PDFCrawler", MockPDFCrawler)
    
    # Create a mock PDF crawler
    pdf_crawler = MockPDFCrawler()
    
    # Process a mock PDF
    pdf_content = await pdf_crawler.process_local_pdf("mock_pdf.pdf")
    
    # Extract entities
    entity_extractor = EntityExtractor(llm_manager=mock_llm_manager)
    entities = await entity_extractor.extract(pdf_content["text"])
    
    # Extract keywords
    keyword_extractor = KeywordExtractor(llm_manager=mock_llm_manager)
    keywords = await keyword_extractor.extract(pdf_content["text"])
    
    # Generate summary
    summarizer = AbstractiveSummarizer(llm_manager=mock_llm_manager)
    summary = await summarizer.summarize(pdf_content["text"])
    
    # Classify content
    topic_classifier = TopicClassifier(llm_manager=mock_llm_manager)
    topics = await topic_classifier.classify(pdf_content["text"])
    
    sentiment_classifier = SentimentClassifier(llm_manager=mock_llm_manager)
    sentiment = await sentiment_classifier.classify(pdf_content["text"])
    
    # Verify results
    assert "artificial intelligence" in pdf_content["text"]
    assert "John Smith" in pdf_content["text"]
    assert "Acme Corp" in pdf_content["text"]
    
    assert "PERSON" in entities
    assert "ORGANIZATION" in entities
    
    assert "keywords" in keywords
    assert "keyphrases" in keywords
    assert "topics" in keywords
    
    assert summary == "This is a summary of the text."
    
    assert "primary_topic" in topics
    assert topics["primary_topic"] == "Technology"
    
    assert "sentiment" in sentiment
    assert sentiment["sentiment"] == "positive"
