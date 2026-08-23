from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class APIDataSource(ABC, Generic[T]):
    @abstractmethod
    async def get_data(self, *args, **kwargs) -> T: ...
