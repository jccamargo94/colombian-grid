import asyncio
import httpx

from colombian_grid.core.infra.http.base import HttpClientBase


class AsyncHttpClient(HttpClientBase):
    """Asynchronous HTTP client with retry and timeout capabilities"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = httpx.AsyncClient(
            base_url=self.base_url, timeout=self.timeout, **self.kwargs
        )

    async def close(self):
        """Close the underlying client"""
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def _request_with_retry(
        self, method: str, url: str, **kwargs
    ) -> httpx.Response:
        """Make a request with retry logic"""
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
