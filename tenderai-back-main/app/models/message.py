from sqlalchemy import Column, String, Text, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
from .question import Question


class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True)
    question_id = Column(String(36), ForeignKey("questions.id"))
    avatar_url = Column(String(255), nullable=False)
    text = Column(Text, nullable=False)
    is_self = Column(Boolean, nullable=False)
    is_selected = Column(Boolean, nullable=False)
    review = Column(Integer, nullable=False)
    question = relationship("Question", back_populates="messages")