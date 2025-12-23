class JiraiyaException(Exception):
    """Base exception for Jiraiya Service."""
    pass

class StoryGenerationError(JiraiyaException):
    """Raised when story generation fails."""
    def __init__(self, message: str, detail: str = None):
        super().__init__(message)
        self.detail = detail

class RateLimitExceeded(JiraiyaException):
    """Raised when external API rate limits are hit."""
    pass
