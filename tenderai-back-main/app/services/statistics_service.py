from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from datetime import datetime, timedelta
from typing import List, Dict

from app.models import Question, Message, Cluster
from app.schemas.statistics import HourlyStats, ClusterStats, StatisticsResponse

def get_statistics(db: Session) -> StatisticsResponse:
    """
    Получает статистику за последние 24 часа:
    - Количество запросов по часам для каждого кластера
    - Количество негативных отзывов (review=2) по часам для каждого кластера
    
    Args:
        db: Сессия базы данных
        
    Returns:
        Статистика в формате StatisticsResponse
    """
    # Получаем временную метку для 24 часов назад
    now = datetime.utcnow()
    day_ago = now - timedelta(hours=24)

    print('day_ago', day_ago)
    
    # Получаем все кластеры
    clusters = db.query(Cluster).all()
    
    # Инициализируем результат
    result = StatisticsResponse(requests=[], reviews=[])
    
    for cluster in clusters:
        # Статистика по запросам
        requests_stats = (
            db.query(
                func.from_unixtime(Question.asked_at, '%Y-%m-%d %H:00:00').label('hour'),
                func.count(Question.id).label('count')
            )
            .filter(
                Question.cluster_id == cluster.id,
                Question.asked_at >= int(day_ago.timestamp())
            )
            .group_by('hour')
            .order_by('hour')
            .all()
        )

        print('requests_stats', requests_stats)
        
        # Преобразуем в нужный формат
        requests_data = []
        for stat in requests_stats:
            if stat.hour is not None:
                try:
                    hour_str = datetime.strptime(stat.hour, '%Y-%m-%d %H:00:00').strftime("%H:00")
                    requests_data.append(
                        HourlyStats(
                            hour=hour_str,
                            count=stat.count
                        )
                    )
                except (ValueError, TypeError):
                    print('error', stat)
                    # Пропускаем некорректные значения
                    continue
        
        # Добавляем статистику по запросам только если есть данные
        if requests_data:
            result.requests.append(
                ClusterStats(
                    cluster_id=cluster.id,
                    title=cluster.title,
                    color=cluster.color,
                    data=requests_data
                )
            )
        
        # Статистика по негативным отзывам
        reviews_stats = (
            db.query(
                func.from_unixtime(Question.asked_at, '%Y-%m-%d %H:00:00').label('hour'),
                func.count(Question.id).label('count')
            )
            .join(Message, Question.id == Message.question_id)
            .filter(
                Question.cluster_id == cluster.id,
                Question.asked_at >= int(day_ago.timestamp()),
                Message.review == 1
            )
            .group_by('hour')
            .order_by('hour')
            .all()
        )
        
        # Преобразуем в нужный формат
        reviews_data = []
        for stat in reviews_stats:
            if stat.hour is not None:
                try:
                    hour_str = datetime.strptime(stat.hour, '%Y-%m-%d %H:00:00').strftime("%H:00")
                    reviews_data.append(
                        HourlyStats(
                            hour=hour_str,
                            count=stat.count
                        )
                    )
                except (ValueError, TypeError):
                    # Пропускаем некорректные значения
                    continue
        
        # Добавляем статистику по отзывам только если есть данные
        if reviews_data:
            result.reviews.append(
                ClusterStats(
                    cluster_id=cluster.id,
                    title=cluster.title,
                    color=cluster.color,
                    data=reviews_data
                )
            )
    
    return result 