"""
XM API Client Module

This module provides high-level clients for interacting with the Colombian XM
electricity market API.
"""

from datetime import date
from typing import Optional, List
import pandas as pd

from colombian_grid.core.infra.http.httpx.async_client import AsyncHttpClient
from colombian_grid.core.base.interfaces.xm.fetchers import (
    AsyncXMFetcher,
    SyncXMFetcher,
)


class AsyncXMClient:
    """
    Asynchronous client for XM API data access.

    This client provides a high-level interface to fetch electricity market data
    from the Colombian XM API with automatic data chunking and retry logic.

    Example:
        >>> async with AsyncXMClient() as client:
        ...     # Get available metrics
        ...     metrics = await client.get_available_metrics()
        ...
        ...     # Fetch generation data
        ...     data = await client.get_data(
        ...         metric="Gene",
        ...         entity="Sistema",
        ...         start_date=date(2024, 1, 1),
        ...         end_date=date(2024, 12, 31)
        ...     )
    """

    def __init__(self, timeout: float = 30.0, max_retries: int = 3):
        """
        Initialize the async XM client.

        Args:
            timeout: Request timeout in seconds (default: 30.0)
            max_retries: Maximum number of retries for failed requests (default: 3)
        """
        self._http_client = AsyncHttpClient(timeout=timeout, max_retries=max_retries)
        self._fetcher = AsyncXMFetcher(self._http_client)

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._http_client.close()

    async def get_available_metrics(self) -> pd.DataFrame:
        """
        Fetch all available metrics from XM API.

        This method retrieves a complete list of available metrics including:
        - Metric IDs and names
        - Entity types (Sistema, Recurso, Agente, etc.)
        - Data granularity (hourly, daily, monthly)
        - Filter options
        - Maximum days allowed per request

        Returns:
            DataFrame with columns: MetricId, MetricName, Entity, MaxDays,
            Type, Url, Filter, MetricUnits, MetricDescription

        Example:
            >>> async with AsyncXMClient() as client:
            ...     metrics = await client.get_available_metrics()
            ...     # Find generation metrics
            ...     gen_metrics = metrics[metrics['MetricName'].str.contains('Generación')]
        """
        return await self._fetcher.get_available_metrics()

    async def get_data(
        self,
        *,
        metric: str,
        entity: str,
        start_date: date,
        end_date: date,
        filter_by: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """
        Fetch data for a specific metric.

        This method automatically handles:
        - Date range chunking based on API restrictions
        - Parallel async requests for better performance
        - Retry logic for failed requests
        - Data concatenation and cleanup

        Args:
            metric: Metric ID (e.g., "Gene", "DemaReal", "PrecBolsNaci")
            entity: Entity type (e.g., "Sistema", "Recurso", "Agente")
            start_date: Start date for data retrieval
            end_date: End date for data retrieval
            filter_by: Optional list of filter values (e.g., resource codes like ["TBST", "GVIO"])

        Returns:
            DataFrame containing the requested data

        Raises:
            ValueError: If metric/entity combination is invalid
            httpx.HTTPStatusError: If API request fails after retries

        Example:
            >>> async with AsyncXMClient() as client:
            ...     # Fetch system-wide generation
            ...     data = await client.get_data(
            ...         metric="Gene",
            ...         entity="Sistema",
            ...         start_date=date(2024, 1, 1),
            ...         end_date=date(2024, 1, 31)
            ...     )
            ...
            ...     # Fetch generation by resource with filtering
            ...     data = await client.get_data(
            ...         metric="Gene",
            ...         entity="Recurso",
            ...         start_date=date(2024, 1, 1),
            ...         end_date=date(2024, 1, 31),
            ...         filter_by=["TBST", "GVIO"]  # Specific power plants
            ...     )
        """
        return await self._fetcher.get_data(
            metric=metric,
            entity=entity,
            start_date=start_date,
            end_date=end_date,
            filter_by=filter_by,
        )


class SyncXMClient:
    """
    Synchronous client for XM API data access.

    This client provides the same interface as AsyncXMClient but with
    synchronous method calls, making it easier to use in non-async contexts.

    Note: Uses sequential requests internally, which may be slower than
    the async client for large date ranges.

    Example:
        >>> with SyncXMClient() as client:
        ...     # Get available metrics
        ...     metrics = client.get_available_metrics()
        ...
        ...     # Fetch generation data
        ...     data = client.get_data(
        ...         metric="Gene",
        ...         entity="Sistema",
        ...         start_date=date(2024, 1, 1),
        ...         end_date=date(2024, 12, 31)
        ...     )
    """

    def __init__(self, timeout: float = 30.0, max_retries: int = 3):
        """
        Initialize the sync XM client.

        Args:
            timeout: Request timeout in seconds (default: 30.0)
            max_retries: Maximum number of retries for failed requests (default: 3)
        """
        self._http_client = AsyncHttpClient(timeout=timeout, max_retries=max_retries)
        self._fetcher = SyncXMFetcher(self._http_client)

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        # For sync context, we don't need explicit cleanup
        pass

    def get_available_metrics(self) -> pd.DataFrame:
        """
        Fetch all available metrics from XM API (synchronous).

        Returns:
            DataFrame with all available metrics and their metadata

        Example:
            >>> with SyncXMClient() as client:
            ...     metrics = client.get_available_metrics()
            ...     print(metrics[['MetricId', 'MetricName', 'Entity']].head())
        """
        return self._fetcher.get_available_metrics()

    def get_data(
        self,
        *,
        metric: str,
        entity: str,
        start_date: date,
        end_date: date,
        filter_by: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """
        Fetch data for a specific metric (synchronous).

        Args:
            metric: Metric ID
            entity: Entity type
            start_date: Start date for data retrieval
            end_date: End date for data retrieval
            filter_by: Optional list of filter values

        Returns:
            DataFrame containing the requested data

        Example:
            >>> with SyncXMClient() as client:
            ...     data = client.get_data(
            ...         metric="DemaReal",
            ...         entity="Sistema",
            ...         start_date=date(2024, 1, 1),
            ...         end_date=date(2024, 1, 31)
            ...     )
        """
        return self._fetcher.get_data(
            metric=metric,
            entity=entity,
            start_date=start_date,
            end_date=end_date,
            filter_by=filter_by,
        )
