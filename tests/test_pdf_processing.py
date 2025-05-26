
"""
Test script for PDF processing module and PDFCrawler.

This script tests the functionality of the PDF processing module and PDFCrawler
class implemented for Project Citadel.
"""

import os
import sys
import unittest
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the modules to test
from citadel_core.pdf_processing import PDFProcessor, extract_text_from_pdf, extract_metadata_from_pdf, chunk_pdf_content
from citadel_core.crawlers.pdf_crawler import PDFCrawler

class TestPDFProcessing(unittest.TestCase):
    """Test case for PDF processing functionality."""
    
    def setUp(self):
        """Set up the test case."""
        self.fixtures_dir = Path(__file__).parent / 'fixtures'
        self.sample_pdf = self.fixtures_dir / 'sample.pdf'
        
        # Skip tests if sample PDF doesn't exist
        if not self.sample_pdf.exists():
            self.skipTest(f"Sample PDF not found at {self.sample_pdf}")
    
    def test_extract_text(self):
        """Test text extraction from PDF."""
        text = extract_text_from_pdf(self.sample_pdf)
        
        # Check that text was extracted
        self.assertIsNotNone(text)
        self.assertGreater(len(text), 0)
        
        # Check for expected content
        self.assertIn('Sample PDF Document', text)
    
    def test_extract_metadata(self):
        """Test metadata extraction from PDF."""
        metadata = extract_metadata_from_pdf(self.sample_pdf)
        
        # Check that metadata was extracted
        self.assertIsNotNone(metadata)
        self.assertIsInstance(metadata, dict)
        
        # Check for page count
        self.assertIn('page_count', metadata)
        self.assertEqual(metadata['page_count'], 1)
    
    def test_chunk_content(self):
        """Test content chunking for LLM integration."""
        # Extract text first to avoid processing the entire PDF
        text = extract_text_from_pdf(self.sample_pdf)
        
        # Create a simple processor and chunk the text directly
        processor = PDFProcessor(ocr_enabled=False)
        chunks = processor.chunk_content(text, chunk_size=100, overlap=20)
        
        # Check that chunks were created
        self.assertIsNotNone(chunks)
        self.assertIsInstance(chunks, list)
        self.assertGreater(len(chunks), 0)
        
        # Check that chunks have the expected size
        for chunk in chunks:
            self.assertLessEqual(len(chunk), 100)
    
    def test_pdf_processor(self):
        """Test the PDFProcessor class."""
        processor = PDFProcessor(ocr_enabled=False)
        
        # Test only the metadata extraction to avoid memory issues
        with open(self.sample_pdf, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            metadata = processor.extract_metadata(reader)
        
        # Check that metadata was extracted
        self.assertIsNotNone(metadata)
        self.assertIsInstance(metadata, dict)
        self.assertIn('page_count', metadata)
        
        # Test structure identification with a simple text
        sample_text = "Section 1: Introduction\nThis is a paragraph.\n\nSection 2: Conclusion\nThis is another paragraph."
        structure = processor._identify_structure(sample_text)
        
        # Check that structure was identified
        self.assertIsNotNone(structure)
        self.assertIsInstance(structure, dict)
        self.assertIn('headings', structure)
        self.assertIn('paragraphs', structure)
        self.assertGreater(len(structure['headings']), 0)
        self.assertGreater(len(structure['paragraphs']), 0)

class TestPDFCrawler(unittest.TestCase):
    """Test case for PDFCrawler functionality."""
    
    def setUp(self):
        """Set up the test case."""
        self.fixtures_dir = Path(__file__).parent / 'fixtures'
        self.sample_pdf = self.fixtures_dir / 'sample.pdf'
        
        # Skip tests if sample PDF doesn't exist
        if not self.sample_pdf.exists():
            self.skipTest(f"Sample PDF not found at {self.sample_pdf}")
        
        # Create a PDFCrawler instance
        self.crawler = PDFCrawler(base_url="https://example.com", ocr_enabled=False)
    
    def test_process_local_pdf(self):
        """Test processing a local PDF file."""
        result = self.crawler.process_local_pdf(self.sample_pdf)
        
        # Check that processing was successful
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        
        # Check for expected keys
        expected_keys = ['metadata', 'pages', 'text', 'images', 'structure', 'chunks', 'source', 'filename', 'filepath']
        for key in expected_keys:
            self.assertIn(key, result)
        
        # Check source information
        self.assertEqual(result['source'], 'local')
        self.assertEqual(result['filename'], self.sample_pdf.name)
        
        # Check that text was extracted
        self.assertGreater(len(result['text']), 0)
        
        # Check that chunks were created
        self.assertGreater(len(result['chunks']), 0)

if __name__ == '__main__':
    unittest.main()
