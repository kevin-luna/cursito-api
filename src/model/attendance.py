from sqlalchemy import Column, Date, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..database import Base
import uuid


class Attendance(Base):
    __tablename__ = "attendances"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    worker_id = Column(UUID(as_uuid=True), ForeignKey("worker.id"), nullable=False)
    course_id = Column(UUID(as_uuid=True), ForeignKey("course.id"), nullable=False)
    date = Column(Date, nullable=False)

    # Relationships
    worker = relationship("Worker", back_populates="attendances")
    course = relationship("Course", back_populates="attendances")

    # Constraints
    __table_args__ = (
        UniqueConstraint('worker_id', 'course_id', 'date', name='unique_worker_course_date'),
    )
