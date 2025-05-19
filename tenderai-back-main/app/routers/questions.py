from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.question import QuestionCreate, Question
from app.services.assistant_service import create_question, get_questions
from app.database import get_db

router = APIRouter(prefix="/api/questions")

@router.post("/", response_model=Question)
def create(question: QuestionCreate, db: Session = Depends(get_db)):
    return create_question(db, question)

@router.get("/", response_model=list[Question])
def get_all(db: Session = Depends(get_db)):
    return get_questions(db)