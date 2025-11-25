from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import date

from .worker import Worker


class AttendanceBase(BaseModel):
    worker_id: UUID
    course_id: UUID
    date: date


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceUpdate(BaseModel):
    worker_id: Optional[UUID] = None
    course_id: Optional[UUID] = None
    date: Optional[date] = None


class Attendance(AttendanceBase):
    id: UUID

    class Config:
        from_attributes = True


class BulkAttendanceCreate(BaseModel):
    course_id: UUID
    date: date
    worker_ids: List[UUID]


class BulkAttendanceResponse(BaseModel):
    created: int
    skipped: int
    errors: List[str] = []

class AttendanceList(BaseModel):
    items: List[Worker]