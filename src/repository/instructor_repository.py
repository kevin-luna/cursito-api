from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from uuid import UUID
import math
from ..model.instructor import Instructor
from ..model.course import Course
from ..dto.instructor import InstructorCreate, InstructorUpdate
from .base import BaseRepository
from datetime import date, time

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

    def check_availability(self, db: Session, worker_id: UUID, start_date: date, end_date: date, start_time: time, end_time: time) -> bool:
        return db.query(Instructor).join(Course).filter(Instructor.worker_id == worker_id, Course.start_date.between(start_date, end_date), Course.end_date.between(start_date, end_date), Course.start_time.between(start_time, end_time), Course.end_time.between(start_time, end_time)).count() == 0

    def check_availability(self, db: Session, worker_list: List[UUID], start_date: date, end_date: date, start_time: time, end_time: time) -> bool:
        return db.query(Instructor).join(Course).filter(Instructor.worker_id.in_(worker_list), Course.start_date.between(start_date, end_date), Course.end_date.between(start_date, end_date), Course.start_time.between(start_time, end_time), Course.end_time.between(start_time, end_time)).count() == 0

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
