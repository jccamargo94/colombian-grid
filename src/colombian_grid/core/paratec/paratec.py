from colombian_grid.core.base.interfaces.paratec.generators import GeneratorFetcher
from colombian_grid.core.infra.http.httpx import AsyncHttpClient, SyncHttpClient


class AsyncParatecClient:
    def __init__(self):
        self._http_client = AsyncHttpClient()
        self._generator_fetcher = GeneratorFetcher(self._http_client)

    async def get_generation_data(self):
        return await self._generator_fetcher.get_data()


class SyncParatecClient:
    def __init__(self):
        self._http_client = SyncHttpClient()
        self._generator_fetcher = GeneratorFetcher(self._http_client)

    def get_generation_data(self):
        return self._generator_fetcher.get_data()
