import asyncio
import json
import logging
import time

from typing import Optional, Any

import httpx

from colombian_grid.core.infra.http.base import HttpClientBase

logger = logging.getLogger("AsyncHTTPClient")
# Cache entry structure: (response, expiration_timestamp)
CacheEntry = tuple[httpx.Response, float]


class AsyncHttpClient(HttpClientBase):
    """
    Async HTTP client implementation using httpx.
    This class provides asynchronous HTTP request methods (GET, POST, PATCH, DELETE)
    with built-in retry logic for handling transient errors. It extends HttpClientBase
    and utilizes httpx.AsyncClient for making asynchronous requests.
    Attributes:
        client (httpx.AsyncClient): The underlying httpx asynchronous client.
    Methods:
        close(): Closes the underlying httpx client.
        __aenter__(): Allows the class to be used as an async context manager.
        __aexit__(exc_type, exc_val, exc_tb): Closes the client when exiting the async context manager.
        _request_with_retry(method: str, url: str, **kwargs) -> httpx.Response:
            Makes an HTTP request with retry logic.
        get(url: str, **kwargs) -> httpx.Response: Performs an async GET request.
        post(url: str, **kwargs) -> httpx.Response: Performs an async POST request.
        patch(url: str, **kwargs) -> httpx.Response: Performs an async PATCH request.
        delete(url: str, **kwargs) -> httpx.Response: Performs an async DELETE request.
    """

    def __init__(self, cache_ttl: Optional[float] = None, **kwargs):
        super().__init__(**kwargs)
        self.client = httpx.AsyncClient(
            base_url=self.base_url, timeout=self.timeout, **self.kwargs
        )
        self._cache: dict[tuple, CacheEntry] = {}
        self._cache_ttl = cache_ttl  # Client-level default TTL
        # Note: The 'clear cache every ttl seconds' is implemented here as
        # 'expire entries after ttl seconds from caching time'. A literal
        # "clear the entire dict" on a timer would require a separate asyncio task.

    async def close(self):
        """Close the underlying HTTPX client."""

        await self.client.aclose()

    async def __aenter__(self):
        """
        Async enter method for the context manager.
        Returns:
            AsyncClient: The AsyncClient instance.
        """

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Asynchronous exit method for the context manager.
        This method is called when the 'async with' block is exited.
        It ensures that the HTTPX client is properly closed, releasing
        any resources it holds.
        Args:
            exc_type: The type of the exception that caused the context to be exited.
                        If the context was exited normally, this is None.
            exc_val: The exception instance that caused the context to be exited.
                        If the context was exited normally, this is None.
            exc_tb: A traceback object describing where the exception occurred.
                    If the context was exited normally, this is None.
        """

        await self.close()
        self._cache = {}

    def _generate_cache_key(self, method: str, url: str, **kwargs) -> tuple:
        """Generates a unique, hashable key for caching a request."""
        # Normalize method to uppercase
        method = method.upper()

        # Combine base_url and request url
        # httpx client handles base_url internally, but let's include it for a robust key
        full_url = (
            f"{self.client.base_url}/{url.lstrip('/')}" if self.client.base_url else url
        )

        # Sort query parameters for consistent key generation
        params = kwargs.get("params")
        sorted_params = (
            tuple(sorted((k, v) for k, v in params.items())) if params else ()
        )

        # Sort data/json body parameters for consistent key generation
        # Need to handle data (form-encoded) and json bodies
        data = kwargs.get("data")
        json_data = kwargs.get("json")

        body_key_part: Any = None
        if data:
            # Assuming data is dict-like or list of tuples
            try:
                # Attempt to sort if it's a dictionary
                sorted_data = tuple(sorted((k, v) for k, v in data.items()))
                body_key_part = ("data", sorted_data)
            except AttributeError:
                # If not a dict, use as is (must be hashable like tuple)
                body_key_part = ("data", data)
        elif json_data is not None:
            # Use json.dumps with sort_keys for consistent JSON representation
            try:
                body_key_part = ("json", json.dumps(json_data, sort_keys=True))
            except TypeError:
                # Handle non-serializable JSON data if necessary, maybe exclude from key
                body_key_part = (
                    "json",
                    "non_serializable",
                )  # Or raise error, or skip caching

        return method, full_url, sorted_params, body_key_part

    async def _request_with_retry(
        self, method: str, url: str, **kwargs
    ) -> httpx.Response:
        """
        Makes an HTTP request with retry logic.
        Args:
            method (str): The HTTP method (e.g., "GET", "POST").
            url (str): The URL to request.
            **kwargs: Additional keyword arguments to pass to the httpx.request method.
        Returns:
            httpx.Response: The HTTP response object.
        Raises:
            httpx.TimeoutException: If a timeout occurs and the maximum number of retries has been reached.
            httpx.NetworkError: If a network error occurs and the maximum number of retries has been reached.
        """
        attempt = 0

        while True:
            attempt += 1
            try:
                response = await self.client.request(method, url, **kwargs)

                if not self._should_retry(response.status_code, attempt):
                    return response

            except (httpx.TimeoutException, httpx.NetworkError):
                if attempt >= self.max_retries:
                    raise

            backoff_time = self._get_backoff_time(attempt)
            await asyncio.sleep(backoff_time)

    async def _send_request_with_cache(
        self, method: str, url: str, use_cache: bool = False, **kwargs
    ) -> httpx.Response:
        """
        Handles cache lookup and storage before and after making a request.
        """
        cache_key = None
        cached_response: Optional[httpx.Response] = None

        # --- Cache Lookup ---
        # Only attempt cache lookup if caching is enabled for this request and the client has a TTL set
        if use_cache and self._cache_ttl is not None:
            try:
                cache_key = self._generate_cache_key(method, url, **kwargs)
                if cache_entry := self._cache.get(cache_key):
                    cached_response, expiration_timestamp = cache_entry
                    # Check if the cached entry is still valid (not expired)
                    if time.time() < expiration_timestamp:
                        logger.debug(f"Cache hit for {method} {url}")
                        # Return the cached response immediately
                        return cached_response
                    else:
                        logger.debug(
                            f"Cache entry expired for {method} {url}"
                        )  # Optional: logging
                        # Cache entry is expired, remove it to clean up
                        del self._cache[cache_key]
                else:
                    logger.debug(f"Cache miss for {method} {url}")  # Optional: logging

            except Exception as e:
                # Handle potential errors during cache key generation or lookup gracefully
                logger.error(f"Error during cache lookup for {method} {url}: {e}")
                cache_key = None  # Invalidate key if generation failed
                # Continue to make the actual request

        # --- Make the Actual Request (if cache miss or caching disabled) ---
        try:
            response = await self._request_with_retry(method, url, **kwargs)

            # --- Cache Storage ---
            # Store response in cache if caching is enabled, key was generated successfully,
            # and the response status is generally cacheable (e.g., 2xx)
            # Typically only GET requests are cached, but you can adjust this logic.
            if use_cache and self._cache_ttl is not None and cache_key is not None:
                # Only cache successful responses (status codes 200-299)
                response.raise_for_status()  # Raises an error for non-2xx responses
                expiration_timestamp = time.time() + self._cache_ttl
                self._cache[cache_key] = (response, expiration_timestamp)
                logger.debug(
                    f"Cached response for {method} {url} with TTL {self._cache_ttl}s"
                )  # Optional: logging

            return response

        except Exception as e:
            # If an error occurred during the request (after exhausting retries),
            # do NOT cache the error response. Re-raise the exception.
            logger.error(f"Request failed after retries for {method} {url}: {e}")
            raise  # Re-raise the exception from _request_with_retry

    async def get(self, url: str, **kwargs) -> httpx.Response:
        """Perform an async GET request"""
        return await self._request_with_retry("GET", url, **kwargs)

    async def post(self, url: str, **kwargs) -> httpx.Response:
        """Perform an async POST request"""
        return await self._request_with_retry("POST", url, **kwargs)

    async def patch(self, url: str, **kwargs) -> httpx.Response:
        """Perform an async PATCH request"""
        return await self._request_with_retry("PATCH", url, **kwargs)

    async def delete(self, url: str, **kwargs) -> httpx.Response:
        """Perform an async DELETE request"""
        return await self._request_with_retry("DELETE", url, **kwargs)
