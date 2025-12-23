from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from src.schemas.story import StoryGenerationRequest, StoryGenerationResponse, HealthCheck
from src.services.story_generator import StoryGeneratorService
from src.core.exceptions import JiraiyaException
from src.api.deps import get_story_service, verify_api_key
from src.core.config import settings
import structlog

logger = structlog.get_logger()
router = APIRouter()

@router.get("/health", response_model=HealthCheck)
async def health_check():
    """Basic health check - always returns 200 if service is running."""
    return HealthCheck(status="ok", version=settings.VERSION)

@router.get("/health/ready")
async def readiness_check():
    """
    Readiness probe for Kubernetes.
    Checks if service dependencies are available.
    """
    health_status = {
        "ready": True,
        "checks": {}
    }
    
    # Check OpenAI configuration
    if settings.OPENAI_API_KEY:
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY, timeout=5.0)
            await client.models.list()
            health_status["checks"]["openai"] = {"status": "healthy"}
        except Exception as e:
            logger.warning("openai_health_check_failed", error=str(e))
            health_status["checks"]["openai"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health_status["ready"] = False
    else:
        health_status["checks"]["openai"] = {
            "status": "not_configured",
            "note": "Running in mock mode"
        }
    
    status_code = status.HTTP_200_OK if health_status["ready"] else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(status_code=status_code, content=health_status)

@router.post("/generate", response_model=StoryGenerationResponse)
async def generate_story(
    request: StoryGenerationRequest,
    service: StoryGeneratorService = Depends(get_story_service),
    api_key: str = Depends(verify_api_key)
):
    """
    Generate a story based on keywords, genre, and tone.
    
    Requires API key authentication via X-API-Key header.
    """
    try:
        logger.info(
            "story_generation_requested",
            keywords=request.keywords,
            genre=request.genre,
            tone=request.tone
        )
        story = await service.generate_story(request)
        logger.info("story_generation_completed", title=story.title)
        return story
    except Exception as e:
        # If it's a known error, re-raise it so the handler catches it
        if isinstance(e, JiraiyaException):
             raise e
        # Otherwise wrap it or let the global 500 handler catch it
        logger.error("story_generation_failed", error=str(e), error_type=type(e).__name__)
        raise HTTPException(status_code=500, detail="Internal server error")
