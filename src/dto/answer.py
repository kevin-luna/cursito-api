from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID


class AnswerBase(BaseModel):
    worker_id: UUID
    course_id: UUID
    question_id: UUID
    value: str


class AnswerCreate(AnswerBase):
    pass


class AnswerUpdate(BaseModel):
    worker_id: Optional[UUID] = None
    course_id: Optional[UUID] = None
    question_id: Optional[UUID] = None
    value: Optional[str] = None


class Answer(AnswerBase):
    id: UUID

    class Config:
        from_attributes = True


class QuestionAnswerItem(BaseModel):
    """Single question answer without worker_id and course_id"""
    question_id: UUID
    value: str


class SurveyAnswersSubmit(BaseModel):
    """Request to submit answers for a survey"""
    worker_id: UUID
    course_id: UUID
    answers: List[QuestionAnswerItem]
