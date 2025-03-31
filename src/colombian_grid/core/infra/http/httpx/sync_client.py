import time

import httpx

from colombian_grid.core.infra.http.base import HttpClientBase


class SyncHttpClient(HttpClientBase):
    """Synchronous HTTP client with retry and timeout capabilities"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client = httpx.Client(
            base_url=self.base_url, timeout=self.timeout, **self.kwargs
        )

    def close(self):
        """Close the underlying client"""
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _request_with_retry(self, method: str, url: str, **kwargs) -> httpx.Response:
        """Make a request with retry logic"""
        attempt = 0

        while True:
            attempt += 1
            try:
                response = self.client.request(method, url, **kwargs)

                if not self._should_retry(response.status_code, attempt):
                    return response

            except (httpx.TimeoutException, httpx.NetworkError):
                if attempt >= self.max_retries:
                    raise

            backoff_time = self._get_backoff_time(attempt)
            time.sleep(backoff_time)

    def get(self, url: str, **kwargs) -> httpx.Response:
        """Perform a GET request"""
        return self._request_with_retry("GET", url, **kwargs)

    def post(self, url: str, **kwargs) -> httpx.Response:
        """Perform a POST request"""
        return self._request_with_retry("POST", url, **kwargs)

    def patch(self, url: str, **kwargs) -> httpx.Response:
        """Perform a PATCH request"""
        return self._request_with_retry("PATCH", url, **kwargs)

    def delete(self, url: str, **kwargs) -> httpx.Response:
        """Perform a DELETE request"""
        return self._request_with_retry("DELETE", url, **kwargs)
