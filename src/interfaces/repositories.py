from abc import ABC, abstractmethod
from typing import List
from core.entities import DataEntity


class DataRepository(ABC):
    @abstractmethod
    def save_all(self, items: List[DataEntity]):
        pass
