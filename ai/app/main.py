import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.errors import AppError, ErrorCategory
from app.routers import health

logger = logging.getLogger(__name__)


def error_response(
    status_code: int,
    code: str,
    category: ErrorCategory,
    message: str,
    retry_after_seconds: int | None = None,
) -> JSONResponse:
    """Jedyne miejsce, które buduje ciało błędu z contract.md."""
    error: dict[str, object] = {
        "code": code,
        "category": category.value,
        "message": message,
    }
    if retry_after_seconds is not None:
        error["retry_after_seconds"] = retry_after_seconds
    return JSONResponse(status_code=status_code, content={"error": error})


def create_app() -> FastAPI:
    app = FastAPI(title="coworker-ai")

    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        return error_response(
            exc.status_code,
            exc.code,
            exc.category,
            exc.message,
            exc.retry_after_seconds,
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        details = "; ".join(
            f"{'.'.join(str(part) for part in err['loc'])}: {err['msg']}"
            for err in exc.errors()
        )
        return error_response(
            422,
            "REQUEST_VALIDATION_FAILED",
            ErrorCategory.PERMANENT,
            details,
        )

    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        category = (
            ErrorCategory.RETRYABLE
            if exc.status_code >= 500
            else ErrorCategory.PERMANENT
        )
        return error_response(
            exc.status_code, f"HTTP_{exc.status_code}", category, str(exc.detail)
        )

    @app.exception_handler(Exception)
    async def handle_unexpected(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Nieobsłużony wyjątek: %s %s", request.method, request.url.path)
        return error_response(
            500,
            "INTERNAL_ERROR",
            ErrorCategory.RETRYABLE,
            "Nieoczekiwany błąd po stronie serwisu AI",
        )

    app.include_router(health.router)
    return app


app = create_app()
