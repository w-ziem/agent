from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_answer_returns_contract_shape() -> None:
    response = client.post("/answer", json={"question": "czym jest entropia"})

    assert response.status_code == 200
    body = response.json()
    assert "czym jest entropia" in body["answer"]
    assert body["sources"] == []


def test_answer_empty_question_is_permanent_error() -> None:
    response = client.post("/answer", json={"question": ""})

    assert response.status_code == 422
    assert response.json()["error"]["category"] == "PERMANENT"
