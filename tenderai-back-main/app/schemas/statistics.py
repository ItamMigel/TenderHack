from pydantic import BaseModel
from typing import List, Dict

class HourlyStats(BaseModel):
    hour: str  # Формат "HH:00"
    count: int

class ClusterStats(BaseModel):
    cluster_id: str
    title: str
    color: str
    data: List[HourlyStats]

class StatisticsResponse(BaseModel):
    requests: List[ClusterStats]
    reviews: List[ClusterStats] 