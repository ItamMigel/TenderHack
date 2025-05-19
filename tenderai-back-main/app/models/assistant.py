from sqlalchemy import Column, String, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
from .dataset import Dataset


class Assistant(Base):
    __tablename__ = "assistants"

    id = Column(String(36), primary_key=True)
    title = Column(String(255), nullable=False)
    avatar_url = Column(String(255), nullable=False)
    neural_network_title = Column(String(255), nullable=False)
    gradient = Column(Text, nullable=False)
    settings = Column(JSON, nullable=False)
    dataset_id = Column(String(36), ForeignKey("datasets.id"))
    dataset = relationship("Dataset", back_populates="assistants")

    questions = relationship("Question", back_populates="assistant")