from unittest import mock, skip
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@skip('TODO: update it!')
@mock.patch('app.api.api_v1.api.action.FeedbackFunctionExecutionService.execute')
@mock.patch('app.api.api_v1.api.action.MessageRepository')
@mock.patch('app.api.api_v1.api.action.SituationContentProvider.get_content')
@mock.patch('app.api.api_v1.api.action.openai.ChatCompletion.create')
def test_action(mock_create, mock_get_content, mock_repo, mock_execute):
    mock_message = mock.Mock()
    mock_message.role = 'system'
    mock_message.content = 'test completion'

    mock_choice = mock.Mock()
    mock_choice.message = mock_message
    # TODO
    # mock_choice.message.get.return_value = mock.Mock(arguments='{"temperature": "22", "unit": "celsius", "description": "Sunny"}')
    mock_choice.message.get.return_value = None
    mock_create.return_value = mock.Mock(choices=[mock_choice])

    # Mock the get_content method to return a test system message
    mock_get_content.return_value = 'You are a helpful assistant.'

    # Mock the repository's methods
    mock_repo.return_value.get_messages_by_user_id.return_value = []
    mock_repo.return_value.add_message.return_value = None

    with mock.patch.dict('os.environ', {'DEBUG': '1', 'CONFIG': '{"openai-api-key":"test", "db-credentials":"mysql+pymysql://user:password@localhost/dbname"}'}):
        response = client.post("/api/v1/action/", json={"input": "example input"})
        assert response.status_code == 200
        assert response.json() == {"messages": [
            {"role": "user", "content": "example input"},
            {"role": "assistant", "content": "test completion"}
        ]}

    # Assert that the repository's add_message and session's commit methods were called
    mock_repo.return_value.get_messages_by_user_id.assert_called_once()
    mock_repo.return_value.add_message.assert_called()

    # Assert that openai.ChatCompletion.create was called with the correct messages
    expected_messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "example input"},
    ]
    mock_create.assert_called_once_with(
        model="gpt-4-1106-preview",
        messages=expected_messages,
        temperature=0.5,
        functions=mock.ANY,
        max_tokens=1000
    )
    