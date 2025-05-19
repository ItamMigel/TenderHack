from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.cluster import ClusterCreate, Cluster
from app.services.assistant_service import create_cluster, get_clusters
from app.database import get_db

router = APIRouter(prefix="/api/clusters")

@router.post("/", response_model=Cluster)
def create(cluster: ClusterCreate, db: Session = Depends(get_db)):
    return create_cluster(db, cluster)

@router.get("/", response_model=list[Cluster])
def get_all(db: Session = Depends(get_db)):
    return get_clusters(db)