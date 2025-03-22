import sqlite3
import json
from typing import Protocol
from pathlib import Path
from interfaces.repositories import DataRepository
from core.entities import DataEntity


class DatabaseConnection(Protocol):
    def execute(self, query: str, params: tuple): ...
    def commit(self): ...


class SQLiteRepository(DataRepository):
    def __init__(self, connection: DatabaseConnection):
        self.conn = connection
        self._create_table()

    def _create_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS processed_data (
                id TEXT PRIMARY KEY,
                content TEXT,
                processed BOOLEAN
            )
        """)

    def save_all(self, items: list[DataEntity]):
        cursor = self.conn.cursor()
        try:
            for item in items:
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO processed_data
                    (id, content, processed)
                    VALUES (?, ?, ?)
                """,
                    (item.id, item.content, item.processed),
                )
            self.conn.commit()
        finally:
            cursor.close()


class LocalStorageRepository(DataRepository):
    def __init__(self, storage_path: str = "local_data"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)

    def save_all(self, items: list[DataEntity]):
        for item in items:
            file_path = self.storage_path / f"{item.id}.json"
            with open(file_path, "w") as f:
                json.dump(
                    {
                        "id": item.id,
                        "content": item.content,
                        "processed": item.processed,
                    },
                    f,
                )


class DatabaseFactory:
    @staticmethod
    def create_repository(db_type: str, connection_str: str = None) -> DataRepository:
        if db_type == "local":
            return LocalStorageRepository(connection_str or "local_data")
        elif db_type == "sqlite":
            conn = sqlite3.connect(connection_str or ":memory:")
            return SQLiteRepository(conn)
        raise ValueError(f"Unknown database type: {db_type}")
