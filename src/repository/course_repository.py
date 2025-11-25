from typing import List, Optional, Tuple
from sqlalchemy.orm import Session, joinedload, noload
from uuid import UUID
from datetime import date
import math
from ..model.course import Course
from ..model.worker import Worker
from ..model.enrolling import Enrolling
from ..model.attendance import Attendance
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

    def update(self, db: Session, db_obj: Course, obj_in: CourseUpdate) -> Course:
        """
        Update a course and handle instructors relationship separately.
        """
        # Get the update data and exclude instructors
        obj_data = obj_in.model_dump(exclude_unset=True, exclude={'instructors'})

        # Update regular fields
        for field, value in obj_data.items():
            setattr(db_obj, field, value)

        # Handle instructors if provided
        if obj_in.instructors is not None:
            # Delete existing instructors
            db.query(Instructor).filter(Instructor.course_id == db_obj.id).delete(synchronize_session=False)

            # Add new instructors
            for instructor_id in obj_in.instructors:
                instructor_obj = Instructor(worker_id=instructor_id, course_id=db_obj.id)
                db.add(instructor_obj)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

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

    def get_enrolled_workers(self, db: Session, course_id: UUID, page: int = 1, limit: int = 100) -> Tuple[List[Enrolling],int,int]:
        offset = (page - 1) * limit
        total_count = db.query(Enrolling).filter(Enrolling.course_id == course_id).count()
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        items = db.query(Enrolling).options(joinedload(Enrolling.worker), noload(Enrolling.course)).filter(Enrolling.course_id == course_id).offset(offset).limit(limit).all()
        return items, total_pages, total_count

    def delete(self, db: Session, id: UUID) -> Optional[Course]:
        """
        Delete a course and all related records (instructors, enrollments, attendances) in cascade.
        """
        # Get the course first
        course = db.query(Course).filter(Course.id == id).first()
        if not course:
            return None

        # Delete related instructors
        db.query(Instructor).filter(Instructor.course_id == id).delete(synchronize_session=False)

        # Delete related attendances
        db.query(Attendance).filter(Attendance.course_id == id).delete(synchronize_session=False)

        # Delete related enrollments
        db.query(Enrolling).filter(Enrolling.course_id == id).delete(synchronize_session=False)

        # Finally, delete the course itself
        db.delete(course)
        db.commit()

        return course