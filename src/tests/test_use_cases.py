from core.use_cases import FetchAndSaveDataUseCase
from unittest.mock import Mock


def test_use_case_execution():
    mock_source = Mock()
    mock_source.fetch_data.return_value = [{"id": "1", "content": "test"}]

    mock_repo = Mock()

    use_case = FetchAndSaveDataUseCase(mock_source, mock_repo)
    result = use_case.execute()

    assert len(result) == 1
    assert result[0].content == "TEST"
    mock_repo.save_all.assert_called_once()
