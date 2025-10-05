from typing import List, Optional
from sqlalchemy.orm import Session
from uuid import UUID
from ..model.answer import Answer
from ..dto.answer import AnswerCreate, AnswerUpdate
from .base import BaseRepository


class AnswerRepository(BaseRepository[Answer, AnswerCreate, AnswerUpdate]):
    def __init__(self):
        super().__init__(Answer)

    def get_by_worker(self, db: Session, worker_id: UUID) -> List[Answer]:
        return db.query(Answer).filter(Answer.worker_id == worker_id).all()

    def get_by_course(self, db: Session, course_id: UUID) -> List[Answer]:
        return db.query(Answer).filter(Answer.course_id == course_id).all()

    def get_by_question(self, db: Session, question_id: UUID) -> List[Answer]:
        return db.query(Answer).filter(Answer.question_id == question_id).all()

    def get_by_worker_and_course(self, db: Session, worker_id: UUID, course_id: UUID) -> List[Answer]:
        return db.query(Answer).filter(
            Answer.worker_id == worker_id,
            Answer.course_id == course_id
        ).all()

    def get_by_worker_course_and_question(self, db: Session, worker_id: UUID, course_id: UUID, question_id: UUID) -> Optional[Answer]:
        return db.query(Answer).filter(
            Answer.worker_id == worker_id,
            Answer.course_id == course_id,
            Answer.question_id == question_id
        ).first()

    def get_by_survey(self, db: Session, survey_id: UUID) -> List[Answer]:
        return db.query(Answer).join(Answer.question).filter(
            Answer.question.has(survey_id=survey_id)
        ).all()

    def search_by_value(self, db: Session, value: str) -> List[Answer]:
        return db.query(Answer).filter(Answer.value.ilike(f"%{value}%")).all()
