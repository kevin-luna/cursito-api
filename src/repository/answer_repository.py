from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from uuid import UUID
import math
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

    def get_by_worker_paginated(self, db: Session, worker_id: UUID, page: int = 1, limit: int = 100) -> Tuple[List[Answer], int, int]:
        offset = (page - 1) * limit
        total_count = db.query(Answer).filter(Answer.worker_id == worker_id).count()
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        items = db.query(Answer).filter(Answer.worker_id == worker_id).offset(offset).limit(limit).all()
        return items, total_pages, total_count

    def get_by_course_paginated(self, db: Session, course_id: UUID, page: int = 1, limit: int = 100) -> Tuple[List[Answer], int, int]:
        offset = (page - 1) * limit
        total_count = db.query(Answer).filter(Answer.course_id == course_id).count()
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        items = db.query(Answer).filter(Answer.course_id == course_id).offset(offset).limit(limit).all()
        return items, total_pages, total_count

    def get_by_question_paginated(self, db: Session, question_id: UUID, page: int = 1, limit: int = 100) -> Tuple[List[Answer], int, int]:
        offset = (page - 1) * limit
        total_count = db.query(Answer).filter(Answer.question_id == question_id).count()
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        items = db.query(Answer).filter(Answer.question_id == question_id).offset(offset).limit(limit).all()
        return items, total_pages, total_count

    def get_by_worker_and_course_paginated(self, db: Session, worker_id: UUID, course_id: UUID, page: int = 1, limit: int = 100) -> Tuple[List[Answer], int, int]:
        offset = (page - 1) * limit
        total_count = db.query(Answer).filter(
            Answer.worker_id == worker_id,
            Answer.course_id == course_id
        ).count()
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        items = db.query(Answer).filter(
            Answer.worker_id == worker_id,
            Answer.course_id == course_id
        ).offset(offset).limit(limit).all()
        return items, total_pages, total_count

    def get_by_survey_paginated(self, db: Session, survey_id: UUID, page: int = 1, limit: int = 100) -> Tuple[List[Answer], int, int]:
        offset = (page - 1) * limit
        total_count = db.query(Answer).join(Answer.question).filter(
            Answer.question.has(survey_id=survey_id)
        ).count()
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        items = db.query(Answer).join(Answer.question).filter(
            Answer.question.has(survey_id=survey_id)
        ).offset(offset).limit(limit).all()
        return items, total_pages, total_count

    def search_by_value_paginated(self, db: Session, value: str, page: int = 1, limit: int = 100) -> Tuple[List[Answer], int, int]:
        offset = (page - 1) * limit
        total_count = db.query(Answer).filter(Answer.value.ilike(f"%{value}%")).count()
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        items = db.query(Answer).filter(Answer.value.ilike(f"%{value}%")).offset(offset).limit(limit).all()
        return items, total_pages, total_count
