# core/use_cases.py
from src.core.entities import DataEntity


class FetchAndSaveDataUseCase:
    def __init__(self, data_source, repository):
        self.data_source = data_source
        self.repository = repository

    def execute(self):
        raw_data = self.data_source.fetch_data()
        processed_data = [self._process_item(item) for item in raw_data]
        self.repository.save_all(processed_data)
        return processed_data

    def _process_item(self, item) -> DataEntity:
        """Example processing logic"""
        return DataEntity(
            id=item["id"], content=item["content"].upper(), processed=True
        )
