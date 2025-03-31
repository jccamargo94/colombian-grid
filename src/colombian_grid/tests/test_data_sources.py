# import pytest
# from interfaces.base import ExampleAPIDataSource
# from unittest.mock import Mock


# @pytest.fixture
# def mock_http_client():
#     client = Mock()
#     client.get.return_value = Mock(
#         status_code=200, json=lambda: [{"id": "1", "content": "test"}]
#     )
#     return client


# def test_data_source_fetch_data(mock_http_client):
#     data_source = ExampleAPIDataSource(mock_http_client, ["http://test.url"])
#     data = data_source.fetch_data()
#     assert len(data) == 1
#     assert data[0]["id"] == "1"
