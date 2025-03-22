from abc import ABC, abstractmethod


class APIDataSource(ABC):
    @abstractmethod
    def fetch_data(self) -> list:
        pass


class ExampleAPIDataSource(APIDataSource):
    def __init__(self, http_client, endpoints):
        self.http_client = http_client
        self.endpoints = endpoints

    def fetch_data(self) -> list:
        data = []
        for url in self.endpoints:
            response = self.http_client.get(url)
            response.raise_for_status()
            data.extend(response.json())
        return data
