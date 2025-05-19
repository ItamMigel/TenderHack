from sqlalchemy.orm import Session
import uuid
import httpx
from fastapi import UploadFile, HTTPException
from typing import List, Dict, Any
import json

from app.models.dataset import Dataset
from app.schemas.dataset import DatasetCreate

async def upload_files_to_ml(files: List[UploadFile]) -> Dict[str, Any]:
    """
    Загружает файлы на ML сервис.
    
    Args:
        files: Список файлов для загрузки
        
    Returns:
        Ответ от ML сервиса
        
    Raises:
        HTTPException: Если произошла ошибка при загрузке файлов
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            files_data = {}
            for i, file in enumerate(files):
                files_data[f"file_{i}"] = (file.filename, file.file, file.content_type)
            
            response = await client.post(
                "https://tenderai-ml.foowe.ru/uploadDataSet",
                files=files_data
            )
            
            # Проверяем статус ответа
            response.raise_for_status()
            
            try:
                # Пробуем распарсить JSON
                return response.json()
            except json.JSONDecodeError:
                # Если не удалось распарсить JSON, возвращаем статус без данных
                return {"status": "success", "message": "Files uploaded but no JSON response"}
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
            detail=f"Unexpected error during file upload: {str(e)}"
        )

def create_dataset(db: Session, dataset: DatasetCreate) -> Dataset:
    """
    Создает новый dataset.
    
    Args:
        db: Сессия базы данных
        dataset: Данные для создания dataset
        
    Returns:
        Созданный dataset
    """
    db_dataset = Dataset(
        id=str(uuid.uuid4()),
        title=dataset.title
    )
    db.add(db_dataset)
    db.commit()
    db.refresh(db_dataset)
    return db_dataset

def get_datasets(db: Session, skip: int = 0, limit: int = 100) -> tuple[List[Dataset], int]:
    """
    Получает список dataset с пагинацией.
    
    Args:
        db: Сессия базы данных
        skip: Смещение для пагинации
        limit: Лимит записей
        
    Returns:
        Кортеж из списка dataset и общего количества
    """
    total = db.query(Dataset).count()
    datasets = db.query(Dataset).offset(skip).limit(limit).all()
    return datasets, total

def get_dataset(db: Session, dataset_id: str) -> Dataset:
    """
    Получает dataset по ID.
    
    Args:
        db: Сессия базы данных
        dataset_id: ID dataset
        
    Returns:
        Dataset
    """
    return db.query(Dataset).filter(Dataset.id == dataset_id).first()

def delete_dataset(db: Session, dataset_id: str) -> bool:
    """
    Удаляет dataset по ID.
    
    Args:
        db: Сессия базы данных
        dataset_id: ID dataset
        
    Returns:
        True если dataset был удален, False если не найден
    """
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if dataset:
        db.delete(dataset)
        db.commit()
        return True
    return False 