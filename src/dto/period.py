from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import date


class PeriodBase(BaseModel):
    name: str
    start_date: date
    end_date: date


class PeriodCreate(PeriodBase):
    pass


class PeriodUpdate(BaseModel):
    name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class Period(PeriodBase):
    id: UUID

    class Config:
        from_attributes = True
