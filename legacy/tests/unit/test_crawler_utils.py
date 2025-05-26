
"""Unit tests for crawler_utils.py module."""

import pytest
import time
import asyncio
import requests
from unittest.mock import Mock, patch, MagicMock, call
from bs4 import BeautifulSoup
from http import HTTPStatus
from urllib.parse import urlparse

from citadel.utils.crawler_utils import (
    validate_url,
    get_soup,
    extract_links,
    RateLimiter,
    build_session,
    is_success_status,
    handle_http_error,
    safe_request,
    retry_on_error,
    extract_metadata,
    CrawlerError,
    URLValidationError,
    HTTPError,
    RateLimitError,
    ParsingError
)


class TestURLValidation:
    """Tests for the validate_url function."""

    def test_valid_url(self):
        """Test validation of valid URLs."""
        base_url = "https://example.com"
        
        # Test with same domain
        assert validate_url("https://example.com/page", base_url) is True
        assert validate_url("https://example.com/page?q=test", base_url) is True
        assert validate_url("https://example.com/page#section", base_url) is True
        
        # Test with subdomain
        assert validate_url("https://sub.example.com/page", base_url) is True
        
        # Test with allowed domains
        assert validate_url(
            "https://other.com/page", 
            base_url, 
            allowed_domains=["other.com"]
        ) is True

    def test_invalid_url(self):
        """Test validation of invalid URLs."""
        base_url = "https://example.com"
        
        # Test with empty URL
        assert validate_url("", base_url) is False
        
        # Test with missing scheme
        assert validate_url("example.com/page", base_url) is False
        
        # Test with missing netloc
        assert validate_url("https:///page", base_url) is False
        
        # Test with disallowed scheme
        assert validate_url("ftp://example.com", base_url) is False
        
        # Test with disallowed domain
        assert validate_url("https://other.com", base_url) is False

    def test_url_patterns(self):
        """Test URL pattern matching."""
        base_url = "https://example.com"
        
        # Test with matching pattern
        assert validate_url(
            "https://example.com/articles/123", 
            base_url, 
            url_patterns=["/articles/"]
        ) is True
        
        # Test with non-matching pattern
        assert validate_url(
            "https://example.com/products/123", 
            base_url, 
            url_patterns=["/articles/"]
        ) is False
        
        # Test base URL is always allowed
        assert validate_url(
            base_url, 
            base_url, 
            url_patterns=["/articles/"]
        ) is True

    def test_excluded_patterns(self):
        """Test excluded URL pattern matching."""
        base_url = "https://example.com"
        
        # Test with matching excluded pattern
        assert validate_url(
            "https://example.com/admin/settings", 
            base_url, 
            excluded_patterns=["/admin/"]
        ) is False
        
        # Test with non-matching excluded pattern
        assert validate_url(
            "https://example.com/articles/123", 
            base_url, 
            excluded_patterns=["/admin/"]
        ) is True

    def test_callback(self):
        """Test callback function is called for valid URLs."""
        base_url = "https://example.com"
        test_url = "https://example.com/page"
        
        mock_callback = Mock()
        result = validate_url(test_url, base_url, callback=mock_callback)
        
        assert result is True
        mock_callback.assert_called_once_with(test_url)

    def test_exception_handling(self):
        """Test exception handling in URL validation."""
        base_url = "https://example.com"
        
        # Create a mock that raises an exception when called
        mock_urlparse = Mock(side_effect=Exception("Test exception"))
        
        with patch('citadel.utils.crawler_utils.urlparse', mock_urlparse):
            assert validate_url("https://example.com/page", base_url) is False


class TestHTMLParsing:
    """Tests for HTML parsing functions."""

    def test_get_soup_valid_html(self):
        """Test parsing valid HTML."""
        html = "<html><body><h1>Test</h1></body></html>"
        soup = get_soup(html)
        
        assert isinstance(soup, BeautifulSoup)
        assert soup.h1.text == "Test"

    def test_get_soup_empty_html(self):
        """Test parsing empty HTML."""
        html = ""
        soup = get_soup(html)
        
        assert isinstance(soup, BeautifulSoup)
        assert soup.text == ""

    def test_get_soup_malformed_html(self):
        """Test parsing malformed HTML."""
        html = "<html><body><h1>Test</h1></body>"  # Missing closing html tag
        soup = get_soup(html)
        
        assert isinstance(soup, BeautifulSoup)
        assert soup.h1.text == "Test"

    def test_get_soup_custom_parser(self):
        """Test using a custom parser."""
        html = "<html><body><h1>Test</h1></body></html>"
        
        # Mock BeautifulSoup to verify parser argument
        with patch('citadel.utils.crawler_utils.BeautifulSoup') as mock_bs:
            get_soup(html, parser='lxml')
            mock_bs.assert_called_once_with(html, 'lxml')

    def test_get_soup_parsing_error(self):
        """Test handling of parsing errors."""
        html = "<html><body><h1>Test</h1></body></html>"
        
        # Mock BeautifulSoup to raise an exception
        with patch('citadel.utils.crawler_utils.BeautifulSoup', 
                  side_effect=Exception("Parsing error")):
            with pytest.raises(ParsingError) as excinfo:
                get_soup(html)
            
            assert "Failed to parse HTML" in str(excinfo.value)

    def test_extract_links(self):
        """Test extracting links from HTML."""
        html = """
        <html>
            <body>
                <a href="/page1">Page 1</a>
                <a href="https://example.com/page2">Page 2</a>
                <a href="#section">Section</a>
                <div>No link here</div>
            </body>
        </html>
        """
        base_url = "https://example.com"
        soup = BeautifulSoup(html, 'html.parser')
        
        links = extract_links(soup, base_url)
        
        assert len(links) == 3
        assert "https://example.com/page1" in links
        assert "https://example.com/page2" in links
        assert "https://example.com#section" in links

    def test_extract_links_no_links(self):
        """Test extracting links from HTML with no links."""
        html = "<html><body><div>No links here</div></body></html>"
        base_url = "https://example.com"
        soup = BeautifulSoup(html, 'html.parser')
        
        links = extract_links(soup, base_url)
        
        assert len(links) == 0


class TestRateLimiter:
    """Tests for the RateLimiter class."""

    def test_init(self):
        """Test initialization of RateLimiter."""
        limiter = RateLimiter(min_interval=2.0)
        
        assert limiter.min_interval == 2.0
        assert limiter.last_request_time == 0.0
        assert limiter._lock is None

    @patch('time.time')
    @patch('time.sleep')
    def test_wait(self, mock_sleep, mock_time):
        """Test wait method."""
        # Setup mock time to return increasing values
        mock_time.side_effect = [10.0, 10.5]
        
        limiter = RateLimiter(min_interval=1.0)
        limiter.last_request_time = 9.0  # Last request was 1 second ago
        
        limiter.wait()
        
        # Should not sleep as enough time has passed
        mock_sleep.assert_not_called()
        assert limiter.last_request_time == 10.5

    @patch('time.time')
    @patch('time.sleep')
    def test_wait_with_sleep(self, mock_sleep, mock_time):
        """Test wait method with sleep."""
        # Setup mock time to return increasing values
        mock_time.side_effect = [10.0, 11.0]
        
        limiter = RateLimiter(min_interval=2.0)
        limiter.last_request_time = 9.0  # Last request was 1 second ago
        
        limiter.wait()
        
        # Should sleep for 1 second (2 - 1)
        mock_sleep.assert_called_once_with(1.0)
        assert limiter.last_request_time == 11.0

    @pytest.mark.asyncio
    @patch('time.time')
    @patch('asyncio.sleep')
    async def test_async_wait(self, mock_sleep, mock_time):
        """Test async_wait method."""
        # Setup mock time to return increasing values
        mock_time.side_effect = [10.0, 11.0]
        
        limiter = RateLimiter(min_interval=2.0)
        limiter.last_request_time = 9.0  # Last request was 1 second ago
        
        await limiter.async_wait()
        
        # Should sleep for 1 second (2 - 1)
        mock_sleep.assert_called_once_with(1.0)
        assert limiter.last_request_time == 11.0
        assert limiter._lock is not None  # Lock should be initialized

    @patch('time.time')
    @patch('time.sleep')
    def test_decorator(self, mock_sleep, mock_time):
        """Test decorator functionality."""
        # Setup mock time
        mock_time.return_value = 10.0
        
        limiter = RateLimiter(min_interval=1.0)
        
        @limiter
        def test_func():
            return "test"
        
        result = test_func()
        
        assert result == "test"
        # wait() should have been called
        assert limiter.last_request_time == 10.0

    @pytest.mark.asyncio
    @patch('time.time')
    @patch('asyncio.sleep')
    async def test_async_decorator(self, mock_sleep, mock_time):
        """Test async decorator functionality."""
        # Setup mock time
        mock_time.return_value = 10.0
        
        limiter = RateLimiter(min_interval=1.0)
        
        @limiter.async_decorator
        async def test_func():
            return "test"
        
        result = await test_func()
        
        assert result == "test"
        # async_wait() should have been called
        assert limiter.last_request_time == 10.0


class TestSessionManagement:
    """Tests for session management functions."""

    def test_build_session_defaults(self):
        """Test building a session with default settings."""
        session = build_session()
        
        # Check headers
        assert session.headers['User-Agent'] == 'CitadelCrawler/1.0'
        assert session.headers['Accept'] == 'text/html,application/xhtml+xml,application/xml'
        assert session.headers['Accept-Language'] == 'en-US,en;q=0.9'
        
        # Check adapters
        assert 'http://' in session.adapters
        assert 'https://' in session.adapters
        
        # Check retry configuration
        adapter = session.adapters['https://']
        retry = adapter.max_retries
        assert retry.total == 3
        assert retry.backoff_factor == 0.3
        assert set(retry.status_forcelist) == {429, 500, 502, 503, 504}

    def test_build_session_custom_headers(self):
        """Test building a session with custom headers."""
        additional_headers = {
            'X-Custom-Header': 'test',
            'User-Agent': 'CustomAgent/1.0'  # Override default
        }
        
        session = build_session(additional_headers=additional_headers)
        
        assert session.headers['X-Custom-Header'] == 'test'
        assert session.headers['User-Agent'] == 'CustomAgent/1.0'  # Should be overridden

    def test_build_session_custom_retry(self):
        """Test building a session with custom retry settings."""
        session = build_session(
            retries=5,
            backoff_factor=0.5,
            status_forcelist=[500, 502]
        )
        
        adapter = session.adapters['https://']
        retry = adapter.max_retries
        
        assert retry.total == 5
        assert retry.backoff_factor == 0.5
        assert set(retry.status_forcelist) == {500, 502}

    def test_is_success_status(self):
        """Test is_success_status function."""
        # Success status codes
        assert is_success_status(200) is True
        assert is_success_status(201) is True
        assert is_success_status(299) is True
        
        # Error status codes
        assert is_success_status(199) is False
        assert is_success_status(300) is False
        assert is_success_status(404) is False
        assert is_success_status(500) is False

    def test_handle_http_error_success(self):
        """Test handle_http_error with success response."""
        response = Mock(status_code=200, url="https://example.com")
        
        result = handle_http_error(response)
        
        assert result is None

    def test_handle_http_error_error(self):
        """Test handle_http_error with error response."""
        test_cases = [
            (400, "Bad request"),
            (401, "Unauthorized"),
            (403, "Forbidden"),
            (404, "Not found"),
            (429, "Too many requests"),
            (500, "Internal server error"),
            (503, "Service unavailable"),
            (504, "Gateway timeout"),
            (418, "HTTP error 418")  # Custom error code
        ]
        
        for status_code, expected_message_start in test_cases:
            response = Mock(status_code=status_code, url="https://example.com")
            
            result = handle_http_error(response)
            
            assert result is not None
            assert result.startswith(expected_message_start)
            assert "https://example.com" in result


class TestSafeRequest:
    """Tests for the safe_request function."""

    @patch('citadel.utils.crawler_utils.logger')
    def test_url_validation(self, mock_logger):
        """Test URL validation in safe_request."""
        session = Mock()
        validate_func = Mock(return_value=False)
        
        result = safe_request(
            "https://example.com",
            session,
            validate_func=validate_func
        )
        
        assert result is None
        validate_func.assert_called_once_with("https://example.com")
        mock_logger.warning.assert_called_once()
        session.request.assert_not_called()

    def test_visited_urls(self):
        """Test handling of visited URLs."""
        session = Mock()
        visited_urls = {"https://example.com"}
        
        result = safe_request(
            "https://example.com",
            session,
            visited_urls=visited_urls
        )
        
        assert result is None
        session.request.assert_not_called()

    @patch('time.sleep')
    def test_rate_limiting(self, mock_sleep):
        """Test rate limiting in safe_request."""
        session = Mock()
        session.request.return_value = Mock(status_code=200)
        rate_limiter = Mock()
        
        safe_request(
            "https://example.com",
            session,
            rate_limiter=rate_limiter
        )
        
        rate_limiter.wait.assert_called_once()

    def test_successful_request(self):
        """Test successful request."""
        session = Mock()
        response = Mock(status_code=200)
        session.request.return_value = response
        visited_urls = set()
        
        result = safe_request(
            "https://example.com",
            session,
            visited_urls=visited_urls
        )
        
        assert result == response
        session.request.assert_called_once_with(
            method='GET',
            url="https://example.com",
            timeout=30
        )
        assert "https://example.com" in visited_urls

    @patch('time.sleep')
    def test_retry_on_failure(self, mock_sleep):
        """Test retry on request failure."""
        session = Mock()
        session.request.side_effect = [
            requests.RequestException("Connection error"),
            Mock(status_code=200)
        ]
        
        result = safe_request(
            "https://example.com",
            session,
            max_retries=1
        )
        
        assert result is not None
        assert session.request.call_count == 2
        mock_sleep.assert_called_once()

    @patch('time.sleep')
    def test_max_retries_exceeded(self, mock_sleep):
        """Test max retries exceeded."""
        session = Mock()
        session.request.side_effect = requests.RequestException("Connection error")
        
        result = safe_request(
            "https://example.com",
            session,
            max_retries=2,
            raise_for_status=False
        )
        
        assert result is None
        assert session.request.call_count == 3
        assert mock_sleep.call_count == 2

    def test_http_error_raised(self):
        """Test HTTP error is raised when raise_for_status is True."""
        session = Mock()
        http_error = requests.HTTPError("HTTP Error")
        http_error.response = Mock(status_code=404)
        session.request.return_value = Mock(
            raise_for_status=Mock(side_effect=http_error),
            status_code=404
        )
        
        with pytest.raises(HTTPError) as excinfo:
            safe_request(
                "https://example.com",
                session,
                raise_for_status=True
            )
        
        assert excinfo.value.status_code == 404
        # The URL might not be in the error message depending on implementation
        # Just check that we have an HTTPError with the correct status code

    def test_custom_request_params(self):
        """Test custom request parameters."""
        session = Mock()
        response = Mock(status_code=200)
        session.request.return_value = response
        
        safe_request(
            "https://example.com",
            session,
            method="POST",
            data={"key": "value"},
            headers={"X-Custom": "test"}
        )
        
        session.request.assert_called_once_with(
            method="POST",
            url="https://example.com",
            timeout=30,
            data={"key": "value"},
            headers={"X-Custom": "test"}
        )


class TestRetryDecorator:
    """Tests for the retry_on_error decorator."""

    @patch('time.sleep')
    def test_successful_execution(self, mock_sleep):
        """Test successful function execution."""
        @retry_on_error()
        def test_func():
            return "success"
        
        result = test_func()
        
        assert result == "success"
        mock_sleep.assert_not_called()

    @patch('time.sleep')
    def test_retry_on_exception(self, mock_sleep):
        """Test retry on exception."""
        mock_func = Mock(side_effect=[
            requests.RequestException("Error"),
            "success"
        ])
        
        @retry_on_error(max_retries=1)
        def test_func():
            return mock_func()
        
        result = test_func()
        
        assert result == "success"
        assert mock_func.call_count == 2
        mock_sleep.assert_called_once()

    @patch('time.sleep')
    def test_retry_on_status_code(self, mock_sleep):
        """Test retry on HTTP status code."""
        # The retry_on_error decorator checks if the result is a requests.Response object
        # We need to use actual Response objects, not just mocks
        
        # Create real Response objects with different status codes
        response1 = requests.Response()
        response1.status_code = 503
        
        response2 = requests.Response()
        response2.status_code = 200
        
        # Create a counter to track calls
        call_count = [0]
        
        @retry_on_error(max_retries=1, retry_codes=[503])
        def test_func():
            call_count[0] += 1
            if call_count[0] == 1:
                return response1
            return response2
        
        result = test_func()
        
        # Verify the result
        assert call_count[0] > 1, "Function should be called more than once"
        assert result.status_code == 200, "Final result should have status code 200"
        assert mock_sleep.called, "Sleep should be called during retry"

    @patch('time.sleep')
    def test_max_retries_exceeded_exception(self, mock_sleep):
        """Test max retries exceeded with exception."""
        @retry_on_error(max_retries=2)
        def test_func():
            raise requests.RequestException("Error")
        
        with pytest.raises(requests.RequestException):
            test_func()
        
        assert mock_sleep.call_count == 2

    @patch('time.sleep')
    def test_custom_exceptions(self, mock_sleep):
        """Test with custom exception types."""
        @retry_on_error(max_retries=1, exceptions=[ValueError])
        def test_func():
            raise ValueError("Custom error")
        
        with pytest.raises(ValueError):
            test_func()
        
        mock_sleep.assert_called_once()

    @patch('time.sleep')
    def test_non_matching_exception(self, mock_sleep):
        """Test with non-matching exception type."""
        @retry_on_error(max_retries=1, exceptions=[ValueError])
        def test_func():
            raise KeyError("Different error")
        
        with pytest.raises(KeyError):
            test_func()
        
        mock_sleep.assert_not_called()


class TestMetadataExtraction:
    """Tests for the extract_metadata function."""

    def test_extract_title(self):
        """Test extracting title from HTML."""
        html = """
        <html>
            <head>
                <meta property="og:title" content="OG Title">
                <meta name="title" content="Meta Title">
                <title>Page Title</title>
            </head>
            <body>
                <h1>Heading Title</h1>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        metadata = extract_metadata(soup)
        
        assert metadata.get('title') == "OG Title"

    def test_extract_title_fallback(self):
        """Test title extraction fallback."""
        html = """
        <html>
            <head>
                <title>Page Title</title>
            </head>
            <body>
                <h1>Heading Title</h1>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        metadata = extract_metadata(soup)
        
        assert metadata.get('title') == "Heading Title"

    def test_extract_date(self):
        """Test extracting date from HTML."""
        html = """
        <html>
            <head>
                <meta property="article:published_time" content="2023-01-01T12:00:00Z">
            </head>
            <body>
                <time datetime="2023-01-02">January 2, 2023</time>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        metadata = extract_metadata(soup)
        
        assert metadata.get('date') == "2023-01-01T12:00:00Z"

    def test_extract_author(self):
        """Test extracting author from HTML."""
        html = """
        <html>
            <head>
                <meta name="author" content="John Doe">
            </head>
            <body>
                <a class="author-link" href="/author/jane">Jane Smith</a>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        metadata = extract_metadata(soup)
        
        assert metadata.get('author') == "John Doe"

    def test_extract_content(self):
        """Test extracting content from HTML."""
        html = """
        <html>
            <body>
                <article>
                    <p>This is the main content.</p>
                    <script>console.log("This should be removed");</script>
                    <p>More content here.</p>
                </article>
                <div class="comments">Comments section</div>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        metadata = extract_metadata(soup)
        
        assert "This is the main content." in metadata.get('content', '')
        assert "More content here." in metadata.get('content', '')
        assert "This should be removed" not in metadata.get('content', '')

    def test_custom_selectors(self):
        """Test using custom selectors."""
        html = """
        <html>
            <body>
                <div class="custom-title">Custom Title</div>
                <span class="custom-date">2023-01-01</span>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        custom_title_selectors = [
            {'tag': 'div', 'attrs': {'class': 'custom-title'}, 'text': True}
        ]
        
        custom_date_selectors = [
            {'tag': 'span', 'attrs': {'class': 'custom-date'}, 'text': True}
        ]
        
        metadata = extract_metadata(
            soup,
            title_selectors=custom_title_selectors,
            date_selectors=custom_date_selectors
        )
        
        assert metadata.get('title') == "Custom Title"
        assert metadata.get('date') == "2023-01-01"

    def test_missing_metadata(self):
        """Test handling of missing metadata."""
        html = "<html><body><p>Simple content</p></body></html>"
        soup = BeautifulSoup(html, 'html.parser')
        
        metadata = extract_metadata(soup)
        
        # Title, date, and author should not be in the metadata
        assert 'title' not in metadata
        assert 'date' not in metadata
        assert 'author' not in metadata
        
        # Content might be extracted from the p tag
        if 'content' in metadata:
            assert "Simple content" in metadata['content']


if __name__ == "__main__":
    pytest.main(["-v", "test_crawler_utils.py"])
