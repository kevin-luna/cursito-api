from typing import List, Optional, Tuple
from sqlalchemy.orm import Session, joinedload
from uuid import UUID
from datetime import date
import math
from ..model.attendance import Attendance
from ..model.worker import Worker
from ..dto.attendance import AttendanceCreate, AttendanceUpdate
from .base import BaseRepository


class AttendanceRepository(BaseRepository[Attendance, AttendanceCreate, AttendanceUpdate]):
    def __init__(self):
        super().__init__(Attendance)

    def get_by_worker(self, db: Session, worker_id: UUID) -> List[Attendance]:
        return db.query(Attendance).filter(Attendance.worker_id == worker_id).all()

    def get_by_course(self, db: Session, course_id: UUID) -> List[Attendance]:
        return db.query(Attendance).filter(Attendance.course_id == course_id).all()

    def get_by_worker_and_course(self, db: Session, worker_id: UUID, course_id: UUID) -> List[Attendance]:
        return db.query(Attendance).filter(
            Attendance.worker_id == worker_id,
            Attendance.course_id == course_id
        ).all()

    def get_by_date(self, db: Session, attendance_date: date) -> List[Attendance]:
        return db.query(Attendance).filter(Attendance.attendance_date == attendance_date).all()

    def get_by_worker_and_date(self, db: Session, worker_id: UUID, attendance_date: date) -> List[Attendance]:
        return db.query(Attendance).filter(
            Attendance.worker_id == worker_id,
            Attendance.attendance_date == attendance_date
        ).all()

    def get_by_course_and_date(self, db: Session, course_id: UUID, attendance_date: date) -> List[Worker]:
        return db.query(Worker).join(Attendance, Attendance.worker_id == Worker.id).filter(
            Attendance.course_id == course_id,
            Attendance.attendance_date == attendance_date
        ).all()

    def get_by_worker_course_and_date(self, db: Session, worker_id: UUID, course_id: UUID, attendance_date: date) -> Optional[Attendance]:
        return db.query(Attendance).filter(
            Attendance.worker_id == worker_id,
            Attendance.course_id == course_id,
            Attendance.attendance_date == attendance_date
        ).first()

    def get_date_range(self, db: Session, start_date: date, end_date: date) -> List[Attendance]:
        return db.query(Attendance).filter(
            Attendance.attendance_date >= start_date,
            Attendance.attendance_date <= end_date
        ).all()

    def get_by_worker_paginated(self, db: Session, worker_id: UUID, page: int = 1, limit: int = 100) -> Tuple[List[Attendance], int, int]:
        offset = (page - 1) * limit
        total_count = db.query(Attendance).filter(Attendance.worker_id == worker_id).count()
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        items = db.query(Attendance).filter(Attendance.worker_id == worker_id).offset(offset).limit(limit).all()
        return items, total_pages, total_count

    def get_by_course_paginated(self, db: Session, course_id: UUID, page: int = 1, limit: int = 100) -> Tuple[List[Attendance], int, int]:
        offset = (page - 1) * limit
        total_count = db.query(Attendance).filter(Attendance.course_id == course_id).count()
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        items = db.query(Attendance).filter(Attendance.course_id == course_id).offset(offset).limit(limit).all()
        return items, total_pages, total_count

    def get_by_worker_and_course_paginated(self, db: Session, worker_id: UUID, course_id: UUID, page: int = 1, limit: int = 100) -> Tuple[List[Attendance], int, int]:
        offset = (page - 1) * limit
        total_count = db.query(Attendance).filter(
            Attendance.worker_id == worker_id,
            Attendance.course_id == course_id
        ).count()
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        items = db.query(Attendance).filter(
            Attendance.worker_id == worker_id,
            Attendance.course_id == course_id
        ).offset(offset).limit(limit).all()
        return items, total_pages, total_count

    def get_by_date_paginated(self, db: Session, attendance_date: date, page: int = 1, limit: int = 100) -> Tuple[List[Attendance], int, int]:
        offset = (page - 1) * limit
        total_count = db.query(Attendance).filter(Attendance.attendance_date == attendance_date).count()
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        items = db.query(Attendance).filter(Attendance.attendance_date == attendance_date).offset(offset).limit(limit).all()
        return items, total_pages, total_count

    def get_date_range_paginated(self, db: Session, start_date: date, end_date: date, page: int = 1, limit: int = 100) -> Tuple[List[Attendance], int, int]:
        offset = (page - 1) * limit
        total_count = db.query(Attendance).filter(
            Attendance.attendance_date >= start_date,
            Attendance.attendance_date <= end_date
        ).count()
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        items = db.query(Attendance).filter(
            Attendance.attendance_date >= start_date,
            Attendance.attendance_date <= end_date
        ).offset(offset).limit(limit).all()
        return items, total_pages, total_count
