"""Tests for citadel.utils.crawler_utils module."""

import unittest
from unittest import mock
import time
import requests
from bs4 import BeautifulSoup

from citadel.utils.crawler_utils import (
    validate_url,
    get_soup,
    extract_links,
    extract_metadata,
    RateLimiter,
    build_session,
    safe_request,
    CrawlerError,
    URLValidationError,
    HTTPError,
    RateLimitError,
    ParsingError,
    is_success_status,
    handle_http_error,
    retry_on_error,
)


class TestUrlValidation(unittest.TestCase):
    """Tests for URL validation functions."""
    
    def test_validate_url_basic(self):
        """Test basic URL validation."""
        # Valid URLs
        self.assertTrue(validate_url(
            "https://example.com/page",
            base_url="https://example.com"
        ))
        
        self.assertTrue(validate_url(
            "https://subdomain.example.com/page",
            base_url="https://example.com"
        ))
        
        # Invalid URLs
        self.assertFalse(validate_url(
            "https://malicious.com/page",
            base_url="https://example.com"
        ))
        
        self.assertFalse(validate_url(
            "ftp://example.com/file",
            base_url="https://example.com"
        ))
        
        self.assertFalse(validate_url(
            "invalid-url",
            base_url="https://example.com"
        ))
    
    def test_validate_url_with_allowed_domains(self):
        """Test URL validation with allowed domains."""
        self.assertTrue(validate_url(
            "https://allowed.com/page",
            base_url="https://example.com",
            allowed_domains=["allowed.com", "also-allowed.com"]
        ))
        
        self.assertFalse(validate_url(
            "https://disallowed.com/page",
            base_url="https://example.com",
            allowed_domains=["allowed.com", "also-allowed.com"]
        ))
    
    def test_validate_url_with_patterns(self):
        """Test URL validation with patterns."""
        self.assertTrue(validate_url(
            "https://example.com/article/123",
            base_url="https://example.com",
            url_patterns=["/article/", "/blog/"]
        ))
        
        self.assertFalse(validate_url(
            "https://example.com/product/123",
            base_url="https://example.com",
            url_patterns=["/article/", "/blog/"]
        ))
        
        # Base URL should always be valid
        self.assertTrue(validate_url(
            "https://example.com",
            base_url="https://example.com",
            url_patterns=["/article/", "/blog/"]
        ))
    
    def test_validate_url_with_excluded_patterns(self):
        """Test URL validation with excluded patterns."""
        self.assertFalse(validate_url(
            "https://example.com/login",
            base_url="https://example.com",
            excluded_patterns=["/login", "/admin"]
        ))
        
        self.assertTrue(validate_url(
            "https://example.com/article/123",
            base_url="https://example.com",
            excluded_patterns=["/login", "/admin"]
        ))
    
    def test_validate_url_with_callback(self):
        """Test URL validation with callback."""
        urls = []
        
        def callback(url):
            urls.append(url)
        
        validate_url(
            "https://example.com/article/123",
            base_url="https://example.com",
            callback=callback
        )
        
        self.assertEqual(urls, ["https://example.com/article/123"])


class TestHtmlParsing(unittest.TestCase):
    """Tests for HTML parsing functions."""
    
    def test_get_soup(self):
        """Test HTML parsing."""
        html = "<html><body><h1>Title</h1><p>Paragraph</p></body></html>"
        soup = get_soup(html)
        
        self.assertIsInstance(soup, BeautifulSoup)
        self.assertEqual(soup.h1.text, "Title")
        self.assertEqual(soup.p.text, "Paragraph")
    
    def test_extract_links(self):
        """Test link extraction."""
        html = """
        <html>
            <body>
                <a href="/page1">Page 1</a>
                <a href="page2">Page 2</a>
                <a href="https://example.org/page3">Page 3</a>
            </body>
        </html>
        """
        soup = get_soup(html)
        links = extract_links(soup, "https://example.com")
        
        self.assertEqual(len(links), 3)
        self.assertEqual(links[0], "https://example.com/page1")
        self.assertEqual(links[1], "https://example.com/page2")
        self.assertEqual(links[2], "https://example.org/page3")
    
    def test_extract_metadata(self):
        """Test metadata extraction."""
        html = """
        <html>
            <head>
                <meta property="og:title" content="Article Title">
                <meta property="article:published_time" content="2023-05-25">
                <meta property="article:author" content="John Doe">
            </head>
            <body>
                <article>
                    <p>This is the article content.</p>
                </article>
            </body>
        </html>
        """
        soup = get_soup(html)
        metadata = extract_metadata(soup)
        
        self.assertEqual(metadata.get("title"), "Article Title")
        self.assertEqual(metadata.get("date"), "2023-05-25")
        self.assertEqual(metadata.get("author"), "John Doe")
        self.assertEqual(metadata.get("content"), "This is the article content.")


class TestRateLimiter(unittest.TestCase):
    """Tests for RateLimiter class."""
    
    def test_rate_limiter_wait(self):
        """Test rate limiter wait method."""
        rate_limiter = RateLimiter(min_interval=1.0)
        
        # First call should not wait
        start_time = time.time()
        rate_limiter.wait()
        elapsed = time.time() - start_time
        self.assertLess(elapsed, 0.1)
        
        # Second call should wait about 1 second
        start_time = time.time()
        rate_limiter.wait()
        elapsed = time.time() - start_time
        self.assertGreater(elapsed, 0.9)
        self.assertLess(elapsed, 1.1)
    
    @mock.patch('time.sleep')
    def test_rate_limiter_decorator(self, mock_sleep):
        """Test rate limiter decorator."""
        rate_limiter = RateLimiter(min_interval=1.0)
        
        @rate_limiter
        def test_function():
            return "result"
        
        # First call should not sleep
        result = test_function()
        self.assertEqual(result, "result")
        mock_sleep.assert_not_called()
        
        # Second call should sleep
        result = test_function()
        self.assertEqual(result, "result")
        mock_sleep.assert_called_once()


class TestHttpSessionManagement(unittest.TestCase):
    """Tests for HTTP session management functions."""
    
    def test_build_session(self):
        """Test session creation."""
        session = build_session(
            user_agent="TestCrawler/1.0",
            accept="text/html",
            accept_language="en-US",
            additional_headers={"X-Test": "test"},
            retries=5,
            backoff_factor=0.5
        )
        
        self.assertIsInstance(session, requests.Session)
        self.assertEqual(session.headers["User-Agent"], "TestCrawler/1.0")
        self.assertEqual(session.headers["Accept"], "text/html")
        self.assertEqual(session.headers["Accept-Language"], "en-US")
        self.assertEqual(session.headers["X-Test"], "test")
        
        # Check that retry adapter is configured
        adapter = session.adapters['https://']
        self.assertEqual(adapter.max_retries.total, 5)
        self.assertEqual(adapter.max_retries.backoff_factor, 0.5)
    
    @mock.patch('requests.Session.request')
    def test_safe_request(self, mock_request):
        """Test safe request function."""
        # Mock session
        session = requests.Session()
        
        # Mock successful response
        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        
        # Test successful request
        response = safe_request(
            url="https://example.com/page",
            session=session,
            timeout=10,
            max_retries=3
        )
        
        self.assertEqual(response, mock_response)
        mock_request.assert_called_once()
        
        # Reset mocks
        mock_request.reset_mock()
        
        # Test request with validation function
        validate_func = lambda url: url.startswith("https://example.com")
        
        # Valid URL
        response = safe_request(
            url="https://example.com/page",
            session=session,
            validate_func=validate_func,
            timeout=10,
            max_retries=3
        )
        
        self.assertEqual(response, mock_response)
        mock_request.assert_called_once()
        
        # Reset mocks
        mock_request.reset_mock()
        
        # Invalid URL
        response = safe_request(
            url="https://malicious.com/page",
            session=session,
            validate_func=validate_func,
            timeout=10,
            max_retries=3
        )
        
        self.assertIsNone(response)
        mock_request.assert_not_called()


class TestErrorHandling(unittest.TestCase):
    """Tests for error handling functions."""
    
    def test_is_success_status(self):
        """Test success status check."""
        self.assertTrue(is_success_status(200))
        self.assertTrue(is_success_status(201))
        self.assertTrue(is_success_status(299))
        
        self.assertFalse(is_success_status(199))
        self.assertFalse(is_success_status(300))
        self.assertFalse(is_success_status(404))
        self.assertFalse(is_success_status(500))
    
    def test_handle_http_error(self):
        """Test HTTP error handling."""
        # Create mock responses
        ok_response = mock.Mock()
        ok_response.status_code = 200
        
        not_found_response = mock.Mock()
        not_found_response.status_code = 404
        not_found_response.url = "https://example.com/not-found"
        
        server_error_response = mock.Mock()
        server_error_response.status_code = 500
        server_error_response.url = "https://example.com/error"
        
        # Test responses
        self.assertIsNone(handle_http_error(ok_response))
        
        error_message = handle_http_error(not_found_response)
        self.assertIn("Not found", error_message)
        self.assertIn("https://example.com/not-found", error_message)
        
        error_message = handle_http_error(server_error_response)
        self.assertIn("Internal server error", error_message)
        self.assertIn("https://example.com/error", error_message)
    
    @mock.patch('time.sleep')
    def test_retry_on_error_decorator(self, mock_sleep):
        """Test retry on error decorator."""
        
        # Test function that fails twice then succeeds
        fail_count = [0]
        
        @retry_on_error(max_retries=3, backoff_factor=0.1)
        def test_function():
            fail_count[0] += 1
            if fail_count[0] <= 2:
                raise requests.RequestException("Test error")
            return "success"
        
        # Function should succeed after retries
        result = test_function()
        self.assertEqual(result, "success")
        self.assertEqual(fail_count[0], 3)
        self.assertEqual(mock_sleep.call_count, 2)
        
        # Reset mocks and counter
        mock_sleep.reset_mock()
        fail_count[0] = 0
        
        # Test function that always fails
        @retry_on_error(max_retries=2, backoff_factor=0.1)
        def always_fails():
            fail_count[0] += 1
            raise requests.RequestException("Always fails")
        
        # Function should raise exception after max retries
        with self.assertRaises(requests.RequestException):
            always_fails()
        
        self.assertEqual(fail_count[0], 3)  # Initial call + 2 retries
        self.assertEqual(mock_sleep.call_count, 2)


if __name__ == "__main__":
    unittest.main()
