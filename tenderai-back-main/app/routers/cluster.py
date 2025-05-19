from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
import json

from app.database import get_db
from app.schemas.cluster import ClusterCreate, ClusterResponse, ClusterListResponse
from app.services.cluster_service import (
    create_cluster,
    get_clusters,
    get_cluster,
    delete_cluster,
    upload_files_to_ml
)

router = APIRouter(prefix="/api/clusters")

@router.post("/", response_model=ClusterResponse)
async def create(
    title: str = Form(...),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Создает новый cluster и загружает файлы на ML сервис.
    
    Args:
        title: Название cluster
        files: Список файлов для загрузки
        db: Сессия базы данных
        
    Returns:
        Созданный cluster
    """
    # Загружаем файлы на ML сервис
    ml_response = await upload_files_to_ml(files)
    
    # Создаем cluster в базе данных
    cluster = ClusterCreate(title=title)
    db_cluster = create_cluster(db, cluster)
    
    return db_cluster

@router.get("/", response_model=ClusterListResponse)
def list_clusters(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Получает список cluster с пагинацией.
    
    Args:
        skip: Смещение для пагинации
        limit: Лимит записей
        db: Сессия базы данных
        
    Returns:
        Список cluster и общее количество
    """
    clusters, total = get_clusters(db, skip, limit)
    return {
        "items": clusters,
        "total": total
    }

@router.get("/{cluster_id}", response_model=ClusterResponse)
def get_cluster_by_id(
    cluster_id: str,
    db: Session = Depends(get_db)
):
    """
    Получает cluster по ID.
    
    Args:
        cluster_id: ID cluster
        db: Сессия базы данных
        
    Returns:
        Cluster
    """
    cluster = get_cluster(db, cluster_id)
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    return cluster

@router.delete("/{cluster_id}")
def delete_cluster_by_id(
    cluster_id: str,
    db: Session = Depends(get_db)
):
    """
    Удаляет cluster по ID.
    
    Args:
        cluster_id: ID cluster
        db: Сессия базы данных
        
    Returns:
        Сообщение об успешном удалении
    """
    if not delete_cluster(db, cluster_id):
        raise HTTPException(status_code=404, detail="Cluster not found")
    return {"message": "Cluster deleted successfully"} 