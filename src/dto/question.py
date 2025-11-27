from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class QuestionBase(BaseModel):
    survey_id: UUID
    question: str
    question_order: int


class QuestionCreate(QuestionBase):
    pass


class QuestionUpdate(BaseModel):
    survey_id: Optional[UUID] = None
    question: Optional[str] = None
    question_order: Optional[int] = None


class Question(QuestionBase):
    id: UUID

    class Config:
        from_attributes = True
