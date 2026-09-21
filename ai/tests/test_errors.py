from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.errors import AppError, ErrorCategory
from app.main import create_app


class Payload(BaseModel):
    document_id: str


def make_client() -> TestClient:
    app = create_app()

    @app.get("/boom/retryable")
    def boom_retryable() -> None:
        raise AppError(
            "EMBEDDING_PROVIDER_TIMEOUT",
            "Provider nie odpowiedział",
            ErrorCategory.RETRYABLE,
            retry_after_seconds=20,
        )

    @app.get("/boom/permanent")
    def boom_permanent() -> None:
        raise AppError("EMPTY_DOCUMENT", "Pusty dokument", ErrorCategory.PERMANENT)

    @app.get("/boom/unexpected")
    def boom_unexpected() -> None:
        raise RuntimeError("cos poszlo nie tak")

    @app.post("/echo")
    def echo(payload: Payload) -> Payload:
        return payload

    return TestClient(app, raise_server_exceptions=False)


def test_retryable_error_uses_contract_format() -> None:
    response = make_client().get("/boom/retryable")

    assert response.status_code == 503
    assert response.json() == {
        "error": {
            "code": "EMBEDDING_PROVIDER_TIMEOUT",
            "category": "RETRYABLE",
            "message": "Provider nie odpowiedział",
            "retry_after_seconds": 20,
        }
    }


def test_permanent_error_has_no_retry_after() -> None:
    response = make_client().get("/boom/permanent")

    assert response.status_code == 422
    assert response.json() == {
        "error": {
            "code": "EMPTY_DOCUMENT",
            "category": "PERMANENT",
            "message": "Pusty dokument",
        }
    }


def test_unhandled_exception_is_retryable_500_without_leaking_details() -> None:
    response = make_client().get("/boom/unexpected")

    assert response.status_code == 500
    error = response.json()["error"]
    assert error["code"] == "INTERNAL_ERROR"
    assert error["category"] == "RETRYABLE"
    assert "cos poszlo nie tak" not in error["message"]


def test_request_validation_error_is_permanent() -> None:
    response = make_client().post("/echo", json={})

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "REQUEST_VALIDATION_FAILED"
    assert error["category"] == "PERMANENT"
    assert "document_id" in error["message"]


def test_unknown_route_is_permanent() -> None:
    response = make_client().get("/nie-ma-takiego")

    assert response.status_code == 404
    error = response.json()["error"]
    assert error["code"] == "HTTP_404"
    assert error["category"] == "PERMANENT"
