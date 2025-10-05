from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..database import get_db
from ..dto.answer import Answer, AnswerCreate, AnswerUpdate
from ..repository.answer_repository import AnswerRepository

router = APIRouter(prefix="/answers", tags=["answers"])
answer_repo = AnswerRepository()


@router.get("/", response_model=List[Answer])
def get_answers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    answers = answer_repo.get_multi(db, skip=skip, limit=limit)
    return answers


@router.get("/{answer_id}", response_model=Answer)
def get_answer(answer_id: UUID, db: Session = Depends(get_db)):
    answer = answer_repo.get(db, id=answer_id)
    if not answer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Answer not found"
        )
    return answer


@router.post("/", response_model=Answer, status_code=status.HTTP_201_CREATED)
def create_answer(answer: AnswerCreate, db: Session = Depends(get_db)):
    # Check if answer already exists for this worker, course, and question
    existing_answer = answer_repo.get_by_worker_course_and_question(
        db, 
        worker_id=answer.worker_id, 
        course_id=answer.course_id, 
        question_id=answer.question_id
    )
    if existing_answer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Answer already exists for this worker, course, and question"
        )
    
    return answer_repo.create(db, obj_in=answer)


@router.put("/{answer_id}", response_model=Answer)
def update_answer(
    answer_id: UUID, 
    answer_update: AnswerUpdate, 
    db: Session = Depends(get_db)
):
    answer = answer_repo.get(db, id=answer_id)
    if not answer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Answer not found"
        )
    
    # Check if new assignment conflicts with existing answer
    worker_id = answer_update.worker_id or answer.worker_id
    course_id = answer_update.course_id or answer.course_id
    question_id = answer_update.question_id or answer.question_id
    existing_answer = answer_repo.get_by_worker_course_and_question(
        db, 
        worker_id=worker_id, 
        course_id=course_id, 
        question_id=question_id
    )
    if existing_answer and existing_answer.id != answer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Answer already exists for this worker, course, and question"
        )
    
    return answer_repo.update(db, db_obj=answer, obj_in=answer_update)


@router.delete("/{answer_id}")
def delete_answer(answer_id: UUID, db: Session = Depends(get_db)):
    answer = answer_repo.delete(db, id=answer_id)
    if not answer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Answer not found"
        )
    return {"message": "Answer deleted successfully"}


@router.get("/worker/{worker_id}", response_model=List[Answer])
def get_answers_by_worker(worker_id: UUID, db: Session = Depends(get_db)):
    answers = answer_repo.get_by_worker(db, worker_id=worker_id)
    return answers


@router.get("/course/{course_id}", response_model=List[Answer])
def get_answers_by_course(course_id: UUID, db: Session = Depends(get_db)):
    answers = answer_repo.get_by_course(db, course_id=course_id)
    return answers


@router.get("/question/{question_id}", response_model=List[Answer])
def get_answers_by_question(question_id: UUID, db: Session = Depends(get_db)):
    answers = answer_repo.get_by_question(db, question_id=question_id)
    return answers


@router.get("/worker/{worker_id}/course/{course_id}", response_model=List[Answer])
def get_answers_by_worker_and_course(
    worker_id: UUID, 
    course_id: UUID, 
    db: Session = Depends(get_db)
):
    answers = answer_repo.get_by_worker_and_course(db, worker_id=worker_id, course_id=course_id)
    return answers


@router.get("/survey/{survey_id}", response_model=List[Answer])
def get_answers_by_survey(survey_id: UUID, db: Session = Depends(get_db)):
    answers = answer_repo.get_by_survey(db, survey_id=survey_id)
    return answers


@router.get("/search/{value}", response_model=List[Answer])
def search_answers(value: str, db: Session = Depends(get_db)):
    answers = answer_repo.search_by_value(db, value=value)
    return answers
