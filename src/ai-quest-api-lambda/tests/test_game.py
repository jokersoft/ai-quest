from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_perform_action():
    response = client.post("/api/v1/action/", json={"input": "example input"})
    assert response.status_code == 200
    assert response.json() == {"input": "example input"}
