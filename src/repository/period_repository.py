from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import date
import math
from ..model.period import Period
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
