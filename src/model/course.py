from sqlalchemy import Column, String, Date, Time, Text, SmallInteger, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..database import Base
import uuid


class Course(Base):
    __tablename__ = "courses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    period_id = Column(UUID(as_uuid=True), ForeignKey("periods.id"), nullable=False)
    target = Column(String(255), nullable=False)
    name = Column(String(150), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    course_type = Column(SmallInteger, nullable=False)  # 0 = diplomado, 1 = taller
    modality = Column(SmallInteger, nullable=False)  # 0 = virtual, 1 = presencial
    course_profile = Column(SmallInteger, nullable=False)  # 0 = formacion, 1 = actualización docente
    goal = Column(Text, nullable=False)
    details = Column(Text)

    # Relationships
    period = relationship("Period", back_populates="courses")
    instructors = relationship("Instructor", back_populates="course")
    enrollments = relationship("Enrolling", back_populates="course")
    attendances = relationship("Attendance", back_populates="course")
    answers = relationship("Answer", back_populates="course")
