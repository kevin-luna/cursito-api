from typing import List, Optional, Tuple
from sqlalchemy.orm import Session, joinedload, noload
from sqlalchemy import exists
from uuid import UUID
import math
from ..model.worker import Worker
from ..model.instructor import Instructor
from ..model.enrolling import Enrolling
from ..model.course import Course
from ..dto.worker import WorkerCreate, WorkerUpdate
from .base import BaseRepository
from datetime import date, time


class WorkerRepository(BaseRepository[Worker, WorkerCreate, WorkerUpdate]):
    def __init__(self):
        super().__init__(Worker)

    def get_by_id(self, db: Session, id: UUID):
        return db.query(Worker).get(id)

    def get_by_email(self, db: Session, email: str) -> Optional[Worker]:
        return db.query(Worker).filter(Worker.email == email).first()

    def get_by_rfc(self, db: Session, rfc: str) -> Optional[Worker]:
        return db.query(Worker).filter(Worker.rfc == rfc).first()

    def get_by_curp(self, db: Session, curp: str) -> Optional[Worker]:
        return db.query(Worker).filter(Worker.curp == curp).first()

    def get_by_department(self, db: Session, department_id: UUID) -> List[Worker]:
        return db.query(Worker).filter(Worker.department_id == department_id).all()

    def get_by_position(self, db: Session, position: int) -> List[Worker]:
        return db.query(Worker).filter(Worker.position == position).all()

    def search_by_name(self, db: Session, name: str) -> List[Worker]:
        return db.query(Worker).filter(
            Worker.name.ilike(f"%{name}%") |
            Worker.father_surname.ilike(f"%{name}%") |
            Worker.mother_surname.ilike(f"%{name}%")
        ).all()

    def check_worker_list(self, db: Session, worker_list: List[UUID]) -> bool:
        return db.query(Worker).filter(Worker.id.in_(worker_list)).count() == len(worker_list)

    def get_by_availability_paginated(self, db: Session, start_date: date, end_date: date, start_time: time, end_time: time, page: int = 1, limit: int = 100) -> Tuple[List[Worker], int, int]:
        offset = (page - 1) * limit
        subquery = (
            db.query(Instructor)
            .join(Course)
            .filter(
                Instructor.worker_id == Worker.id,
                Course.start_date < end_date,
                Course.end_date > start_date,
                Course.start_time < end_time,
                Course.end_time > start_time
            )
        )
        total_count = db.query(Worker).filter(~exists(subquery)).count()
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        items = db.query(Worker).filter(~exists(subquery)).offset(offset).limit(limit).all()
        return items, total_pages, total_count

    def get_by_department_paginated(self, db: Session, department_id: UUID, page: int = 1, limit: int = 100) -> Tuple[List[Worker], int, int]:
        offset = (page - 1) * limit
        total_count = db.query(Worker).filter(Worker.department_id == department_id).count()
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        items = db.query(Worker).filter(Worker.department_id == department_id).offset(offset).limit(limit).all()
        return items, total_pages, total_count

    def get_by_position_paginated(self, db: Session, position: int, page: int = 1, limit: int = 100) -> Tuple[List[Worker], int, int]:
        offset = (page - 1) * limit
        total_count = db.query(Worker).filter(Worker.position == position).count()
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        items = db.query(Worker).filter(Worker.position == position).offset(offset).limit(limit).all()
        return items, total_pages, total_count

    def search_by_name_paginated(self, db: Session, name: str, page: int = 1, limit: int = 100) -> Tuple[List[Worker], int, int]:
        offset = (page - 1) * limit
        total_count = db.query(Worker).filter(
            Worker.name.ilike(f"%{name}%") |
            Worker.father_surname.ilike(f"%{name}%") |
            Worker.mother_surname.ilike(f"%{name}%")
        ).count()
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        items = db.query(Worker).filter(
            Worker.name.ilike(f"%{name}%") |
            Worker.father_surname.ilike(f"%{name}%") |
            Worker.mother_surname.ilike(f"%{name}%")
        ).offset(offset).limit(limit).all()
        return items, total_pages, total_count

    def get_teaching_courses(self, db: Session, instructor: UUID, page: int = 1, limit: int = 100) -> Tuple[List[Course],int,int]:
        offset = (page - 1) * limit
        total_count = db.query(Course).join(Instructor, Course.id == Instructor.course_id).filter(Instructor.worker_id == instructor).count()
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        items = db.query(Course).join(Instructor).filter(Course.id == Instructor.course_id).filter(Instructor.worker_id == instructor).all()
        return items, total_pages, total_count
    
    def get_enrolled_courses(self, db: Session, instructor: UUID, page: int = 1, limit: int = 100) -> Tuple[List[Course],int,int]:
        offset = (page - 1) * limit
        total_count = db.query(Course).join(Enrolling, Course.id == Enrolling.course_id).filter(Enrolling.worker_id == instructor).count()
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        items = db.query(Course).join(Enrolling, Course.id == Enrolling.course_id).filter(Enrolling.worker_id == instructor).all()
        return items, total_pages, total_count
    
    def get_enrollments(self, db: Session, worker_id: UUID, page: int = 1, limit: int = 100) -> Tuple[List[Enrolling], int, int]:
        offset = (page - 1) * limit
        total_count = db.query(Enrolling).filter(Enrolling.worker_id == worker_id).count()
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        items = db.query(Enrolling).options(joinedload(Enrolling.course), noload(Enrolling.worker)).filter(Enrolling.worker_id == worker_id).offset(offset).limit(limit).all()
        return items, total_pages, total_count

    def get_available_courses(self, db: Session, worker_id: UUID, page: int = 1, limit: int = 100) -> Tuple[List[Course], int, int]:
        """
        Get courses available for a worker to enroll in.
        Filters out:
        - Courses where the worker is an instructor
        - Courses that have already started (start_date <= today)
        - Courses where the worker is already enrolled
        """
        offset = (page - 1) * limit
        today = date.today()

        # Subquery for courses where worker is an instructor
        instructor_subquery = db.query(Instructor.course_id).filter(
            Instructor.worker_id == worker_id
        )

        # Subquery for courses where worker is already enrolled
        enrolled_subquery = db.query(Enrolling.course_id).filter(
            Enrolling.worker_id == worker_id
        )

        # Main query: courses with start_date > today, worker is not instructor, and worker is not enrolled
        base_query = db.query(Course).filter(
            Course.start_date > today,
            ~Course.id.in_(instructor_subquery),
            ~Course.id.in_(enrolled_subquery)
        )

        total_count = base_query.count()
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        items = base_query.offset(offset).limit(limit).all()

        return items, total_pages, total_count