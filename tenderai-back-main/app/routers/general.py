from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from app.database import get_db
from app.models import Question, Message
from app.schemas.general import LatestQuestionsResponse, QuestionText
from app.schemas.message import PaginatedHistoryResponse, HistoryItem
from app.services import get_history
from typing import List, Dict, Any

router = APIRouter(prefix="/api/general")

@router.post("/")
def create(db: Session = Depends(get_db)):
    return {}

@router.get("/latest-questions", response_model=LatestQuestionsResponse)
def get_latest_questions(db: Session = Depends(get_db)):
    """
    Получает последние 3 вопроса для каждого кластера (1, 2, 3) и их первые сообщения,
    а также последние 3 вопроса без привязки к кластеру и их первые сообщения.
    """
    result = {
        "clusters": {},
        "latest": []
    }
    
    # Получаем последние 3 вопроса для каждого кластера (1, 2, 3)
    for cluster_id in [1, 2, 3]:
        # Получаем последние 3 вопроса для кластера
        questions = db.query(Question).filter(
            Question.cluster_id == str(cluster_id)
        ).order_by(desc(Question.asked_at)).limit(3).all()
        
        cluster_questions = []
        for question in questions:
            # Находим первое сообщение для вопроса
            first_message = db.query(Message).filter(
                Message.question_id == question.id
            ).filter(Message.is_self == True).order_by(Message.id).first()
            
            if first_message:
                cluster_questions.append(first_message.text)
        
        result["clusters"][str(cluster_id)] = cluster_questions
    
    # Получаем последние 3 вопроса без привязки к кластеру
    latest_questions = db.query(Question).order_by(desc(Question.asked_at)).limit(3).all()
    
    for question in latest_questions:
        # Находим первое сообщение для вопроса
        first_message = db.query(Message).filter(
            Message.question_id == question.id
        ).filter(Message.is_self == True).order_by(Message.id).first()
        
        if first_message:
            result["latest"].append(first_message.text)
    
    return result

@router.get("/history", response_model=PaginatedHistoryResponse)
def get_questions_history(
    limit: int = Query(100, description="Максимальное количество записей для возврата"),
    offset: int = Query(0, description="Смещение для пагинации"),
    db: Session = Depends(get_db)
):
    """
    Получает историю вопросов с информацией из связанных таблиц.
    
    Args:
        limit: Максимальное количество записей для возврата
        offset: Смещение для пагинации
        db: Сессия базы данных
        
    Returns:
        История вопросов с информацией из связанных таблиц и метаданными пагинации
    """
    # Получаем общее количество записей
    total = db.query(func.count(Question.id)).scalar()
    
    # Получаем записи с пагинацией
    history_items = get_history(db, limit, offset)
    
    # Проверяем, есть ли еще записи
    has_more = (offset + limit) < total
    
    return {
        "items": history_items,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": has_more
    }