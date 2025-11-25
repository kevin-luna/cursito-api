from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import PositiveInt
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import date

from ..database import get_db
from ..dto.attendance import Attendance, AttendanceCreate, AttendanceUpdate, BulkAttendanceCreate, BulkAttendanceResponse
from ..dto.pagination import PaginatedResponse
from ..repository.attendance_repository import AttendanceRepository
from ..repository.course_repository import CourseRepository

router = APIRouter(prefix="/attendances", tags=["attendances"])
attendance_repo = AttendanceRepository()
course_repo = CourseRepository()


@router.get("/", response_model=PaginatedResponse[Attendance])
def get_attendances(page: PositiveInt = 1, limit: int = 100, db: Session = Depends(get_db)):
    attendances, total_pages, total_count = attendance_repo.get_multi_paginated(db, page=page, limit=limit)
    return PaginatedResponse(
        items=attendances,
        total_pages=total_pages,
        page=page,
        total_count=total_count
    )


@router.get("/{attendance_id}", response_model=Attendance)
def get_attendance(attendance_id: UUID, db: Session = Depends(get_db)):
    attendance = attendance_repo.get(db, id=attendance_id)
    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance not found"
        )
    return attendance


@router.post("/", response_model=Attendance, status_code=status.HTTP_201_CREATED)
def create_attendance(attendance: AttendanceCreate, db: Session = Depends(get_db)):
    # Check if attendance already exists for this worker, course, and date
    existing_attendance = attendance_repo.get_by_worker_course_and_date(
        db, 
        worker_id=attendance.worker_id, 
        course_id=attendance.course_id, 
        attendance_date=attendance.date
    )
    if existing_attendance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Attendance already recorded for this worker, course, and date"
        )
    
    return attendance_repo.create(db, obj_in=attendance)


@router.put("/{attendance_id}", response_model=Attendance)
def update_attendance(
    attendance_id: UUID, 
    attendance_update: AttendanceUpdate, 
    db: Session = Depends(get_db)
):
    attendance = attendance_repo.get(db, id=attendance_id)
    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance not found"
        )
    
    # Check if new assignment conflicts with existing attendance
    worker_id = attendance_update.worker_id or attendance.worker_id
    course_id = attendance_update.course_id or attendance.course_id
    attendance_date = attendance_update.date or attendance.date
    existing_attendance = attendance_repo.get_by_worker_course_and_date(
        db, 
        worker_id=worker_id, 
        course_id=course_id, 
        attendance_date=attendance_date
    )
    if existing_attendance and existing_attendance.id != attendance_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Attendance already recorded for this worker, course, and date"
        )
    
    return attendance_repo.update(db, db_obj=attendance, obj_in=attendance_update)


@router.delete("/{attendance_id}")
def delete_attendance(attendance_id: UUID, db: Session = Depends(get_db)):
    attendance = attendance_repo.delete(db, id=attendance_id)
    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attendance not found"
        )
    return {"message": "Attendance deleted successfully"}


@router.get("/worker/{worker_id}", response_model=PaginatedResponse[Attendance])
def get_attendances_by_worker(worker_id: UUID, page: PositiveInt = 1, limit: int = 100, db: Session = Depends(get_db)):
    attendances, total_pages, total_count = attendance_repo.get_by_worker_paginated(db, worker_id=worker_id, page=page, limit=limit)
    return PaginatedResponse(
        items=attendances,
        total_pages=total_pages,
        page=page,
        total_count=total_count
    )


@router.get("/course/{course_id}", response_model=PaginatedResponse[Attendance])
def get_attendances_by_course(course_id: UUID, page: PositiveInt = 1, limit: int = 100, db: Session = Depends(get_db)):
    attendances, total_pages, total_count = attendance_repo.get_by_course_paginated(db, course_id=course_id, page=page, limit=limit)
    return PaginatedResponse(
        items=attendances,
        total_pages=total_pages,
        page=page,
        total_count=total_count
    )


@router.get("/worker/{worker_id}/course/{course_id}", response_model=PaginatedResponse[Attendance])
def get_attendances_by_worker_and_course(
    worker_id: UUID,
    course_id: UUID,
    page: PositiveInt = 1,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    attendances, total_pages, total_count = attendance_repo.get_by_worker_and_course_paginated(db, worker_id=worker_id, course_id=course_id, page=page, limit=limit)
    return PaginatedResponse(
        items=attendances,
        total_pages=total_pages,
        page=page,
        total_count=total_count
    )


@router.get("/date/{attendance_date}", response_model=PaginatedResponse[Attendance])
def get_attendances_by_date(attendance_date: date, page: PositiveInt = 1, limit: int = 100, db: Session = Depends(get_db)):
    attendances, total_pages, total_count = attendance_repo.get_by_date_paginated(db, attendance_date=attendance_date, page=page, limit=limit)
    return PaginatedResponse(
        items=attendances,
        total_pages=total_pages,
        page=page,
        total_count=total_count
    )


@router.get("/worker/{worker_id}/date/{attendance_date}", response_model=List[Attendance])
def get_attendances_by_worker_and_date(
    worker_id: UUID, 
    attendance_date: date, 
    db: Session = Depends(get_db)
):
    attendances = attendance_repo.get_by_worker_and_date(db, worker_id=worker_id, attendance_date=attendance_date)
    return attendances


@router.get("/date-range/", response_model=PaginatedResponse[Attendance])
def get_attendances_by_date_range(
    start_date: date,
    end_date: date,
    page: PositiveInt = 1,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date must be before or equal to end date"
        )
    attendances, total_pages, total_count = attendance_repo.get_date_range_paginated(db, start_date=start_date, end_date=end_date, page=page, limit=limit)
    return PaginatedResponse(
        items=attendances,
        total_pages=total_pages,
        page=page,
        total_count=total_count
    )


@router.post("/bulk", response_model=BulkAttendanceResponse, status_code=status.HTTP_201_CREATED)
def create_bulk_attendances(
    bulk_data: BulkAttendanceCreate,
    db: Session = Depends(get_db)
):
    # Validate that the course exists
    course = course_repo.get(db, id=bulk_data.course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    # Validate that the date is within the course duration
    if bulk_data.date < course.start_date or bulk_data.date > course.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Attendance date must be between course start date ({course.start_date}) and end date ({course.end_date})"
        )

    created = 0
    skipped = 0
    errors = []

    for worker_id in bulk_data.worker_ids:
        try:
            # Check if attendance already exists
            existing_attendance = attendance_repo.get_by_worker_course_and_date(
                db,
                worker_id=worker_id,
                course_id=bulk_data.course_id,
                attendance_date=bulk_data.date
            )

            if existing_attendance:
                skipped += 1
                errors.append(f"Attendance already exists for worker {worker_id}")
                continue

            # Create attendance
            attendance_create = AttendanceCreate(
                worker_id=worker_id,
                course_id=bulk_data.course_id,
                attendance_date=bulk_data.date
            )
            attendance_repo.create(db, obj_in=attendance_create)
            created += 1

        except Exception as e:
            skipped += 1
            errors.append(f"Error creating attendance for worker {worker_id}: {str(e)}")

    return BulkAttendanceResponse(
        created=created,
        skipped=skipped,
        errors=errors
    )
