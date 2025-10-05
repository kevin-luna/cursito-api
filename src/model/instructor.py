from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..database import Base
import uuid


class Instructor(Base):
    __tablename__ = "instructors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    worker_id = Column(UUID(as_uuid=True), ForeignKey("worker.id"), nullable=False)
    course_id = Column(UUID(as_uuid=True), ForeignKey("course.id"), nullable=False)

    # Relationships
    worker = relationship("Worker", back_populates="instructor_courses")
    course = relationship("Course", back_populates="instructors")

    # Constraints
    __table_args__ = (
        UniqueConstraint('worker_id', 'course_id', name='unique_worker_course'),
    )
