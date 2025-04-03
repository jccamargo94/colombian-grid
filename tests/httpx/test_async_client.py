import pytest
import httpx
from unittest.mock import patch, AsyncMock
from colombian_grid.core.infra.http.httpx.async_client import AsyncHttpClient


@pytest.mark.asyncio
async def test_async_http_client_get_success():
    with patch.object(httpx.AsyncClient, "request") as mock_request:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        async with AsyncHttpClient(base_url="http://test.com") as client:
            response = await client.get("/test")

        assert response.status_code == 200
        mock_request.assert_called_once_with("GET", "/test")


@pytest.mark.asyncio
async def test_async_http_client_post_success():
    with patch.object(httpx.AsyncClient, "request") as mock_request:
        mock_response = AsyncMock()
        mock_response.status_code = 201
        mock_request.return_value = mock_response

        async with AsyncHttpClient(base_url="http://test.com") as client:
            response = await client.post("/test", json={"key": "value"})

        assert response.status_code == 201
        mock_request.assert_called_once_with("POST", "/test", json={"key": "value"})


@pytest.mark.asyncio
async def test_async_http_client_patch_success():
    with patch.object(httpx.AsyncClient, "request") as mock_request:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        async with AsyncHttpClient(base_url="http://test.com") as client:
            response = await client.patch("/test", json={"key": "value"})

        assert response.status_code == 200
        mock_request.assert_called_once_with("PATCH", "/test", json={"key": "value"})


@pytest.mark.asyncio
async def test_async_http_client_delete_success():
    with patch.object(httpx.AsyncClient, "request") as mock_request:
        mock_response = AsyncMock()
        mock_response.status_code = 204
        mock_request.return_value = mock_response

        async with AsyncHttpClient(base_url="http://test.com") as client:
            response = await client.delete("/test")

        assert response.status_code == 204
        mock_request.assert_called_once_with("DELETE", "/test")


@pytest.mark.asyncio
async def test_async_http_client_retry_success():
    with (
        patch.object(httpx.AsyncClient, "request") as mock_request,
        patch.object(AsyncHttpClient, "_get_backoff_time") as mock_backoff,
    ):
        mock_backoff.return_value = 0.01
        mock_response_500 = AsyncMock()
        mock_response_500.status_code = 500

        mock_response_200 = AsyncMock()
        mock_response_200.status_code = 200

        mock_request.side_effect = [mock_response_500, mock_response_200]

        async with AsyncHttpClient(base_url="http://test.com") as client:
            response = await client.get("/test")

        assert response.status_code == 200
        assert mock_request.call_count == 2


@pytest.mark.asyncio
async def test_async_http_client_timeout_exception():
    with (
        patch.object(httpx.AsyncClient, "request") as mock_request,
        patch.object(AsyncHttpClient, "_get_backoff_time") as mock_backoff,
    ):
        mock_backoff.return_value = 0.01

        mock_request.side_effect = httpx.TimeoutException("Timeout")

        async with AsyncHttpClient(base_url="http://test.com", max_retries=2) as client:
            with pytest.raises(httpx.TimeoutException):
                await client.get("/test")
        assert mock_request.call_count == 2


@pytest.mark.asyncio
async def test_async_http_client_network_error_exception():
    with (
        patch.object(httpx.AsyncClient, "request") as mock_request,
        patch.object(AsyncHttpClient, "_get_backoff_time") as mock_backoff,
    ):
        mock_backoff.return_value = 0.01

        mock_request.side_effect = httpx.NetworkError("Network Error")

        async with AsyncHttpClient(base_url="http://test.com", max_retries=2) as client:
            with pytest.raises(httpx.NetworkError):
                await client.get("/test")
        assert mock_request.call_count == 2
