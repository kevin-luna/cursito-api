from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import PositiveInt
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from enum import Enum

from ..database import get_db
from ..dto.worker import Worker, WorkerCreate, WorkerUpdate, WorkerResponse
from ..dto.pagination import PaginatedResponse
from ..repository.worker_repository import WorkerRepository
from ..dto.course import Course
from ..dto.enrolling import Enrolling

router = APIRouter(prefix="/workers", tags=["workers"])
worker_repo = WorkerRepository()

class CourseType(str, Enum):
    teaching = "teaching"
    enrolled = "enrolled"


@router.get("/", response_model=PaginatedResponse[Worker])
def get_workers(page: PositiveInt = 1, limit: int = 100, db: Session = Depends(get_db)):
    workers, total_pages, total_count = worker_repo.get_multi_paginated(db, page=page, limit=limit)
    return PaginatedResponse(
        items=workers,
        total_pages=total_pages,
        page=page,
        total_count=total_count
    )


@router.get("/{worker_id}", response_model=Worker)
def get_worker(worker_id: UUID, db: Session = Depends(get_db)):
    worker = worker_repo.get(db, id=worker_id)
    if not worker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Worker not found"
        )
    return worker


@router.post("/", response_model=Worker, status_code=status.HTTP_201_CREATED)
def create_worker(worker: WorkerCreate, db: Session = Depends(get_db)):
    # Sanitize all string fields - remove extra spaces at start and end
    worker.email = worker.email.strip()
    worker.rfc = worker.rfc.strip()
    worker.curp = worker.curp.strip()
    worker.name = worker.name.strip()
    worker.father_surname = worker.father_surname.strip()
    if worker.mother_surname:
        worker.mother_surname = worker.mother_surname.strip()
    if worker.telephone:
        worker.telephone = worker.telephone.strip()
    if worker.password:
        worker.password = worker.password.strip()

    # Check if worker with same email already exists (case-insensitive comparison)
    existing_worker = worker_repo.get_by_email(db, email=worker.email.lower())
    if existing_worker:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Worker with this email already exists"
        )

    # Check if worker with same RFC already exists
    existing_worker = worker_repo.get_by_rfc(db, rfc=worker.rfc)
    if existing_worker:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Worker with this RFC already exists"
        )

    # Check if worker with same CURP already exists
    existing_worker = worker_repo.get_by_curp(db, curp=worker.curp)
    if existing_worker:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Worker with this CURP already exists"
        )

    # Convert email to lowercase before saving
    worker.email = worker.email.lower()

    return worker_repo.create(db, obj_in=worker)


@router.put("/{worker_id}", response_model=Worker)
def update_worker(
    worker_id: UUID,
    worker_update: WorkerUpdate,
    db: Session = Depends(get_db)
):
    worker = worker_repo.get(db, id=worker_id)
    if not worker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Worker not found"
        )

    # Sanitize all string fields - remove extra spaces at start and end
    if worker_update.email:
        worker_update.email = worker_update.email.strip()
    if worker_update.rfc:
        worker_update.rfc = worker_update.rfc.strip()
    if worker_update.curp:
        worker_update.curp = worker_update.curp.strip()
    if worker_update.name:
        worker_update.name = worker_update.name.strip()
    if worker_update.father_surname:
        worker_update.father_surname = worker_update.father_surname.strip()
    if worker_update.mother_surname:
        worker_update.mother_surname = worker_update.mother_surname.strip()
    if worker_update.telephone:
        worker_update.telephone = worker_update.telephone.strip()
    if worker_update.password:
        worker_update.password = worker_update.password.strip()

    # Check if new email conflicts with existing worker (case-insensitive comparison)
    if worker_update.email:
        # Compare with existing worker's email in lowercase
        if worker.email.lower() != worker_update.email.lower():
            existing_worker = worker_repo.get_by_email(db, email=worker_update.email.lower())
            if existing_worker and existing_worker.id != worker_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Worker with this email already exists"
                )
        # Convert email to lowercase before saving
        worker_update.email = worker_update.email.lower()

    # Check if new RFC conflicts with existing worker
    if worker_update.rfc:
        existing_worker = worker_repo.get_by_rfc(db, rfc=worker_update.rfc)
        if existing_worker and existing_worker.id != worker_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Worker with this RFC already exists"
            )

    # Check if new CURP conflicts with existing worker
    if worker_update.curp:
        existing_worker = worker_repo.get_by_curp(db, curp=worker_update.curp)
        if existing_worker and existing_worker.id != worker_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Worker with this CURP already exists"
            )

    return worker_repo.update(db, db_obj=worker, obj_in=worker_update)


@router.delete("/{worker_id}")
def delete_worker(worker_id: UUID, db: Session = Depends(get_db)):
    worker = worker_repo.delete(db, id=worker_id)
    if not worker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Worker not found"
        )
    return {"message": "Worker deleted successfully"}


@router.get("/department/{department_id}", response_model=PaginatedResponse[Worker])
def get_workers_by_department(department_id: UUID, page: PositiveInt = 1, limit: int = 100, db: Session = Depends(get_db)):
    workers, total_pages, total_count = worker_repo.get_by_department_paginated(db, department_id=department_id, page=page, limit=limit)
    return PaginatedResponse(
        items=workers,
        total_pages=total_pages,
        page=page,
        total_count=total_count
    )


@router.get("/position/{position}", response_model=PaginatedResponse[Worker])
def get_workers_by_position(position: int, page: PositiveInt = 1, limit: int = 100, db: Session = Depends(get_db)):
    workers, total_pages, total_count = worker_repo.get_by_position_paginated(db, position=position, page=page, limit=limit)
    return PaginatedResponse(
        items=workers,
        total_pages=total_pages,
        page=page,
        total_count=total_count
    )


@router.get("/search/{name}", response_model=PaginatedResponse[Worker])
def search_workers(name: str, page: PositiveInt = 1, limit: int = 100, db: Session = Depends(get_db)):
    workers, total_pages, total_count = worker_repo.search_by_name_paginated(db, name=name, page=page, limit=limit)
    return PaginatedResponse(
        items=workers,
        total_pages=total_pages,
        page=page,
        total_count=total_count
    )


@router.get("/email/{email}", response_model=Worker)
def get_worker_by_email(email: str, db: Session = Depends(get_db)):
    worker = worker_repo.get_by_email(db, email=email)
    if not worker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Worker not found"
        )
    return worker

@router.get("/{worker_id}/courses", response_model=PaginatedResponse[Course])
def get_teaching_courses(worker_id: UUID, courseType: CourseType, page: PositiveInt = 1, limit: int = 100, db: Session = Depends(get_db)):
    if(courseType == 'teaching'):
        courses, total_pages, total_count = worker_repo.get_teaching_courses(db,worker_id)
    elif(courseType == 'enrolled'):
        courses, total_pages, total_count = worker_repo.get_enrolled_courses(db,worker_id)
    return PaginatedResponse(
        items=courses,
        total_pages=total_pages,
        page=page,
        total_count=total_count
    )

@router.get("/{worker_id}/enrollments", response_model=PaginatedResponse[Enrolling])
def get_enrollments(worker_id: UUID, page: PositiveInt = 1, limit: int = 100, db: Session = Depends(get_db)):
    enrollings, total_pages, total_count = worker_repo.get_enrollments(db, worker_id=worker_id, page=page, limit=limit)
    return PaginatedResponse(
        items=enrollings,
        total_pages=total_pages,
        page=page,
        total_count=total_count
    )