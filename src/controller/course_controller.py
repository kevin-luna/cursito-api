from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import PositiveInt
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import date

from ..database import get_db
from ..dto.course import Course, CourseCreate, CourseUpdate
from ..dto.pagination import PaginatedResponse
from ..repository.course_repository import CourseRepository
from ..repository.instructor_repository import InstructorRepository

router = APIRouter(prefix="/courses", tags=["courses"])
course_repo = CourseRepository()
instructor_repo = InstructorRepository()


@router.get("/", response_model=PaginatedResponse[Course])
def get_courses(page: PositiveInt = 1, limit: int = 100, db: Session = Depends(get_db)):
    courses, total_pages, total_count = course_repo.get_multi_paginated(db, page=page, limit=limit)
    return PaginatedResponse(
        items=courses,
        total_pages=total_pages,
        page=page,
        total_count=total_count
    )


@router.get("/{course_id}", response_model=Course)
def get_course(course_id: UUID, db: Session = Depends(get_db)):
    course = course_repo.get(db, id=course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    return course


@router.post("/", response_model=Course, status_code=status.HTTP_201_CREATED)
def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    #Validate instructors
    instructors_count = len(course.instructors)
    if instructors_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A course must have at least 1 instructor"
        )

    if instructors_count > 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A course can only have 2 instructors"
        )

    if not instructor_repo.check_instructor_list(db, course.instructors):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid instructors"
        )

    if not instructor_repo.check_availability(db, course.instructors, course.start_date, course.end_date, course.start_time, course.end_time):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Instructor is not available"
        )
    

    # Validate date range
    if course.start_date >= course.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date must be before end date"
        )
    
    # Validate time range
    if course.start_time >= course.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start time must be before end time"
        )
    
    return course_repo.create(db, course)


@router.put("/{course_id}", response_model=Course)
def update_course(
    course_id: UUID, 
    course_update: CourseUpdate, 
    db: Session = Depends(get_db)
):
    course = course_repo.get(db, id=course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Validate date range if dates are being updated
    start_date = course_update.start_date or course.start_date
    end_date = course_update.end_date or course.end_date
    if start_date >= end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date must be before end date"
        )
    
    # Validate time range if times are being updated
    start_time = course_update.start_time or course.start_time
    end_time = course_update.end_time or course.end_time
    if start_time >= end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start time must be before end time"
        )
    
    return course_repo.update(db, db_obj=course, obj_in=course_update)


@router.delete("/{course_id}")
def delete_course(course_id: UUID, db: Session = Depends(get_db)):
    course = course_repo.delete(db, id=course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    return {"message": "Course deleted successfully"}


@router.get("/period/{period_id}", response_model=PaginatedResponse[Course])
def get_courses_by_period(period_id: UUID, page: PositiveInt = 1, limit: int = 100, db: Session = Depends(get_db)):
    courses, total_pages, total_count = course_repo.get_by_period_paginated(db, period_id=period_id, page=page, limit=limit)
    return PaginatedResponse(
        items=courses,
        total_pages=total_pages,
        page=page,
        total_count=total_count
    )


@router.get("/type/{course_type}", response_model=PaginatedResponse[Course])
def get_courses_by_type(course_type: int, page: PositiveInt = 1, limit: int = 100, db: Session = Depends(get_db)):
    courses, total_pages, total_count = course_repo.get_by_type_paginated(db, course_type=course_type, page=page, limit=limit)
    return PaginatedResponse(
        items=courses,
        total_pages=total_pages,
        page=page,
        total_count=total_count
    )


@router.get("/mode/{mode}", response_model=PaginatedResponse[Course])
def get_courses_by_mode(mode: int, page: PositiveInt = 1, limit: int = 100, db: Session = Depends(get_db)):
    courses, total_pages, total_count = course_repo.get_by_mode_paginated(db, mode=mode, page=page, limit=limit)
    return PaginatedResponse(
        items=courses,
        total_pages=total_pages,
        page=page,
        total_count=total_count
    )


@router.get("/profile/{profile}", response_model=PaginatedResponse[Course])
def get_courses_by_profile(profile: int, page: PositiveInt = 1, limit: int = 100, db: Session = Depends(get_db)):
    courses, total_pages, total_count = course_repo.get_by_profile_paginated(db, profile=profile, page=page, limit=limit)
    return PaginatedResponse(
        items=courses,
        total_pages=total_pages,
        page=page,
        total_count=total_count
    )


@router.get("/active/", response_model=PaginatedResponse[Course])
def get_active_courses(current_date: date = None, page: PositiveInt = 1, limit: int = 100, db: Session = Depends(get_db)):
    if current_date is None:
        current_date = date.today()
    courses, total_pages, total_count = course_repo.get_active_courses_paginated(db, current_date=current_date, page=page, limit=limit)
    return PaginatedResponse(
        items=courses,
        total_pages=total_pages,
        page=page,
        total_count=total_count
    )


@router.get("/date-range/", response_model=PaginatedResponse[Course])
def get_courses_by_date_range(
    start_date: date,
    end_date: date,
    page: PositiveInt = 1,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    if start_date >= end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date must be before end date"
        )
    courses, total_pages, total_count = course_repo.get_by_date_range_paginated(db, start_date=start_date, end_date=end_date, page=page, limit=limit)
    return PaginatedResponse(
        items=courses,
        total_pages=total_pages,
        page=page,
        total_count=total_count
    )


@router.get("/search/{name}", response_model=PaginatedResponse[Course])
def search_courses(name: str, page: PositiveInt = 1, limit: int = 100, db: Session = Depends(get_db)):
    courses, total_pages, total_count = course_repo.search_by_name_paginated(db, name=name, page=page, limit=limit)
    return PaginatedResponse(
        items=courses,
        total_pages=total_pages,
        page=page,
        total_count=total_count
    )
