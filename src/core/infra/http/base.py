import random


class HttpClientBase:
    """Base class for HTTP clients with common functionality"""

    def __init__(
        self,
        base_url: str = "",
        timeout: float = 10.0,
        max_retries: int = 3,
        backoff_factor: float = 0.3,
        status_forcelist: list[int] = None,
        **kwargs,
    ):
        self.base_url = base_url.removesuffix("/").removeprefix("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.status_forcelist = status_forcelist or [408, 429, 500, 502, 503, 504]
        self.kwargs = kwargs

    def _should_retry(self, status_code: int, attempt: int) -> bool:
        """Determine if a request should be retried"""
        return attempt < self.max_retries and status_code in self.status_forcelist

    def _get_backoff_time(self, attempt: int) -> float:
        """Calculate backoff time using exponential backoff with jitter"""
        backoff = self.backoff_factor * (2 ** (attempt - 1))
        jitter = random.uniform(0, 0.1 * backoff)
        return backoff + jitter
