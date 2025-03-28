from abc import ABC, abstractmethod


class APIDataSource(ABC):
    @abstractmethod
    async def get_data(self, *args, **kwargs) -> list: ...
