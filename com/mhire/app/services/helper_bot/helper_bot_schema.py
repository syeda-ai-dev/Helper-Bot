from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class UserType(str, Enum):
    CUSTOMER = "customer"
    ENGINEER = "engineer"

class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="User query, max 500 characters"
    )
    user_type: UserType = Field(
        ...,
        description="Type of user making the request"
    )

class ChatResponse(BaseModel):
    message: str = Field(
        ...,
        description="Response message"
    )
    source: str = Field(
        "faq",
        description="Source of the response: 'faq' or 'gpt'"
    )
    confidence_score: Optional[float] = Field(
        None,
        description="Confidence score of the response",
        ge=0.0,
        le=1.0
    )

class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error code or identifier")
    message: str = Field(..., description="Detailed error message")
    status_code: int = Field(..., description="HTTP status code")