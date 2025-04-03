from typing import Optional

from httpx import Response
from pydantic import BaseModel, AnyHttpUrl

from colombian_grid.core.base.interfaces.base import APIDataSource
from colombian_grid.core.infra.http.httpx.async_client import AsyncHttpClient
from colombian_grid.core.base.interfaces.paratec.utils import HYDROLOGY_URL


class HydroFetcher(APIDataSource):
    def __init__(
        self, http_client: AsyncHttpClient, url: AnyHttpUrl | str = HYDROLOGY_URL
    ) -> None:
        self._http_client = http_client
        self._url = url

    async def get_data(self, *, output_schema: Optional[BaseModel] = None) -> list:
        response: Response = await self._http_client.get(self._url)
        response.raise_for_status()
        return (
            output_schema.model_validate(response.json())
            if output_schema
            else response.json()
        )

    async def get_hydro_data(
        self, *, output_schema: Optional[BaseModel] = None
    ) -> list:
        return await self.get_data(output_schema=output_schema)
