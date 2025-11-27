"""
Report Controller
Handles PDF report generation endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from uuid import UUID

from ..database import get_db
from ..services.pdf_report_service import PDFReportService

router = APIRouter(prefix="/reports", tags=["Reports"])
pdf_service = PDFReportService()


@router.get("/attendance/{course_id}")
def download_attendance_list(
    course_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Download attendance list PDF for a course

    Returns a PDF with:
    - Course information
    - List of enrolled workers with attendance per day
    """
    try:
        pdf_buffer = pdf_service.generate_attendance_list(db, course_id)

        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=attendance_list_{course_id}.pdf"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")


@router.get("/grades/{course_id}")
def download_grades_list(
    course_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Download grades list PDF for a course

    Returns a PDF with:
    - Course information
    - List of enrolled workers with RFC, gender, and final grades
    """
    try:
        pdf_buffer = pdf_service.generate_grades_list(db, course_id)

        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=grades_list_{course_id}.pdf"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")


@router.get("/enrollment/{worker_id}/{course_id}")
def download_enrollment_certificate(
    worker_id: UUID,
    course_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Download enrollment certificate PDF for a worker in a course

    Returns a PDF with:
    - Worker information
    - Course information
    - Enrollment date
    """
    try:
        pdf_buffer = pdf_service.generate_enrollment_certificate(db, worker_id, course_id)

        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=enrollment_certificate_{worker_id}_{course_id}.pdf"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")


@router.get("/instructor-courses/{worker_id}")
def download_instructor_courses_list(
    worker_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Download list of courses taught by an instructor

    Returns a PDF with:
    - Instructor information
    - All courses taught with full details
    """
    try:
        pdf_buffer = pdf_service.generate_instructor_courses_list(db, worker_id)

        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=instructor_courses_{worker_id}.pdf"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")


@router.get("/survey/{worker_id}/{course_id}/followup")
def download_followup_survey_responses(
    worker_id: UUID,
    course_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Download follow-up survey responses PDF

    Returns a PDF with:
    - Worker and course information
    - All follow-up survey responses
    """
    try:
        pdf_buffer = pdf_service.generate_survey_responses(db, worker_id, course_id, 'followup')

        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=followup_survey_{worker_id}_{course_id}.pdf"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")


@router.get("/survey/{worker_id}/{course_id}/opinion")
def download_opinion_survey_responses(
    worker_id: UUID,
    course_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Download opinion survey responses PDF

    Returns a PDF with:
    - Worker and course information
    - All opinion survey responses
    """
    try:
        pdf_buffer = pdf_service.generate_survey_responses(db, worker_id, course_id, 'opinion')

        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=opinion_survey_{worker_id}_{course_id}.pdf"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")
