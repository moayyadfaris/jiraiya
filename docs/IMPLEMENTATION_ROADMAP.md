# 🎯 Jiraiya Service - Implementation Roadmap

This document provides a step-by-step implementation guide with code examples for bringing Jiraiya Service to enterprise production standards.

---

## Week 1: Core Infrastructure (Critical)

### Day 1-2: Configuration & Logging (10 hours)

#### Step 1: Enhanced Configuration (4 hours)

**File: `src/core/config.py`**
```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator
from typing import Optional, List
from enum import Enum

class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class Settings(BaseSettings):
    # Application
    PROJECT_NAME: str = "Jiraiya Service"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json or text
    
    # CORS
    CORS_ORIGINS: List[str] = Field(default=["http://localhost:3000"])
    
    # Security
    JWT_SECRET: str = Field(..., min_length=32)  # Required!
    JWT_ALGORITHM: str = "HS256"
    API_KEYS: List[str] = Field(default=[])
    
    # OpenAI
    OPENAI_API_KEY: str = Field(..., min_length=20)  # Required!
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_MAX_TOKENS: int = 2000
    OPENAI_TEMPERATURE: float = 0.7
    OPENAI_TIMEOUT: int = 30
    OPENAI_MAX_RETRIES: int = 3
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 10
    RATE_LIMIT_PER_HOUR: int = 100
    
    # Monitoring
    ENABLE_METRICS: bool = True
    ENABLE_TRACING: bool = False
    
    @validator("ENVIRONMENT", pre=True)
    def validate_environment(cls, v):
        if isinstance(v, str):
            return Environment(v.lower())
        return v
    
    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level. Must be one of {valid_levels}")
        return v.upper()
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == Environment.PRODUCTION
    
    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == Environment.DEVELOPMENT
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()

# Validate critical settings on startup
def validate_settings():
    """Validate settings on application startup"""
    if settings.is_production:
        assert len(settings.JWT_SECRET) >= 32, "JWT_SECRET too short for production"
        assert settings.OPENAI_API_KEY.startswith("sk-"), "Invalid OpenAI API key"
        assert not settings.DEBUG, "DEBUG must be False in production"
        assert settings.LOG_LEVEL in ["INFO", "WARNING", "ERROR"], "Invalid log level for production"
```

**File: `.env.example`**
```env
# Application
ENVIRONMENT=development
DEBUG=true

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=1

# Logging
LOG_LEVEL=DEBUG
LOG_FORMAT=json

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]

# Security
JWT_SECRET=your-super-secret-jwt-key-at-least-32-characters-long
JWT_ALGORITHM=HS256
API_KEYS=["dev-key-12345"]

# OpenAI
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_MAX_TOKENS=2000
OPENAI_TEMPERATURE=0.7
OPENAI_TIMEOUT=30
OPENAI_MAX_RETRIES=3

# Rate Limiting
RATE_LIMIT_PER_MINUTE=10
RATE_LIMIT_PER_HOUR=100

# Monitoring
ENABLE_METRICS=true
ENABLE_TRACING=false
```

---

#### Step 2: Structured Logging (6 hours)

**File: `src/core/logging_config.py`**
```python
import logging
import structlog
from typing import Any
from contextvars import ContextVar

# Context variable for correlation ID
correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="")

def add_correlation_id(logger, method_name, event_dict):
    """Add correlation ID to all log entries"""
    correlation_id = correlation_id_var.get("")
    if correlation_id:
        event_dict["correlation_id"] = correlation_id
    return event_dict

def configure_logging(log_level: str = "INFO", log_format: str = "json"):
    """Configure structured logging"""
    
    # Configure stdlib logging
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, log_level),
    )
    
    # Configure structlog
    processors = [
        structlog.contextvars.merge_contextvars,
        add_correlation_id,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]
    
    if log_format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

def get_logger(name: str = None) -> Any:
    """Get a structured logger instance"""
    return structlog.get_logger(name)
```

**File: `src/middleware/logging_middleware.py`**
```python
import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from src.core.logging_config import correlation_id_var, get_logger

logger = get_logger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Generate or extract correlation ID
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        correlation_id_var.set(correlation_id)
        
        # Log request
        logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
            query_params=dict(request.query_params),
            client_host=request.client.host if request.client else None,
        )
        
        # Process request
        start_time = time.time()
        try:
            response = await call_next(request)
            duration_ms = (time.time() - start_time) * 1000
            
            # Log response
            logger.info(
                "request_completed",
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
            )
            
            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id
            
            return response
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                "request_failed",
                error=str(e),
                error_type=type(e).__name__,
                duration_ms=round(duration_ms, 2),
            )
            raise
```

---

### Day 3: Error Handling (5 hours)

**File: `src/core/exceptions.py`**
```python
from typing import Any, Dict, Optional

class JiraiyaException(Exception):
    """Base exception for Jiraiya Service"""
    
    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class ValidationException(JiraiyaException):
    """Input validation errors"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=400,
            details=details
        )

class AIServiceException(JiraiyaException):
    """AI service errors (OpenAI, LangChain)"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            message=message,
            error_code="AI_SERVICE_ERROR",
            status_code=502,
            details=details
        )

class AuthenticationException(JiraiyaException):
    """Authentication errors"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            status_code=401
        )

class RateLimitException(JiraiyaException):
    """Rate limit exceeded"""
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=429
        )

class ConfigurationException(JiraiyaException):
    """Configuration errors"""
    def __init__(self, message: str):
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            status_code=500
        )
```

**File: `src/middleware/error_handler.py`**
```python
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from src.core.exceptions import JiraiyaException
from src.core.logging_config import get_logger, correlation_id_var

logger = get_logger(__name__)

async def jiraiya_exception_handler(request: Request, exc: JiraiyaException) -> JSONResponse:
    """Handle custom Jiraiya exceptions"""
    logger.error(
        "application_error",
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details,
        path=request.url.path,
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details,
                "correlation_id": correlation_id_var.get(""),
                "path": str(request.url.path),
            }
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic validation errors"""
    logger.warning(
        "validation_error",
        errors=exc.errors(),
        path=request.url.path,
    )
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": {"validation_errors": exc.errors()},
                "correlation_id": correlation_id_var.get(""),
                "path": str(request.url.path),
            }
        }
    )

async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected errors"""
    logger.exception(
        "unexpected_error",
        error=str(exc),
        error_type=type(exc).__name__,
        path=request.url.path,
    )
    
    # Don't leak internal errors in production
    from src.core.config import settings
    error_message = str(exc) if settings.DEBUG else "Internal server error"
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": error_message,
                "correlation_id": correlation_id_var.get(""),
                "path": str(request.url.path),
            }
        }
    )
```

---

### Day 4: Health Checks (4 hours)

**File: `src/services/health_checker.py`**
```python
from typing import Dict, Any
from datetime import datetime
import asyncio
import openai
from src.core.config import settings
from src.core.logging_config import get_logger

logger = get_logger(__name__)

class HealthCheckService:
    """Service for checking application and dependency health"""
    
    async def check_openai_api(self) -> Dict[str, Any]:
        """Check OpenAI API connectivity"""
        try:
            start_time = asyncio.get_event_loop().time()
            
            # Make a simple API call
            client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            await client.models.list()
            
            latency_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            
            return {
                "status": "healthy",
                "latency_ms": round(latency_ms, 2),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error("openai_health_check_failed", error=str(e))
            return {
                "status": "unhealthy",
                "error": str(e),
                "error_type": type(e).__name__,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def check_configuration(self) -> Dict[str, Any]:
        """Check if required configuration is present"""
        checks = {
            "openai_api_key_set": bool(settings.OPENAI_API_KEY),
            "jwt_secret_set": bool(settings.JWT_SECRET),
            "environment": settings.ENVIRONMENT.value,
        }
        
        all_healthy = all([
            checks["openai_api_key_set"],
            checks["jwt_secret_set"],
        ])
        
        return {
            "status": "healthy" if all_healthy else "unhealthy",
            "checks": checks,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_health(self) -> Dict[str, Any]:
        """Basic health check - always returns 200"""
        return {
            "status": "ok",
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT.value,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_readiness(self) -> Dict[str, Any]:
        """Readiness probe - checks if service is ready to accept traffic"""
        checks = {
            "openai": await self.check_openai_api(),
            "configuration": self.check_configuration(),
        }
        
        all_ready = all(
            check["status"] == "healthy" 
            for check in checks.values()
        )
        
        return {
            "ready": all_ready,
            "checks": checks,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_liveness(self) -> Dict[str, Any]:
        """Liveness probe - checks if service is alive"""
        return {
            "alive": True,
            "timestamp": datetime.utcnow().isoformat()
        }

health_service = HealthCheckService()
```

**File: `src/api/v1/health.py`**
```python
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from src.services.health_checker import health_service
from src.schemas.health import HealthResponse, ReadinessResponse, LivenessResponse

router = APIRouter(tags=["Health"])

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Basic health check"""
    return await health_service.get_health()

@router.get("/health/ready", response_model=ReadinessResponse)
async def readiness_check():
    """Readiness probe for Kubernetes"""
    result = await health_service.get_readiness()
    status_code = status.HTTP_200_OK if result["ready"] else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(status_code=status_code, content=result)

@router.get("/health/live", response_model=LivenessResponse)
async def liveness_check():
    """Liveness probe for Kubernetes"""
    return await health_service.get_liveness()
```

---

## Week 2: AI Service & Security

### Day 5-6: Real LangChain Implementation (8 hours)

**File: `src/services/story_generator.py`**
```python
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from openai import RateLimitError, APIError
from src.schemas.story import StoryGenerationRequest, StoryGenerationResponse, StoryOutput
from src.core.config import settings
from src.core.logging_config import get_logger
from src.core.exceptions import AIServiceException

logger = get_logger(__name__)

class StoryGeneratorService:
    """Real AI story generation using LangChain + OpenAI"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            temperature=settings.OPENAI_TEMPERATURE,
            max_tokens=settings.OPENAI_MAX_TOKENS,
            timeout=settings.OPENAI_TIMEOUT,
            max_retries=0,  # We handle retries ourselves
        )
        
        # Output parser for structured responses
        self.parser = PydanticOutputParser(pydantic_object=StoryOutput)
        
        # Prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a creative story writer. Generate an engaging story based on the given parameters.
            
{format_instructions}

The story should:
- Include ALL the provided keywords naturally
- Match the specified genre
- Maintain the requested tone
- Be between {min_length} and {max_length} words
- Have a compelling title
- Be creative and engaging"""),
            ("human", """Generate a story with these parameters:
            
Keywords: {keywords}
Genre: {genre}
Tone: {tone}
Length: {min_length}-{max_length} words""")
        ])
    
    @retry(
        retry=retry_if_exception_type((RateLimitError, APIError)),
        stop=stop_after_attempt(settings.OPENAI_MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        before_sleep=lambda retry_state: logger.warning(
            "retrying_ai_request",
            attempt=retry_state.attempt_number,
            wait_seconds=retry_state.next_action.sleep
        )
    )
    async def generate_story(self, request: StoryGenerationRequest) -> StoryGenerationResponse:
        """Generate a story using AI"""
        
        logger.info(
            "generating_story",
            keywords=request.keywords,
            genre=request.genre,
            tone=request.tone,
            max_length=request.max_length
        )
        
        try:
            # Prepare prompt
            formatted_prompt = self.prompt.format_messages(
                format_instructions=self.parser.get_format_instructions(),
                keywords=", ".join(request.keywords),
                genre=request.genre,
                tone=request.tone,
                min_length=request.min_length or 100,
                max_length=request.max_length
            )
            
            # Generate story
            response = await self.llm.ainvoke(formatted_prompt)
            
            # Parse response
            story_output = self.parser.parse(response.content)
            
            logger.info(
                "story_generated",
                title=story_output.title,
                content_length=len(story_output.content),
                keywords_used=len(story_output.keywords_used)
            )
            
            return StoryGenerationResponse(
                title=story_output.title,
                content=story_output.content,
                keywords_used=story_output.keywords_used
            )
            
        except Exception as e:
            logger.error(
                "story_generation_failed",
                error=str(e),
                error_type=type(e).__name__
            )
            raise AIServiceException(
                message="Failed to generate story",
                details={"error": str(e), "error_type": type(e).__name__}
            )

story_service = StoryGeneratorService()
```

**File: `src/schemas/story.py`** (updated)
```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional
import re

class StoryGenerationRequest(BaseModel):
    keywords: List[str] = Field(
        ..., 
        min_length=1,
        max_length=10,
        description="Keywords to include (1-10)"
    )
    genre: str = Field(
        ..., 
        min_length=3,
        max_length=50,
        description="Story genre"
    )
    tone: str = Field(
        "neutral",
        description="Story tone"
    )
    max_length: int = Field(
        500,
        ge=100,
        le=2000,
        description="Maximum length in words"
    )
    min_length: Optional[int] = Field(
        None,
        ge=50,
        le=1000,
        description="Minimum length in words"
    )
    
    @validator("keywords")
    def validate_keywords(cls, v):
        if not v:
            raise ValueError("At least one keyword is required")
        # Remove empty strings and duplicates
        keywords = list(set(k.strip() for k in v if k.strip()))
        if not keywords:
            raise ValueError("At least one non-empty keyword is required")
        return keywords
    
    @validator("tone")
    def validate_tone(cls, v):
        valid_tones = ["neutral", "humorous", "dark", "epic", "romantic", "mysterious"]
        if v.lower() not in valid_tones:
            raise ValueError(f"Tone must be one of: {', '.join(valid_tones)}")
        return v.lower()
    
    @validator("min_length")
    def validate_length_range(cls, v, values):
        if v and "max_length" in values and v > values["max_length"]:
            raise ValueError("min_length cannot be greater than max_length")
        return v

class StoryOutput(BaseModel):
    """Output format for AI-generated story"""
    title: str = Field(..., description="Story title")
    content: str = Field(..., description="Story content")
    keywords_used: List[str] = Field(..., description="Keywords included in story")

class StoryGenerationResponse(BaseModel):
    title: str = Field(..., description="Generated story title")
    content: str = Field(..., description="Generated story content")
    keywords_used: List[str] = Field(..., description="Keywords that were used")

class HealthCheck(BaseModel):
    status: str = "ok"
    version: str
    service: str
    environment: str
    timestamp: str
```

---

### Day 7-8: Authentication & Security (8 hours)

See `ENTERPRISE_PROGRESS.md` Phase 3 for detailed authentication implementation.

---

## Quick Setup Script

**File: `scripts/setup-dev.sh`**
```bash
#!/bin/bash

echo "🐸 Setting up Jiraiya Service development environment"

# Check Python version
python_version=$(python3 --version | cut -d' ' -f2)
echo "✓ Python version: $python_version"

# Install Poetry
if ! command -v poetry &> /dev/null; then
    echo "Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
fi

# Install dependencies
echo "Installing dependencies..."
poetry install

# Copy .env.example if .env doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please update .env with your API keys"
fi

# Run tests
echo "Running tests..."
poetry run pytest

echo "✅ Setup complete! Run 'poetry run uvicorn src.main:app --reload' to start"
```

---

## Next Steps

After implementing Week 1, continue with:
- Week 2: Security & Testing
- Week 3: Observability & Monitoring  
- Week 4: Documentation & Deployment

See `ENTERPRISE_PROGRESS.md` for complete roadmap.

---

**Last Updated:** December 23, 2025  
**Status:** Ready for Implementation
