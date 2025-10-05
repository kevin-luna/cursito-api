from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class InstructorBase(BaseModel):
    worker_id: UUID
    course_id: UUID


class InstructorCreate(InstructorBase):
    pass


class InstructorUpdate(BaseModel):
    worker_id: Optional[UUID] = None
    course_id: Optional[UUID] = None


class Instructor(InstructorBase):
    id: UUID

    class Config:
        from_attributes = True
