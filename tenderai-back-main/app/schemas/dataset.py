from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class DatasetBase(BaseModel):
    title: str

class DatasetCreate(DatasetBase):
    pass

class Dataset(DatasetBase):
    id: str
    title: str

    model_config = ConfigDict(from_attributes=True)

class DatasetResponse(Dataset):
    pass

class DatasetListResponse(BaseModel):
    items: List[Dataset]
    total: int