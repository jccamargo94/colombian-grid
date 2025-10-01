"""
Tests for XM API fetchers

This module tests both async and sync XM data fetchers.
"""

import pytest
from datetime import date
from unittest.mock import patch, AsyncMock, MagicMock
import pandas as pd

from colombian_grid.core.infra.http.httpx.async_client import AsyncHttpClient
from colombian_grid.core.base.interfaces.xm.fetchers import (
    AsyncXMFetcher,
    SyncXMFetcher,
    _generate_date_chunks,
    _generate_year_chunks,
)


# Test data generation functions
def test_generate_date_chunks():
    """Test date chunking for API restrictions."""
    start = date(2024, 1, 1)
    end = date(2024, 3, 15)
    max_days = 30

    chunks = _generate_date_chunks(start, end, max_days)

    assert len(chunks) == 3
    assert chunks[0] == (date(2024, 1, 1), date(2024, 1, 30))
    # 2024 is a leap year, so Feb has 29 days
    assert chunks[1] == (date(2024, 1, 31), date(2024, 2, 29))
    assert chunks[2] == (date(2024, 3, 1), date(2024, 3, 15))


def test_generate_year_chunks():
    """Test year-based chunking for very long time spans."""
    start = date(2020, 1, 1)
    end = date(2025, 12, 31)
    max_years = 2

    chunks = _generate_year_chunks(start, end, max_years)

    assert len(chunks) == 3
    assert chunks[0] == (date(2020, 1, 1), date(2022, 1, 1))
    assert chunks[1] == (date(2022, 1, 2), date(2024, 1, 2))
    assert chunks[2] == (date(2024, 1, 3), date(2025, 12, 31))


# Async fetcher tests
@pytest.mark.asyncio
async def test_async_fetcher_get_available_metrics():
    """Test fetching available metrics asynchronously."""
    mock_response = AsyncMock()
    mock_response.status_code = 200
    # Make raise_for_status synchronous (not a coroutine)
    mock_response.raise_for_status = MagicMock()
    # Make json() return an awaitable coroutine
    mock_response.json = AsyncMock(
        return_value={
            "Items": [
                {
                    "ListEntities": [
                        {
                            "Values_MetricId": "Gene",
                            "Values_MetricName": "Generación",
                            "Values_Entity": "Sistema",
                            "Values_MaxDays": 31,
                            "Values_Type": "HourlyEntities",
                            "Values_Url": "http://servapibi.xm.com.co/hourly",
                        }
                    ],
                    "Date": "2024-01-01",
                }
            ]
        }
    )

    with patch.object(AsyncHttpClient, "post", return_value=mock_response):
        async with AsyncHttpClient() as http_client:
            fetcher = AsyncXMFetcher(http_client)
            metrics = await fetcher.get_available_metrics()

            assert isinstance(metrics, pd.DataFrame)
            assert "MetricId" in metrics.columns
            assert len(metrics) > 0


@pytest.mark.asyncio
async def test_async_fetcher_get_data():
    """Test fetching data for a metric asynchronously."""
    # Mock metrics response
    mock_metrics_response = AsyncMock()
    mock_metrics_response.status_code = 200
    # Make raise_for_status synchronous (not a coroutine)
    mock_metrics_response.raise_for_status = MagicMock()
    # Make json() return an awaitable coroutine
    mock_metrics_response.json = AsyncMock(
        return_value={
            "Items": [
                {
                    "ListEntities": [
                        {
                            "Values_MetricId": "Gene",
                            "Values_MetricName": "Generación",
                            "Values_Entity": "Sistema",
                            "Values_MaxDays": 31,
                            "Values_Type": "HourlyEntities",
                            "Values_Url": "http://servapibi.xm.com.co/hourly",
                        }
                    ],
                    "Date": "2024-01-01",
                }
            ]
        }
    )

    # Mock data response
    mock_data_response = AsyncMock()
    mock_data_response.status_code = 200
    # Make raise_for_status synchronous (not a coroutine)
    mock_data_response.raise_for_status = MagicMock()
    # Make json() return an awaitable coroutine
    mock_data_response.json = AsyncMock(
        return_value={
            "Items": [
                {
                    "HourlyEntities": [
                        {
                            "Values_Hour01": 1000.0,
                            "Values_Hour02": 1100.0,
                        }
                    ],
                    "Date": "2024-01-01",
                }
            ]
        }
    )

    with patch.object(
        AsyncHttpClient,
        "post",
        side_effect=[mock_metrics_response, mock_data_response],
    ):
        async with AsyncHttpClient() as http_client:
            fetcher = AsyncXMFetcher(http_client)

            data = await fetcher.get_data(
                metric="Gene",
                entity="Sistema",
                start_date=date(2024, 1, 1),
                end_date=date(2024, 1, 5),
            )

            assert isinstance(data, pd.DataFrame)
            assert len(data) > 0


@pytest.mark.asyncio
async def test_async_fetcher_invalid_metric():
    """Test error handling for invalid metric/entity combination."""
    mock_response = AsyncMock()
    mock_response.status_code = 200
    # Make raise_for_status synchronous (not a coroutine)
    mock_response.raise_for_status = MagicMock()
    # Make json() return an awaitable coroutine
    mock_response.json = AsyncMock(
        return_value={
            "Items": [
                {
                    "ListEntities": [
                        {
                            "Values_MetricId": "Gene",
                            "Values_MetricName": "Generación",
                            "Values_Entity": "Sistema",
                            "Values_MaxDays": 31,
                            "Values_Type": "HourlyEntities",
                            "Values_Url": "http://servapibi.xm.com.co/hourly",
                        }
                    ],
                    "Date": "2024-01-01",
                }
            ]
        }
    )

    with patch.object(AsyncHttpClient, "post", return_value=mock_response):
        async with AsyncHttpClient() as http_client:
            fetcher = AsyncXMFetcher(http_client)

            with pytest.raises(ValueError, match="Invalid metric/entity combination"):
                await fetcher.get_data(
                    metric="InvalidMetric",
                    entity="InvalidEntity",
                    start_date=date(2024, 1, 1),
                    end_date=date(2024, 1, 5),
                )


# Sync fetcher tests
def test_sync_fetcher_get_available_metrics():
    """Test fetching available metrics synchronously."""
    mock_response = AsyncMock()
    mock_response.status_code = 200
    # Make raise_for_status synchronous (not a coroutine)
    mock_response.raise_for_status = MagicMock()
    # Make json() return an awaitable coroutine
    mock_response.json = AsyncMock(
        return_value={
            "Items": [
                {
                    "ListEntities": [
                        {
                            "Values_MetricId": "DemaReal",
                            "Values_MetricName": "Demanda Real",
                            "Values_Entity": "Sistema",
                            "Values_MaxDays": 31,
                            "Values_Type": "HourlyEntities",
                            "Values_Url": "http://servapibi.xm.com.co/hourly",
                        }
                    ],
                    "Date": "2024-01-01",
                }
            ]
        }
    )

    with patch.object(AsyncHttpClient, "post", return_value=mock_response):
        http_client = AsyncHttpClient()
        fetcher = SyncXMFetcher(http_client)
        metrics = fetcher.get_available_metrics()

        assert isinstance(metrics, pd.DataFrame)
        assert "MetricId" in metrics.columns
        assert len(metrics) > 0


def test_sync_fetcher_get_data():
    """Test fetching data synchronously."""
    # Mock metrics response
    mock_metrics_response = AsyncMock()
    mock_metrics_response.status_code = 200
    # Make raise_for_status synchronous (not a coroutine)
    mock_metrics_response.raise_for_status = MagicMock()
    # Make json() return an awaitable coroutine
    mock_metrics_response.json = AsyncMock(
        return_value={
            "Items": [
                {
                    "ListEntities": [
                        {
                            "Values_MetricId": "DemaReal",
                            "Values_MetricName": "Demanda Real",
                            "Values_Entity": "Sistema",
                            "Values_MaxDays": 31,
                            "Values_Type": "DailyEntities",
                            "Values_Url": "http://servapibi.xm.com.co/daily",
                        }
                    ],
                    "Date": "2024-01-01",
                }
            ]
        }
    )

    # Mock data response
    mock_data_response = AsyncMock()
    mock_data_response.status_code = 200
    # Make raise_for_status synchronous (not a coroutine)
    mock_data_response.raise_for_status = MagicMock()
    # Make json() return an awaitable coroutine
    mock_data_response.json = AsyncMock(
        return_value={
            "Items": [
                {
                    "DailyEntities": [
                        {
                            "Values_Day01": 50000.0,
                            "Values_Day02": 51000.0,
                        }
                    ],
                    "Date": "2024-01-01",
                }
            ]
        }
    )

    with patch.object(
        AsyncHttpClient,
        "post",
        side_effect=[mock_metrics_response, mock_data_response],
    ):
        http_client = AsyncHttpClient()
        fetcher = SyncXMFetcher(http_client)

        data = fetcher.get_data(
            metric="DemaReal",
            entity="Sistema",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 10),
        )

        assert isinstance(data, pd.DataFrame)
        assert len(data) > 0


def test_sync_fetcher_with_filters():
    """Test sync fetcher with filter parameter."""
    mock_metrics_response = AsyncMock()
    mock_metrics_response.status_code = 200
    # Make raise_for_status synchronous (not a coroutine)
    mock_metrics_response.raise_for_status = MagicMock()
    # Make json() return an awaitable coroutine
    mock_metrics_response.json = AsyncMock(
        return_value={
            "Items": [
                {
                    "ListEntities": [
                        {
                            "Values_MetricId": "Gene",
                            "Values_MetricName": "Generación",
                            "Values_Entity": "Recurso",
                            "Values_MaxDays": 31,
                            "Values_Type": "HourlyEntities",
                            "Values_Url": "http://servapibi.xm.com.co/hourly",
                            "Values_Filter": "Codigo Recurso",
                        }
                    ],
                    "Date": "2024-01-01",
                }
            ]
        }
    )

    mock_data_response = AsyncMock()
    mock_data_response.status_code = 200
    # Make raise_for_status synchronous (not a coroutine)
    mock_data_response.raise_for_status = MagicMock()
    # Make json() return an awaitable coroutine
    mock_data_response.json = AsyncMock(
        return_value={
            "Items": [
                {
                    "HourlyEntities": [
                        {
                            "Values_Code": "TBST",
                            "Values_Hour01": 500.0,
                        }
                    ],
                    "Date": "2024-01-01",
                }
            ]
        }
    )

    with patch.object(
        AsyncHttpClient,
        "post",
        side_effect=[mock_metrics_response, mock_data_response],
    ):
        http_client = AsyncHttpClient()
        fetcher = SyncXMFetcher(http_client)

        data = fetcher.get_data(
            metric="Gene",
            entity="Recurso",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 5),
            filter_by=["TBST", "GVIO"],
        )

        assert isinstance(data, pd.DataFrame)
        assert len(data) > 0
