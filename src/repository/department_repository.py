from typing import List, Optional
from sqlalchemy.orm import Session
from uuid import UUID
from ..model.department import Department
from ..dto.department import DepartmentCreate, DepartmentUpdate
from .base import BaseRepository


class DepartmentRepository(BaseRepository[Department, DepartmentCreate, DepartmentUpdate]):
    def __init__(self):
        super().__init__(Department)

    def get_by_name(self, db: Session, name: str) -> Optional[Department]:
        return db.query(Department).filter(Department.name == name).first()

    def search_by_name(self, db: Session, name: str) -> List[Department]:
        return db.query(Department).filter(Department.name.ilike(f"%{name}%")).all()
