from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship

from .base import Base


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(String(36), primary_key=True)
    title = Column(String(255), nullable=False)
    assistants = relationship("Assistant", back_populates="dataset")