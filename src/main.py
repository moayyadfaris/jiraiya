from fastapi import FastAPI
from asgi_correlation_id import CorrelationIdMiddleware
from src.core.config import settings, validate_settings
from src.core.logging import configure_logging
from src.core.exceptions import JiraiyaException, StoryGenerationError
from src.api.errors import jiraiya_exception_handler, story_generation_exception_handler
from src.api.v1.router import router as api_router
import structlog

# Configure structured logging
configure_logging(settings.LOG_LEVEL)

logger = structlog.get_logger()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"/docs",
    redoc_url=f"/redoc",
)

# Middleware
app.add_middleware(CorrelationIdMiddleware)

# Exception Handlers
app.add_exception_handler(JiraiyaException, jiraiya_exception_handler)
app.add_exception_handler(StoryGenerationError, story_generation_exception_handler)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    """Validate configuration and log startup."""
    try:
        validate_settings()
        logger.info(
            "service_starting",
            service=settings.PROJECT_NAME,
            version=settings.VERSION,
            environment=settings.ENVIRONMENT,
            ai_configured=bool(settings.OPENAI_API_KEY),
            auth_enabled=bool(settings.API_KEY)
        )
    except ValueError as e:
        logger.error("configuration_error", error=str(e))
        raise

@app.get("/")
def root():
    return {"message": "Welcome to Jiraiya Service 🐸"}
