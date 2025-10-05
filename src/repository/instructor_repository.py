from typing import List, Optional
from sqlalchemy.orm import Session
from uuid import UUID
from ..model.instructor import Instructor
from ..dto.instructor import InstructorCreate, InstructorUpdate
from .base import BaseRepository


class InstructorRepository(BaseRepository[Instructor, InstructorCreate, InstructorUpdate]):
    def __init__(self):
        super().__init__(Instructor)

    def get_by_worker(self, db: Session, worker_id: UUID) -> List[Instructor]:
        return db.query(Instructor).filter(Instructor.worker_id == worker_id).all()

    def get_by_course(self, db: Session, course_id: UUID) -> List[Instructor]:
        return db.query(Instructor).filter(Instructor.course_id == course_id).all()

    def get_by_worker_and_course(self, db: Session, worker_id: UUID, course_id: UUID) -> Optional[Instructor]:
        return db.query(Instructor).filter(
            Instructor.worker_id == worker_id,
            Instructor.course_id == course_id
        ).first()

    def get_courses_by_worker(self, db: Session, worker_id: UUID) -> List[Instructor]:
        return db.query(Instructor).filter(Instructor.worker_id == worker_id).all()

    def get_workers_by_course(self, db: Session, course_id: UUID) -> List[Instructor]:
        return db.query(Instructor).filter(Instructor.course_id == course_id).all()
