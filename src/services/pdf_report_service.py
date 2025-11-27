"""
PDF Report Generation Service
Provides functions to generate various PDF reports using ReportLab
"""
from io import BytesIO
from typing import List, Optional
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.platypus.flowables import KeepTogether
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from sqlalchemy.orm import Session
from uuid import UUID

from ..model.course import Course
from ..model.worker import Worker
from ..model.enrolling import Enrolling
from ..model.answer import Answer
from ..model.question import Question
from ..model.instructor import Instructor
from ..repository.course_repository import CourseRepository
from ..repository.worker_repository import WorkerRepository
from ..repository.enrolling_repository import EnrollingRepository
from ..repository.answer_repository import AnswerRepository
from ..repository.question_repository import QuestionRepository
from ..repository.instructor_repository import InstructorRepository


class PDFReportService:
    """Service for generating PDF reports"""

    def __init__(self):
        self.course_repo = CourseRepository()
        self.worker_repo = WorkerRepository()
        self.enrolling_repo = EnrollingRepository()
        self.answer_repo = AnswerRepository()
        self.question_repo = QuestionRepository()
        self.instructor_repo = InstructorRepository()

    def _get_styles(self):
        """Get custom styles for the PDF"""
        styles = getSampleStyleSheet()

        # Custom title style
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#1976d2'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Custom subtitle style
        styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#424242'),
            spaceAfter=10,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        ))

        # Custom info style
        styles.add(ParagraphStyle(
            name='CustomInfo',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#616161'),
            spaceAfter=6,
            alignment=TA_LEFT
        ))

        return styles

    def generate_attendance_list(self, db: Session, course_id: UUID) -> BytesIO:
        """
        Generate attendance list PDF for a course
        Includes: course info, enrolled workers with RFC, gender, and grades
        """
        # Fetch course data
        course = self.course_repo.get(db, course_id)
        if not course:
            raise ValueError(f"Course with ID {course_id} not found")

        # Fetch enrollments
        enrollments = self.enrolling_repo.get_by_course(db, course_id)

        # Create PDF buffer
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75*inch, bottomMargin=0.75*inch)
        story = []
        styles = self._get_styles()

        # Header
        story.append(Paragraph("LISTA DE ASISTENCIA", styles['CustomTitle']))
        story.append(Spacer(1, 0.2*inch))

        # Course information
        course_info = [
            f"<b>Curso:</b> {course.name}",
            f"<b>Tipo:</b> {'Diplomado' if course.course_type == 0 else 'Taller'}",
            f"<b>Modalidad:</b> {'Virtual' if course.modality == 0 else 'Presencial'}",
            f"<b>Perfil:</b> {'Formación' if course.course_profile == 0 else 'Actualización Docente'}",
            f"<b>Periodo:</b> {course.start_date} - {course.end_date}" if course.start_date and course.end_date else "",
            f"<b>Horario:</b> {course.start_time} - {course.end_time}" if course.start_time and course.end_time else "",
        ]

        for info in course_info:
            if info:
                story.append(Paragraph(info, styles['CustomInfo']))

        story.append(Spacer(1, 0.3*inch))

        # Attendance table
        table_data = [
            ['No.', 'Nombre Completo', 'RFC', 'Sexo', 'Calificación']
        ]

        for idx, enrollment in enumerate(enrollments, start=1):
            worker = enrollment.worker
            full_name = f"{worker.name} {worker.father_surname or ''} {worker.mother_surname or ''}".strip()
            gender = 'M' if worker.sex == 0 else 'F' if worker.sex == 1 else 'N/A'
            grade = str(enrollment.final_grade) if enrollment.final_grade else 'N/A'

            table_data.append([
                str(idx),
                full_name,
                worker.rfc or 'N/A',
                gender,
                grade
            ])

        # Create table
        table = Table(table_data, colWidths=[0.5*inch, 3*inch, 1.5*inch, 0.8*inch, 1*inch])
        table.setStyle(TableStyle([
            # Header style
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976d2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

            # Body style
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),

            # Grid
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        story.append(table)
        story.append(Spacer(1, 0.3*inch))

        # Footer
        footer_text = f"<i>Total de participantes: {len(enrollments)}</i><br/>" \
                     f"<i>Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}</i>"
        story.append(Paragraph(footer_text, styles['CustomInfo']))

        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer

    def generate_enrollment_certificate(self, db: Session, worker_id: UUID, course_id: UUID) -> BytesIO:
        """
        Generate enrollment certificate PDF for a worker in a course
        Includes: worker info, course info, enrollment date
        """
        # Fetch data
        worker = self.worker_repo.get(db, worker_id)
        if not worker:
            raise ValueError(f"Worker with ID {worker_id} not found")

        course = self.course_repo.get(db, course_id)
        if not course:
            raise ValueError(f"Course with ID {course_id} not found")

        # Get enrollment
        enrollments = self.enrolling_repo.get_by_worker(db, worker_id)
        enrollment = next((e for e in enrollments if e.course_id == course_id), None)
        if not enrollment:
            raise ValueError(f"Enrollment not found for worker {worker_id} in course {course_id}")

        # Create PDF buffer
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=inch, bottomMargin=inch)
        story = []
        styles = self._get_styles()

        # Header
        story.append(Paragraph("CÉDULA DE INSCRIPCIÓN", styles['CustomTitle']))
        story.append(Spacer(1, 0.4*inch))

        # Worker Information Section
        story.append(Paragraph("DATOS DEL TRABAJADOR", styles['CustomSubtitle']))
        story.append(Spacer(1, 0.1*inch))

        worker_data = [
            ['Campo', 'Información'],
            ['Nombre Completo', f"{worker.name} {worker.father_surname or ''} {worker.mother_surname or ''}".strip()],
            ['RFC', worker.rfc or 'N/A'],
            ['CURP', worker.curp or 'N/A'],
            ['Email', worker.email or 'N/A'],
            ['Teléfono', worker.telephone or 'N/A'],
            ['Sexo', 'Masculino' if worker.sex == 0 else 'Femenino' if worker.sex == 1 else 'N/A'],
            ['Departamento', worker.department.name if worker.department else 'N/A'],
            ['Rol', 'Jefe de Departamento' if worker.position == 0 else 'Docente' if worker.role == 1 else 'N/A'],
        ]

        worker_table = Table(worker_data, colWidths=[2*inch, 4.5*inch])
        worker_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976d2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#e3f2fd')),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        story.append(worker_table)
        story.append(Spacer(1, 0.3*inch))

        # Course Information Section
        story.append(Paragraph("DATOS DEL CURSO", styles['CustomSubtitle']))
        story.append(Spacer(1, 0.1*inch))

        course_data = [
            ['Campo', 'Información'],
            ['Nombre del Curso', course.name],
            ['Objetivo', course.target or 'N/A'],
            ['Tipo', 'Diplomado' if course.course_type == 0 else 'Taller'],
            ['Modalidad', 'Virtual' if course.modality == 0 else 'Presencial'],
            ['Perfil', 'Formación' if course.course_profile == 0 else 'Actualización Docente'],
            ['Fecha Inicio', str(course.start_date) if course.start_date else 'N/A'],
            ['Fecha Fin', str(course.end_date) if course.end_date else 'N/A'],
            ['Horario', f"{course.start_time} - {course.end_time}" if course.start_time and course.end_time else 'N/A'],
            ['Meta', course.goal or 'N/A'],
        ]

        course_table = Table(course_data, colWidths=[2*inch, 4.5*inch])
        course_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976d2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#e3f2fd')),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        story.append(course_table)
        story.append(Spacer(1, 0.3*inch))

        # Enrollment Information
        story.append(Paragraph("DATOS DE INSCRIPCIÓN", styles['CustomSubtitle']))
        story.append(Spacer(1, 0.1*inch))

        enrollment_data = [
        #    ['Fecha de Inscripción', str(enrollment.created_at.date()) if enrollment.created_at else 'N/A'],
            ['Calificación Final', str(enrollment.final_grade) if enrollment.final_grade else 'Pendiente'],
        ]

        enrollment_table = Table(enrollment_data, colWidths=[2*inch, 4.5*inch])
        enrollment_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e3f2fd')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        story.append(enrollment_table)
        story.append(Spacer(1, 0.5*inch))

        # Footer
        footer_text = f"<i>Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}</i>"
        story.append(Paragraph(footer_text, styles['CustomInfo']))

        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer

    def generate_instructor_courses_list(self, db: Session, worker_id: UUID) -> BytesIO:
        """
        Generate PDF list of courses taught by an instructor
        Includes: all course information for each course
        """
        # Fetch worker
        worker = self.worker_repo.get(db, worker_id)
        if not worker:
            raise ValueError(f"Worker with ID {worker_id} not found")

        # Get instructor records
        instructor_records = self.instructor_repo.get_by_worker(db, worker_id)

        # Create PDF buffer
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75*inch, bottomMargin=0.75*inch)
        story = []
        styles = self._get_styles()

        # Header
        story.append(Paragraph("LISTA DE CURSOS IMPARTIDOS", styles['CustomTitle']))
        story.append(Spacer(1, 0.2*inch))

        # Instructor info
        instructor_name = f"{worker.name} {worker.father_surname or ''} {worker.mother_surname or ''}".strip()
        story.append(Paragraph(f"<b>Instructor:</b> {instructor_name}", styles['CustomInfo']))
        story.append(Paragraph(f"<b>RFC:</b> {worker.rfc or 'N/A'}", styles['CustomInfo']))
        story.append(Paragraph(f"<b>Departamento:</b> {worker.department.name if worker.department else 'N/A'}", styles['CustomInfo']))
        story.append(Spacer(1, 0.3*inch))

        if not instructor_records:
            story.append(Paragraph("<i>No se encontraron cursos impartidos por este instructor.</i>", styles['CustomInfo']))
        else:
            # Add each course
            for idx, instructor_record in enumerate(instructor_records, start=1):
                course = instructor_record.course

                # Course header
                story.append(Paragraph(f"CURSO {idx}: {course.name}", styles['CustomSubtitle']))
                story.append(Spacer(1, 0.1*inch))

                # Course details table
                course_data = [
                    ['Campo', 'Información'],
                    ['Nombre', course.name],
                    ['Objetivo', course.target or 'N/A'],
                    ['Tipo', 'Diplomado' if course.course_type == 0 else 'Taller'],
                    ['Modalidad', 'Virtual' if course.modality == 0 else 'Presencial'],
                    ['Perfil', 'Formación' if course.course_profile == 0 else 'Actualización Docente'],
                    ['Fecha Inicio', str(course.start_date) if course.start_date else 'N/A'],
                    ['Fecha Fin', str(course.end_date) if course.end_date else 'N/A'],
                    ['Horario', f"{course.start_time} - {course.end_time}" if course.start_time and course.end_time else 'N/A'],
                    ['Meta', course.goal or 'N/A'],
                    ['Detalles', course.details or 'N/A'],
                ]

                course_table = Table(course_data, colWidths=[2*inch, 4.5*inch])
                course_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976d2')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#e3f2fd')),
                    ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 8),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))

                story.append(course_table)
                story.append(Spacer(1, 0.3*inch))

        # Footer
        footer_text = f"<i>Total de cursos: {len(instructor_records)}</i><br/>" \
                     f"<i>Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}</i>"
        story.append(Paragraph(footer_text, styles['CustomInfo']))

        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer

    def generate_survey_responses(self, db: Session, worker_id: UUID, course_id: UUID, survey_type: str) -> BytesIO:
        """
        Generate PDF with survey responses for a worker in a course
        survey_type: 'followup' or 'opinion'
        """
        # Survey IDs
        FOLLOWUP_SURVEY_ID = UUID('3d1fa6a2-6d4a-42fa-a474-68c83156f541')
        OPINION_SURVEY_ID = UUID('c2a77b75-8552-4fe0-ab49-231803244ace')

        survey_id = FOLLOWUP_SURVEY_ID if survey_type == 'followup' else OPINION_SURVEY_ID
        survey_name = "Evaluación de Seguimiento" if survey_type == 'followup' else "Encuesta de Opinión"

        # Fetch data
        worker = self.worker_repo.get(db, worker_id)
        if not worker:
            raise ValueError(f"Worker with ID {worker_id} not found")

        course = self.course_repo.get(db, course_id)
        if not course:
            raise ValueError(f"Course with ID {course_id} not found")

        # Get answers
        answers = self.answer_repo.get_by_worker_survey_and_course(db, worker_id, survey_id, course_id)

        if not answers:
            raise ValueError(f"No answers found for this survey")

        # Create PDF buffer
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75*inch, bottomMargin=0.75*inch)
        story = []
        styles = self._get_styles()

        # Header
        story.append(Paragraph(survey_name.upper(), styles['CustomTitle']))
        story.append(Spacer(1, 0.2*inch))

        # Worker and course info
        worker_name = f"{worker.name} {worker.father_surname or ''} {worker.mother_surname or ''}".strip()
        story.append(Paragraph(f"<b>Trabajador:</b> {worker_name}", styles['CustomInfo']))
        story.append(Paragraph(f"<b>Curso:</b> {course.name}", styles['CustomInfo']))
        story.append(Paragraph(f"<b>Fecha de generación:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['CustomInfo']))
        story.append(Spacer(1, 0.3*inch))

        # Responses
        story.append(Paragraph("RESPUESTAS", styles['CustomSubtitle']))
        story.append(Spacer(1, 0.1*inch))

        # Create table with questions and answers
        table_data = [['No.', 'Pregunta', 'Respuesta']]

        for idx, answer in enumerate(answers, start=1):
            question = answer.question
            question_text = question.question if question else 'N/A'

            # Format answer value based on type
            answer_value = answer.value

            # Try to parse as JSON for multi-select questions
            try:
                import json
                parsed = json.loads(answer_value)
                if isinstance(parsed, dict):
                    # Multi-select checkbox format
                    selected = [k for k, v in parsed.items() if v]
                    answer_value = ', '.join(selected) if selected else 'Ninguna'
                elif isinstance(parsed, list):
                    answer_value = ', '.join(str(item) for item in parsed)
            except:
                # Try to interpret as Likert scale
                if answer_value.isdigit():
                    value = int(answer_value)
                    likert_map = {
                        1: 'Totalmente en desacuerdo',
                        2: 'En desacuerdo',
                        3: 'Neutral',
                        4: 'De acuerdo',
                        5: 'Totalmente de acuerdo'
                    }
                    answer_value = likert_map.get(value, answer_value)

            table_data.append([
                str(idx),
                Paragraph(question_text, styles['Normal']),
                Paragraph(answer_value, styles['Normal'])
            ])

        # Create table
        table = Table(table_data, colWidths=[0.5*inch, 4*inch, 2*inch])
        table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1976d2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

            # Body
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),

            # Grid
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        story.append(table)

        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
