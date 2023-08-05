from unittest import mock
from fastapi.testclient import TestClient
from app.main import app
from sqlalchemy.orm import Session


client = TestClient(app)

@mock.patch('app.api.api_v1.api.action.MessageRepository')
@mock.patch('app.api.api_v1.api.action.SituationContentProvider.get_content')
@mock.patch('app.api.api_v1.api.action.openai.ChatCompletion.create')
def test_action(mock_create, mock_get_content, mock_repo):
    mock_message = mock.Mock()
    mock_message.role = 'system'
    mock_message.content = 'test completion'

    mock_choice = mock.Mock()
    mock_choice.message = mock_message
    mock_create.return_value = mock.Mock(choices=[mock_choice])

    # Mock the get_content method to return a test system message
    mock_get_content.return_value = 'You are a helpful assistant.'

    # Mock the repository's methods
    mock_repo.return_value.get_messages_by_user_id.return_value = []
    mock_repo.return_value.add_message.return_value = None

    with mock.patch.dict('os.environ', {'DEBUG': '1', 'CONFIG': '{"openai-api-key":"test", "db-credentials":"mysql+pymysql://user:password@localhost/dbname"}'}):
        response = client.post("/api/v1/action/", json={"input": "example input"})
        assert response.status_code == 200
        assert response.json() == {"output": "test completion"}

    # Assert that the repository's add_message and session's commit methods were called
    mock_repo.return_value.get_messages_by_user_id.assert_called_once()
    mock_repo.return_value.add_message.assert_called()
