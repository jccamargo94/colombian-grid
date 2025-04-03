from typing import Optional

from httpx import Response
from pydantic import BaseModel, AnyHttpUrl

from colombian_grid.core.base.interfaces.base import APIDataSource
from colombian_grid.core.infra.http.httpx.async_client import AsyncHttpClient
from colombian_grid.core.base.interfaces.paratec.utils import (
    TRANSMISSION_LINE_URL,
    SUBSTATION_URL,
)


class TransmissionFetcher(APIDataSource):
    """This class is responsible for fetching transmission-related data from external APIs.
    It uses an asynchronous HTTP client to make requests to predefined URLs for
    transmission lines and substations. The class provides methods to retrieve and
    process data from these endpoints, with optional schema validation using
    pydantic models.

    Attributes:
        _http_client (AsyncHttpClient): An asynchronous HTTP client for making requests.
        _transmission_line_url (AnyHttpUrl | str): The URL for fetching transmission line data.
        _substation_url (AnyHttpUrl | str): The URL for fetching substation data.

    Methods:
        __init__(self, http_client: AsyncHttpClient, transmission_line_url: AnyHttpUrl | str = TRANSMISSION_LINE_URL, substation_url: AnyHttpUrl | str = SUBSTATION_URL) -> None:
            Initializes the TransmissionFetcher with an HTTP client and URLs for transmission lines and substations.

        get_data(self, *, output_schema: Optional[BaseModel] = None) -> list:
            Fetches data from a specified URL and optionally validates it against a pydantic schema.

        get_transmission_line_data(self, *, output_schema: Optional[BaseModel] = None) -> list:
        get_substation_data(self, *, output_schema: Optional[BaseModel] = None) -> list:
    """

    def __init__(
        self,
        http_client: AsyncHttpClient,
        transmission_line_url: AnyHttpUrl | str = TRANSMISSION_LINE_URL,
        substation_url: AnyHttpUrl | str = SUBSTATION_URL,
    ) -> None:
        self._http_client = http_client
        self._transmission_line_url = transmission_line_url
        self._substation_url = substation_url

    async def get_data(
        self, *, url: str, output_schema: Optional[BaseModel] = None
    ) -> list:
        """Fetches data from a specified URL and optionally validates it against a pydantic schema.

        Retrieves data from the given URL using the asynchronous HTTP client.
        If an output schema is provided, the fetched data is validated against the schema.

        Args:
            url (AnyHttpUrl | str): The URL to fetch data from.
            output_schema (BaseModel, optional): The pydantic schema to validate the data against. Defaults to None.

        Returns:
            list: The fetched data, either as a list or a validated pydantic model.
        """
        response: Response = await self._http_client.get(url)
        response.raise_for_status()
        return (
            output_schema.model_validate(response.json())
            if output_schema
            else response.json()
        )

    async def get_transmission_line_data(
        self, *, output_schema: Optional[BaseModel] = None
    ) -> list:
        """
        Retrieves transmission data from the specified URL.

        Args:
            output_schema (Optional[BaseModel]): An optional Pydantic model to
            parse the data into. If None, the raw JSON data is returned.

        Returns:
            list: A list of transmission data, either as raw JSON or parsed
            into the specified Pydantic model.
        """
        return await self.get_data(
            url=self._transmission_line_url, output_schema=output_schema
        )

    async def get_substation_data(
        self, *, output_schema: Optional[BaseModel] = None
    ) -> list:
        """
        Asynchronously retrieves substation data from the specified URL.

        Args:
            output_schema (Optional[BaseModel], optional): A pydantic model to parse each
            element of the response. Defaults to None.

        Returns:
            list: A list of substation data, parsed according to the output_schema if provided.
        """
        return await self.get_data(
            url=self._substation_url, output_schema=output_schema
        )
