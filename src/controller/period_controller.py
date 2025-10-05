from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import date

from ..database import get_db
from ..dto.period import Period, PeriodCreate, PeriodUpdate
from ..repository.period_repository import PeriodRepository

router = APIRouter(prefix="/periods", tags=["periods"])
period_repo = PeriodRepository()


@router.get("/", response_model=List[Period])
def get_periods(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    periods = period_repo.get_multi(db, skip=skip, limit=limit)
    return periods


@router.get("/{period_id}", response_model=Period)
def get_period(period_id: UUID, db: Session = Depends(get_db)):
    period = period_repo.get(db, id=period_id)
    if not period:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Period not found"
        )
    return period


@router.post("/", response_model=Period, status_code=status.HTTP_201_CREATED)
def create_period(period: PeriodCreate, db: Session = Depends(get_db)):
    # Check if period with same name already exists
    existing_period = period_repo.get_by_name(db, name=period.name)
    if existing_period:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Period with this name already exists"
        )
    
    # Validate date range
    if period.start_date >= period.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date must be before end date"
        )
    
    return period_repo.create(db, obj_in=period)


@router.put("/{period_id}", response_model=Period)
def update_period(
    period_id: UUID, 
    period_update: PeriodUpdate, 
    db: Session = Depends(get_db)
):
    period = period_repo.get(db, id=period_id)
    if not period:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Period not found"
        )
    
    # Check if new name conflicts with existing period
    if period_update.name:
        existing_period = period_repo.get_by_name(db, name=period_update.name)
        if existing_period and existing_period.id != period_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Period with this name already exists"
            )
    
    # Validate date range if dates are being updated
    start_date = period_update.start_date or period.start_date
    end_date = period_update.end_date or period.end_date
    if start_date >= end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date must be before end date"
        )
    
    return period_repo.update(db, db_obj=period, obj_in=period_update)


@router.delete("/{period_id}")
def delete_period(period_id: UUID, db: Session = Depends(get_db)):
    period = period_repo.delete(db, id=period_id)
    if not period:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Period not found"
        )
    return {"message": "Period deleted successfully"}


@router.get("/active/", response_model=List[Period])
def get_active_periods(current_date: date = None, db: Session = Depends(get_db)):
    if current_date is None:
        current_date = date.today()
    periods = period_repo.get_active_periods(db, current_date=current_date)
    return periods


@router.get("/date-range/", response_model=List[Period])
def get_periods_by_date_range(
    start_date: date, 
    end_date: date, 
    db: Session = Depends(get_db)
):
    if start_date >= end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date must be before end date"
        )
    periods = period_repo.get_by_date_range(db, start_date=start_date, end_date=end_date)
    return periods
