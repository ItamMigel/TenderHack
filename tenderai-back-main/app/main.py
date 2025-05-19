from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import assistants, messages, questions, clusters, external_api, general, dataset, cluster, statistics

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(assistants.router)
app.include_router(messages.router)
app.include_router(questions.router)
app.include_router(clusters.router)
app.include_router(external_api.router)
app.include_router(general.router)
app.include_router(dataset.router)
app.include_router(cluster.router)
app.include_router(statistics.router)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/health")
def health_check():
    """
    Роут для проверки работоспособности API.
    Используется в мониторинге и health-check контейнера.
    """
    return {
        "status": "ok",
        "service": "tender-api"
    }