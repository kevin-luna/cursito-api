from sqlalchemy import Column, ForeignKey, UniqueConstraint, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..database import Base
import uuid


class Enrolling(Base):
    __tablename__ = "enrollings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    worker_id = Column(UUID(as_uuid=True), ForeignKey("worker.id"), nullable=False)
    course_id = Column(UUID(as_uuid=True), ForeignKey("course.id"), nullable=False)
    final_grade = Column(Numeric(5, 2))

    # Relationships
    worker = relationship("Worker", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")

    # Constraints
    __table_args__ = (
        UniqueConstraint('worker_id', 'course_id', name='unique_worker_course_enrollment'),
    )
