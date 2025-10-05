from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..database import get_db
from ..dto.question import Question, QuestionCreate, QuestionUpdate
from ..repository.question_repository import QuestionRepository

router = APIRouter(prefix="/questions", tags=["questions"])
question_repo = QuestionRepository()


@router.get("/", response_model=List[Question])
def get_questions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    questions = question_repo.get_multi(db, skip=skip, limit=limit)
    return questions


@router.get("/{question_id}", response_model=Question)
def get_question(question_id: UUID, db: Session = Depends(get_db)):
    question = question_repo.get(db, id=question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    return question


@router.post("/", response_model=Question, status_code=status.HTTP_201_CREATED)
def create_question(question: QuestionCreate, db: Session = Depends(get_db)):
    # Check if position already exists for this survey
    existing_question = question_repo.get_by_position(db, survey_id=question.survey_id, position=question.position)
    if existing_question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question with this position already exists for this survey"
        )
    
    return question_repo.create(db, obj_in=question)


@router.put("/{question_id}", response_model=Question)
def update_question(
    question_id: UUID, 
    question_update: QuestionUpdate, 
    db: Session = Depends(get_db)
):
    question = question_repo.get(db, id=question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    # Check if new position conflicts with existing question
    if question_update.position:
        survey_id = question_update.survey_id or question.survey_id
        existing_question = question_repo.get_by_position(db, survey_id=survey_id, position=question_update.position)
        if existing_question and existing_question.id != question_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Question with this position already exists for this survey"
            )
    
    return question_repo.update(db, db_obj=question, obj_in=question_update)


@router.delete("/{question_id}")
def delete_question(question_id: UUID, db: Session = Depends(get_db)):
    question = question_repo.delete(db, id=question_id)
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    return {"message": "Question deleted successfully"}


@router.get("/survey/{survey_id}", response_model=List[Question])
def get_questions_by_survey(survey_id: UUID, db: Session = Depends(get_db)):
    questions = question_repo.get_by_survey(db, survey_id=survey_id)
    return questions


@router.get("/search/{text}", response_model=List[Question])
def search_questions(text: str, db: Session = Depends(get_db)):
    questions = question_repo.search_by_text(db, text=text)
    return questions
