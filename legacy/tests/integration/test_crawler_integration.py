"""
Integration tests for crawler implementations.

These tests verify that the crawler implementations correctly use the functions
from crawler_utils.py and that the error handling improvements work as expected.
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
import aiohttp
from aiohttp.client_exceptions import ClientError, ClientResponseError, ClientConnectionError
import requests
from requests.exceptions import RequestException, Timeout, HTTPError
from bs4 import BeautifulSoup
import sys
import os
from typing import Dict, Any, List, Optional, Union

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

# Import crawler utilities
from citadel.utils.crawler_utils import (
    validate_url, get_soup, extract_links, RateLimiter, build_session,
    safe_request, retry_on_error, extract_metadata, handle_http_error,
    CrawlerError, URLValidationError, HTTPError as CrawlerHTTPError,
    RateLimitError, ParsingError
)


# Test data
SAMPLE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
    <meta name="description" content="Test description">
    <meta property="og:title" content="OG Test Title">
</head>
<body>
    <h1>Test Heading</h1>
    <p>Test paragraph with <a href="https://example.com/page1">link 1</a> and 
       <a href="/page2">link 2</a>.</p>
    <div class="content">
        <p>Some content here</p>
    </div>
</body>
</html>
"""

SAMPLE_CONFIG = {
    'user_agent': 'TestCrawler/1.0',
    'timeout': 5,
    'max_retries': 2,
    'retry_delay': 0.1,
    'headers': {'Accept': 'text/html'},
    'extraction_patterns': {
        'main_content': '.content',
        'heading': 'h1'
    },
    'validate_ssl': False,
    'max_depth': 2,
    'max_urls': 10,
    'follow_external_links': False,
    'max_concurrent_requests': 3,
    'min_request_interval': 0.1,
    'base_url': 'https://example.com'
}


# Fixtures
@pytest.fixture
def mock_requests_session():
    """Create a mock requests Session."""
    session = MagicMock()
    response = MagicMock()
    response.status_code = 200
    response.text = SAMPLE_HTML
    response.content = SAMPLE_HTML.encode('utf-8')
    response.url = "https://example.com"
    response.raise_for_status = MagicMock()
    session.get.return_value = response
    session.request.return_value = response
    return session


# Helper functions
def async_return(result):
    """Helper to create an awaitable that returns a value."""
    f = asyncio.Future()
    f.set_result(result)
    return f


# Tests for validate_url function
class TestValidateUrl:
    """Tests for the validate_url function."""

    def test_valid_url(self):
        """Test that validate_url correctly validates a valid URL."""
        # Arrange
        url = "https://example.com/page"
        base_url = "https://example.com"
        
        # Act
        result = validate_url(url, base_url)
        
        # Assert
        assert result is True

    def test_invalid_url(self):
        """Test that validate_url correctly invalidates an invalid URL."""
        # Arrange
        url = "invalid://example.com"
        base_url = "https://example.com"
        
        # Act
        result = validate_url(url, base_url)
        
        # Assert
        assert result is False

    def test_url_with_allowed_domains(self):
        """Test that validate_url correctly validates a URL with allowed domains."""
        # Arrange
        url = "https://subdomain.example.com/page"
        base_url = "https://example.com"
        allowed_domains = ["subdomain.example.com"]
        
        # Act
        result = validate_url(url, base_url, allowed_domains=allowed_domains)
        
        # Assert
        assert result is True

    def test_url_with_excluded_patterns(self):
        """Test that validate_url correctly invalidates a URL with excluded patterns."""
        # Arrange
        url = "https://example.com/admin/page"
        base_url = "https://example.com"
        excluded_patterns = ["/admin/"]
        
        # Act
        result = validate_url(url, base_url, excluded_patterns=excluded_patterns)
        
        # Assert
        assert result is False


# Tests for get_soup function
class TestGetSoup:
    """Tests for the get_soup function."""

    def test_valid_html(self):
        """Test that get_soup correctly parses valid HTML."""
        # Arrange
        html = SAMPLE_HTML
        
        # Act
        soup = get_soup(html)
        
        # Assert
        assert soup is not None
        assert soup.title.text == "Test Page"

    def test_invalid_html(self):
        """Test that get_soup handles invalid HTML gracefully."""
        # Arrange
        html = "<html><unclosed_tag>"
        
        # Act
        soup = get_soup(html)
        
        # Assert
        assert soup is not None  # BeautifulSoup is quite forgiving with malformed HTML


# Tests for extract_links function
class TestExtractLinks:
    """Tests for the extract_links function."""

    def test_extract_links(self):
        """Test that extract_links correctly extracts links from HTML."""
        # Arrange
        soup = BeautifulSoup(SAMPLE_HTML, 'html.parser')
        base_url = "https://example.com"
        
        # Act
        links = extract_links(soup, base_url)
        
        # Assert
        assert len(links) == 2
        assert "https://example.com/page1" in links
        assert "https://example.com/page2" in links


# Tests for RateLimiter class
class TestRateLimiter:
    """Tests for the RateLimiter class."""

    def test_wait(self):
        """Test that RateLimiter.wait correctly delays execution."""
        # Arrange
        rate_limiter = RateLimiter(min_interval=0.1)
        
        # Act & Assert
        with patch('time.sleep') as mock_sleep:
            rate_limiter.wait()  # First call should not sleep
            assert not mock_sleep.called
            
            rate_limiter.wait()  # Second call should sleep
            assert mock_sleep.called

    def test_decorator(self):
        """Test that RateLimiter can be used as a decorator."""
        # Arrange
        rate_limiter = RateLimiter(min_interval=0.1)
        
        @rate_limiter
        def test_func():
            return "test"
        
        # Act & Assert
        with patch('time.sleep') as mock_sleep:
            test_func()  # First call should not sleep
            assert not mock_sleep.called
            
            test_func()  # Second call should sleep
            assert mock_sleep.called


# Tests for safe_request function
class TestSafeRequest:
    """Tests for the safe_request function."""

    def test_successful_request(self, mock_requests_session):
        """Test a successful request with the safe_request function."""
        # Arrange
        url = "https://example.com/test"
        
        # Act
        response = safe_request(
            url=url,
            session=mock_requests_session,
            timeout=5,
            max_retries=2
        )
        
        # Assert
        assert response is not None
        assert response.status_code == 200
        assert response.text == SAMPLE_HTML
        
        # Verify that session.request was called with the correct parameters
        mock_requests_session.request.assert_called_once_with(
            method='GET',
            url=url,
            timeout=5
        )

    def test_request_with_validation(self, mock_requests_session):
        """Test a request with URL validation."""
        # Arrange
        url = "https://example.com/test"
        validate_func = lambda u: u.startswith('https://')
        
        # Act
        response = safe_request(
            url=url,
            session=mock_requests_session,
            validate_func=validate_func,
            timeout=5,
            max_retries=2
        )
        
        # Assert
        assert response is not None
        assert response.status_code == 200
        
        # Test with invalid URL
        invalid_url = "http://example.com/test"  # Not https
        
        # Act
        response = safe_request(
            url=invalid_url,
            session=mock_requests_session,
            validate_func=validate_func,
            timeout=5,
            max_retries=2
        )
        
        # Assert
        assert response is None

    def test_request_with_rate_limiting(self, mock_requests_session):
        """Test a request with rate limiting."""
        # Arrange
        url = "https://example.com/test"
        rate_limiter = RateLimiter(min_interval=0.1)
        
        # Mock time.sleep to track calls
        with patch('time.sleep') as mock_sleep:
            # Act
            # First request should not trigger rate limiting
            safe_request(
                url=url,
                session=mock_requests_session,
                rate_limiter=rate_limiter,
                timeout=5,
                max_retries=2
            )
            
            # Second request should trigger rate limiting
            safe_request(
                url=url,
                session=mock_requests_session,
                rate_limiter=rate_limiter,
                timeout=5,
                max_retries=2
            )
            
            # Assert
            # Verify that time.sleep was called at least once
            assert mock_sleep.called

    def test_request_with_retry(self, mock_requests_session):
        """Test a request with retry on error."""
        # Arrange
        url = "https://example.com/test"
        
        # Make the session.request method raise an exception twice, then succeed
        mock_requests_session.request.side_effect = [
            requests.ConnectionError("Connection refused"),
            requests.ConnectionError("Connection refused"),
            mock_requests_session.request.return_value
        ]
        
        # Mock time.sleep to avoid actual delays
        with patch('time.sleep'):
            # Act
            response = safe_request(
                url=url,
                session=mock_requests_session,
                timeout=5,
                max_retries=2
            )
            
            # Assert
            assert response is not None
            assert response.status_code == 200
            
            # Verify that session.request was called 3 times (2 failures + 1 success)
            assert mock_requests_session.request.call_count == 3


# Tests for retry_on_error decorator
class TestRetryOnError:
    """Tests for the retry_on_error decorator."""

    def test_retry_on_exception(self):
        """Test that the retry_on_error decorator retries on exceptions."""
        # Arrange
        mock_func = MagicMock()
        mock_func.side_effect = [
            requests.ConnectionError("Connection refused"),
            requests.ConnectionError("Connection refused"),
            "success"
        ]
        
        # Apply the decorator
        decorated_func = retry_on_error(
            max_retries=2,
            backoff_factor=0.1,
            exceptions=[requests.RequestException]
        )(mock_func)
        
        # Mock time.sleep to avoid actual delays
        with patch('time.sleep'):
            # Act
            result = decorated_func()
            
            # Assert
            assert result == "success"
            assert mock_func.call_count == 3

    def test_max_retries_exceeded(self):
        """Test that the retry_on_error decorator raises an exception when max retries are exceeded."""
        # Arrange
        mock_func = MagicMock()
        mock_func.side_effect = requests.ConnectionError("Connection refused")
        
        # Apply the decorator
        decorated_func = retry_on_error(
            max_retries=2,
            backoff_factor=0.1,
            exceptions=[requests.RequestException]
        )(mock_func)
        
        # Mock time.sleep to avoid actual delays
        with patch('time.sleep'):
            # Act & Assert
            with pytest.raises(requests.ConnectionError):
                decorated_func()
                
            # Verify that the function was called 3 times (initial + 2 retries)
            assert mock_func.call_count == 3


# Run the tests
if __name__ == "__main__":
    pytest.main(["-v", __file__])
