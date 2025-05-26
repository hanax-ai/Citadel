"""Utility functions for web crawlers.

This module provides common utility functions for web crawlers to avoid code duplication
across different crawler implementations. It includes URL validation, HTML parsing,
rate limiting, error handling, and HTTP session management.
"""

import time
import asyncio
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Optional, Dict, Any, List, Union, Set, Callable, TypeVar, Type
from bs4 import BeautifulSoup
import re
import logging
import functools
from urllib.parse import urlparse, urljoin
from http import HTTPStatus

logger = logging.getLogger(__name__)

# Type variables for better type hinting
T = TypeVar('T')
R = TypeVar('R')


class CrawlerError(Exception):
    """Base exception class for crawler errors."""
    pass


class URLValidationError(CrawlerError):
    """Exception raised for URL validation errors."""
    pass


class HTTPError(CrawlerError):
    """Exception raised for HTTP errors."""
    def __init__(self, status_code: int, url: str, message: Optional[str] = None):
        self.status_code = status_code
        self.url = url
        self.message = message or f"HTTP error {status_code} for URL: {url}"
        super().__init__(self.message)


class RateLimitError(CrawlerError):
    """Exception raised when rate limit is exceeded."""
    pass


class ParsingError(CrawlerError):
    """Exception raised for HTML parsing errors."""
    pass


def validate_url(url: str, base_url: str, allowed_domains: Optional[List[str]] = None,
                 allowed_schemes: Optional[List[str]] = None,
                 url_patterns: Optional[List[str]] = None,
                 excluded_patterns: Optional[List[str]] = None,
                 callback: Optional[Callable[[str], None]] = None) -> bool:
    """Validate if a URL is valid and belongs to the allowed domains.
    
    This function checks if a URL is valid and belongs to the allowed domains.
    It also checks if the URL matches any of the allowed patterns and doesn't match
    any of the excluded patterns.
    
    Args:
        url: URL to validate
        base_url: Base URL for the crawler
        allowed_domains: List of allowed domains. If None, only the base domain is allowed
        allowed_schemes: List of allowed URL schemes. Defaults to ['http', 'https']
        url_patterns: List of URL patterns to include. URLs matching any of these patterns
                     will be considered valid
        excluded_patterns: List of URL patterns to exclude. URLs matching any of these patterns
                          will be considered invalid
        callback: Optional callback function to call with the URL if it's valid
        
    Returns:
        True if URL is valid, False otherwise
    """
    if not url:
        return False
        
    # Set defaults
    if allowed_schemes is None:
        allowed_schemes = ['http', 'https']
        
    # Parse the URL
    try:
        parsed_url = urlparse(url)
        
        # Check if scheme and netloc are present
        if not parsed_url.scheme or not parsed_url.netloc:
            return False
            
        # Check if URL uses allowed schemes
        if parsed_url.scheme not in allowed_schemes:
            return False
            
        # Check if URL belongs to the allowed domains
        base_domain = urlparse(base_url).netloc
        
        # If no additional allowed domains are specified, only allow the base domain
        domains_to_check = [base_domain]
        if allowed_domains:
            domains_to_check.extend(allowed_domains)
            
        domain_valid = False
        for domain in domains_to_check:
            if parsed_url.netloc == domain or parsed_url.netloc.endswith('.' + domain):
                domain_valid = True
                break
                
        if not domain_valid:
            return False
            
        # Check excluded patterns
        if excluded_patterns:
            if any(pattern in url for pattern in excluded_patterns):
                return False
                
        # Check URL patterns
        if url_patterns:
            # If URL patterns are specified, at least one must match
            # Exception: the base URL itself is always allowed
            if url == base_url:
                pass  # Allow the base URL
            elif not any(pattern in url for pattern in url_patterns):
                return False
                
        # If a callback is provided, call it with the URL
        if callback:
            callback(url)
            
        return True
        
    except Exception as e:
        logger.error(f"Error validating URL {url}: {str(e)}")
        return False


def get_soup(html_content: str, parser: str = 'html.parser') -> BeautifulSoup:
    """Parse HTML content using BeautifulSoup.
    
    Args:
        html_content: Raw HTML content
        parser: HTML parser to use. Default is 'html.parser', but 'lxml' might be faster
                if installed
        
    Returns:
        BeautifulSoup object
    
    Raises:
        ParsingError: If parsing fails
    """
    try:
        return BeautifulSoup(html_content, parser)
    except Exception as e:
        raise ParsingError(f"Failed to parse HTML: {str(e)}")


def extract_links(soup: BeautifulSoup, base_url: str) -> List[str]:
    """Extract all links from a BeautifulSoup object.
    
    Args:
        soup: BeautifulSoup object
        base_url: Base URL to resolve relative links
        
    Returns:
        List of absolute URLs
    """
    links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        absolute_url = urljoin(base_url, href)
        links.append(absolute_url)
    return links


class RateLimiter:
    """Rate limiter for controlling request frequency.
    
    This class provides methods for rate limiting both synchronous and asynchronous
    functions to avoid overloading servers.
    
    Attributes:
        min_interval: Minimum interval between requests in seconds
        last_request_time: Timestamp of the last request
    """
    
    def __init__(self, min_interval: float = 1.0):
        """Initialize the rate limiter.
        
        Args:
            min_interval: Minimum interval between requests in seconds
        """
        self.min_interval = min_interval
        self.last_request_time = 0.0
        self._lock = None  # Will be initialized when needed for async
    
    def wait(self) -> None:
        """Wait if needed to maintain the minimum interval between requests."""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        
        if elapsed < self.min_interval:
            sleep_time = self.min_interval - elapsed
            time.sleep(sleep_time)
            
        self.last_request_time = time.time()
    
    async def async_wait(self) -> None:
        """Asynchronously wait if needed to maintain the minimum interval between requests."""
        if self._lock is None:
            self._lock = asyncio.Lock()
            
        async with self._lock:
            current_time = time.time()
            elapsed = current_time - self.last_request_time
            
            if elapsed < self.min_interval:
                sleep_time = self.min_interval - elapsed
                await asyncio.sleep(sleep_time)
                
            self.last_request_time = time.time()
    
    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        """Decorator to apply rate limiting to a function.
        
        Args:
            func: Function to decorate
            
        Returns:
            Decorated function
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            self.wait()
            return func(*args, **kwargs)
            
        return wrapper
    
    def async_decorator(self, func: Callable[..., T]) -> Callable[..., T]:
        """Decorator to apply rate limiting to an async function.
        
        Args:
            func: Async function to decorate
            
        Returns:
            Decorated async function
        """
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            await self.async_wait()
            return await func(*args, **kwargs)
            
        return wrapper


def build_session(
    user_agent: str = 'CitadelCrawler/1.0',
    accept: str = 'text/html,application/xhtml+xml,application/xml',
    accept_language: str = 'en-US,en;q=0.9',
    additional_headers: Optional[Dict[str, str]] = None,
    retries: int = 3,
    backoff_factor: float = 0.3,
    status_forcelist: Optional[List[int]] = None,
    timeout: Optional[float] = 30.0
) -> requests.Session:
    """Create and configure a requests session with retry capabilities.
    
    Args:
        user_agent: User agent string
        accept: Accept header
        accept_language: Accept-Language header
        additional_headers: Additional headers to add to the session
        retries: Number of retries for failed requests
        backoff_factor: Backoff factor for retries
        status_forcelist: List of HTTP status codes to retry on
        timeout: Request timeout in seconds
        
    Returns:
        Configured requests session
    """
    session = requests.Session()
    
    # Set default headers
    headers = {
        'User-Agent': user_agent,
        'Accept': accept,
        'Accept-Language': accept_language,
    }
    
    if additional_headers:
        headers.update(additional_headers)
        
    session.headers.update(headers)
    
    # Configure retry behavior
    if status_forcelist is None:
        status_forcelist = [429, 500, 502, 503, 504]
        
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"]
    )
    
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    return session


def is_success_status(status_code: int) -> bool:
    """Check if an HTTP status code indicates success.
    
    Args:
        status_code: HTTP status code
        
    Returns:
        True if status code indicates success, False otherwise
    """
    return 200 <= status_code < 300


def handle_http_error(response: requests.Response) -> Optional[str]:
    """Handle HTTP errors and return an appropriate error message.
    
    Args:
        response: HTTP response
        
    Returns:
        Error message or None if no error
    """
    if is_success_status(response.status_code):
        return None
        
    status_messages = {
        HTTPStatus.BAD_REQUEST: "Bad request",
        HTTPStatus.UNAUTHORIZED: "Unauthorized",
        HTTPStatus.FORBIDDEN: "Forbidden",
        HTTPStatus.NOT_FOUND: "Not found",
        HTTPStatus.TOO_MANY_REQUESTS: "Too many requests",
        HTTPStatus.INTERNAL_SERVER_ERROR: "Internal server error",
        HTTPStatus.SERVICE_UNAVAILABLE: "Service unavailable",
        HTTPStatus.GATEWAY_TIMEOUT: "Gateway timeout",
    }
    
    message = status_messages.get(response.status_code, f"HTTP error {response.status_code}")
    return f"{message}: {response.url}"


def safe_request(
    url: str, 
    session: requests.Session, 
    validate_func: Optional[Callable[[str], bool]] = None,
    rate_limiter: Optional[RateLimiter] = None,
    visited_urls: Optional[Set[str]] = None,
    timeout: int = 30, 
    max_retries: int = 3,
    method: str = 'GET',
    backoff_factor: float = 0.3,
    raise_for_status: bool = True,
    **kwargs
) -> Optional[requests.Response]:
    """Make a safe HTTP request with error handling and retries.
    
    Args:
        url: URL to request
        session: Requests session to use
        validate_func: Optional function to validate the URL
        rate_limiter: Optional rate limiter to control request frequency
        visited_urls: Optional set of visited URLs to avoid duplicates
        timeout: Request timeout in seconds
        max_retries: Maximum number of retries for failed requests
        method: HTTP method (GET, POST, etc.)
        backoff_factor: Factor to use for exponential backoff between retries
        raise_for_status: Whether to raise an exception for HTTP errors
        **kwargs: Additional arguments to pass to requests
        
    Returns:
        Response object or None if request failed
        
    Raises:
        URLValidationError: If URL validation fails
        HTTPError: If HTTP request fails and raise_for_status is True
    """
    # Validate URL if a validation function is provided
    if validate_func and not validate_func(url):
        logger.warning(f"Invalid URL: {url}")
        return None
        
    # Check if URL has already been visited
    if visited_urls is not None and url in visited_urls:
        logger.debug(f"Skipping already visited URL: {url}")
        return None
        
    # Apply rate limiting if a rate limiter is provided
    if rate_limiter:
        rate_limiter.wait()
        
    for attempt in range(max_retries + 1):
        try:
            response = session.request(
                method=method,
                url=url,
                timeout=timeout,
                **kwargs
            )
            
            if raise_for_status:
                response.raise_for_status()
                
            # Add URL to visited set if provided
            if visited_urls is not None:
                visited_urls.add(url)
                
            return response
            
        except requests.RequestException as e:
            logger.warning(f"Request failed (attempt {attempt+1}/{max_retries+1}): {url}, Error: {str(e)}")
            
            if attempt < max_retries:
                # Exponential backoff
                wait_time = backoff_factor * (2 ** attempt)
                logger.info(f"Retrying in {wait_time:.2f} seconds...")
                time.sleep(wait_time)
            else:
                logger.error(f"Max retries exceeded for URL: {url}")
                if raise_for_status and isinstance(e, requests.HTTPError):
                    raise HTTPError(e.response.status_code, url, str(e))
                return None


def retry_on_error(
    max_retries: int = 3, 
    retry_codes: Optional[List[int]] = None,
    backoff_factor: float = 0.3,
    exceptions: Optional[List[Type[Exception]]] = None
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator to retry a function on error.
    
    Args:
        max_retries: Maximum number of retries
        retry_codes: List of HTTP status codes to retry on. If None, retry on all errors
        backoff_factor: Factor to use for exponential backoff between retries
        exceptions: List of exception types to catch and retry on
        
    Returns:
        Decorated function
    """
    if retry_codes is None:
        retry_codes = [429, 500, 502, 503, 504]  # Common retry codes
        
    if exceptions is None:
        exceptions = [requests.RequestException]
        
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            for attempt in range(max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    
                    # Check if result is a Response object and has a status code
                    if isinstance(result, requests.Response):
                        if result.status_code in retry_codes:
                            if attempt < max_retries:
                                wait_time = backoff_factor * (2 ** attempt)
                                logger.info(f"Retrying due to status code {result.status_code} in {wait_time:.2f} seconds...")
                                time.sleep(wait_time)
                                continue
                                
                    return result
                    
                except tuple(exceptions) as e:
                    if attempt < max_retries:
                        wait_time = backoff_factor * (2 ** attempt)
                        logger.warning(f"Error: {str(e)}. Retrying in {wait_time:.2f} seconds... (attempt {attempt+1}/{max_retries})")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"Max retries exceeded. Last error: {str(e)}")
                        raise
                        
            # This should never be reached due to the raise in the except block
            return func(*args, **kwargs)
            
        return wrapper
        
    return decorator


def extract_metadata(
    soup: BeautifulSoup, 
    title_selectors: Optional[List[Dict[str, Any]]] = None,
    date_selectors: Optional[List[Dict[str, Any]]] = None,
    author_selectors: Optional[List[Dict[str, Any]]] = None,
    content_selectors: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Extract metadata from HTML using various selectors.
    
    This function attempts to extract metadata like title, date, author, and content
    from HTML using a list of selectors. It tries each selector in order until one succeeds.
    
    Args:
        soup: BeautifulSoup object
        title_selectors: List of selectors for title extraction
        date_selectors: List of selectors for date extraction
        author_selectors: List of selectors for author extraction
        content_selectors: List of selectors for content extraction
        
    Returns:
        Dictionary with extracted metadata
    """
    metadata = {}
    
    # Default selectors for title
    if title_selectors is None:
        title_selectors = [
            {'tag': 'meta', 'attrs': {'property': 'og:title'}, 'attr': 'content'},
            {'tag': 'meta', 'attrs': {'name': 'title'}, 'attr': 'content'},
            {'tag': 'h1', 'attrs': {}, 'text': True}
        ]
    
    # Default selectors for date
    if date_selectors is None:
        date_selectors = [
            {'tag': 'meta', 'attrs': {'property': 'article:published_time'}, 'attr': 'content'},
            {'tag': 'meta', 'attrs': {'name': 'publication_date'}, 'attr': 'content'},
            {'tag': 'time', 'attrs': {}, 'text': True}
        ]
    
    # Default selectors for author
    if author_selectors is None:
        author_selectors = [
            {'tag': 'meta', 'attrs': {'property': 'article:author'}, 'attr': 'content'},
            {'tag': 'meta', 'attrs': {'name': 'author'}, 'attr': 'content'},
            {'tag': 'a', 'attrs': {'class': re.compile(r'author', re.I)}, 'text': True}
        ]
    
    # Default selectors for content
    if content_selectors is None:
        content_selectors = [
            {'tag': 'article', 'attrs': {}, 'text': True},
            {'tag': 'div', 'attrs': {'class': re.compile(r'article|content|story', re.I)}, 'text': True},
            {'tag': 'div', 'attrs': {'id': re.compile(r'article|content|story', re.I)}, 'text': True}
        ]
    
    # Extract title
    for selector in title_selectors:
        elem = soup.find(selector['tag'], selector.get('attrs', {}))
        if elem:
            if selector.get('text', False):
                metadata['title'] = elem.get_text(strip=True)
            else:
                metadata['title'] = elem.get(selector.get('attr', ''), '')
            break
    
    # Extract date
    for selector in date_selectors:
        elem = soup.find(selector['tag'], selector.get('attrs', {}))
        if elem:
            if selector.get('text', False):
                metadata['date'] = elem.get_text(strip=True)
            else:
                metadata['date'] = elem.get(selector.get('attr', ''), '')
            break
    
    # Extract author
    for selector in author_selectors:
        elem = soup.find(selector['tag'], selector.get('attrs', {}))
        if elem:
            if selector.get('text', False):
                metadata['author'] = elem.get_text(strip=True)
            else:
                metadata['author'] = elem.get(selector.get('attr', ''), '')
            break
    
    # Extract content
    for selector in content_selectors:
        elem = soup.find(selector['tag'], selector.get('attrs', {}))
        if elem:
            # Remove script and style elements
            for script in elem(['script', 'style']):
                script.decompose()
            
            metadata['content'] = elem.get_text(separator=' ', strip=True)
            break
    
    return metadata
