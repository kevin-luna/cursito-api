from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import PositiveInt
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import date, timedelta

from ..database import get_db
from ..dto.course import Course, CourseCreate, CourseUpdate
from ..dto.worker import Worker
from ..dto.enrolling import Enrolling
from ..dto.pagination import PaginatedResponse
from ..dto.attendance import AttendanceList
from ..repository.course_repository import CourseRepository
from ..repository.instructor_repository import InstructorRepository
from ..repository.period_repository import PeriodRepository
from ..repository.attendance_repository import AttendanceRepository

router = APIRouter(prefix="/courses", tags=["courses"])
course_repo = CourseRepository()
instructor_repo = InstructorRepository()
period_repo = PeriodRepository()
attendance_repo = AttendanceRepository()


def validate_course_duration_and_weekdays(start_date: date, end_date: date):
    """
    Validates that a course:
    1. Does not last more than 5 days
    2. Does not include weekend days (Saturday=5, Sunday=6)
    """
    # Calculate duration in days
    duration = (end_date - start_date).days + 1

    if duration > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course duration cannot exceed 5 days"
        )

    # Check if any day in the range falls on a weekend
    current_date = start_date
    while current_date <= end_date:
        # weekday() returns 0=Monday, 6=Sunday
        if current_date.weekday() in [5, 6]:  # Saturday or Sunday
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Course dates cannot include weekends (Saturday or Sunday)"
            )
        current_date += timedelta(days=1)


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
    # Sanitize all string fields - remove extra spaces at start and end
    course.target = course.target.strip()
    course.name = course.name.strip()
    course.goal = course.goal.strip()
    if course.details:
        course.details = course.details.strip()

    # Validate period exists
    period = period_repo.get(db, id=course.period_id)
    if not period:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Period not found"
        )

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

    # Validate course duration and weekdays
    validate_course_duration_and_weekdays(course.start_date, course.end_date)

    # Validate time range
    if course.start_time >= course.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start time must be before end time"
        )

    # Validate course dates are within period dates
    if course.start_date < period.start_date or course.start_date > period.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Course start date must be between period start date ({period.start_date}) and end date ({period.end_date})"
        )

    if course.end_date < period.start_date or course.end_date > period.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Course end date must be between period start date ({period.start_date}) and end date ({period.end_date})"
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

    # Sanitize all string fields - remove extra spaces at start and end
    if course_update.target:
        course_update.target = course_update.target.strip()
    if course_update.name:
        course_update.name = course_update.name.strip()
    if course_update.goal:
        course_update.goal = course_update.goal.strip()
    if course_update.details:
        course_update.details = course_update.details.strip()

    # Get the period (use updated period_id or existing one)
    period_id = course_update.period_id or course.period_id
    period = period_repo.get(db, id=period_id)
    if not period:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Period not found"
        )

    # Validate instructors if provided
    if course_update.instructors is not None:
        instructors_count = len(course_update.instructors)
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

        if not instructor_repo.check_instructor_list(db, course_update.instructors):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid instructors"
            )

    # Validate date range if dates are being updated
    start_date = course_update.start_date or course.start_date
    end_date = course_update.end_date or course.end_date
    if start_date >= end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date must be before end date"
        )

    # Validate course duration and weekdays
    validate_course_duration_and_weekdays(start_date, end_date)

    # Validate time range if times are being updated
    start_time = course_update.start_time or course.start_time
    end_time = course_update.end_time or course.end_time
    if start_time >= end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start time must be before end time"
        )

    # Validate course dates are within period dates
    if start_date < period.start_date or start_date > period.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Course start date must be between period start date ({period.start_date}) and end date ({period.end_date})"
        )

    if end_date < period.start_date or end_date > period.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Course end date must be between period start date ({period.start_date}) and end date ({period.end_date})"
        )

    # Validate instructor availability if instructors are being updated
    if course_update.instructors is not None:
        if not instructor_repo.check_availability(db, course_update.instructors, start_date, end_date, start_time, end_time, exclude_course_id=course_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Instructor is not available"
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


@router.get("/{course_id}/instructors", response_model=PaginatedResponse[Worker])
def get_instructors(course_id: UUID, page: PositiveInt = 1, limit: int = 100, db: Session = Depends(get_db)):
    course = course_repo.get(db, id=course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    instructors, total_pages, total_count = course_repo.get_instructors(db, course_id)
    return PaginatedResponse(
        items=instructors,
        total_pages=total_pages,
        page=page,
        total_count=total_count
    )


@router.get("/{course_id}/enrollments", response_model=PaginatedResponse[Enrolling])
def get_enrolled_workers(course_id: UUID,  page: PositiveInt = 1, limit: int = 100, db: Session = Depends(get_db)):
    course = course_repo.get(db, id=course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    enrollments, total_pages, total_count = course_repo.get_enrolled_workers(db, course_id)
    return PaginatedResponse(
        items=enrollments,
        total_pages=total_pages,
        page=page,
        total_count=total_count
    )

@router.get("/{course_id}/attendances", response_model=AttendanceList)
def get_attendances_by_course_and_date(
    course_id: UUID, 
    attendance_date: date, 
    db: Session = Depends(get_db)
):
    attendances = attendance_repo.get_by_course_and_date(db, course_id=course_id, attendance_date=attendance_date)
    return AttendanceList(items=attendances)