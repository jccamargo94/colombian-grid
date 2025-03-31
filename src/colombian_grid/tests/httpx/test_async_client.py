import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock, patch
from colombian_grid.core.infra.http.httpx.async_client import AsyncHttpClient


@pytest.fixture
def mock_httpx_client():
    with patch("httpx.AsyncClient") as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.request = AsyncMock()
        mock_instance.aclose = AsyncMock()
        yield mock_instance


@pytest.fixture
async def client(mock_httpx_client):
    client = AsyncHttpClient(
        base_url="https://api.example.com", timeout=10, max_retries=3
    )
    yield client
    await client.close()


@pytest.mark.asyncio
async def test_init():
    """Test client initialization with correct parameters"""
    client = AsyncHttpClient(
        base_url="https://api.example.com", timeout=5, max_retries=3
    )
    assert client.base_url == "https://api.example.com"
    assert client.timeout == 5
    assert client.max_retries == 3


@pytest.mark.asyncio
async def test_context_manager(mock_httpx_client):
    """Test async context manager functionality"""
    async with AsyncHttpClient(base_url="https://api.example.com") as client:
        assert client is not None

    # Verify close was called
    mock_httpx_client.aclose.assert_called_once()


@pytest.mark.asyncio
async def test_request_with_retry_success(client, mock_httpx_client):
    """Test successful request without retries"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_httpx_client.request.return_value = mock_response

    response = await client.get("/users")

    mock_httpx_client.request.assert_called_once_with("GET", "/users")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_request_with_retry_retry_once(client, mock_httpx_client):
    """Test request that succeeds after one retry"""
    error_response = MagicMock()
    error_response.status_code = 500
    success_response = MagicMock()
    success_response.status_code = 200

    mock_httpx_client.request.side_effect = [error_response, success_response]

    with patch.object(client, "_should_retry", return_value=True) as mock_should_retry:
        with patch.object(client, "_get_backoff_time", return_value=0) as mock_backoff:
            response = await client.get("/users")

    assert mock_httpx_client.request.call_count == 2
    assert response.status_code == 200
    mock_should_retry.assert_called_once()
    mock_backoff.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_request_with_timeout_exception(client, mock_httpx_client):
    """Test request with timeout exception that exceeds retries"""
    mock_httpx_client.request.side_effect = httpx.TimeoutException("Timeout")

    with patch.object(client, "_get_backoff_time", return_value=0):
        with pytest.raises(httpx.TimeoutException):
            await client.get("/users")

    assert mock_httpx_client.request.call_count == client.max_retries


@pytest.mark.asyncio
async def test_http_methods(client, mock_httpx_client):
    """Test all HTTP methods call the underlying client with correct parameters"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_httpx_client.request.return_value = mock_response

    # Test GET
    await client.get("/users", params={"id": 1})
    mock_httpx_client.request.assert_called_with("GET", "/users", params={"id": 1})

    # Test POST
    await client.post("/users", json={"name": "Test"})
    mock_httpx_client.request.assert_called_with(
        "POST", "/users", json={"name": "Test"}
    )

    # Test PATCH
    await client.patch("/users/1", json={"name": "Updated"})
    mock_httpx_client.request.assert_called_with(
        "PATCH", "/users/1", json={"name": "Updated"}
    )

    # Test DELETE
    await client.delete("/users/1")
    mock_httpx_client.request.assert_called_with("DELETE", "/users/1")
