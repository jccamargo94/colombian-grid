from typing import Optional

from httpx import Response
from pydantic import BaseModel, AnyHttpUrl

from colombian_grid.core.base.interfaces.base import APIDataSource
from colombian_grid.core.infra.http.httpx.async_client import AsyncHttpClient
from colombian_grid.core.base.interfaces.paratec.utils import HYDROLOGY_URL


class HydroFetcher(APIDataSource):
    """
    HydroFetcher is a class that fetches hydrological data from a specified URL using an asynchronous HTTP client.
    It inherits from APIDataSource and provides methods to retrieve and process the data.
    Attributes:
        _http_client (AsyncHttpClient): An asynchronous HTTP client used to make requests.
        _url (AnyHttpUrl | str): The URL from which to fetch the hydrological data. Defaults to HYDROLOGY_URL.
    Methods:
        __init__(http_client: AsyncHttpClient, url: AnyHttpUrl | str = HYDROLOGY_URL) -> None:
            Initializes a new instance of the HydroFetcher class.
        get_data(*, output_schema: Optional[BaseModel] = None) -> list:
            Fetches data from the specified URL and returns it as a list.
            If an output schema is provided, the data is validated against the schema before being returned.
        get_hydro_data(*, output_schema: Optional[BaseModel] = None) -> list:
            A convenience method that calls get_data to retrieve hydrological data.
            If an output schema is provided, the data is validated against the schema before being returned.
    """

    def __init__(
        self, http_client: AsyncHttpClient, url: AnyHttpUrl | str = HYDROLOGY_URL
    ) -> None:
        self._http_client = http_client
        self._url = url

    async def get_data(self, *, output_schema: Optional[BaseModel] = None) -> list:
        """Asynchronously retrieves data from the specified URL.
        Args:
            output_schema (Optional[BaseModel], optional): A pydantic model to validate the data against.
                Defaults to None. If provided, the returned data will be validated
                against this schema.
        Returns:
            list: A list of data, either as a raw JSON object or validated
                against the provided output schema.
        Raises:
            HTTPError: If the HTTP request returns an error status code.
        """

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
        """Asynchronously retrieves hydrological data.
        Args:
            output_schema (Optional[BaseModel], optional): An optional Pydantic model
            to which the data will be parsed. Defaults to None.
        Returns:
            list: A list of hydrological data, parsed according to the output_schema
            if provided, otherwise returned as is from the API.
        """
        return await self.get_data(output_schema=output_schema)
