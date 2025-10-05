from typing import TypeVar, Generic, Type, Optional, List, Any, Tuple
from sqlalchemy.orm import Session
from pydantic import BaseModel
from uuid import UUID
import math

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: UUID) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def get_multi_paginated(self, db: Session, page: int = 1, limit: int = 100) -> Tuple[List[ModelType], int, int]:
        """
        Get paginated results with total count and total pages.
        Returns: (items, total_pages, total_count)
        """
        # Calculate offset
        offset = (page - 1) * limit
        
        # Get total count
        total_count = db.query(self.model).count()
        
        # Calculate total pages
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        
        # Get paginated results
        items = db.query(self.model).offset(offset).limit(limit).all()
        
        return items, total_pages, total_count

    def create(self, db: Session, obj_in: CreateSchemaType) -> ModelType:
        obj_data = obj_in.dict()
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType:
        obj_data = obj_in.dict(exclude_unset=True)
        for field, value in obj_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: UUID) -> Optional[ModelType]:
        obj = db.query(self.model).filter(self.model.id == id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj

    def get_by_field(self, db: Session, field: str, value: Any) -> Optional[ModelType]:
        return db.query(self.model).filter(getattr(self.model, field) == value).first()

    def get_multi_by_field(self, db: Session, field: str, value: Any) -> List[ModelType]:
        return db.query(self.model).filter(getattr(self.model, field) == value).all()

    def get_multi_by_field_paginated(self, db: Session, field: str, value: Any, page: int = 1, limit: int = 100) -> Tuple[List[ModelType], int, int]:
        """
        Get paginated results filtered by field with total count and total pages.
        Returns: (items, total_pages, total_count)
        """
        # Calculate offset
        offset = (page - 1) * limit
        
        # Get total count
        total_count = db.query(self.model).filter(getattr(self.model, field) == value).count()
        
        # Calculate total pages
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        
        # Get paginated results
        items = db.query(self.model).filter(getattr(self.model, field) == value).offset(offset).limit(limit).all()
        
        return items, total_pages, total_count
