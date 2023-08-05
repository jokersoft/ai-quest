from unittest import mock
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)

@mock.patch.dict('os.environ', {'DEBUG': '1', 'CONFIG': '{"openai-api-key":"test"}'})
@mock.patch('app.api.api_v1.api.action.openai.Completion.create')
def test_action(mock_create):
    mock_create.return_value = mock.Mock(choices=[mock.Mock(text='test completion')])

    response = client.post("/api/v1/action/", json={"input": "example input"})
    assert response.status_code == 200
    assert response.json() == {"output": "test completion"}
