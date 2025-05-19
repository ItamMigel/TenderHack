from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from typing import Dict, List

class QuestionText(BaseModel):
    question_id: str
    text: str

class LatestQuestionsResponse(BaseModel):
    clusters: Dict[str, List[str]]
    latest: List[str]

    model_config = ConfigDict(from_attributes=True)

class HistoryItem(BaseModel):
    id: str
    assistant: str
    dataset: str
    cluster: str
    question: str
    review: int
    date: int

class HistoryResponse(BaseModel):
    items: List[HistoryItem]