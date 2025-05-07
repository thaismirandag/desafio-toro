from datetime import datetime

from pydantic import BaseModel, Field


class QuestionBase(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)


class QuestionCreate(QuestionBase):
    pass


class QuestionResponse(QuestionBase):
    id: str
    session_id: str
    answer: str | None = None
    status: str = Field(..., pattern="^(pendente|respondida|erro)$")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 