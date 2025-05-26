"""
Base Crawler Abstract Class for Project Citadel.

This module defines the abstract base class that all crawler implementations must extend.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
import asyncio
from dataclasses import dataclass
from citadel.utils.crawler_utils import validate_url


@dataclass
class CrawlResult:
    """Data class representing the result of a crawl operation."""
    url: str
    content: str
    metadata: Dict[str, Any]
    status_code: int
    success: bool
    error: Optional[Exception] = None


class BaseCrawler(ABC):
    """
    Abstract base class for all crawler implementations in Project Citadel.
    
    All crawler types must extend this class and implement its abstract methods.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the base crawler with configuration.
        
        Args:
            config: Dictionary containing crawler configuration parameters
        """
        self.config = config
        self.user_agent = config.get('user_agent', 'Project Citadel Crawler/1.0')
        self.timeout = config.get('timeout', 30)
        self.max_retries = config.get('max_retries', 3)
        self.retry_delay = config.get('retry_delay', 2)
        self.headers = {
            'User-Agent': self.user_agent,
            **config.get('headers', {})
        }
    
    @abstractmethod
    async def crawl(self, url: str, **kwargs) -> Union[CrawlResult, List[CrawlResult]]:
        """
        Crawl the specified URL and return the result.
        
        Args:
            url: The URL to crawl
            **kwargs: Additional crawler-specific parameters
            
        Returns:
            CrawlResult or List[CrawlResult] containing the crawled data
        """
        pass
    
    @abstractmethod
    async def extract_data(self, html: str, url: str) -> Dict[str, Any]:
        """
        Extract structured data from the HTML content.
        
        Args:
            html: The HTML content to parse
            url: The URL the content was fetched from
            
        Returns:
            Dictionary containing extracted data with standardized error handling.
            The dictionary should include:
            - success: Boolean indicating if extraction was successful
            - partial_success: Boolean indicating if some data was extracted despite errors
            - errors: List of error objects with type and message fields
            - Other extracted data fields
        """
        pass
    
    @abstractmethod
    async def handle_rate_limits(self) -> None:
        """
        Implement rate limiting strategy to avoid overloading target servers.
        
        This method should manage delays between requests based on the crawler's
        configuration and target site requirements.
        """
        pass
    
    def validate_url(self, url: str) -> bool:
        """Use the utility function to validate URLs."""
        # Call the imported validate_url function with appropriate parameters
        return validate_url(
            url=url,
            base_url=self.base_url,
            allowed_domains=getattr(self, 'allowed_domains', None),
            allowed_schemes=getattr(self, 'allowed_schemes', None),
            url_patterns=getattr(self, 'url_patterns', None),
            excluded_patterns=getattr(self, 'excluded_patterns', None)
        )
