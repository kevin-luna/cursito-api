from typing import List, Optional
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import date
from ..model.course import Course
from ..dto.course import CourseCreate, CourseUpdate
from .base import BaseRepository


class CourseRepository(BaseRepository[Course, CourseCreate, CourseUpdate]):
    def __init__(self):
        super().__init__(Course)

    def get_by_period(self, db: Session, period_id: UUID) -> List[Course]:
        return db.query(Course).filter(Course.period_id == period_id).all()

    def get_by_type(self, db: Session, course_type: int) -> List[Course]:
        return db.query(Course).filter(Course.type == course_type).all()

    def get_by_mode(self, db: Session, mode: int) -> List[Course]:
        return db.query(Course).filter(Course.mode == mode).all()

    def get_by_profile(self, db: Session, profile: int) -> List[Course]:
        return db.query(Course).filter(Course.profile == profile).all()

    def get_by_date_range(self, db: Session, start_date: date, end_date: date) -> List[Course]:
        return db.query(Course).filter(
            Course.start_date <= end_date,
            Course.end_date >= start_date
        ).all()

    def get_active_courses(self, db: Session, current_date: date) -> List[Course]:
        return db.query(Course).filter(
            Course.start_date <= current_date,
            Course.end_date >= current_date
        ).all()

    def search_by_name(self, db: Session, name: str) -> List[Course]:
        return db.query(Course).filter(Course.name.ilike(f"%{name}%")).all()
