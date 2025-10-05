from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from uuid import UUID
import math
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

    def get_by_worker_paginated(self, db: Session, worker_id: UUID, page: int = 1, limit: int = 100) -> Tuple[List[Instructor], int, int]:
        offset = (page - 1) * limit
        total_count = db.query(Instructor).filter(Instructor.worker_id == worker_id).count()
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        items = db.query(Instructor).filter(Instructor.worker_id == worker_id).offset(offset).limit(limit).all()
        return items, total_pages, total_count

    def get_by_course_paginated(self, db: Session, course_id: UUID, page: int = 1, limit: int = 100) -> Tuple[List[Instructor], int, int]:
        offset = (page - 1) * limit
        total_count = db.query(Instructor).filter(Instructor.course_id == course_id).count()
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        items = db.query(Instructor).filter(Instructor.course_id == course_id).offset(offset).limit(limit).all()
        return items, total_pages, total_count

    def get_courses_by_worker_paginated(self, db: Session, worker_id: UUID, page: int = 1, limit: int = 100) -> Tuple[List[Instructor], int, int]:
        offset = (page - 1) * limit
        total_count = db.query(Instructor).filter(Instructor.worker_id == worker_id).count()
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        items = db.query(Instructor).filter(Instructor.worker_id == worker_id).offset(offset).limit(limit).all()
        return items, total_pages, total_count

    def get_workers_by_course_paginated(self, db: Session, course_id: UUID, page: int = 1, limit: int = 100) -> Tuple[List[Instructor], int, int]:
        offset = (page - 1) * limit
        total_count = db.query(Instructor).filter(Instructor.course_id == course_id).count()
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        items = db.query(Instructor).filter(Instructor.course_id == course_id).offset(offset).limit(limit).all()
        return items, total_pages, total_count
