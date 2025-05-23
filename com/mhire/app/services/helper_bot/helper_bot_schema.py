from pydantic import BaseModel, Field
from typing import Optional, List


class ChatRequest(BaseModel):
    message: str = Field(..., description="The user's message to the chatbot", example="How do I change my profile picture?")


class ChatResponse(BaseModel):
    message: str = Field(..., description="The chatbot's response message")
    navigation_path: Optional[List[str]] = Field(None, description="Navigation path in the site structure if applicable")