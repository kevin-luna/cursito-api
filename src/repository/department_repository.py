from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from uuid import UUID
import math
from ..model.department import Department
from ..model.worker import Worker
from ..model.instructor import Instructor
from ..model.enrolling import Enrolling
from ..model.attendance import Attendance
from ..model.answer import Answer
from ..dto.department import DepartmentCreate, DepartmentUpdate
from .base import BaseRepository


class DepartmentRepository(BaseRepository[Department, DepartmentCreate, DepartmentUpdate]):
    def __init__(self):
        super().__init__(Department)

    def get_by_name(self, db: Session, name: str) -> Optional[Department]:
        return db.query(Department).filter(Department.name == name).first()

    def search_by_name(self, db: Session, name: str) -> List[Department]:
        return db.query(Department).filter(Department.name.ilike(f"%{name}%")).all()

    def search_by_name_paginated(self, db: Session, name: str, page: int = 1, limit: int = 100) -> Tuple[List[Department], int, int]:
        offset = (page - 1) * limit
        total_count = db.query(Department).filter(Department.name.ilike(f"%{name}%")).count()
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        items = db.query(Department).filter(Department.name.ilike(f"%{name}%")).offset(offset).limit(limit).all()
        return items, total_pages, total_count

    def delete(self, db: Session, id: UUID) -> Optional[Department]:
        """
        Delete a department and all related records in cascade.
        Deletes: workers (and their related instructors, enrollments, attendances, answers)
        """
        # Get the department first
        department = db.query(Department).filter(Department.id == id).first()
        if not department:
            return None

        # Get all workers in this department
        worker_ids = db.query(Worker.id).filter(Worker.department_id == id).all()
        worker_ids = [w[0] for w in worker_ids]

        # For each worker, delete their related records
        for worker_id in worker_ids:
            # Delete worker's answers
            db.query(Answer).filter(Answer.worker_id == worker_id).delete(synchronize_session=False)
            # Delete worker's attendances
            db.query(Attendance).filter(Attendance.worker_id == worker_id).delete(synchronize_session=False)
            # Delete worker's enrollments
            db.query(Enrolling).filter(Enrolling.worker_id == worker_id).delete(synchronize_session=False)
            # Delete worker's instructor records
            db.query(Instructor).filter(Instructor.worker_id == worker_id).delete(synchronize_session=False)

        # Delete all workers in this department
        db.query(Worker).filter(Worker.department_id == id).delete(synchronize_session=False)

        # Finally, delete the department itself
        db.delete(department)
        db.commit()

        return department
