import torch
from sentence_transformers import SentenceTransformer
from typing import List
import time

# Загружаем модель один раз
model = SentenceTransformer("deepvk/USER-bge-m3", device="cpu")

def get_local_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Получение эмбедингов для списка текстов с использованием локальной модели SentenceTransformer.
    
    Args:
        texts: Список текстов для преобразования в эмбединги
        
    Returns:
        Список векторов эмбедингов
    """
    # Кодируем входной батч
    embeddings = model.encode(
        texts,
        convert_to_tensor=True,  # получаем тензоры
        device="cpu",            # принудительно на CPU
        batch_size=20,           # батчинг
        show_progress_bar=False  # скрыть прогресс
    )
    
    # Преобразуем в список списков (обычные float значения)
    return embeddings.cpu().tolist()


import asyncio

texts = [
    "Text 1", "Text 2", "Text 3",  # и т.д. до 20
]

# Завернуто в ассинхронный main
async def main():
    time_start = time.time()
    embeddings = await get_local_embeddings(texts)
    print(time.time() - time_start)
    print(embeddings)

asyncio.run(main())
