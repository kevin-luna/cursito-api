from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import date

from ..database import get_db
from ..dto.course import Course, CourseCreate, CourseUpdate
from ..repository.course_repository import CourseRepository

router = APIRouter(prefix="/courses", tags=["courses"])
course_repo = CourseRepository()


@router.get("/", response_model=List[Course])
def get_courses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    courses = course_repo.get_multi(db, skip=skip, limit=limit)
    return courses


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
    
    return course_repo.create(db, obj_in=course)


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


@router.get("/period/{period_id}", response_model=List[Course])
def get_courses_by_period(period_id: UUID, db: Session = Depends(get_db)):
    courses = course_repo.get_by_period(db, period_id=period_id)
    return courses


@router.get("/type/{course_type}", response_model=List[Course])
def get_courses_by_type(course_type: int, db: Session = Depends(get_db)):
    courses = course_repo.get_by_type(db, course_type=course_type)
    return courses


@router.get("/mode/{mode}", response_model=List[Course])
def get_courses_by_mode(mode: int, db: Session = Depends(get_db)):
    courses = course_repo.get_by_mode(db, mode=mode)
    return courses


@router.get("/profile/{profile}", response_model=List[Course])
def get_courses_by_profile(profile: int, db: Session = Depends(get_db)):
    courses = course_repo.get_by_profile(db, profile=profile)
    return courses


@router.get("/active/", response_model=List[Course])
def get_active_courses(current_date: date = None, db: Session = Depends(get_db)):
    if current_date is None:
        current_date = date.today()
    courses = course_repo.get_active_courses(db, current_date=current_date)
    return courses


@router.get("/date-range/", response_model=List[Course])
def get_courses_by_date_range(
    start_date: date, 
    end_date: date, 
    db: Session = Depends(get_db)
):
    if start_date >= end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date must be before end date"
        )
    courses = course_repo.get_by_date_range(db, start_date=start_date, end_date=end_date)
    return courses


@router.get("/search/{name}", response_model=List[Course])
def search_courses(name: str, db: Session = Depends(get_db)):
    courses = course_repo.search_by_name(db, name=name)
    return courses
