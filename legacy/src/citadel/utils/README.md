# Citadel Crawler Utilities

This module provides common utility functions for web crawlers to avoid code duplication across different crawler implementations. It includes functionality for URL validation, HTML parsing, rate limiting, error handling, and HTTP session management.

## Features

### URL Validation

- `validate_url()`: Validates if a URL is valid and belongs to allowed domains, with support for patterns and exclusions.

### HTML Parsing

- `get_soup()`: Parses HTML content using BeautifulSoup.
- `extract_links()`: Extracts all links from a BeautifulSoup object.
- `extract_metadata()`: Extracts metadata like title, date, author, and content from HTML.

### Rate Limiting

- `RateLimiter`: Class for controlling request frequency with both synchronous and asynchronous support.

### HTTP Session Management

- `build_session()`: Creates and configures a requests session with retry capabilities.
- `safe_request()`: Makes a safe HTTP request with error handling and retries.

### Error Handling

- `CrawlerError` hierarchy: Base exception class with specialized subclasses.
- `is_success_status()`: Checks if an HTTP status code indicates success.
- `handle_http_error()`: Handles HTTP errors and returns appropriate error messages.
- `retry_on_error()`: Decorator to retry a function on error.

## Usage Examples

### Basic URL Validation

```python
from citadel.utils.crawler_utils import validate_url

is_valid = validate_url(
    "https://example.com/article/123",
    base_url="https://example.com",
    url_patterns=["/article/", "/blog/"],
    excluded_patterns=["/admin/", "/login/"]
)
```

### HTML Parsing

```python
from citadel.utils.crawler_utils import get_soup, extract_links, extract_metadata

# Parse HTML
soup = get_soup(html_content)

# Extract links
links = extract_links(soup, "https://example.com")

# Extract metadata
metadata = extract_metadata(soup)
```

### Rate Limiting

```python
from citadel.utils.crawler_utils import RateLimiter

# Create a rate limiter with 1 second interval
rate_limiter = RateLimiter(min_interval=1.0)

# Use as a decorator
@rate_limiter
def fetch_url(url):
    # ...

# Use directly
def process_urls(urls):
    for url in urls:
        rate_limiter.wait()
        # Process url...
```

### HTTP Session Management

```python
from citadel.utils.crawler_utils import build_session, safe_request

# Create a session with retry capabilities
session = build_session(
    user_agent="MyCrawler/1.0",
    retries=3,
    backoff_factor=0.3
)

# Make a safe request
response = safe_request(
    url="https://example.com/page",
    session=session,
    timeout=30,
    max_retries=3
)
```

### Error Handling

```python
from citadel.utils.crawler_utils import retry_on_error, HTTPError

# Retry a function on error
@retry_on_error(max_retries=3, backoff_factor=0.3)
def fetch_data(url):
    # ...

# Handle HTTP errors
try:
    response = safe_request(url, session)
except HTTPError as e:
    print(f"HTTP error {e.status_code}: {e.message}")
```

## Error Hierarchy

- `CrawlerError`: Base exception class
  - `URLValidationError`: URL validation errors
  - `HTTPError`: HTTP request errors
  - `RateLimitError`: Rate limit exceeded errors
  - `ParsingError`: HTML parsing errors
