from typing import Optional

from httpx import Response
from pydantic import BaseModel, AnyHttpUrl

from colombian_grid.core.base.interfaces.base import APIDataSource
from colombian_grid.core.infra.http.httpx.async_client import AsyncHttpClient
from colombian_grid.core.base.interfaces.paratec.utils import GENERATOR_DATA_URL


class GeneratorFetcher(APIDataSource):
    """
    A data source class for retrieving generator data from multiple API endpoints.
    This class extends APIDataSource and is designed to fetch and combine data
    from a list of predefined API endpoints. It uses an HTTP client to make
    asynchronous requests to these endpoints and aggregates the JSON responses
    into a single list.
    """

    def __init__(
        self, http_client: AsyncHttpClient, url: AnyHttpUrl | str = GENERATOR_DATA_URL
    ) -> None:
        self._http_client = http_client
        self._url = url

    async def get_data(self, *, output_schema: Optional[BaseModel] = None) -> list:
        """
        Retrieves data from multiple endpoints.
        Args:
            url (AnyHttpUrl | str): The URL to fetch data from. This argument is not used,
            as the method iterates over the `endpoints` attribute.
        Returns:
            list: A list containing the combined JSON responses from all endpoints.
        Raises:
            httpx.HTTPStatusError: If any of the HTTP requests return an error status code.
        """
        response: Response = await self._http_client.get(self._url)
        response.raise_for_status()
        return (
            output_schema.model_validate(response.json())
            if output_schema
            else response.json()
        )

    async def fetch_generator_data(
        self, *, output_schema: Optional[BaseModel] = None
    ) -> list:
        """
        Retrieves data from multiple endpoints.
        Args:
            url (AnyHttpUrl | str): The URL to fetch data from. This argument is not used,
            as the method iterates over the `endpoints` attribute.
        Returns:
            list: A list containing the combined JSON responses from all endpoints.
        Raises:
            httpx.HTTPStatusError: If any of the HTTP requests return an error status code.
        """
        return await self.get_data(output_schema=output_schema)
