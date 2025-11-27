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
            gender = 'M' if worker.sex == 1 else 'F' if worker.sex == 0 else 'N/A'
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
            ['Sexo', 'Masculino' if worker.sex == 1 else 'Femenino' if worker.sex == 0 else 'N/A'],
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

        # Generate responses based on survey type
        if survey_type == 'followup':
            self._add_followup_survey_content(story, styles, answers)
        else:
            self._add_opinion_survey_content(story, styles, answers)

        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer

    def _add_followup_survey_content(self, story, styles, answers):
        """Add follow-up survey content in form format (no tables)"""
        import json

        # Create answer map
        answer_map = {str(answer.question_id): answer.value for answer in answers}

        # Question IDs for follow-up survey
        question_ids = {
            'q1': '35860b6b-24b7-4269-a4d5-5f3e9d7c6174',
            'q2': '99d63963-cdc6-41b7-bcbf-01fe09ef6c88',
            'q3': '0ef61261-a82e-43dc-b13e-642430980b5c',
            'q4': 'f27d05f4-7bfa-4d41-ad34-b0154943d0f6',
            'obstacles': '4b67a52c-ee25-4970-9b1a-8881eadf83a8',
            'comments': 'b5673bc5-6d8e-46f6-9839-81dfa7b63ec2'
        }

        # Likert options
        likert_options = [
            '1 - En desacuerdo',
            '2 - Parcialmente en desacuerdo',
            '3 - Indiferente',
            '4 - Parcialmente de acuerdo',
            '5 - Totalmente de acuerdo'
        ]

        # Section 1: Aplicación de Conocimientos
        story.append(Paragraph("APLICACIÓN DE CONOCIMIENTOS", styles['CustomSubtitle']))
        story.append(Spacer(1, 0.1*inch))

        questions_section1 = [
            "1. Los conocimientos adquiridos en el curso tienen aplicación en su ámbito laboral en el corto y mediano plazo.",
            "2. El curso le ayudó a mejorar el desempeño de sus funciones.",
            "3. El curso le ayudó a considerar nuevas formas de trabajo."
        ]

        for idx, question_text in enumerate(questions_section1, 1):
            story.append(Paragraph(f"<b>{question_text}</b>", styles['Normal']))
            story.append(Spacer(1, 0.05*inch))

            # Get the answer value
            answer_value = answer_map.get(question_ids[f'q{idx}'], '0')
            try:
                selected_value = int(answer_value)
            except:
                selected_value = 0

            # Display options with selection marked
            for option in likert_options:
                option_value = int(option[0])
                if option_value == selected_value:
                    story.append(Paragraph(f"✓ <b>{option}</b>", styles['Normal']))
                else:
                    story.append(Paragraph(f"○ {option}", styles['Normal']))

            story.append(Spacer(1, 0.15*inch))

        # Section 2: Beneficios del Curso
        story.append(Paragraph("BENEFICIOS DEL CURSO", styles['CustomSubtitle']))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph("<b>4. El curso que tomó le:</b>", styles['Normal']))
        story.append(Paragraph("<i>(Seleccione todas las opciones que apliquen)</i>", styles['CustomInfo']))
        story.append(Spacer(1, 0.05*inch))

        # Parse question 4 (multiple selection)
        q4_value = answer_map.get(question_ids['q4'], '{}')
        try:
            q4_selected = json.loads(q4_value)
        except:
            q4_selected = {}

        q4_options = [
            ('a', 'Produjo un incremento en su motivación'),
            ('b', 'Ha servido para su desarrollo personal'),
            ('c', 'Sirvió para integrarse mejor con sus compañeros(as) de trabajo'),
            ('d', 'Produjo una mayor comprensión del servicio que presta al Tecnológico Nacional de México'),
            ('e', 'Facilitó una mejoría en su actitud hacia el Tecnológico Nacional de México o sus compañeros de trabajo'),
            ('f', 'Permitió desarrollar algunas habilidades adicionales'),
            ('g', 'Generó una mejor comprensión de los conceptos generales del curso aplicables en su trabajo'),
            ('h', 'Ofrecieron valores compatibles con los suyos')
        ]

        for key, text in q4_options:
            if q4_selected.get(key, False):
                story.append(Paragraph(f"✓ <b>{text}</b>", styles['Normal']))
            else:
                story.append(Paragraph(f"○ {text}", styles['Normal']))

        story.append(Spacer(1, 0.2*inch))

        # Section 3: Obstáculos
        story.append(Paragraph("OBSTÁCULOS PARA APLICAR CONOCIMIENTOS", styles['CustomSubtitle']))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph("<i>En caso de considerar que existen obstáculos que le impidan aplicar los conocimientos del curso, señale los correspondientes:</i>", styles['CustomInfo']))
        story.append(Spacer(1, 0.05*inch))

        # Parse obstacles
        obstacles_value = answer_map.get(question_ids['obstacles'], '{}')
        try:
            obstacles = json.loads(obstacles_value)
        except:
            obstacles = {}

        obstacle_options = [
            ('equipment', 'Falta de equipo y/o material'),
            ('support', 'Falta de apoyo en el área de trabajo'),
            ('other', 'Otro')
        ]

        for key, text in obstacle_options:
            if obstacles.get(key, False):
                story.append(Paragraph(f"✓ <b>{text}</b>", styles['Normal']))
                if key == 'other' and obstacles.get('otherText'):
                    story.append(Paragraph(f"   <i>Especificación: {obstacles.get('otherText')}</i>", styles['CustomInfo']))
            else:
                story.append(Paragraph(f"○ {text}", styles['Normal']))

        story.append(Spacer(1, 0.2*inch))

        # Section 4: Comments
        story.append(Paragraph("COMENTARIOS Y SUGERENCIAS", styles['CustomSubtitle']))
        story.append(Spacer(1, 0.1*inch))

        comments = answer_map.get(question_ids['comments'], '')
        if comments:
            story.append(Paragraph(comments, styles['Normal']))
        else:
            story.append(Paragraph("<i>Sin comentarios</i>", styles['CustomInfo']))

    def _add_opinion_survey_content(self, story, styles, answers):
        """Add opinion survey content in form format (no tables)"""

        # Create answer map
        answer_map = {str(answer.question_id): answer.value for answer in answers}

        # Question IDs for opinion survey
        instructor_ids = [
            'c613744d-a2cc-4e5b-b0a4-c9e1488b7658',
            'd6ade9fe-b02a-4435-8254-00b009fcc8a6',
            '6577645c-96f6-495d-ae31-65727e029d68',
            'a2b6fbd2-e431-485d-910f-d1440c4fc6f4',
            '8775f5a8-d88a-46c1-9eb8-9a44a1aee56a',
            '747f6e4a-1103-4fd3-91da-7743c623dd60',
            'e6b27138-4041-4253-a1fb-8a6c530ed06c'
        ]
        material_ids = [
            '44c6af40-e6c3-4b01-90d6-7b1bc20f33d1',
            '2b884a85-b41e-4c91-8a42-c98a41583f5f',
            'e619993e-cc69-45bb-a990-6e3bf840dca7'
        ]
        course_ids = [
            'f47b08ed-1f5b-4e4f-b0d4-d2446df19157',
            'c648f340-b4d4-4d8a-85bb-501314c4b83a',
            '8b0cc047-eb89-4409-a81a-ac481299369a',
            'e4e69b3d-a4e2-4c4b-8991-d38071d9a20f'
        ]
        infrastructure_ids = [
            'c16802fa-af4a-4855-bb20-f20ceaa2f28e',
            '43292b9b-14d1-40ca-96a9-77bc88f49128',
            'f2665c3d-d0d5-405d-ac73-533c3bc41d29',
            'a3326530-b3f4-4122-a38f-bf2b231b0de0',
            'cba33950-6190-4401-a749-26dff08cb6ab',
            '4e376ddf-922b-4d57-8551-0cd679d218db'
        ]
        comments_id = '085773da-7b07-4619-8178-cdffcb5ea7dc'

        # Likert options
        likert_options = [
            '1 - En desacuerdo',
            '2 - Parcialmente en desacuerdo',
            '3 - Indiferente',
            '4 - Parcialmente de acuerdo',
            '5 - Totalmente de acuerdo'
        ]

        # Questions text
        instructor_questions = [
            "Expuso el objetivo y temario del curso.",
            "Mostró dominio del contenido abordado.",
            "Fomentó la participación del grupo.",
            "Aclaró las dudas que se presentaron.",
            "Dio retroalimentación a los ejercicios realizados.",
            "Aplicó una evaluación final relacionada con los contenidos del curso.",
            "Inició y concluyó puntualmente las sesiones."
        ]
        material_questions = [
            "El material didáctico fue útil a lo largo del curso.",
            "La impresión del material didáctico fue legible.",
            "La variedad del material didáctico fue suficiente para apoyar su aprendizaje."
        ]
        course_questions = [
            "La distribución del tiempo fue adecuada para cubrir el contenido.",
            "Los temas fueron suficientes para alcanzar el objetivo del curso.",
            "El curso comprendió ejercicios de práctica relacionados con el contenido.",
            "El curso cubrió sus expectativas."
        ]
        infrastructure_questions = [
            "La iluminación del aula fue adecuada.",
            "La ventilación del aula fue adecuada.",
            "El aseo del aula fue adecuado.",
            "El servicio de los sanitarios fue adecuado (limpieza, abasto de papel, toallas, jabón, etc.).",
            "El servicio de café fue adecuado.",
            "Recibió apoyo del personal que coordinó el curso."
        ]

        # Section 1: Instructor
        story.append(Paragraph("INSTRUCTOR", styles['CustomSubtitle']))
        story.append(Spacer(1, 0.1*inch))

        for idx, (question_id, question_text) in enumerate(zip(instructor_ids, instructor_questions), 1):
            story.append(Paragraph(f"<b>{idx}. {question_text}</b>", styles['Normal']))
            story.append(Spacer(1, 0.05*inch))

            answer_value = answer_map.get(question_id, '0')
            try:
                selected_value = int(answer_value)
            except:
                selected_value = 0

            for option in likert_options:
                option_value = int(option[0])
                if option_value == selected_value:
                    story.append(Paragraph(f"✓ <b>{option}</b>", styles['Normal']))
                else:
                    story.append(Paragraph(f"○ {option}", styles['Normal']))

            story.append(Spacer(1, 0.15*inch))

        # Section 2: Material Didáctico
        story.append(PageBreak())
        story.append(Paragraph("MATERIAL DIDÁCTICO", styles['CustomSubtitle']))
        story.append(Spacer(1, 0.1*inch))

        for idx, (question_id, question_text) in enumerate(zip(material_ids, material_questions), 1):
            story.append(Paragraph(f"<b>{idx}. {question_text}</b>", styles['Normal']))
            story.append(Spacer(1, 0.05*inch))

            answer_value = answer_map.get(question_id, '0')
            try:
                selected_value = int(answer_value)
            except:
                selected_value = 0

            for option in likert_options:
                option_value = int(option[0])
                if option_value == selected_value:
                    story.append(Paragraph(f"✓ <b>{option}</b>", styles['Normal']))
                else:
                    story.append(Paragraph(f"○ {option}", styles['Normal']))

            story.append(Spacer(1, 0.15*inch))

        # Section 3: Curso
        story.append(Paragraph("CURSO", styles['CustomSubtitle']))
        story.append(Spacer(1, 0.1*inch))

        for idx, (question_id, question_text) in enumerate(zip(course_ids, course_questions), 1):
            story.append(Paragraph(f"<b>{idx}. {question_text}</b>", styles['Normal']))
            story.append(Spacer(1, 0.05*inch))

            answer_value = answer_map.get(question_id, '0')
            try:
                selected_value = int(answer_value)
            except:
                selected_value = 0

            for option in likert_options:
                option_value = int(option[0])
                if option_value == selected_value:
                    story.append(Paragraph(f"✓ <b>{option}</b>", styles['Normal']))
                else:
                    story.append(Paragraph(f"○ {option}", styles['Normal']))

            story.append(Spacer(1, 0.15*inch))

        # Section 4: Infraestructura
        story.append(Paragraph("INFRAESTRUCTURA", styles['CustomSubtitle']))
        story.append(Spacer(1, 0.1*inch))

        for idx, (question_id, question_text) in enumerate(zip(infrastructure_ids, infrastructure_questions), 1):
            story.append(Paragraph(f"<b>{idx}. {question_text}</b>", styles['Normal']))
            story.append(Spacer(1, 0.05*inch))

            answer_value = answer_map.get(question_id, '0')
            try:
                selected_value = int(answer_value)
            except:
                selected_value = 0

            for option in likert_options:
                option_value = int(option[0])
                if option_value == selected_value:
                    story.append(Paragraph(f"✓ <b>{option}</b>", styles['Normal']))
                else:
                    story.append(Paragraph(f"○ {option}", styles['Normal']))

            story.append(Spacer(1, 0.15*inch))

        # Section 5: Comments
        story.append(Paragraph("COMENTARIOS Y SUGERENCIAS", styles['CustomSubtitle']))
        story.append(Spacer(1, 0.1*inch))

        comments = answer_map.get(comments_id, '')
        if comments:
            story.append(Paragraph(comments, styles['Normal']))
        else:
            story.append(Paragraph("<i>Sin comentarios</i>", styles['CustomInfo']))
