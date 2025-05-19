from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from enum import Enum
from typing import List, Optional, Dict

class MessageReview(Enum):
    none = 0
    like = 1
    dislike = 2

class MessageBase(BaseModel):
    avatar_url: str
    text: str
    is_self: bool
    is_selected: bool
    review: MessageReview

class MessageCreate(BaseModel):
    avatar_url: str = 'avater_url'
    text: str = ''
    is_self: bool = True
    is_selected: bool = False
    review: MessageReview = MessageReview.none
    question_id: Optional[str] = None
    isNew: Optional[bool] = False
    cluster_id: Optional[int] = 1

class Message(MessageBase):
    id: str
    question_id: str

    model_config = ConfigDict(from_attributes=True)

class MessageReviewUpdate(BaseModel):
    review: MessageReview

class MessageItem(BaseModel):
    id: str
    avatar_url: str
    text: str
    is_self: bool
    is_selected: bool
    review: int
    
    model_config = ConfigDict(from_attributes=True)

class HistoryItem(BaseModel):
    id: str
    assistant: str
    dataset: str
    cluster: str
    color: str
    question: str
    review: int
    date: int
    messages: List[MessageItem] = []

class PaginatedHistoryResponse(BaseModel):
    items: List[HistoryItem]
    total: int
    limit: int
    offset: int
    has_more: bool