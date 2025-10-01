"""
XM API Data Fetchers

This module provides both synchronous and asynchronous implementations
for fetching data from the Colombian XM electricity market API.
"""

import asyncio
import inspect
import logging
from abc import ABC, abstractmethod
from datetime import date, timedelta

import pandas as pd
from httpx import Response
from pydantic import BaseModel

from colombian_grid.core.base.interfaces.base import APIDataSource
from colombian_grid.core.infra.http.httpx.async_client import AsyncHttpClient
from colombian_grid.core.base.interfaces.xm.utils import (
    XM_LISTS_URL,
    XM_HOURLY_URL,
    XM_DAILY_URL,
    XM_MONTHLY_URL,
    MAX_DAYS_RESTRICTIONS,
    MAX_CHUNK_YEARS,
)
from colombian_grid.core.schemas.xm import (
    XMMetricEntity,
)

logger = logging.getLogger(__name__)


def _generate_date_chunks(
    start_date: date, end_date: date, max_days: int
) -> list[tuple[date, date]]:
    """
    Generate date range chunks respecting API limits.

    Args:
        start_date: Start date
        end_date: End date
        max_days: Maximum days per chunk

    Returns:
        List of (start_date, end_date) tuples
    """
    chunks = []
    current_start = start_date

    while current_start <= end_date:
        current_end = min(
            current_start + timedelta(days=max_days - 1),
            end_date,
        )
        chunks.append((current_start, current_end))
        current_start = current_end + timedelta(days=1)

    return chunks


def _generate_year_chunks(
    start_date: date, end_date: date, max_years: int = MAX_CHUNK_YEARS
) -> list[tuple[date, date]]:
    """
    Generate date range chunks by years for very long time spans.

    Args:
        start_date: Start date
        end_date: End date
        max_years: Maximum years per chunk

    Returns:
        List of (start_date, end_date) tuples
    """
    chunks = []
    current_start = start_date

    while current_start <= end_date:
        # Calculate end date for this chunk (max_years later)
        try:
            current_end = date(
                current_start.year + max_years, current_start.month, current_start.day
            )
        except ValueError:
            # Handle leap year edge case (Feb 29)
            current_end = date(current_start.year + max_years, current_start.month, 28)

        current_end = min(current_end, end_date)
        chunks.append((current_start, current_end))
        current_start = current_end + timedelta(days=1)

    return chunks


def _determine_data_type(metric_info: XMMetricEntity) -> str:
    """
    Determine data type (hourly, daily, monthly) from metric information.

    Args:
        metric_info: Metric entity information

    Returns:
        Data type string (hourly, daily, monthly, or annual)
    """
    type_mapping = {
        "HourlyEntities": "hourly",
        "DailyEntities": "daily",
        "MonthlyEntities": "monthly",
        "AnnualEntities": "annual",
    }
    return type_mapping.get(metric_info.Type, "daily")


def _get_endpoint_url(data_type: str) -> str:
    """
    Get API endpoint URL for data type.

    Args:
        data_type: Data type (hourly, daily, monthly)

    Returns:
        API endpoint URL
    """
    url_mapping = {
        "hourly": XM_HOURLY_URL,
        "daily": XM_DAILY_URL,
        "monthly": XM_MONTHLY_URL,
        "annual": XM_MONTHLY_URL,  # Annual uses monthly endpoint
    }
    return url_mapping.get(data_type, XM_DAILY_URL)


class BaseXMFetcher(ABC):
    """
    Base data fetcher for XM API with shared functionality.

    This abstract class contains all common logic for fetching data from
    the XM electricity market API, including chunking, data processing,
    and metrics caching.

    Attributes:
        _http_client: HTTP client for making requests
        _metrics_cache: Cached list of available metrics
    """

    def __init__(self, http_client: AsyncHttpClient) -> None:
        """
        Initialize the base XM fetcher.

        Args:
            http_client: HTTP client instance
        """
        self._http_client = http_client
        self._metrics_cache: pd.DataFrame | None = None

    async def _fetch_metrics(self) -> pd.DataFrame:
        """
        Fetch all available metrics from XM API (internal async method).

        Returns:
            DataFrame containing all available metrics with their metadata
        """
        if self._metrics_cache is not None:
            return self._metrics_cache

        request_body = {"MetricId": "ListadoMetricas"}

        response: Response = await self._http_client.post(
            XM_LISTS_URL, json=request_body
        )
        response.raise_for_status()

        # Handle both sync and async json() methods (for mock compatibility)
        if inspect.iscoroutinefunction(response.json):
            data = await response.json()
        else:
            data = response.json()

        # Normalize nested JSON structure
        df = pd.json_normalize(data.get("Items", []), "ListEntities", "Date", sep="_")

        # Clean up column names
        df.columns = [col.replace("Values_", "") for col in df.columns]
        df.drop(columns=["Id"], inplace=True, errors="ignore")

        self._metrics_cache = df
        return df

    def _prepare_chunks(
        self,
        start_date: date,
        end_date: date,
        max_days: int,
    ) -> list[tuple[date, date]]:
        """
        Prepare date chunks based on date range and restrictions.

        Args:
            start_date: Start date
            end_date: End date
            max_days: Maximum days per chunk

        Returns:
            List of (start_date, end_date) tuples
        """
        days_diff = (end_date - start_date).days

        # Determine chunking strategy
        if days_diff > (MAX_CHUNK_YEARS * 365):
            # For very long periods, chunk by years first
            year_chunks = _generate_year_chunks(start_date, end_date)
            all_chunks = []
            for year_start, year_end in year_chunks:
                # Further chunk each year segment by max_days
                day_chunks = _generate_date_chunks(year_start, year_end, max_days)
                all_chunks.extend(day_chunks)
        else:
            # For shorter periods, chunk by days only
            all_chunks = _generate_date_chunks(start_date, end_date, max_days)

        return all_chunks

    async def _fetch_single_chunk(
        self,
        metric: str,
        entity: str,
        start_date: date,
        end_date: date,
        filter_by: list[str] | None,
        data_type: str,
    ) -> pd.DataFrame:
        """
        Fetch data for a single chunk (internal method).

        Args:
            metric: Metric ID
            entity: Entity type
            start_date: Chunk start date
            end_date: Chunk end date
            filter_by: Optional filter list
            data_type: Data type (hourly, daily, monthly)

        Returns:
            DataFrame for this chunk
        """
        endpoint_url = _get_endpoint_url(data_type)

        request_body = {
            "MetricId": metric,
            "StartDate": start_date.strftime("%Y-%m-%d"),
            "EndDate": end_date.strftime("%Y-%m-%d"),
            "Entity": entity,
            "Filter": filter_by or [],
        }

        response: Response = await self._http_client.post(
            endpoint_url, json=request_body
        )
        response.raise_for_status()

        # Handle both sync and async json() methods (for mock compatibility)
        if inspect.iscoroutinefunction(response.json):
            data = await response.json()
        else:
            data = response.json()

        # Determine the correct entity key for normalization
        entity_key_mapping = {
            "HourlyEntities": "HourlyEntities",
            "DailyEntities": "DailyEntities",
            "MonthlyEntities": "MonthlyEntities",
            "AnnualEntities": "AnnualEntities",
        }

        # Get metric info to find entity key
        metrics_df = await self._fetch_metrics()
        metric_info = metrics_df[
            (metrics_df["MetricId"] == metric) & (metrics_df["Entity"] == entity)
        ]
        metric_type = None if metric_info.empty else metric_info.iloc[0]["Type"]

        entity_key = entity_key_mapping.get(metric_type, "DailyEntities")

        # Normalize the nested JSON structure
        df = pd.json_normalize(data.get("Items", []), entity_key, "Date", sep="_")

        # Clean up column names
        df.columns = [col.replace("Values_", "") for col in df.columns]

        # Convert date column if present
        if "Date" in df.columns:
            try:
                df["Date"] = pd.to_datetime(df["Date"])
            except Exception:
                logger.error(
                    f"Failed to convert 'Date' column to datetime in metric {metric} "
                    f"for entity {entity} from {start_date} to {end_date}. "
                    "Keeping original format."
                )
        return df

    async def _validate_and_get_metric_info(
        self,
        metric: str,
        entity: str,
    ) -> tuple[XMMetricEntity, str, int]:
        """
        Validate metric/entity combination and return metadata.

        Args:
            metric: Metric ID
            entity: Entity type

        Returns:
            Tuple of (metric_info, data_type, max_days)

        Raises:
            ValueError: If metric/entity combination is invalid
        """
        metrics_df = await self._fetch_metrics()

        metric_info = metrics_df[
            (metrics_df["MetricId"] == metric) & (metrics_df["Entity"] == entity)
        ]

        if metric_info.empty:
            raise ValueError(
                f"Invalid metric/entity combination: {metric}/{entity}. "
                f"Use get_available_metrics() to see valid options."
            )

        metric_row = XMMetricEntity(**metric_info.iloc[0].to_dict())
        data_type = _determine_data_type(metric_row)
        max_days = MAX_DAYS_RESTRICTIONS.get(data_type, 30)

        return metric_row, data_type, max_days

    @abstractmethod
    async def _execute_fetch_strategy(
        self,
        chunks: list[tuple[date, date]],
        metric: str,
        entity: str,
        filter_by: list[str] | None,
        data_type: str,
    ) -> list[pd.DataFrame]:
        """
        Execute the fetch strategy (parallel or sequential).

        This method must be implemented by subclasses to define
        whether chunks are fetched in parallel (async) or sequentially (sync).

        Args:
            chunks: List of date chunks to fetch
            metric: Metric ID
            entity: Entity type
            filter_by: Optional filter list
            data_type: Data type

        Returns:
            List of DataFrames, one per chunk
        """
        pass

    async def _get_data_internal(
        self,
        *,
        metric: str,
        entity: str,
        start_date: date,
        end_date: date,
        filter_by: list[str] | None = None,
        output_schema: type[BaseModel] | None = None,
    ) -> pd.DataFrame:
        """
        Internal method to fetch data with automatic chunking.

        Args:
            metric: Metric ID to fetch
            entity: Entity type
            start_date: Start date for data
            end_date: End date for data
            filter_by: Optional list of filter values
            output_schema: Optional Pydantic schema for response validation

        Returns:
            DataFrame containing the requested data

        Raises:
            ValueError: If metric/entity combination is invalid
            httpx.HTTPStatusError: If API request fails
        """
        # Validate and get metric metadata
        metric_row, data_type, max_days = await self._validate_and_get_metric_info(
            metric, entity
        )

        # Prepare chunks
        all_chunks = self._prepare_chunks(start_date, end_date, max_days)

        # Execute fetch strategy (parallel or sequential)
        results = await self._execute_fetch_strategy(
            chunks=all_chunks,
            metric=metric,
            entity=entity,
            filter_by=filter_by,
            data_type=data_type,
        )

        return pd.concat(results, ignore_index=True)


class AsyncXMFetcher(BaseXMFetcher, APIDataSource):
    """
    Asynchronous data fetcher for XM API.

    This class handles fetching data from the XM electricity market API
    with automatic chunking for large date ranges and parallel execution
    of chunks for better performance.
    """

    async def get_available_metrics(
        self, *, output_schema: type[BaseModel] | None = None
    ) -> pd.DataFrame:
        """
        Fetch all available metrics from XM API.

        Returns:
            DataFrame containing all available metrics with their metadata
        """
        return await self._fetch_metrics()

    async def _execute_fetch_strategy(
        self,
        chunks: list[tuple[date, date]],
        metric: str,
        entity: str,
        filter_by: list[str] | None,
        data_type: str,
    ) -> list[pd.DataFrame]:
        """
        Execute parallel fetch strategy for async client.

        Fetches all chunks in parallel using asyncio.gather for
        maximum performance.

        Args:
            chunks: List of date chunks to fetch
            metric: Metric ID
            entity: Entity type
            filter_by: Optional filter list
            data_type: Data type

        Returns:
            List of DataFrames, one per chunk
        """
        tasks = [
            self._fetch_single_chunk(
                metric=metric,
                entity=entity,
                start_date=chunk_start,
                end_date=chunk_end,
                filter_by=filter_by,
                data_type=data_type,
            )
            for chunk_start, chunk_end in chunks
        ]

        return await asyncio.gather(*tasks)

    async def get_data(
        self,
        *,
        metric: str,
        entity: str,
        start_date: date,
        end_date: date,
        filter_by: list[str] | None = None,
        output_schema: type[BaseModel] | None = None,
    ) -> pd.DataFrame:
        """
        Fetch data for a specific metric with automatic chunking.

        Args:
            metric: Metric ID to fetch (e.g., "Gene", "DemaReal")
            entity: Entity type (e.g., "Sistema", "Recurso", "Agente")
            start_date: Start date for data
            end_date: End date for data
            filter_by: Optional list of filter values (e.g., resource codes)
            output_schema: Optional Pydantic schema for response validation

        Returns:
            DataFrame containing the requested data

        Raises:
            ValueError: If metric/entity combination is invalid
            httpx.HTTPStatusError: If API request fails
        """
        return await self._get_data_internal(
            metric=metric,
            entity=entity,
            start_date=start_date,
            end_date=end_date,
            filter_by=filter_by,
            output_schema=output_schema,
        )


class SyncXMFetcher(BaseXMFetcher):
    """
    Synchronous data fetcher for XM API.

    This class provides a synchronous interface to fetch data from XM API,
    using sequential requests instead of async operations for simpler
    usage in non-async contexts.
    """

    def get_available_metrics(
        self, *, output_schema: type[BaseModel] | None = None
    ) -> pd.DataFrame:
        """
        Fetch all available metrics from XM API (synchronous).

        Returns:
            DataFrame containing all available metrics with their metadata
        """
        return asyncio.run(self._fetch_metrics())

    async def _execute_fetch_strategy(
        self,
        chunks: list[tuple[date, date]],
        metric: str,
        entity: str,
        filter_by: list[str] | None,
        data_type: str,
    ) -> list[pd.DataFrame]:
        """
        Execute sequential fetch strategy for sync client.

        Fetches chunks one by one to avoid overwhelming the API
        and for simpler execution flow in synchronous contexts.

        Args:
            chunks: List of date chunks to fetch
            metric: Metric ID
            entity: Entity type
            filter_by: Optional filter list
            data_type: Data type

        Returns:
            List of DataFrames, one per chunk
        """
        results = []
        for chunk_start, chunk_end in chunks:
            chunk_df = await self._fetch_single_chunk(
                metric=metric,
                entity=entity,
                start_date=chunk_start,
                end_date=chunk_end,
                filter_by=filter_by,
                data_type=data_type,
            )
            results.append(chunk_df)
        return results

    def get_data(
        self,
        *,
        metric: str,
        entity: str,
        start_date: date,
        end_date: date,
        filter_by: list[str] | None = None,
        output_schema: type[BaseModel] | None = None,
    ) -> pd.DataFrame:
        """
        Fetch data for a specific metric with automatic chunking (synchronous).

        Args:
            metric: Metric ID to fetch
            entity: Entity type
            start_date: Start date for data
            end_date: End date for data
            filter_by: Optional list of filter values
            output_schema: Optional Pydantic schema for response validation

        Returns:
            DataFrame containing the requested data

        Raises:
            ValueError: If metric/entity combination is invalid
            httpx.HTTPStatusError: If API request fails
        """
        return asyncio.run(
            self._get_data_internal(
                metric=metric,
                entity=entity,
                start_date=start_date,
                end_date=end_date,
                filter_by=filter_by,
                output_schema=output_schema,
            )
        )
