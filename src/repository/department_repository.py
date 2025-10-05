from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from uuid import UUID
import math
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

    def search_by_name_paginated(self, db: Session, name: str, page: int = 1, limit: int = 100) -> Tuple[List[Department], int, int]:
        offset = (page - 1) * limit
        total_count = db.query(Department).filter(Department.name.ilike(f"%{name}%")).count()
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        items = db.query(Department).filter(Department.name.ilike(f"%{name}%")).offset(offset).limit(limit).all()
        return items, total_pages, total_count
