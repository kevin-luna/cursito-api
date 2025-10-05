from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from uuid import UUID
import math
from ..model.worker import Worker
from ..dto.worker import WorkerCreate, WorkerUpdate
from .base import BaseRepository


class WorkerRepository(BaseRepository[Worker, WorkerCreate, WorkerUpdate]):
    def __init__(self):
        super().__init__(Worker)

    def get_by_email(self, db: Session, email: str) -> Optional[Worker]:
        return db.query(Worker).filter(Worker.email == email).first()

    def get_by_rfc(self, db: Session, rfc: str) -> Optional[Worker]:
        return db.query(Worker).filter(Worker.rfc == rfc).first()

    def get_by_curp(self, db: Session, curp: str) -> Optional[Worker]:
        return db.query(Worker).filter(Worker.curp == curp).first()

    def get_by_department(self, db: Session, department_id: UUID) -> List[Worker]:
        return db.query(Worker).filter(Worker.department_id == department_id).all()

    def get_by_role(self, db: Session, role: int) -> List[Worker]:
        return db.query(Worker).filter(Worker.role == role).all()

    def search_by_name(self, db: Session, name: str) -> List[Worker]:
        return db.query(Worker).filter(
            Worker.name.ilike(f"%{name}%") |
            Worker.fathers_surname.ilike(f"%{name}%") |
            Worker.mother_surname.ilike(f"%{name}%")
        ).all()

    def get_by_department_paginated(self, db: Session, department_id: UUID, page: int = 1, limit: int = 100) -> Tuple[List[Worker], int, int]:
        offset = (page - 1) * limit
        total_count = db.query(Worker).filter(Worker.department_id == department_id).count()
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        items = db.query(Worker).filter(Worker.department_id == department_id).offset(offset).limit(limit).all()
        return items, total_pages, total_count

    def get_by_role_paginated(self, db: Session, role: int, page: int = 1, limit: int = 100) -> Tuple[List[Worker], int, int]:
        offset = (page - 1) * limit
        total_count = db.query(Worker).filter(Worker.role == role).count()
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        items = db.query(Worker).filter(Worker.role == role).offset(offset).limit(limit).all()
        return items, total_pages, total_count

    def search_by_name_paginated(self, db: Session, name: str, page: int = 1, limit: int = 100) -> Tuple[List[Worker], int, int]:
        offset = (page - 1) * limit
        total_count = db.query(Worker).filter(
            Worker.name.ilike(f"%{name}%") |
            Worker.fathers_surname.ilike(f"%{name}%") |
            Worker.mother_surname.ilike(f"%{name}%")
        ).count()
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        items = db.query(Worker).filter(
            Worker.name.ilike(f"%{name}%") |
            Worker.fathers_surname.ilike(f"%{name}%") |
            Worker.mother_surname.ilike(f"%{name}%")
        ).offset(offset).limit(limit).all()
        return items, total_pages, total_count
