from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import date
import math
from ..model.period import Period
from ..model.course import Course
from ..model.instructor import Instructor
from ..model.enrolling import Enrolling
from ..model.attendance import Attendance
from ..dto.period import PeriodCreate, PeriodUpdate
from .base import BaseRepository


class PeriodRepository(BaseRepository[Period, PeriodCreate, PeriodUpdate]):
    def __init__(self):
        super().__init__(Period)

    def get_by_name(self, db: Session, name: str) -> Optional[Period]:
        return db.query(Period).filter(Period.name == name).first()

    def get_by_date_range(self, db: Session, start_date: date, end_date: date) -> List[Period]:
        return db.query(Period).filter(
            Period.start_date <= end_date,
            Period.end_date >= start_date
        ).all()

    def get_active_periods(self, db: Session, current_date: date) -> List[Period]:
        return db.query(Period).filter(
            Period.start_date <= current_date,
            Period.end_date >= current_date
        ).all()

    def get_by_date_range_paginated(self, db: Session, start_date: date, end_date: date, page: int = 1, limit: int = 100) -> Tuple[List[Period], int, int]:
        offset = (page - 1) * limit
        total_count = db.query(Period).filter(
            Period.start_date <= end_date,
            Period.end_date >= start_date
        ).count()
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        items = db.query(Period).filter(
            Period.start_date <= end_date,
            Period.end_date >= start_date
        ).offset(offset).limit(limit).all()
        return items, total_pages, total_count

    def get_active_periods_paginated(self, db: Session, current_date: date, page: int = 1, limit: int = 100) -> Tuple[List[Period], int, int]:
        offset = (page - 1) * limit
        total_count = db.query(Period).filter(
            Period.start_date <= current_date,
            Period.end_date >= current_date
        ).count()
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        items = db.query(Period).filter(
            Period.start_date <= current_date,
            Period.end_date >= current_date
        ).offset(offset).limit(limit).all()
        return items, total_pages, total_count

    def delete(self, db: Session, id: UUID) -> Optional[Period]:
        """
        Delete a period and all related records in cascade.
        Deletes: courses (and their related instructors, enrollments, attendances)
        """
        # Get the period first
        period = db.query(Period).filter(Period.id == id).first()
        if not period:
            return None

        # Get all courses in this period
        course_ids = db.query(Course.id).filter(Course.period_id == id).all()
        course_ids = [c[0] for c in course_ids]

        # For each course, delete their related records
        for course_id in course_ids:
            # Delete course's instructors
            db.query(Instructor).filter(Instructor.course_id == course_id).delete(synchronize_session=False)
            # Delete course's attendances
            db.query(Attendance).filter(Attendance.course_id == course_id).delete(synchronize_session=False)
            # Delete course's enrollments
            db.query(Enrolling).filter(Enrolling.course_id == course_id).delete(synchronize_session=False)

        # Delete all courses in this period
        db.query(Course).filter(Course.period_id == id).delete(synchronize_session=False)

        # Finally, delete the period itself
        db.delete(period)
        db.commit()

        return period
