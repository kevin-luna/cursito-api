from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import date


class SurveyBase(BaseModel):
    name: str


class SurveyCreate(SurveyBase):
    pass


class SurveyUpdate(BaseModel):
    name: Optional[str] = None


class Survey(SurveyBase):
    id: UUID
    created_at: date

    class Config:
        from_attributes = True
