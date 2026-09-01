import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from app.api.v1 import api_router
from app.core.config import get_settings
from app.core.errors import (
    AppError,
    RequestIDMiddleware,
    app_error_handler,
    database_error_handler,
    request_validation_error_handler,
    unhandled_exception_handler,
)

logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # docs/llm/GROQ_SPEC.md "At startup, configuration must be validated."
    # This only logs (never raises) so local dev and the pytest suite keep
    # working without a Groq key (docs/llm/GROQ_SPEC.md "Testing").
    if not settings.GROQ_API_KEY:
        logger.warning("startup_config_warning: GROQ_API_KEY is not configured")
    if not settings.GROQ_MODEL:
        logger.warning("startup_config_warning: GROQ_MODEL is not configured")
    yield


app = FastAPI(title="AI Customer Support Assistant", lifespan=lifespan)

app.add_middleware(RequestIDMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(RequestValidationError, request_validation_error_handler)
app.add_exception_handler(SQLAlchemyError, database_error_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

app.include_router(api_router)
