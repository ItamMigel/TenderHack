from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.statistics import StatisticsResponse
from app.services.statistics_service import get_statistics

router = APIRouter(prefix="/api/statistics")

@router.get("/24h", response_model=StatisticsResponse)
def get_24h_statistics(db: Session = Depends(get_db)):
    """
    Получает статистику за последние 24 часа:
    - Количество запросов по часам для каждого кластера
    - Количество негативных отзывов (review=2) по часам для каждого кластера
    
    Returns:
        Статистика в формате:
        {
            "requests": [
                {
                    "cluster_id": "123",
                    "title": "Cluster 1",
                    "color": "#FF0000",
                    "data": [
                        {"hour": "11:00", "count": 5},
                        {"hour": "12:00", "count": 3},
                        ...
                    ]
                },
                ...
            ],
            "reviews": [
                {
                    "cluster_id": "123",
                    "title": "Cluster 1",
                    "color": "#FF0000",
                    "data": [
                        {"hour": "11:00", "count": 2},
                        {"hour": "12:00", "count": 1},
                        ...
                    ]
                },
                ...
            ]
        }
    """
    return get_statistics(db) 