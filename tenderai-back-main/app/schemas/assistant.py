from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from typing import Dict, Optional
from ..schemas.dataset import DatasetBase

class AssistantBase(BaseModel):
    title: str
    avatar_url: str
    neural_network_title: str
    gradient: str
    settings: Dict
    dataset_id: str

class AssistantCreate(AssistantBase):
    pass

class Assistant(AssistantBase):
    id: str
    dataset: Optional[DatasetBase]  # Используется DatasetBase из правильного модуля

    model_config = ConfigDict(from_attributes=True)