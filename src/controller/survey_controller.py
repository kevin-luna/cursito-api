from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..database import get_db
from ..dto.survey import Survey, SurveyCreate, SurveyUpdate
from ..repository.survey_repository import SurveyRepository

router = APIRouter(prefix="/surveys", tags=["surveys"])
survey_repo = SurveyRepository()


@router.get("/", response_model=List[Survey])
def get_surveys(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    surveys = survey_repo.get_multi(db, skip=skip, limit=limit)
    return surveys


@router.get("/{survey_id}", response_model=Survey)
def get_survey(survey_id: UUID, db: Session = Depends(get_db)):
    survey = survey_repo.get(db, id=survey_id)
    if not survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Survey not found"
        )
    return survey


@router.post("/", response_model=Survey, status_code=status.HTTP_201_CREATED)
def create_survey(survey: SurveyCreate, db: Session = Depends(get_db)):
    # Check if survey with same name already exists
    existing_survey = survey_repo.get_by_name(db, name=survey.name)
    if existing_survey:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Survey with this name already exists"
        )
    return survey_repo.create(db, obj_in=survey)


@router.put("/{survey_id}", response_model=Survey)
def update_survey(
    survey_id: UUID, 
    survey_update: SurveyUpdate, 
    db: Session = Depends(get_db)
):
    survey = survey_repo.get(db, id=survey_id)
    if not survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Survey not found"
        )
    
    # Check if new name conflicts with existing survey
    if survey_update.name:
        existing_survey = survey_repo.get_by_name(db, name=survey_update.name)
        if existing_survey and existing_survey.id != survey_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Survey with this name already exists"
            )
    
    return survey_repo.update(db, db_obj=survey, obj_in=survey_update)


@router.delete("/{survey_id}")
def delete_survey(survey_id: UUID, db: Session = Depends(get_db)):
    survey = survey_repo.delete(db, id=survey_id)
    if not survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Survey not found"
        )
    return {"message": "Survey deleted successfully"}


@router.get("/search/{name}", response_model=List[Survey])
def search_surveys(name: str, db: Session = Depends(get_db)):
    surveys = survey_repo.search_by_name(db, name=name)
    return surveys
