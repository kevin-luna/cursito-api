from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import PositiveInt
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from decimal import Decimal

from ..database import get_db
from ..dto.enrolling import Enrolling, EnrollingCreate, EnrollingUpdate, BulkGradeUpdate, BulkGradeResponse
from ..dto.pagination import PaginatedResponse
from ..repository.enrolling_repository import EnrollingRepository
from ..repository.course_repository import CourseRepository

router = APIRouter(prefix="/enrollings", tags=["enrollings"])
enrolling_repo = EnrollingRepository()
course_repo = CourseRepository()


@router.get("/", response_model=PaginatedResponse[Enrolling])
def get_enrollings(page: PositiveInt = 1, limit: int = 100, db: Session = Depends(get_db)):
    enrollings, total_pages, total_count = enrolling_repo.get_multi_paginated(db, page=page, limit=limit)
    return PaginatedResponse(
        items=enrollings,
        total_pages=total_pages,
        page=page,
        total_count=total_count
    )


@router.get("/{enrolling_id}", response_model=Enrolling)
def get_enrolling(enrolling_id: UUID, db: Session = Depends(get_db)):
    enrolling = enrolling_repo.get(db, id=enrolling_id)
    if not enrolling:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrolling not found"
        )
    return enrolling


@router.post("/", response_model=Enrolling, status_code=status.HTTP_201_CREATED)
def create_enrolling(enrolling: EnrollingCreate, db: Session = Depends(get_db)):
    # Check if worker is already enrolled in this course
    existing_enrolling = enrolling_repo.get_by_worker_and_course(
        db, worker_id=enrolling.worker_id, course_id=enrolling.course_id
    )
    if existing_enrolling:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Worker is already enrolled in this course"
        )

    # Check if course has reached maximum capacity of 30 students
    current_enrollments = db.query(enrolling_repo.model).filter(
        enrolling_repo.model.course_id == enrolling.course_id
    ).count()
    if current_enrollments >= 30:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course has reached maximum capacity of 30 students"
        )

    return enrolling_repo.create(db, obj_in=enrolling)


@router.put("/{enrolling_id}", response_model=Enrolling)
def update_enrolling(
    enrolling_id: UUID,
    enrolling_update: EnrollingUpdate,
    db: Session = Depends(get_db)
):
    enrolling = enrolling_repo.get(db, id=enrolling_id)
    if not enrolling:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrolling not found"
        )

    # Check if new assignment conflicts with existing enrolling
    worker_id = enrolling_update.worker_id or enrolling.worker_id
    course_id = enrolling_update.course_id or enrolling.course_id
    existing_enrolling = enrolling_repo.get_by_worker_and_course(
        db, worker_id=worker_id, course_id=course_id
    )
    if existing_enrolling and existing_enrolling.id != enrolling_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Worker is already enrolled in this course"
        )

    # Check if course change would exceed maximum capacity
    if enrolling_update.course_id and enrolling_update.course_id != enrolling.course_id:
        current_enrollments = db.query(enrolling_repo.model).filter(
            enrolling_repo.model.course_id == course_id
        ).count()
        if current_enrollments >= 30:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Course has reached maximum capacity of 30 students"
            )

    return enrolling_repo.update(db, db_obj=enrolling, obj_in=enrolling_update)


@router.delete("/{enrolling_id}")
def delete_enrolling(enrolling_id: UUID, db: Session = Depends(get_db)):
    enrolling = enrolling_repo.delete(db, id=enrolling_id)
    if not enrolling:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrolling not found"
        )
    return {"message": "Enrolling deleted successfully"}


@router.get("/worker/{worker_id}", response_model=PaginatedResponse[Enrolling])
def get_enrollings_by_worker(worker_id: UUID, page: PositiveInt = 1, limit: int = 100, db: Session = Depends(get_db)):
    enrollings, total_pages, total_count = enrolling_repo.get_by_worker_paginated(db, worker_id=worker_id, page=page, limit=limit)
    return PaginatedResponse(
        items=enrollings,
        total_pages=total_pages,
        page=page,
        total_count=total_count
    )


@router.get("/course/{course_id}", response_model=PaginatedResponse[Enrolling])
def get_enrollings_by_course(course_id: UUID, page: PositiveInt = 1, limit: int = 100, db: Session = Depends(get_db)):
    enrollings, total_pages, total_count = enrolling_repo.get_by_course_paginated(db, course_id=course_id, page=page, limit=limit)
    return PaginatedResponse(
        items=enrollings,
        total_pages=total_pages,
        page=page,
        total_count=total_count
    )


@router.get("/grade-range/", response_model=PaginatedResponse[Enrolling])
def get_enrollings_by_grade_range(
    min_grade: Decimal,
    max_grade: Decimal,
    page: PositiveInt = 1,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    if min_grade > max_grade:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Min grade must be less than or equal to max grade"
        )
    enrollings, total_pages, total_count = enrolling_repo.get_by_grade_range_paginated(db, min_grade=min_grade, max_grade=max_grade, page=page, limit=limit)
    return PaginatedResponse(
        items=enrollings,
        total_pages=total_pages,
        page=page,
        total_count=total_count
    )


@router.post("/bulk-grades", response_model=BulkGradeResponse)
def update_bulk_grades(
    bulk_data: BulkGradeUpdate,
    db: Session = Depends(get_db)
):
    # Validate that the course exists
    course = course_repo.get(db, id=bulk_data.course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    updated = 0
    skipped = 0
    errors = []

    for grade_data in bulk_data.grades:
        try:
            # Validate grade range (0-100)
            if grade_data.final_grade < 0 or grade_data.final_grade > 100:
                skipped += 1
                errors.append(f"Grade for worker {grade_data.worker_id} must be between 0 and 100")
                continue

            # Find the enrollment
            enrolling = enrolling_repo.get_by_worker_and_course(
                db,
                worker_id=grade_data.worker_id,
                course_id=bulk_data.course_id
            )

            if not enrolling:
                skipped += 1
                errors.append(f"Worker {grade_data.worker_id} is not enrolled in this course")
                continue

            # Update the grade
            enrolling_update = EnrollingUpdate(final_grade=grade_data.final_grade)
            enrolling_repo.update(db, db_obj=enrolling, obj_in=enrolling_update)
            updated += 1

        except Exception as e:
            skipped += 1
            errors.append(f"Error updating grade for worker {grade_data.worker_id}: {str(e)}")

    return BulkGradeResponse(
        updated=updated,
        skipped=skipped,
        errors=errors
    )
