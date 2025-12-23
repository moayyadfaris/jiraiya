from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

class StoryPrompts:
    """
    Centralized repository of prompt templates for Jiraiya.
    """
    
    STANDARD_STORYTELLER = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(
            "You are Jiraiya, a master storyteller and legendary author. "
            "Write creative, engaging stories based on the user's request. "
            "Adhere to the requested genre, tone, and constraints."
        ),
        HumanMessagePromptTemplate.from_template(
            "Write a story with the following details:\n"
            "- Keywords: {keywords}\n"
            "- Genre: {genre}\n"
            "- Tone: {tone}\n"
            "- Target Length: approx {max_length} words\n"
            "- Minimum Length: {min_length} words\n\n"
            "Story Title and Content:"
        ),
    ])

prompts = StoryPrompts()
