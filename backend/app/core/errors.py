import logging
import uuid

from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

REQUEST_ID_HEADER = "X-Request-ID"
REQUEST_ID_STATE_KEY = "request_id"

ERROR_CODES = frozenset(
    {
        "validation_error",
        "model_unavailable",
        "retrieval_error",
        "llm_error",
        "database_error",
        "not_found",
        "internal_error",
    }
)


class AppError(Exception):
    code = "internal_error"
    status_code = 500

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class ValidationAppError(AppError):
    code = "validation_error"
    status_code = 422


class ModelUnavailableError(AppError):
    code = "model_unavailable"
    status_code = 503


class RetrievalError(AppError):
    code = "retrieval_error"
    status_code = 502


class LLMError(AppError):
    code = "llm_error"
    status_code = 502


class DatabaseError(AppError):
    code = "database_error"
    status_code = 503


class NotFoundError(AppError):
    code = "not_found"
    status_code = 404


class InternalError(AppError):
    code = "internal_error"
    status_code = 500


def build_error_envelope(code: str, message: str, request_id: str) -> dict:
    return {"error": {"code": code, "message": message, "request_id": request_id}}


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get(REQUEST_ID_HEADER, str(uuid.uuid4()))
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers[REQUEST_ID_HEADER] = request_id
        return response


def get_request_id(request: Request) -> str:
    return getattr(request.state, REQUEST_ID_STATE_KEY, str(uuid.uuid4()))


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    request_id = get_request_id(request)
    return JSONResponse(
        status_code=exc.status_code,
        content=build_error_envelope(exc.code, exc.message, request_id),
        headers={REQUEST_ID_HEADER: request_id},
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = get_request_id(request)
    return JSONResponse(
        status_code=500,
        content=build_error_envelope(
            "internal_error", "An unexpected error occurred.", request_id
        ),
        headers={REQUEST_ID_HEADER: request_id},
    )


async def database_error_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Map any uncaught SQLAlchemy failure (connection lost, etc.) to `database_error`.

    docs/architecture/SYSTEM_ARCHITECTURE.md "Failure boundaries": "If
    database fails: return service-unavailable response." Never includes the
    raw exception (it can carry the connection string/credentials) in the
    response; full detail is logged server-side only
    (docs/backend/ERROR_HANDLING_SPEC.md "Do not expose ... SQL
    credentials").
    """
    request_id = get_request_id(request)
    logger.error(
        "database_error", extra={"request_id": request_id, "error_type": exc.__class__.__name__}
    )
    return JSONResponse(
        status_code=503,
        content=build_error_envelope(
            "database_error", "A database error occurred. Please try again shortly.", request_id
        ),
        headers={REQUEST_ID_HEADER: request_id},
    )


async def request_validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Render FastAPI/Pydantic request validation failures in the same error envelope.

    Without this handler, FastAPI's built-in default handler would return its
    own `{"detail": [...]}` shape for request-body/query/path validation
    failures (e.g. an empty or oversized complaint), bypassing the consistent
    envelope required by docs/backend/ERROR_HANDLING_SPEC.md.
    """
    request_id = get_request_id(request)
    errors = exc.errors()
    message = errors[0]["msg"] if errors else "Invalid request."
    return JSONResponse(
        status_code=422,
        content=build_error_envelope("validation_error", message, request_id),
        headers={REQUEST_ID_HEADER: request_id},
    )
