from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from src.schemas.story import StoryGenerationRequest, StoryGenerationResponse
from src.core.config import settings
from src.core.prompts import prompts
from src.core.exceptions import StoryGenerationError
import random
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from openai import RateLimitError, APIError

logger = structlog.get_logger(__name__)

class StoryGeneratorService:
    def __init__(self):
        self.llm = None
        if settings.OPENAI_API_KEY:
            self.llm = ChatOpenAI(
                api_key=settings.OPENAI_API_KEY,
                model="gpt-4o",
                temperature=0.7
            )
    
    async def generate_story(self, request: StoryGenerationRequest) -> StoryGenerationResponse:
        """
        Generates a story using OpenAI (if key is present) or falls back to mock.
        """
        if self.llm:
            return await self._generate_with_ai(request)
        
        logger.warning("openai_not_configured", message="Using mock generator")
        return self._generate_mock(request)

    @retry(
        retry=retry_if_exception_type((RateLimitError, APIError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        before_sleep=lambda retry_state: logger.warning(
            "retrying_ai_request",
            attempt=retry_state.attempt_number,
            wait_seconds=retry_state.next_action.sleep
        )
    )
    async def _generate_with_ai(self, request: StoryGenerationRequest) -> StoryGenerationResponse:
        try:
            chain = prompts.STANDARD_STORYTELLER | self.llm | StrOutputParser()
            
            # Prepare inputs
            inputs = {
                "keywords": ", ".join(request.keywords),
                "genre": request.genre,
                "tone": request.tone,
                "max_length": request.max_length,
                "min_length": request.min_length or "Not specified",
            }
            
            logger.debug("invoking_ai_chain", inputs=inputs)
            full_response = await chain.ainvoke(inputs)
            
            # Simple parsing strategy: Assume first line is title if separated by newline
            # Ideally, we would ask the LLM to output JSON, but for now we parse text
            lines = full_response.strip().split("\n", 1)
            if len(lines) == 2:
                title = lines[0].strip().replace("Title:", "").replace("title:", "").strip()
                content = lines[1].strip()
            else:
                title = "Untitled Story"
                content = full_response
            
            logger.info(
                "ai_story_generated",
                title=title,
                content_length=len(content),
                keywords_count=len(request.keywords)
            )
                
            return StoryGenerationResponse(
                title=title,
                content=content,
                keywords_used=request.keywords
            )
        except (RateLimitError, APIError) as e:
            # Let retry handle these
            logger.warning("ai_service_error", error=str(e), error_type=type(e).__name__)
            raise
        except Exception as e:
            logger.error("story_generation_failed", error=str(e), error_type=type(e).__name__)
            raise StoryGenerationError(
                f"Failed to generate story: {str(e)}",
                detail=type(e).__name__
            )

    def _generate_mock(self, request: StoryGenerationRequest) -> StoryGenerationResponse:
        """Generate a mock story for testing without OpenAI."""
        titles = [
            f"The Tale of the {request.genre.capitalize()}",
            f"Journey to the {request.keywords[0].capitalize()}"
        ]
        
        mock_content = (
            f"Once upon a time in a {request.genre} world, there was a {request.keywords[0]}. "
            f"It was a {request.tone} day. The {request.keywords[0]} decided to go on an adventure. "
            f"Min length requested was {request.min_length}. "
            "And they lived happily ever after."
        )
        
        logger.info("mock_story_generated", keywords=request.keywords, genre=request.genre)

        return StoryGenerationResponse(
            title=random.choice(titles),
            content=mock_content,
            keywords_used=request.keywords
        )

story_service = StoryGeneratorService()
