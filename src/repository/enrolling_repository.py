from typing import List, Optional
from sqlalchemy.orm import Session
from uuid import UUID
from decimal import Decimal
from ..model.enrolling import Enrolling
from ..dto.enrolling import EnrollingCreate, EnrollingUpdate
from .base import BaseRepository


class EnrollingRepository(BaseRepository[Enrolling, EnrollingCreate, EnrollingUpdate]):
    def __init__(self):
        super().__init__(Enrolling)

    def get_by_worker(self, db: Session, worker_id: UUID) -> List[Enrolling]:
        return db.query(Enrolling).filter(Enrolling.worker_id == worker_id).all()

    def get_by_course(self, db: Session, course_id: UUID) -> List[Enrolling]:
        return db.query(Enrolling).filter(Enrolling.course_id == course_id).all()

    def get_by_worker_and_course(self, db: Session, worker_id: UUID, course_id: UUID) -> Optional[Enrolling]:
        return db.query(Enrolling).filter(
            Enrolling.worker_id == worker_id,
            Enrolling.course_id == course_id
        ).first()

    def get_by_grade_range(self, db: Session, min_grade: Decimal, max_grade: Decimal) -> List[Enrolling]:
        return db.query(Enrolling).filter(
            Enrolling.final_grade >= min_grade,
            Enrolling.final_grade <= max_grade
        ).all()

    def get_enrolled_workers(self, db: Session, course_id: UUID) -> List[Enrolling]:
        return db.query(Enrolling).filter(Enrolling.course_id == course_id).all()

    def get_worker_enrollments(self, db: Session, worker_id: UUID) -> List[Enrolling]:
        return db.query(Enrolling).filter(Enrolling.worker_id == worker_id).all()
