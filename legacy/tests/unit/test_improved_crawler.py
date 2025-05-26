"""Tests for the ImprovedCrawler class."""

import unittest
from unittest import mock
import requests
from bs4 import BeautifulSoup

from citadel_revisions.crawlers.improved_crawler import ImprovedCrawler


class TestImprovedCrawler(unittest.TestCase):
    """Tests for the ImprovedCrawler class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.crawler = ImprovedCrawler("https://example.com")
    
    def test_initialization(self):
        """Test crawler initialization."""
        self.assertEqual(self.crawler.base_url, "https://example.com")
        self.assertEqual(self.crawler.timeout, 30)
        self.assertEqual(self.crawler.max_retries, 3)
        self.assertEqual(self.crawler.min_request_interval, 1.5)
        self.assertIsInstance(self.crawler.session, requests.Session)
        self.assertEqual(self.crawler.session.headers["User-Agent"], "ImprovedCrawler/1.0")
        self.assertEqual(self.crawler.session.headers["X-Crawler"], "ImprovedCrawler")
    
    def test_validate_url(self):
        """Test URL validation."""
        # Valid URLs
        self.assertTrue(self.crawler._validate_url("https://example.com/content/123"))
        self.assertTrue(self.crawler._validate_url("https://example.com/article/123"))
        self.assertTrue(self.crawler._validate_url("https://example.com/data/123"))
        
        # Invalid URLs
        self.assertFalse(self.crawler._validate_url("https://malicious.com/content/123"))
        self.assertFalse(self.crawler._validate_url("https://example.com/login"))
        self.assertFalse(self.crawler._validate_url("https://example.com/signup"))
        self.assertFalse(self.crawler._validate_url("https://example.com/admin"))
        self.assertFalse(self.crawler._validate_url("https://example.com/other/123"))
    
    def test_is_error_result(self):
        """Test error result detection."""
        # Error result
        error_result = {
            'error': True,
            'error_type': 'test_error',
            'error_message': 'Test error message',
            'url': 'https://example.com'
        }
        self.assertTrue(self.crawler._is_error_result(error_result))
        
        # Non-error result
        data_result = {
            'url': 'https://example.com',
            'title': 'Test Title',
            'content': 'Test Content'
        }
        self.assertFalse(self.crawler._is_error_result(data_result))
    
    def test_create_error_result(self):
        """Test error result creation."""
        error_result = self.crawler._create_error_result(
            error_type='test_error',
            error_message='Test error message',
            url='https://example.com',
            additional_info={'test_key': 'test_value'}
        )
        
        self.assertTrue(error_result['error'])
        self.assertEqual(error_result['error_type'], 'test_error')
        self.assertEqual(error_result['error_message'], 'Test error message')
        self.assertEqual(error_result['url'], 'https://example.com')
        self.assertEqual(error_result['additional_info']['test_key'], 'test_value')
        self.assertIn('timestamp', error_result)
    
    @mock.patch('citadel_revisions.crawler_utils.safe_request')
    def test_safe_request(self, mock_safe_request):
        """Test safe request method."""
        mock_response = mock.Mock()
        mock_safe_request.return_value = mock_response
        
        response = self.crawler._safe_request('https://example.com/content/123')
        
        self.assertEqual(response, mock_response)
        mock_safe_request.assert_called_once_with(
            url='https://example.com/content/123',
            session=self.crawler.session,
            validate_func=self.crawler._validate_url,
            rate_limit_func=self.crawler._rate_limit,
            visited_urls=self.crawler.visited_urls,
            timeout=30,
            max_retries=3,
            method='GET'
        )
    
    @mock.patch('citadel_revisions.crawler_utils.parse_html')
    @mock.patch('citadel_revisions.crawler_utils.handle_http_error')
    @mock.patch('citadel_revisions.crawler_utils.safe_request')
    def test_extract_data_success(self, mock_safe_request, mock_handle_http_error, mock_parse_html):
        """Test successful data extraction."""
        # Mock response
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body><h1>Test Title</h1><main>Test Content</main></body></html>'
        mock_safe_request.return_value = mock_response
        mock_handle_http_error.return_value = None  # No error
        
        # Mock BeautifulSoup
        mock_soup = mock.Mock()
        mock_soup.find.side_effect = lambda *args, **kwargs: mock.Mock(text='Test Title', get_text=lambda separator=' ', strip=True: 'Test Content') if args[0] in ['h1', 'main', 'article', 'div'] else None
        mock_soup.find_all.return_value = []  # No links or meta tags
        mock_parse_html.return_value = mock_soup
        
        # Extract data
        result = self.crawler.extract_data('https://example.com/content/123')
        
        # Verify result
        self.assertEqual(result['url'], 'https://example.com/content/123')
        self.assertIn('title', result)
        self.assertIn('content', result)
        self.assertIn('extracted_at', result)
        self.assertFalse(self.crawler._is_error_result(result))
    
    @mock.patch('citadel_revisions.crawler_utils.safe_request')
    def test_extract_data_network_error(self, mock_safe_request):
        """Test data extraction with network error."""
        # Mock network error
        mock_safe_request.return_value = None
        
        # Extract data
        result = self.crawler.extract_data('https://example.com/content/123')
        
        # Verify result is an error result
        self.assertTrue(self.crawler._is_error_result(result))
        self.assertEqual(result['error_type'], 'network_error')
        self.assertEqual(result['url'], 'https://example.com/content/123')
    
    @mock.patch('citadel_revisions.crawler_utils.parse_html')
    @mock.patch('citadel_revisions.crawler_utils.handle_http_error')
    @mock.patch('citadel_revisions.crawler_utils.safe_request')
    def test_extract_data_parsing_error(self, mock_safe_request, mock_handle_http_error, mock_parse_html):
        """Test data extraction with parsing error."""
        # Mock response
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.text = '<html><body><h1>Test Title</h1><main>Test Content</main></body></html>'
        mock_safe_request.return_value = mock_response
        mock_handle_http_error.return_value = None  # No error
        
        # Mock parsing error
        mock_parse_html.side_effect = Exception("Parsing error")
        
        # Extract data
        result = self.crawler.extract_data('https://example.com/content/123')
        
        # Verify result is an error result
        self.assertTrue(self.crawler._is_error_result(result))
        self.assertEqual(result['error_type'], 'parsing_error')
        self.assertEqual(result['url'], 'https://example.com/content/123')


if __name__ == "__main__":
    unittest.main()
