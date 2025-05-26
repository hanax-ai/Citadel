"""
Test script for PDFCrawler class.

This script tests the functionality of the PDFCrawler class
implemented for Project Citadel.
"""

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the modules to test
from citadel_core.crawlers.pdf_crawler import PDFCrawler

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
    
    @patch('citadel_core.crawlers.pdf_crawler.PDFCrawler._safe_request')
    def test_download_pdf(self, mock_safe_request):
        """Test downloading a PDF from a URL."""
        # Read the sample PDF file
        with open(self.sample_pdf, 'rb') as f:
            sample_pdf_data = f.read()
        
        # Mock the response
        mock_response = MagicMock()
        mock_response.content = sample_pdf_data
        mock_response.headers = {'Content-Type': 'application/pdf'}
        mock_safe_request.return_value = mock_response
        
        # Test downloading the PDF
        pdf_data = self.crawler._download_pdf('https://example.com/sample.pdf')
        
        # Check that the PDF was downloaded
        self.assertIsNotNone(pdf_data)
        self.assertEqual(pdf_data, sample_pdf_data)
        
        # Check that _safe_request was called with the correct URL
        mock_safe_request.assert_called_once_with('https://example.com/sample.pdf')
    
    @patch('citadel_core.crawlers.pdf_crawler.PDFCrawler._download_pdf')
    def test_crawl(self, mock_download_pdf):
        """Test crawling a PDF from a URL."""
        # Read the sample PDF file
        with open(self.sample_pdf, 'rb') as f:
            sample_pdf_data = f.read()
        
        # Mock the download_pdf method
        mock_download_pdf.return_value = sample_pdf_data
        
        # Test crawling the PDF
        results = self.crawler.crawl(['https://example.com/sample.pdf'])
        
        # Check that crawling was successful
        self.assertIsNotNone(results)
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 1)
        
        # Check the result
        result = results[0]
        self.assertIsInstance(result, dict)
        
        # Check for expected keys
        expected_keys = ['metadata', 'pages', 'text', 'images', 'structure', 'chunks', 'source_url', 'filename']
        for key in expected_keys:
            self.assertIn(key, result)
        
        # Check source information
        self.assertEqual(result['source_url'], 'https://example.com/sample.pdf')
        self.assertEqual(result['filename'], 'sample.pdf')
        
        # Check that text was extracted
        self.assertGreater(len(result['text']), 0)
        
        # Check that chunks were created
        self.assertGreater(len(result['chunks']), 0)

if __name__ == '__main__':
    unittest.main()
