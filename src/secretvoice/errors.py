"""SecretVoice SDK errors — every API failure maps to a typed exception."""

from __future__ import annotations


class SecretVoiceError(Exception):
    """Base error. `status_code` is the HTTP status (or None for network/WS)."""

    def __init__(self, message: str = "", status_code: int | None = None, detail: str = ""):
        super().__init__(message or detail or "SecretVoice request failed")
        self.status_code = status_code
        self.detail = detail


class AuthenticationError(SecretVoiceError):
    """HTTP 401 — the API key is missing or invalid."""


class InsufficientBalanceError(SecretVoiceError):
    """HTTP 402 — the account ran out of credits."""


class NotFoundError(SecretVoiceError):
    """HTTP 404 — voice/model/history item not found."""


class ValidationError(SecretVoiceError):
    """HTTP 422 — the request payload failed validation."""


class RateLimitError(SecretVoiceError):
    """HTTP 429 — too many requests; slow down."""


class ServerError(SecretVoiceError):
    """HTTP 5xx — the API hiccuped; retry after a short backoff."""


class WebSocketError(SecretVoiceError):
    """Realtime WebSocket failure."""


_STATUS_TO_ERROR = {
    400: ValidationError,
    401: AuthenticationError,
    402: InsufficientBalanceError,
    404: NotFoundError,
    422: ValidationError,
    429: RateLimitError,
}


def error_for_status(status_code: int, detail: str = "") -> SecretVoiceError:
    cls = _STATUS_TO_ERROR.get(status_code, ServerError if status_code >= 500 else SecretVoiceError)
    return cls(detail=detail, status_code=status_code, message=f"SecretVoice HTTP {status_code}")