from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..database import get_db
from ..dto.instructor import Instructor, InstructorCreate, InstructorUpdate
from ..dto.pagination import PaginatedResponse
from ..repository.instructor_repository import InstructorRepository

router = APIRouter(prefix="/instructors", tags=["instructors"])
instructor_repo = InstructorRepository()


@router.get("/", response_model=PaginatedResponse[Instructor])
def get_instructors(page: int = 1, limit: int = 100, db: Session = Depends(get_db)):
    instructors, total_pages, total_count = instructor_repo.get_multi_paginated(db, page=page, limit=limit)
    return PaginatedResponse(
        items=instructors,
        total_pages=total_pages,
        page=page,
        total_count=total_count
    )


@router.get("/{instructor_id}", response_model=Instructor)
def get_instructor(instructor_id: UUID, db: Session = Depends(get_db)):
    instructor = instructor_repo.get(db, id=instructor_id)
    if not instructor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instructor not found"
        )
    return instructor


@router.post("/", response_model=Instructor, status_code=status.HTTP_201_CREATED)
def create_instructor(instructor: InstructorCreate, db: Session = Depends(get_db)):
    # Check if instructor already exists for this course
    existing_instructor = instructor_repo.get_by_worker_and_course(
        db, worker_id=instructor.worker_id, course_id=instructor.course_id
    )
    if existing_instructor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Instructor already assigned to this course"
        )
    
    return instructor_repo.create(db, obj_in=instructor)


@router.put("/{instructor_id}", response_model=Instructor)
def update_instructor(
    instructor_id: UUID, 
    instructor_update: InstructorUpdate, 
    db: Session = Depends(get_db)
):
    instructor = instructor_repo.get(db, id=instructor_id)
    if not instructor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instructor not found"
        )
    
    # Check if new assignment conflicts with existing instructor
    worker_id = instructor_update.worker_id or instructor.worker_id
    course_id = instructor_update.course_id or instructor.course_id
    existing_instructor = instructor_repo.get_by_worker_and_course(
        db, worker_id=worker_id, course_id=course_id
    )
    if existing_instructor and existing_instructor.id != instructor_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Instructor already assigned to this course"
        )
    
    return instructor_repo.update(db, db_obj=instructor, obj_in=instructor_update)


@router.delete("/{instructor_id}")
def delete_instructor(instructor_id: UUID, db: Session = Depends(get_db)):
    instructor = instructor_repo.delete(db, id=instructor_id)
    if not instructor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instructor not found"
        )
    return {"message": "Instructor deleted successfully"}


@router.get("/worker/{worker_id}", response_model=PaginatedResponse[Instructor])
def get_instructors_by_worker(worker_id: UUID, page: int = 1, limit: int = 100, db: Session = Depends(get_db)):
    instructors, total_pages, total_count = instructor_repo.get_by_worker_paginated(db, worker_id=worker_id, page=page, limit=limit)
    return PaginatedResponse(
        items=instructors,
        total_pages=total_pages,
        page=page,
        total_count=total_count
    )


@router.get("/course/{course_id}", response_model=PaginatedResponse[Instructor])
def get_instructors_by_course(course_id: UUID, page: int = 1, limit: int = 100, db: Session = Depends(get_db)):
    instructors, total_pages, total_count = instructor_repo.get_by_course_paginated(db, course_id=course_id, page=page, limit=limit)
    return PaginatedResponse(
        items=instructors,
        total_pages=total_pages,
        page=page,
        total_count=total_count
    )


@router.get("/worker/{worker_id}/courses", response_model=PaginatedResponse[Instructor])
def get_courses_by_worker(worker_id: UUID, page: int = 1, limit: int = 100, db: Session = Depends(get_db)):
    instructors, total_pages, total_count = instructor_repo.get_courses_by_worker_paginated(db, worker_id=worker_id, page=page, limit=limit)
    return PaginatedResponse(
        items=instructors,
        total_pages=total_pages,
        page=page,
        total_count=total_count
    )


@router.get("/course/{course_id}/workers", response_model=PaginatedResponse[Instructor])
def get_workers_by_course(course_id: UUID, page: int = 1, limit: int = 100, db: Session = Depends(get_db)):
    instructors, total_pages, total_count = instructor_repo.get_workers_by_course_paginated(db, course_id=course_id, page=page, limit=limit)
    return PaginatedResponse(
        items=instructors,
        total_pages=total_pages,
        page=page,
        total_count=total_count
    )
