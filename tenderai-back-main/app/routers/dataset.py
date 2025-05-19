from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
import json

from app.database import get_db
from app.schemas.dataset import DatasetCreate, DatasetResponse, DatasetListResponse
from app.services.dataset_service import (
    create_dataset,
    get_datasets,
    get_dataset,
    delete_dataset,
    upload_files_to_ml
)

router = APIRouter(prefix="/api/datasets")

@router.post("/", response_model=DatasetResponse)
async def create(
    title: str = Form(...),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Создает новый dataset и загружает файлы на ML сервис.
    
    Args:
        title: Название dataset
        files: Список файлов для загрузки
        db: Сессия базы данных
        
    Returns:
        Созданный dataset
    """
    try:
        # # Загружаем файлы на ML сервис
        # ml_response = await upload_files_to_ml(files)
        
        # Создаем dataset в базе данных
        dataset = DatasetCreate(title=title)
        db_dataset = create_dataset(db, dataset)
        
        return db_dataset
    except HTTPException as e:
        # Перебрасываем ошибку HTTPException
        raise e
    except Exception as e:
        # Логируем неожиданные ошибки
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create dataset: {str(e)}"
        )

@router.get("/", response_model=DatasetListResponse)
def list_datasets(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Получает список dataset с пагинацией.
    
    Args:
        skip: Смещение для пагинации
        limit: Лимит записей
        db: Сессия базы данных
        
    Returns:
        Список dataset и общее количество
    """
    datasets, total = get_datasets(db, skip, limit)
    return {
        "items": datasets,
        "total": total
    }

@router.get("/{dataset_id}", response_model=DatasetResponse)
def get_dataset_by_id(
    dataset_id: str,
    db: Session = Depends(get_db)
):
    """
    Получает dataset по ID.
    
    Args:
        dataset_id: ID dataset
        db: Сессия базы данных
        
    Returns:
        Dataset
    """
    dataset = get_dataset(db, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset

@router.delete("/{dataset_id}")
def delete_dataset_by_id(
    dataset_id: str,
    db: Session = Depends(get_db)
):
    """
    Удаляет dataset по ID.
    
    Args:
        dataset_id: ID dataset
        db: Сессия базы данных
        
    Returns:
        Сообщение об успешном удалении
    """
    if not delete_dataset(db, dataset_id):
        raise HTTPException(status_code=404, detail="Dataset not found")
    return {"message": "Dataset deleted successfully"} 