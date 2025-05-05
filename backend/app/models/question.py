from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, UUID4

class QuestionBase(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)


class QuestionCreate(QuestionBase):
    pass


class QuestionResponse(QuestionBase):
    id: UUID4
    user_id: UUID4
    answer: Optional[str] = None
    status: str = Field(..., pattern="^(pendente|respondida|erro)$")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 