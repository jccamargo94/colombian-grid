import pytest
from colombian_grid.core.infra.http.base import HttpClientBase


class TestHttpClientBase:
    @pytest.fixture
    def http_client(self):
        return HttpClientBase(
            base_url="https://example.com",
            timeout=5.0,
            max_retries=5,
            backoff_factor=0.5,
            status_forcelist=[400, 401, 402, 403, 404, 500, 501, 502],
        )

    def test_initialization(self):
        client = HttpClientBase(
            base_url="https://test.com/",
            timeout=15.0,
            max_retries=4,
            backoff_factor=0.2,
            status_forcelist=[401, 403],
            test_arg="test",
        )
        assert client.base_url == "https://test.com"
        assert client.timeout == 15.0
        assert client.max_retries == 4
        assert client.backoff_factor == 0.2
        assert client.status_forcelist == [401, 403]
        assert client.kwargs == {"test_arg": "test"}

    def test_initialization_with_defaults(self):
        client = HttpClientBase()
        assert client.base_url == ""
        assert client.timeout == 10.0
        assert client.max_retries == 3
        assert client.backoff_factor == 0.3
        assert client.status_forcelist == [408, 429, 500, 502, 503, 504]
        assert client.kwargs == {}

    def test_should_retry(self, http_client):
        assert http_client._should_retry(400, 2) is True
        assert http_client._should_retry(401, 2) is True
        assert http_client._should_retry(429, 2) is False
        assert http_client._should_retry(500, 4) is True
        assert http_client._should_retry(500, 10) is False
        assert http_client._should_retry(200, 1) is False
        assert http_client._should_retry(400, 5) is False
        assert http_client._should_retry(400, 6) is False

    def test_get_backoff_time(self, http_client):
        attempt = 2
        backoff_time = http_client._get_backoff_time(attempt)
        assert backoff_time == pytest.approx(1.0, rel=0.2)

        attempt = 3
        backoff_time = http_client._get_backoff_time(attempt)
        assert backoff_time == pytest.approx(2, rel=0.2)
