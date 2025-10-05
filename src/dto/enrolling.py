from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from decimal import Decimal


class EnrollingBase(BaseModel):
    worker_id: UUID
    course_id: UUID
    final_grade: Optional[Decimal] = None


class EnrollingCreate(EnrollingBase):
    pass


class EnrollingUpdate(BaseModel):
    worker_id: Optional[UUID] = None
    course_id: Optional[UUID] = None
    final_grade: Optional[Decimal] = None


class Enrolling(EnrollingBase):
    id: UUID

    class Config:
        from_attributes = True
