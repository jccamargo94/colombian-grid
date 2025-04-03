import asyncio
import httpx

from colombian_grid.core.infra.http.base import HttpClientBase


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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = httpx.AsyncClient(
            base_url=self.base_url, timeout=self.timeout, **self.kwargs
        )

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
