from sqlalchemy import Column, String, SmallInteger, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..database import Base
import uuid


class Question(Base):
    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    survey_id = Column(UUID(as_uuid=True), ForeignKey("surveys.id"), nullable=False)
    question = Column(String(100), nullable=False)
    question_order = Column(SmallInteger, nullable=False)

    # Relationships
    survey = relationship("Survey", back_populates="questions")
    answers = relationship("Answer", back_populates="question")
