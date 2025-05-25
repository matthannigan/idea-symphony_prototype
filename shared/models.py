from pydantic import BaseModel, Field
from typing import List, Optional

class IdeaInput(BaseModel):
    """Initial user input for idea brainstorming"""
    idea_text: str = Field(description="The initial idea description")
    document_content: Optional[str] = Field(None, description="Optional uploaded document content")

class BrainstormingContext(BaseModel):
    """Distilled context document for brainstorming"""
    context: str = Field(description="Distilled context for brainstorming")

class BrainstormQuestion(BaseModel):
    """Individual brainstorming question"""
    short_summary: str = Field(description="Short summary of the question")
    full_description: str = Field(description="Full description of the question")

class BrainstormQuestionGroup(BaseModel):
    """Group of related questions under a heading"""
    heading: str = Field(description="Heading for the group of questions")
    questions: List[BrainstormQuestion] = Field(description="List of questions in this group")

class BrainstormQuestions(BaseModel):
    """Complete set of brainstorming questions"""
    question_groups: List[BrainstormQuestionGroup] = Field(description="Groups of questions")

class BrainstormResponse(BaseModel):
    """Response to a brainstorming question"""
    question: str = Field(description="The question being answered")
    answers: List[str] = Field(description="List of unique responses to the question")

class BrainstormSynthesis(BaseModel):
    """Final synthesis of all brainstorming responses"""
    synthesized_content: str = Field(description="Synthesized content from all responses")
    attributed_content: Optional[str] = Field(None, description="Content with attribution to participants") 