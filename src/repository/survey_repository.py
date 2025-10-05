from typing import List, Optional
from sqlalchemy.orm import Session
from uuid import UUID
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
