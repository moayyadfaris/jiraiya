from functools import lru_cache
from typing import Generator
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from src.services.story_generator import StoryGeneratorService
from src.core.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    """
    Verifies the API key from the header.
    """
    if settings.API_KEY and api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    return api_key

@lru_cache()
def get_story_service() -> StoryGeneratorService:
    """
    Dependency provider for StoryGeneratorService.
    Uses lru_cache to ensure we only create one instance (Singleton).
    """
    return StoryGeneratorService()
