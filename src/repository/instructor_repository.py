from typing import List, Optional, Tuple
from sqlalchemy import delete
from sqlalchemy.orm import Session
from uuid import UUID
import math
from ..model.instructor import Instructor
from ..model.course import Course
from ..model.worker import Worker
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
    
    def check_instructor_list(self, db: Session, instructors: List[UUID]) -> bool:
        unique_instructor_ids = set(instructors)
        expected_count = len(unique_instructor_ids)
        found_count = db.query(Worker).filter(
            Worker.id.in_(unique_instructor_ids)
        ).count()
        return expected_count == found_count

    def check_availability(self, db: Session, worker_list: List[UUID], start_date: date, end_date: date, start_time: time, end_time: time, exclude_course_id: Optional[UUID] = None) -> bool:
        """
        Check if workers are available (no schedule conflicts) for the given date and time range.
        Returns True if all workers are available, False if there's a conflict.

        A conflict occurs when:
        - Date ranges overlap: new_start <= existing_end AND new_end >= existing_start
        - AND time ranges overlap: new_start_time < existing_end_time AND new_end_time > existing_start_time
        """
        query = db.query(Instructor).join(Course).filter(
            Instructor.worker_id.in_(worker_list),
            # Date overlap: new course dates overlap with existing course dates
            Course.start_date <= end_date,
            Course.end_date >= start_date,
            # Time overlap: new course times overlap with existing course times
            Course.start_time < end_time,
            Course.end_time > start_time
        )

        # Exclude the current course when updating
        if exclude_course_id is not None:
            query = query.filter(Course.id != exclude_course_id)

        # If count > 0, there's a conflict (not available)
        # If count == 0, no conflicts (available)
        return query.count() == 0

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
