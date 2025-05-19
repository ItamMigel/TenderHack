from sqlalchemy import Column, String, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(String(36), primary_key=True)
    assistant_id = Column(String(36), ForeignKey("assistants.id"))
    asked_at = Column(BigInteger, nullable=False)
    cluster_id = Column(String(36), ForeignKey("clusters.id"))

    assistant = relationship("Assistant", back_populates="questions")
    cluster = relationship("Cluster", back_populates="questions", lazy="selectin")
    messages = relationship("Message", back_populates="question")