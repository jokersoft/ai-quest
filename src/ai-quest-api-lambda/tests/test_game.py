from unittest import mock
from fastapi.testclient import TestClient
from app.main import app
from sqlalchemy.orm import Session


client = TestClient(app)

@mock.patch('app.api.api_v1.api.action.openai.ChatCompletion.create')
@mock.patch.object(Session, 'commit', return_value=None)
@mock.patch.object(Session, 'add', return_value=None)
def test_action(mock_add, mock_commit, mock_create):
    mock_message = mock.Mock()
    mock_message.role = 'system'
    mock_message.content = 'test completion'

    mock_choice = mock.Mock()
    mock_choice.message = mock_message
    mock_create.return_value = mock.Mock(choices=[mock_choice])

    with mock.patch.dict('os.environ', {'DEBUG': '1', 'CONFIG': '{"openai-api-key":"test", "db-credentials":"mysql+pymysql://user:password@localhost/dbname"}'}):
        response = client.post("/api/v1/action/", json={"input": "example input"})
        assert response.status_code == 200
        assert response.json() == {"output": "test completion"}

    # Assert that the session's add and commit methods were called
    assert mock_add.call_count == 2
    assert mock_commit.call_count == 1
