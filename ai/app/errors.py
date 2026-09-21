from enum import StrEnum


class ErrorCategory(StrEnum):
    RETRYABLE = "RETRYABLE"
    PERMANENT = "PERMANENT"


class AppError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        category: ErrorCategory,
        *,
        status_code: int | None = None,
        retry_after_seconds: int | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.category = category
        # status HTTP jest tylko podpowiedzią, decyduje category
        self.status_code = status_code or (
            503 if category is ErrorCategory.RETRYABLE else 422
        )
        self.retry_after_seconds = retry_after_seconds
