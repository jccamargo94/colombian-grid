import sqlite3
import json
import pytest
from core.entities import DataEntity
from src.infra.db.db import SQLiteRepository, LocalStorageRepository


@pytest.fixture
def sqlite_repo(tmp_path):
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(db_path)
    yield SQLiteRepository(conn)
    conn.close()


@pytest.fixture
def local_repo(tmp_path):
    return LocalStorageRepository(tmp_path)


def test_sqlite_repository_save(sqlite_repo):
    item = DataEntity(id="1", content="TEST", processed=True)
    sqlite_repo.save_all([item])

    cursor = sqlite_repo.conn.cursor()
    cursor.execute("SELECT * FROM processed_data")
    result = cursor.fetchone()
    assert result == ("1", "TEST", 1)


def test_local_repository_save(local_repo, tmp_path):
    item = DataEntity(id="1", content="TEST", processed=True)
    local_repo.save_all([item])

    file_path = tmp_path / "1.json"
    assert file_path.exists()
    with open(file_path) as f:
        data = json.load(f)
    assert data["content"] == "TEST"
