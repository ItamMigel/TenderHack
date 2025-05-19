from sqlalchemy.orm import Session, selectinload, joinedload
import uuid
from datetime import datetime
import time
from fastapi import HTTPException
import httpx

from app.models import Message, Question, Cluster
from app.models.assistant import Assistant
from app.models.dataset import Dataset
from app.schemas import MessageCreate, QuestionCreate, ClusterCreate
from app.schemas.assistant import AssistantCreate
from app.schemas.cluster import Cluster as ClusterSchema
from app.schemas.message import HistoryItem, MessageReview, MessageItem, MessageReviewUpdate

def create_assistant(db: Session, assistant: AssistantCreate):
    assistant_data = assistant.dict()
    assistant_data["id"] = str(uuid.uuid4())
    db_assistant = Assistant(**assistant_data)
    db.add(db_assistant)
    db.commit()
    db.refresh(db_assistant)
    return db_assistant

def get_assistants(db: Session):
    return db.query(Assistant).all()

async def create_message(db: Session, data: MessageCreate):
    """
    Создаёт новое сообщение. Если isNew=True, то также создаёт новый вопрос
    и связывает сообщение с ним. Затем отправляет запрос в ML сервис и создаёт
    ответное сообщение.
    
    Args:
        db: Сессия базы данных
        data: Данные для создания сообщения
    
    Returns:
        Созданное сообщение и ответ от ML
    """
    # Создаем новый вопрос, если указан флаг isNew или не указан question_id
    if data.isNew == True:
        # Создаем новый вопрос
        current_time = int(time.time())  # текущий timestamp
        question_data = {
            "id": str(uuid.uuid4()),
            "assistant_id": 1,
            "asked_at": current_time,
            "cluster_id": data.cluster_id
        }
        db_question = Question(**question_data)
        db.add(db_question)
        db.commit()
        db.refresh(db_question)
        
        # Используем ID созданного вопроса для сообщения
        data.question_id = db_question.id
    elif data.question_id is None:
        # Если question_id не указан и isNew=False, это ошибка
        raise HTTPException(status_code=400, detail="question_id is required when not creating a new question")

    # Создаем сообщение пользователя
    message_data = dict()
    message_data["text"] = data.text
    message_data["question_id"] = str(data.question_id)
    message_data["is_self"] = True
    message_data["is_selected"] = False
    message_data["review"] = MessageReview.none.value
    message_data["avatar_url"] = "avatar_url"
    message_data["id"] = str(uuid.uuid4())
    user_message = Message(**message_data)
    db.add(user_message)
    db.commit()
    db.refresh(user_message)
    
    # Отправляем запрос к ML сервису
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            ml_response = await client.get(
                "http://hkc7lifxnonzn2-1002.proxy.runpod.net/ask_question",
                params={"query": data.text}
            )
            ml_response.raise_for_status()
            ml_data = ml_response.json()
            
            # Получаем ответ от ML
            ml_answer = ml_data.get("result", "Извините, не удалось получить ответ")
            ml_chunks = ml_data.get("relevant_chunks", [])
            
            # Формируем текст с источниками
            if ml_chunks:
                # Создаем список уникальных источников
                sources = []
                for chunk in ml_chunks:
                    if "metadata" in chunk and "filename" in chunk["metadata"] and "page" in chunk["metadata"]:
                        filename = chunk["metadata"]["filename"]
                        page = chunk["metadata"]["page"]
                        source = f"{filename} - стр.{page}"
                        if source not in sources:
                            sources.append(source)
                
                # Добавляем источники к ответу
                if sources:
                    sources_text = "Данные были взяты из: " + ", ".join(sources)
                    ml_answer = f"{ml_answer}\n\n{sources_text}"
            
            # Создаем ответное сообщение от бота
            bot_message_data = {
                "id": str(uuid.uuid4()),
                "text": ml_answer,
                "question_id": str(data.question_id),
                "is_self": False,
                "is_selected": False,
                "review": MessageReview.none.value,
                "avatar_url": "bot_avatar_url"
            }
            bot_message = Message(**bot_message_data)
            db.add(bot_message)
            db.commit()
            db.refresh(bot_message)
            
            return {
                "message": user_message,
                "answer": bot_message
            }
            
    except httpx.HTTPStatusError as e:
        # Ошибка HTTP статуса
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"ML service error: {e.response.text}"
        )
    except httpx.RequestError as e:
        # Ошибка сетевого уровня
        raise HTTPException(
            status_code=500,
            detail=f"Error connecting to ML service: {str(e)}"
        )
    except Exception as e:
        # Другие ошибки
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )

def create_question(db: Session, question: QuestionCreate):
    question_data = question.dict()
    question_data["id"] = str(uuid.uuid4())
    db_question = Question(**question_data)
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question

def create_cluster(db: Session, cluster: ClusterCreate):
    cluster_data = cluster.dict()
    cluster_data["id"] = str(uuid.uuid4())
    db_cluster = Cluster(**cluster_data)
    db.add(db_cluster)
    db.commit()
    db.refresh(db_cluster)
    return db_cluster

def get_questions(db: Session):
    return db.query(Question).all()

def get_clusters(db: Session):
    clusters = db.query(Cluster).options(joinedload(Cluster.questions)).all()
    return [
        ClusterSchema(
            id=c.id,
            color=c.color,
            title=c.title,
            questions=[q.id for q in c.questions]  # Берем ID из связанных вопросов
        )
        for c in clusters
    ]

def get_history(db: Session, limit: int = 100, offset: int = 0):
    """
    Получает историю вопросов с информацией из связанных таблиц.
    
    Args:
        db: Сессия базы данных
        limit: Максимальное количество записей для возврата
        offset: Смещение для пагинации
        
    Returns:
        Список объектов HistoryItem с информацией о вопросах и связанных сообщениях
    """
    # Выполняем запрос с join'ами для получения всех необходимых данных
    questions = (
        db.query(Question)
        .join(Assistant, Question.assistant_id == Assistant.id)
        .join(Dataset, Assistant.dataset_id == Dataset.id)
        .outerjoin(Cluster, Question.cluster_id == Cluster.id)
        .order_by(Question.asked_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    
    result = []
    for question in questions:
        # Получаем все сообщения для вопроса
        messages = (
            db.query(Message)
            .filter(Message.question_id == question.id)
            .order_by(Message.id.asc())
            .all()
        )
        
        # Получаем первое сообщение для основной информации
        first_message = messages[0] if messages else None
        
        review = MessageReview.none.value
        if first_message and first_message.review is not None:
            review = first_message.review
        
        # asked_at уже является timestamp (целым числом)
        timestamp = question.asked_at if question.asked_at else 0
        
        # Преобразуем сообщения в MessageItem
        message_items = []
        for message in messages:
            msg_review = MessageReview.none.value
            if message.review is not None:
                msg_review = message.review
            
            message_item = MessageItem(
                id=message.id,
                avatar_url=message.avatar_url,
                text=message.text,
                is_self=message.is_self,
                is_selected=message.is_selected,
                review=msg_review
            )
            message_items.append(message_item)
        
        # Создаем объект HistoryItem
        history_item = HistoryItem(
            id=question.id,
            assistant=question.assistant.title,
            dataset=question.assistant.dataset.title,
            cluster=question.cluster.title if question.cluster else "Без кластера",
            color=question.cluster.color if question.cluster else "#000000",
            question=first_message.text if first_message else "",
            review=review,
            date=timestamp,
            messages=message_items
        )
        
        result.append(history_item)
    
    return result

def update_message_review(db: Session, message_id: str, review_data: MessageReviewUpdate):
    """
    Обновляет статус review для сообщения.
    
    Args:
        db: Сессия базы данных
        message_id: ID сообщения
        review_data: Данные для обновления review
        
    Returns:
        Обновленное сообщение
        
    Raises:
        HTTPException: Если сообщение не найдено
    """
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    # Обновляем review
    message.review = review_data.review.value
    db.commit()
    db.refresh(message)
    
    return message