from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services.external_api_service import call_external_api
from app.schemas.message import MessageCreate
from app.database import get_db
from app.models import Question, Assistant

router = APIRouter(prefix="/api/generate")


@router.post("/response")
async def generate_response(
        message: MessageCreate,
        db: Session = Depends(get_db)
):
    try:
        # Получаем вопрос и связанного с ним ассистента
        question = db.query(Question).filter(Question.id == message.question_id).first()
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        assistant = db.query(Assistant).filter(Assistant.id == question.assistant_id).first()
        if not assistant:
            raise HTTPException(status_code=404, detail="Assistant not found")

        # Подготавливаем промпт и получаем настройки
        prompt = f"User: {message.text}"
        settings = assistant.settings

        response = await call_external_api(prompt, settings)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))