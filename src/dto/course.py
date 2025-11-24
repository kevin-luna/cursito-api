from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import date, time


class CourseBase(BaseModel):
    period_id: UUID
    target: str
    name: str
    start_date: date
    end_date: date
    start_time: time
    end_time: time
    course_type: int  # 0 = diplomado, 1 = taller
    modality: int  # 0 = virtual, 1 = presencial
    course_profile: int  # 0 = formacion, 1 = actualización docente
    goal: str
    details: Optional[str] = None


class CourseCreate(CourseBase):
    instructors: List[UUID]  # Required for creating a course


class CourseUpdate(BaseModel):
    period_id: Optional[UUID] = None
    target: Optional[str] = None
    name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    course_type: Optional[int] = None
    modality: Optional[int] = None
    course_profile: Optional[int] = None
    goal: Optional[str] = None
    details: Optional[str] = None
    instructors: Optional[List[UUID]] = None


class Course(CourseBase):
    id: UUID

    class Config:
        from_attributes = True
