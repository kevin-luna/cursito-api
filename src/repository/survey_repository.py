from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from uuid import UUID
import math
from ..model.survey import Survey
from ..dto.survey import SurveyCreate, SurveyUpdate
from .base import BaseRepository


class SurveyRepository(BaseRepository[Survey, SurveyCreate, SurveyUpdate]):
    def __init__(self):
        super().__init__(Survey)

    def get_by_name(self, db: Session, name: str) -> Optional[Survey]:
        return db.query(Survey).filter(Survey.name == name).first()

    def search_by_name(self, db: Session, name: str) -> List[Survey]:
        return db.query(Survey).filter(Survey.name.ilike(f"%{name}%")).all()

    def search_by_name_paginated(self, db: Session, name: str, page: int = 1, limit: int = 100) -> Tuple[List[Survey], int, int]:
        offset = (page - 1) * limit
        total_count = db.query(Survey).filter(Survey.name.ilike(f"%{name}%")).count()
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        items = db.query(Survey).filter(Survey.name.ilike(f"%{name}%")).offset(offset).limit(limit).all()
        return items, total_pages, total_count
