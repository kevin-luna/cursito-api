from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import PositiveInt
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..database import get_db
from ..dto.survey import Survey, SurveyCreate, SurveyUpdate
from ..dto.answer import Answer, SurveyAnswersSubmit, AnswerCreate
from ..dto.pagination import PaginatedResponse
from ..repository.survey_repository import SurveyRepository
from ..repository.answer_repository import AnswerRepository
from ..repository.question_repository import QuestionRepository

router = APIRouter(prefix="/surveys", tags=["surveys"])
survey_repo = SurveyRepository()
answer_repo = AnswerRepository()
question_repo = QuestionRepository()


@router.get("/", response_model=PaginatedResponse[Survey])
def get_surveys(page: PositiveInt = 1, limit: int = 100, db: Session = Depends(get_db)):
    surveys, total_pages, total_count = survey_repo.get_multi_paginated(db, page=page, limit=limit)
    return PaginatedResponse(
        items=surveys,
        total_pages=total_pages,
        page=page,
        total_count=total_count
    )


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


@router.get("/search/{name}", response_model=PaginatedResponse[Survey])
def search_surveys(name: str, page: PositiveInt = 1, limit: int = 100, db: Session = Depends(get_db)):
    surveys, total_pages, total_count = survey_repo.search_by_name_paginated(db, name=name, page=page, limit=limit)
    return PaginatedResponse(
        items=surveys,
        total_pages=total_pages,
        page=page,
        total_count=total_count
    )


@router.post("/{survey_id}/submit", response_model=List[Answer], status_code=status.HTTP_201_CREATED)
def submit_survey_answers(
    survey_id: UUID,
    submission: SurveyAnswersSubmit,
    db: Session = Depends(get_db)
):
    """
    Submit all answers for a worker's survey response for a specific course.
    Validates that the worker has not already responded to this survey for this course.
    """
    # Verify survey exists
    survey = survey_repo.get(db, id=survey_id)
    if not survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Survey not found"
        )

    # Check if worker has already answered this survey for this course
    existing_answers = answer_repo.get_by_worker_survey_and_course(
        db,
        worker_id=submission.worker_id,
        survey_id=survey_id,
        course_id=submission.course_id
    )

    if existing_answers:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Worker has already submitted answers for this survey and course"
        )

    # Get all questions for this survey to validate
    questions = question_repo.get_by_survey(db, survey_id=survey_id)
    question_ids = {q.id for q in questions}

    # Validate that all question_ids belong to this survey
    submitted_question_ids = {answer.question_id for answer in submission.answers}
    invalid_questions = submitted_question_ids - question_ids
    if invalid_questions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid question IDs for this survey: {invalid_questions}"
        )

    created_answers = []

    # Create all answers (we already validated they don't exist)
    for answer_item in submission.answers:
        answer_create = AnswerCreate(
            worker_id=submission.worker_id,
            course_id=submission.course_id,
            question_id=answer_item.question_id,
            value=answer_item.value
        )
        new_answer = answer_repo.create(db, obj_in=answer_create)
        created_answers.append(new_answer)

    return created_answers


@router.get("/{survey_id}/worker/{worker_id}/course/{course_id}/answers", response_model=List[Answer])
def get_worker_survey_answers(
    survey_id: UUID,
    worker_id: UUID,
    course_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get all answers from a specific worker for a specific survey and course.
    Returns all responses without pagination.
    """
    # Verify survey exists
    survey = survey_repo.get(db, id=survey_id)
    if not survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Survey not found"
        )

    answers = answer_repo.get_by_worker_survey_and_course(
        db,
        worker_id=worker_id,
        survey_id=survey_id,
        course_id=course_id
    )

    return answers
