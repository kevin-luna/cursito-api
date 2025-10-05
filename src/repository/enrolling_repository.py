from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from uuid import UUID
from decimal import Decimal
import math
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

    def get_by_worker_paginated(self, db: Session, worker_id: UUID, page: int = 1, limit: int = 100) -> Tuple[List[Enrolling], int, int]:
        offset = (page - 1) * limit
        total_count = db.query(Enrolling).filter(Enrolling.worker_id == worker_id).count()
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        items = db.query(Enrolling).filter(Enrolling.worker_id == worker_id).offset(offset).limit(limit).all()
        return items, total_pages, total_count

    def get_by_course_paginated(self, db: Session, course_id: UUID, page: int = 1, limit: int = 100) -> Tuple[List[Enrolling], int, int]:
        offset = (page - 1) * limit
        total_count = db.query(Enrolling).filter(Enrolling.course_id == course_id).count()
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        items = db.query(Enrolling).filter(Enrolling.course_id == course_id).offset(offset).limit(limit).all()
        return items, total_pages, total_count

    def get_by_grade_range_paginated(self, db: Session, min_grade: Decimal, max_grade: Decimal, page: int = 1, limit: int = 100) -> Tuple[List[Enrolling], int, int]:
        offset = (page - 1) * limit
        total_count = db.query(Enrolling).filter(
            Enrolling.final_grade >= min_grade,
            Enrolling.final_grade <= max_grade
        ).count()
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        items = db.query(Enrolling).filter(
            Enrolling.final_grade >= min_grade,
            Enrolling.final_grade <= max_grade
        ).offset(offset).limit(limit).all()
        return items, total_pages, total_count

    def get_enrolled_workers_paginated(self, db: Session, course_id: UUID, page: int = 1, limit: int = 100) -> Tuple[List[Enrolling], int, int]:
        offset = (page - 1) * limit
        total_count = db.query(Enrolling).filter(Enrolling.course_id == course_id).count()
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        items = db.query(Enrolling).filter(Enrolling.course_id == course_id).offset(offset).limit(limit).all()
        return items, total_pages, total_count

    def get_worker_enrollments_paginated(self, db: Session, worker_id: UUID, page: int = 1, limit: int = 100) -> Tuple[List[Enrolling], int, int]:
        offset = (page - 1) * limit
        total_count = db.query(Enrolling).filter(Enrolling.worker_id == worker_id).count()
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        items = db.query(Enrolling).filter(Enrolling.worker_id == worker_id).offset(offset).limit(limit).all()
        return items, total_pages, total_count
