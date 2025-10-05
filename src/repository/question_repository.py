from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from uuid import UUID
import math
from ..model.question import Question
from ..dto.question import QuestionCreate, QuestionUpdate
from .base import BaseRepository


class QuestionRepository(BaseRepository[Question, QuestionCreate, QuestionUpdate]):
    def __init__(self):
        super().__init__(Question)

    def get_by_survey(self, db: Session, survey_id: UUID) -> List[Question]:
        return db.query(Question).filter(Question.survey_id == survey_id).order_by(Question.position).all()

    def get_by_position(self, db: Session, survey_id: UUID, position: int) -> Optional[Question]:
        return db.query(Question).filter(
            Question.survey_id == survey_id,
            Question.position == position
        ).first()

    def search_by_text(self, db: Session, text: str) -> List[Question]:
        return db.query(Question).filter(Question.question.ilike(f"%{text}%")).all()

    def get_by_survey_paginated(self, db: Session, survey_id: UUID, page: int = 1, limit: int = 100) -> Tuple[List[Question], int, int]:
        offset = (page - 1) * limit
        total_count = db.query(Question).filter(Question.survey_id == survey_id).count()
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        items = db.query(Question).filter(Question.survey_id == survey_id).order_by(Question.position).offset(offset).limit(limit).all()
        return items, total_pages, total_count

    def search_by_text_paginated(self, db: Session, text: str, page: int = 1, limit: int = 100) -> Tuple[List[Question], int, int]:
        offset = (page - 1) * limit
        total_count = db.query(Question).filter(Question.question.ilike(f"%{text}%")).count()
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        items = db.query(Question).filter(Question.question.ilike(f"%{text}%")).offset(offset).limit(limit).all()
        return items, total_pages, total_count
