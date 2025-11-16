from sqlalchemy import Column, String, SmallInteger, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..database import Base
import uuid


class Worker(Base):
    __tablename__ = "workers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=False)
    rfc = Column(String(13), nullable=False, unique=True)
    curp = Column(String(18), nullable=False, unique=True)
    sex = Column(SmallInteger, nullable=False)  # 0 = mujer, 1 = hombre
    telephone = Column(String(10))
    email = Column(String(64), nullable=False, unique=True)
    password = Column(String(255), nullable=False)  # Almacenar como hash
    name = Column(String(45), nullable=False)
    fathers_surname = Column(String(40), nullable=False)
    mother_surname = Column(String(40))
    position = Column(SmallInteger, nullable=False)  # 0 = docente, 1 = jefe de departamento

    # Relationships
    department = relationship("Department", back_populates="workers")
    instructor_courses = relationship("Instructor", back_populates="worker")
    enrollments = relationship("Enrolling", back_populates="worker")
    attendances = relationship("Attendance", back_populates="worker")
    answers = relationship("Answer", back_populates="worker")
