from colombian_grid.core.base.interfaces.paratec.generators import GeneratorFetcher
from colombian_grid.core.base.interfaces.paratec.transmission import TransmissionFetcher
from colombian_grid.core.base.interfaces.paratec.hydrology import HydroFetcher
from colombian_grid.core.infra.http.httpx import AsyncHttpClient


class AsyncParatecClient:
    """
    AsyncParatecClient is an asynchronous client for fetching data from the Paratec API.
    It provides methods to retrieve generation, substation, and transmission line data.

    Attributes:
        _http_client (AsyncHttpClient): An asynchronous HTTP client for making requests.
        _generator_fetcher (GeneratorFetcher): A fetcher for retrieving generation data.
        _transmission_fetcher (TransmissionFetcher): A fetcher for retrieving transmission data.
        _hydro_fetcher (HydroFetcher): A fetcher for retrieving hydrology data.

    Methods:
        get_generation_data(): Asynchronously retrieves generation data.
        get_substation_data(): Asynchronously retrieves substation data.
        get_transmission_line_data(): Asynchronously retrieves transmission line data.
        get_hydro_data(): Asynchronously retrieves hydrology data.
    """

    def __init__(self):
        self._http_client = AsyncHttpClient()
        self._generator_fetcher = GeneratorFetcher(self._http_client)
        self._transmission_fetcher = TransmissionFetcher(self._http_client)
        self._hydro_fetcher = HydroFetcher(self._http_client)

    async def get_generation_data(self) -> list:
        """
        Asynchronously retrieves generation data using the injected generator fetcher.

        Returns:
            list: A list of generator data dictionaries.
        """
        return await self._generator_fetcher.get_data()

    async def get_substation_data(self) -> list:
        """
        Asynchronously retrieves substation data using the transmission fetcher.

        Returns:
            list: A list of substation data dictionaries.
        """
        return await self._transmission_fetcher.get_substation_data()

    async def get_transmission_line_data(self) -> list:
        """
        Retrieves transmission line data.

        Returns:
            list: A list of transmission line data dictionaries.
        """
        return await self._transmission_fetcher.get_transmission_line_data()

    async def get_hydro_data(self) -> list:
        """
        Asynchronously retrieves hydro data using the injected hydro fetcher.

        Returns:
            list: A list of hydrology data dictionaries.
        """
        return await self._hydro_fetcher.get_hydro_data()
