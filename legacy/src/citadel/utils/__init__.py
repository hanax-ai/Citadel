"""Utility modules for the Citadel project."""

from citadel.utils.crawler_utils import (
    # URL validation
    validate_url,
    
    # HTML parsing
    get_soup,
    extract_links,
    extract_metadata,
    
    # Rate limiting
    RateLimiter,
    
    # HTTP session management
    build_session,
    safe_request,
    
    # Error handling
    CrawlerError,
    URLValidationError,
    HTTPError,
    RateLimitError,
    ParsingError,
    is_success_status,
    handle_http_error,
    retry_on_error,
)

__all__ = [
    'validate_url',
    'get_soup',
    'extract_links',
    'extract_metadata',
    'RateLimiter',
    'build_session',
    'safe_request',
    'CrawlerError',
    'URLValidationError',
    'HTTPError',
    'RateLimitError',
    'ParsingError',
    'is_success_status',
    'handle_http_error',
    'retry_on_error',
]
