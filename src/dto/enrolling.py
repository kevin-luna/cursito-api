from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from .course import Course
from .worker import Worker


class EnrollingBase(BaseModel):
    worker: Optional[Worker]
    course: Optional[Course]
    final_grade: Optional[Decimal] = None


class EnrollingCreate(BaseModel):
    worker_id: UUID
    course_id: UUID
    final_grade: Optional[Decimal] = None


class EnrollingUpdate(BaseModel):
    worker_id: Optional[UUID] = None
    course_id: Optional[UUID] = None
    final_grade: Optional[Decimal] = None


class Enrolling(EnrollingBase):
    id: UUID

    class Config:
        from_attributes = True


class WorkerGrade(BaseModel):
    worker_id: UUID
    final_grade: Decimal


class BulkGradeUpdate(BaseModel):
    course_id: UUID
    grades: List[WorkerGrade]


class BulkGradeResponse(BaseModel):
    updated: int
    skipped: int
    errors: List[str] = []
