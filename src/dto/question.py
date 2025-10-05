from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class QuestionBase(BaseModel):
    survey_id: UUID
    question: str
    position: int


class QuestionCreate(QuestionBase):
    pass


class QuestionUpdate(BaseModel):
    survey_id: Optional[UUID] = None
    question: Optional[str] = None
    position: Optional[int] = None


class Question(QuestionBase):
    id: UUID

    class Config:
        from_attributes = True
