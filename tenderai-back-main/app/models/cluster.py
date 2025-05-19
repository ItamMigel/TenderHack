from sqlalchemy import Column, String, ARRAY
from sqlalchemy.orm import relationship
from .base import Base


class Cluster(Base):
    __tablename__ = "clusters"

    id = Column(String(36), primary_key=True)
    color = Column(String(7), nullable=False)  # Для HEX цвета (#RRGGBB)
    title = Column(String(255), nullable=False)

    questions = relationship("Question", back_populates="cluster")