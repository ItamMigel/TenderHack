import os
# Отключаем поддержку mllama, чтобы избежать ошибки загрузки __init__.so
os.environ["TRANSFORMERS_NO_MLLAMA"] = "1"

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import numpy as np
from transformers import AutoTokenizer, AutoModel
import torch
import faiss
import uvicorn
from typing import List
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Query Recommendation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables to store models and data
tokenizer = None
model = None
queries = []
index = None

class QueryRequest(BaseModel):
    text: str

class QueryResponse(BaseModel):
    similar_queries: List[str]
    similarities: List[float]

def load_dataset(file_path):
    df = pd.read_excel(file_path)
    return df['Заголовок статьи'].drop_duplicates().tolist()

def get_embeddings(texts, batch_size=32):
    global tokenizer, model
    
    embeddings = []
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i + batch_size]
        inputs = tokenizer(batch_texts, padding=True, truncation=True, return_tensors="pt", max_length=512)
        with torch.no_grad():
            outputs = model(**inputs)
        batch_embeddings = outputs.last_hidden_state.mean(dim=1).cpu().numpy()
        batch_embeddings = batch_embeddings / np.linalg.norm(batch_embeddings, axis=1, keepdims=True)
        embeddings.append(batch_embeddings)

    return np.vstack(embeddings)

def build_faiss_index(embeddings):
    dimension = embeddings.shape[1]
    idx = faiss.IndexFlatIP(dimension)
    idx.add(embeddings)
    return idx

def find_nearest_queries(user_query, k=3):
    global index, queries, tokenizer, model
    
    user_embedding = get_embeddings([user_query], batch_size=1)[0]
    user_embedding = np.expand_dims(user_embedding, axis=0)

    distances, indices = index.search(user_embedding, k=k)
    nearest_queries = [queries[idx] for idx in indices[0]]
    similarities = distances[0].tolist()

    return nearest_queries, similarities

@app.on_event("startup")
async def startup_event():
    global tokenizer, model, queries, index
    
    # Загрузка модели с параметром torch_dtype=torch.bfloat16 для bf16
    model_name = "Tochka-AI/ruRoPEBert-e5-base-2k"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name, torch_dtype=torch.float32)
    
    # Загрузка датасета
    file_path = "zaprosy.xlsx"  # Обновите путь к файлу при необходимости
    queries = load_dataset(file_path)
    
    # Построение FAISS-индекса (однократно при старте)
    embeddings = get_embeddings(queries)
    index = build_faiss_index(embeddings)
    
    print("✅ Модель загружена и FAISS индекс успешно построен")

@app.post("/recommend", response_model=QueryResponse)
async def recommend_queries(request: QueryRequest):
    if not index:
        raise HTTPException(status_code=500, detail="Модель не инициализирована")
    
    nearest_queries, similarities = find_nearest_queries(request.text)
    
    return QueryResponse(
        similar_queries=nearest_queries,
        similarities=similarities
    )

if __name__ == "__main__":
    uvicorn.run("recommend:app", host="0.0.0.0", port=1000, reload=True)
