from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.assistant import AssistantCreate, Assistant
from app.services.assistant_service import create_assistant, get_assistants
from app.database import get_db

router = APIRouter(prefix="/api/assistants")

@router.post("/", response_model=Assistant)
def create(assistant: AssistantCreate, db: Session = Depends(get_db)):
    return create_assistant(db, assistant)