from abc import ABC

from colombian_grid.core.infra.http.httpx import AsyncHttpClient


class AsyncSourceClient(ABC):
    """Shared HTTP lifecycle contract for async data-source clients."""

    def __init__(self, timeout: float = 10.0, max_retries: int = 3, **kwargs):
        self._http_client = AsyncHttpClient(
            timeout=timeout, max_retries=max_retries, **kwargs
        )

    async def close(self) -> None:
        await self._http_client.close()

    async def __aenter__(self) -> "AsyncSourceClient":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()
