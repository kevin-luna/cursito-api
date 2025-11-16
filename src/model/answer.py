from sqlalchemy import Column, Text, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..database import Base
import uuid


class Answer(Base):
    __tablename__ = "answers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    worker_id = Column(UUID(as_uuid=True), ForeignKey("workers.id"), nullable=False)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id"), nullable=False)
    value = Column(Text, nullable=False)

    # Relationships
    worker = relationship("Worker", back_populates="answers")
    course = relationship("Course", back_populates="answers")
    question = relationship("Question", back_populates="answers")

    # Constraints
    __table_args__ = (
        UniqueConstraint('worker_id', 'course_id', 'question_id', name='unique_worker_course_question'),
    )
