import os
import debugpy


def main():
    if os.getenv("DEBUG_MODE") == "1":
        debugpy.listen(5678)
        print("Waiting for debugger to attach...")
        debugpy.wait_for_client()

    # Setup dependencies
    from src.infra.http.client import HTTPClient
    from src.infra.db.db import DatabaseFactory
    from src.interfaces.data_sources import ExampleAPIDataSource
    from src.core.use_cases import FetchAndSaveDataUseCase

    http_client = HTTPClient()
    endpoints = ["https://api.example.com/data1", "https://api.example.com/data2"]

    data_source = ExampleAPIDataSource(http_client, endpoints)
    repository = DatabaseFactory.create_repository(
        os.getenv("DB_TYPE", "sqlite"), os.getenv("DB_CONNECTION")
    )

    use_case = FetchAndSaveDataUseCase(data_source, repository)
    result = use_case.execute()

    http_client.close()
    return result


if __name__ == "__main__":
    main()
