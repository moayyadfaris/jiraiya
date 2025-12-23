from unittest.mock import AsyncMock, MagicMock

# Mock response for OpenAI
MOCK_OPENAI_RESPONSE = "Title: Test Story\nOnce upon a time in a test environment..."

def mock_langchain_chain():
    """
    Returns a mock chain that behaves like prompts | llm | output_parser
    """
    mock_chain = AsyncMock()
    mock_chain.ainvoke.return_value = MOCK_OPENAI_RESPONSE
    return mock_chain
