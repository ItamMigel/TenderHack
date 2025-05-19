from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session
from app.schemas.message import MessageCreate, Message, PaginatedHistoryResponse, MessageReviewUpdate
from app.database import get_db
from app.models import Message as MessageModel
from app.services import create_message, update_message_review

router = APIRouter(prefix="/api/messages")

@router.post("/")
async def create(
    data: MessageCreate,
    db: Session = Depends(get_db)
):
    """
    Создаёт новое сообщение. Если параметр isNew=True, то также создаёт новый вопрос
    и связывает сообщение с ним. Затем отправляет запрос к ML сервису и создаёт
    ответное сообщение.
    
    Args:
        data: Данные для создания сообщения
        db: Сессия базы данных
        
    Returns:
        Созданное сообщение и ответ от ML
    """
    return await create_message(db, data)

@router.put("/{message_id}/review", response_model=Message)
def update_review(
    message_id: str = Path(..., description="ID сообщения"),
    review_data: MessageReviewUpdate = None,
    db: Session = Depends(get_db)
):
    """
    Обновляет оценку (review) сообщения.
    
    Args:
        message_id: ID сообщения для обновления
        review_data: Новое значение оценки
        db: Сессия базы данных
        
    Returns:
        Обновленное сообщение
    """

    print('message_id', message_id)
    return update_message_review(db, message_id, review_data)

@router.get("/history", response_model=PaginatedHistoryResponse)
def get_history(db: Session = Depends(get_db)):
    """
    Получает историю сообщений.
    """
    messages = db.query(MessageModel).all()
    return {"items": messages}