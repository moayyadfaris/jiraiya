from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Jiraiya Service"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    ENVIRONMENT: str = Field(default="development", pattern="^(development|staging|production)$")
    LOG_LEVEL: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    
    OPENAI_API_KEY: Optional[str] = Field(default=None, min_length=20)
    API_KEY: Optional[str] = Field(default=None, min_length=8)  # For securing this service
    
    @field_validator("OPENAI_API_KEY")
    @classmethod
    def validate_openai_key(cls, v):
        """Validate OpenAI API key format."""
        if v and not v.startswith("sk-"):
            raise ValueError("OpenAI API key must start with 'sk-'")
        return v
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"
    
    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

settings = Settings()

def validate_settings():
    """Validate critical settings on startup."""
    if settings.is_production:
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required in production")
        if not settings.API_KEY:
            raise ValueError("API_KEY is required in production")
        if len(settings.API_KEY) < 16:
            raise ValueError("API_KEY must be at least 16 characters in production")
