from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..database import get_db
from ..dto.worker import Worker, WorkerCreate, WorkerUpdate, WorkerResponse
from ..repository.worker_repository import WorkerRepository

router = APIRouter(prefix="/workers", tags=["workers"])
worker_repo = WorkerRepository()


@router.get("/", response_model=List[Worker])
def get_workers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    workers = worker_repo.get_multi(db, skip=skip, limit=limit)
    return workers


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
    # Check if worker with same email already exists
    existing_worker = worker_repo.get_by_email(db, email=worker.email)
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
    
    # Check if new email conflicts with existing worker
    if worker_update.email:
        existing_worker = worker_repo.get_by_email(db, email=worker_update.email)
        if existing_worker and existing_worker.id != worker_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Worker with this email already exists"
            )
    
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


@router.get("/department/{department_id}", response_model=List[Worker])
def get_workers_by_department(department_id: UUID, db: Session = Depends(get_db)):
    workers = worker_repo.get_by_department(db, department_id=department_id)
    return workers


@router.get("/role/{role}", response_model=List[Worker])
def get_workers_by_role(role: int, db: Session = Depends(get_db)):
    workers = worker_repo.get_by_role(db, role=role)
    return workers


@router.get("/search/{name}", response_model=List[Worker])
def search_workers(name: str, db: Session = Depends(get_db)):
    workers = worker_repo.search_by_name(db, name=name)
    return workers


@router.get("/email/{email}", response_model=Worker)
def get_worker_by_email(email: str, db: Session = Depends(get_db)):
    worker = worker_repo.get_by_email(db, email=email)
    if not worker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Worker not found"
        )
    return worker
