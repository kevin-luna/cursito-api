from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import PositiveInt
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..database import get_db
from ..dto.department import Department, DepartmentCreate, DepartmentUpdate
from ..dto.pagination import PaginatedResponse
from ..repository.department_repository import DepartmentRepository

router = APIRouter(prefix="/departments", tags=["departments"])
department_repo = DepartmentRepository()


@router.get("/", response_model=PaginatedResponse[Department])
def get_departments(page: PositiveInt = 1, limit: int = 100, db: Session = Depends(get_db)):
    departments, total_pages, total_count = department_repo.get_multi_paginated(db, page=page, limit=limit)
    return PaginatedResponse(
        items=departments,
        total_pages=total_pages,
        page=page,
        total_count=total_count
    )


@router.get("/{department_id}", response_model=Department)
def get_department(department_id: UUID, db: Session = Depends(get_db)):
    department = department_repo.get(db, id=department_id)
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    return department


@router.post("/", response_model=Department, status_code=status.HTTP_201_CREATED)
def create_department(department: DepartmentCreate, db: Session = Depends(get_db)):
    # Check if department with same name already exists
    existing_department = department_repo.get_by_name(db, name=department.name)
    if existing_department:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Department with this name already exists"
        )
    return department_repo.create(db, obj_in=department)


@router.put("/{department_id}", response_model=Department)
def update_department(
    department_id: UUID, 
    department_update: DepartmentUpdate, 
    db: Session = Depends(get_db)
):
    department = department_repo.get(db, id=department_id)
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    
    # Check if new name conflicts with existing department
    if department_update.name:
        existing_department = department_repo.get_by_name(db, name=department_update.name)
        if existing_department and existing_department.id != department_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Department with this name already exists"
            )
    
    return department_repo.update(db, db_obj=department, obj_in=department_update)


@router.delete("/{department_id}")
def delete_department(department_id: UUID, db: Session = Depends(get_db)):
    department = department_repo.delete(db, id=department_id)
    if not department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Department not found"
        )
    return {"message": "Department deleted successfully"}


@router.get("/search/{name}", response_model=PaginatedResponse[Department])
def search_departments(name: str, page: PositiveInt = 1, limit: int = 100, db: Session = Depends(get_db)):
    departments, total_pages, total_count = department_repo.search_by_name_paginated(db, name=name, page=page, limit=limit)
    return PaginatedResponse(
        items=departments,
        total_pages=total_pages,
        page=page,
        total_count=total_count
    )
