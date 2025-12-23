from fastapi import Request, status
from fastapi.responses import JSONResponse
from src.core.exceptions import JiraiyaException, StoryGenerationError
import structlog

logger = structlog.get_logger()

async def jiraiya_exception_handler(request: Request, exc: JiraiyaException):
    """
    Handle generic Jiraiya exceptions.
    """
    error_msg = str(exc)
    logger.error("jiraiya_error", error=error_msg, path=request.url.path)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "type": "about:blank",
            "title": "Internal Server Error",
            "status": 500,
            "detail": error_msg,
            "instance": request.url.path
        },
    )

async def story_generation_exception_handler(request: Request, exc: StoryGenerationError):
    """
    Handle specific story generation errors.
    """
    logger.error("story_generation_error", error=str(exc), detail=exc.detail)
    
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "type": "driver:error",
            "title": "Story Generation Failed",
            "status": 503,
            "detail": str(exc),
            "instance": request.url.path
        },
    )
