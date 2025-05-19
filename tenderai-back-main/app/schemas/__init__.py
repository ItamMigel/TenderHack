from .message import Message, MessageCreate, MessageReview, HistoryItem, PaginatedHistoryResponse
from .assistant import Assistant, AssistantCreate
from .question import Question, QuestionCreate
from .cluster import Cluster, ClusterCreate
from .dataset import Dataset, DatasetCreate
from .general import LatestQuestionsResponse, QuestionText
from .response import ResponseModel
from typing import List, Optional

# Перестраиваем модели после всех импортов
Question.model_rebuild(
    _types_namespace={
        "Optional": Optional,
        "List": List,
        "Cluster": Cluster,
        "Assistant": Assistant,
        "Message": Message
    }
)

Cluster.model_rebuild(
    _types_namespace={
        "Optional": Optional,
        "List": List,
        "Question": Question
    }
)

__all__ = [
    "Message",
    "MessageCreate",
    "MessageReview",
    "Assistant",
    "AssistantCreate",
    "Question",
    "QuestionCreate",
    "Cluster",
    "ClusterCreate",
    "Dataset",
    "DatasetCreate",
    "HistoryItem",
    "PaginatedHistoryResponse",
    "LatestQuestionsResponse",
    "QuestionText",
    "ResponseModel"
]