from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import date
import math
from ..model.course import Course
from ..model.worker import Worker
from ..dto.course import CourseCreate, CourseUpdate
from .base import BaseRepository
from ..model.instructor import Instructor


class CourseRepository(BaseRepository[Course, CourseCreate, CourseUpdate]):
    def __init__(self):
        super().__init__(Course)

    def create(self, db: Session, course: CourseCreate) -> Course:
        course_obj = Course(**course.model_dump(exclude={'instructors'}))
        db.add(course_obj)
        course_obj.instructors = []
        for instructor in course.instructors:
            instructor_obj = Instructor(worker_id=instructor, course_id=course_obj.id)
            db.add(instructor_obj)
            course_obj.instructors.append(instructor_obj)
        db.commit()
        db.refresh(course_obj)
        return course_obj

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

    def get_by_period_paginated(self, db: Session, period_id: UUID, page: int = 1, limit: int = 100) -> Tuple[List[Course], int, int]:
        offset = (page - 1) * limit
        total_count = db.query(Course).filter(Course.period_id == period_id).count()
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        items = db.query(Course).filter(Course.period_id == period_id).offset(offset).limit(limit).all()
        return items, total_pages, total_count

    def get_by_type_paginated(self, db: Session, course_type: int, page: int = 1, limit: int = 100) -> Tuple[List[Course], int, int]:
        offset = (page - 1) * limit
        total_count = db.query(Course).filter(Course.type == course_type).count()
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        items = db.query(Course).filter(Course.type == course_type).offset(offset).limit(limit).all()
        return items, total_pages, total_count

    def get_by_mode_paginated(self, db: Session, mode: int, page: int = 1, limit: int = 100) -> Tuple[List[Course], int, int]:
        offset = (page - 1) * limit
        total_count = db.query(Course).filter(Course.mode == mode).count()
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        items = db.query(Course).filter(Course.mode == mode).offset(offset).limit(limit).all()
        return items, total_pages, total_count

    def get_by_profile_paginated(self, db: Session, profile: int, page: int = 1, limit: int = 100) -> Tuple[List[Course], int, int]:
        offset = (page - 1) * limit
        total_count = db.query(Course).filter(Course.profile == profile).count()
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        items = db.query(Course).filter(Course.profile == profile).offset(offset).limit(limit).all()
        return items, total_pages, total_count

    def get_by_date_range_paginated(self, db: Session, start_date: date, end_date: date, page: int = 1, limit: int = 100) -> Tuple[List[Course], int, int]:
        offset = (page - 1) * limit
        total_count = db.query(Course).filter(
            Course.start_date <= end_date,
            Course.end_date >= start_date
        ).count()
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        items = db.query(Course).filter(
            Course.start_date <= end_date,
            Course.end_date >= start_date
        ).offset(offset).limit(limit).all()
        return items, total_pages, total_count

    def get_active_courses_paginated(self, db: Session, current_date: date, page: int = 1, limit: int = 100) -> Tuple[List[Course], int, int]:
        offset = (page - 1) * limit
        total_count = db.query(Course).filter(
            Course.start_date <= current_date,
            Course.end_date >= current_date
        ).count()
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        items = db.query(Course).filter(
            Course.start_date <= current_date,
            Course.end_date >= current_date
        ).offset(offset).limit(limit).all()
        return items, total_pages, total_count

    def search_by_name_paginated(self, db: Session, name: str, page: int = 1, limit: int = 100) -> Tuple[List[Course], int, int]:
        offset = (page - 1) * limit
        total_count = db.query(Course).filter(Course.name.ilike(f"%{name}%")).count()
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        items = db.query(Course).filter(Course.name.ilike(f"%{name}%")).offset(offset).limit(limit).all()
        return items, total_pages, total_count

    def get_instructors(self, db: Session, courseId: UUID, page: int = 1, limit: int = 100) -> Tuple[List[Worker], int, int]:
        offset = (page - 1) * limit
        total_count = db.query(Worker).join(Instructor, Instructor.worker_id == Worker.id).filter(Instructor.course_id == courseId).count()
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        items = db.query(Worker).join(Instructor, Instructor.worker_id == Worker.id).filter(Instructor.course_id == courseId).all()
        return items, total_pages, total_count