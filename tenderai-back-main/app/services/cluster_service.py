from sqlalchemy.orm import Session
import uuid
import httpx
from fastapi import UploadFile
from typing import List

from app.models.cluster import Cluster
from app.schemas.cluster import ClusterCreate

async def upload_files_to_ml(files: List[UploadFile]) -> dict:
    """
    Загружает файлы на ML сервис.
    
    Args:
        files: Список файлов для загрузки
        
    Returns:
        Ответ от ML сервиса
    """
    async with httpx.AsyncClient() as client:
        files_data = {f"files": (file.filename, file.file, file.content_type) for file in files}
        response = await client.post(
            "https://tenderai-ml.foowe.ru/uploadClusterDataSet",
            files=files_data
        )
        return response.json()

def create_cluster(db: Session, cluster: ClusterCreate) -> Cluster:
    """
    Создает новый cluster.
    
    Args:
        db: Сессия базы данных
        cluster: Данные для создания cluster
        
    Returns:
        Созданный cluster
    """
    db_cluster = Cluster(
        id=str(uuid.uuid4()),
        title=cluster.title
    )
    db.add(db_cluster)
    db.commit()
    db.refresh(db_cluster)
    return db_cluster

def get_clusters(db: Session, skip: int = 0, limit: int = 100) -> tuple[List[Cluster], int]:
    """
    Получает список cluster с пагинацией.
    
    Args:
        db: Сессия базы данных
        skip: Смещение для пагинации
        limit: Лимит записей
        
    Returns:
        Кортеж из списка cluster и общего количества
    """
    total = db.query(Cluster).count()
    clusters = db.query(Cluster).offset(skip).limit(limit).all()
    return clusters, total

def get_cluster(db: Session, cluster_id: str) -> Cluster:
    """
    Получает cluster по ID.
    
    Args:
        db: Сессия базы данных
        cluster_id: ID cluster
        
    Returns:
        Cluster
    """
    return db.query(Cluster).filter(Cluster.id == cluster_id).first()

def delete_cluster(db: Session, cluster_id: str) -> bool:
    """
    Удаляет cluster по ID.
    
    Args:
        db: Сессия базы данных
        cluster_id: ID cluster
        
    Returns:
        True если cluster был удален, False если не найден
    """
    cluster = db.query(Cluster).filter(Cluster.id == cluster_id).first()
    if cluster:
        db.delete(cluster)
        db.commit()
        return True
    return False 