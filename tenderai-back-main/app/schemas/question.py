from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from .assistant import Assistant
from .message import Message

class QuestionBase(BaseModel):
    assistant_id: str = Field(..., alias="assistantId")
    asked_at: int = Field(..., alias="askedAt")
    cluster_id: str = Field(..., alias="clusterId")

class QuestionCreate(QuestionBase):
    pass

class Question(QuestionBase):
    id: str
    assistant: Optional[Assistant]
    cluster: List[str]  # Только ID кластера
    messages: List[Message] = []

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )