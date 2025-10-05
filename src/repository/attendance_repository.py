from typing import List, Optional
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import date
from ..model.attendance import Attendance
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
        return db.query(Attendance).filter(Attendance.date == attendance_date).all()

    def get_by_worker_and_date(self, db: Session, worker_id: UUID, attendance_date: date) -> List[Attendance]:
        return db.query(Attendance).filter(
            Attendance.worker_id == worker_id,
            Attendance.date == attendance_date
        ).all()

    def get_by_course_and_date(self, db: Session, course_id: UUID, attendance_date: date) -> List[Attendance]:
        return db.query(Attendance).filter(
            Attendance.course_id == course_id,
            Attendance.date == attendance_date
        ).all()

    def get_by_worker_course_and_date(self, db: Session, worker_id: UUID, course_id: UUID, attendance_date: date) -> Optional[Attendance]:
        return db.query(Attendance).filter(
            Attendance.worker_id == worker_id,
            Attendance.course_id == course_id,
            Attendance.date == attendance_date
        ).first()

    def get_date_range(self, db: Session, start_date: date, end_date: date) -> List[Attendance]:
        return db.query(Attendance).filter(
            Attendance.date >= start_date,
            Attendance.date <= end_date
        ).all()
