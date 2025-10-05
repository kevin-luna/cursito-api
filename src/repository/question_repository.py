from typing import List, Optional
from sqlalchemy.orm import Session
from uuid import UUID
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
