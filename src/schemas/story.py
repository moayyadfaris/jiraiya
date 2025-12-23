from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

class StoryGenerationRequest(BaseModel):
    keywords: List[str] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Keywords to include in the story (1-10 keywords)"
    )
    genre: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Genre of the story (e.g., fantasy, sci-fi)"
    )
    tone: Optional[str] = Field(
        "neutral",
        description="Tone of the story (e.g., humorous, dark, epic, mysterious)"
    )
    max_length: Optional[int] = Field(
        500,
        ge=100,
        le=2000,
        description="Approximate maximum length in words (100-2000)"
    )
    min_length: Optional[int] = Field(
        None,
        ge=50,
        le=1000,
        description="Approximate minimum length in words (50-1000)"
    )
    
    @field_validator("keywords")
    @classmethod
    def validate_keywords(cls, v):
        """Remove empty strings and duplicates from keywords."""
        keywords = list(set(k.strip() for k in v if k.strip()))
        if not keywords:
            raise ValueError("At least one non-empty keyword is required")
        return keywords
    
    @field_validator("tone")
    @classmethod
    def validate_tone(cls, v):
        """Validate tone is one of the supported options."""
        valid_tones = ["neutral", "humorous", "dark", "epic", "romantic", "mysterious", "dramatic"]
        if v.lower() not in valid_tones:
            raise ValueError(f"Tone must be one of: {', '.join(valid_tones)}")
        return v.lower()
    
    @field_validator("min_length")
    @classmethod
    def validate_length_range(cls, v, info):
        """Ensure min_length is not greater than max_length."""
        if v and "max_length" in info.data and v > info.data["max_length"]:
            raise ValueError("min_length cannot be greater than max_length")
        return v

class StoryGenerationResponse(BaseModel):
    title: str = Field(..., description="Generated title of the story")
    content: str = Field(..., description="The generated story content")
    keywords_used: List[str] = Field(..., description="Keywords that were actually used")

class HealthCheck(BaseModel):
    status: str = "ok"
    version: str
