from __future__ import annotations
from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class ClusterBase(BaseModel):
    title: str

class ClusterCreate(ClusterBase):
    pass

class Cluster(ClusterBase):
    id: str
    title: str

    model_config = ConfigDict(from_attributes=True)

class ClusterResponse(Cluster):
    pass

class ClusterListResponse(BaseModel):
    items: List[Cluster]
    total: int