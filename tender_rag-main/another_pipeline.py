import os
import sys
from pathlib import Path
from pyprojroot import here
import os
import json
import pickle
from pathlib import Path
from tqdm import tqdm
from dotenv import load_dotenv
from rank_bm25 import BM25Okapi
import chromadb
import numpy as np
from tenacity import retry, wait_fixed, stop_after_attempt
import json
import logging
from typing import List, Dict
import pickle
from pathlib import Path
from dotenv import load_dotenv
import os
import numpy as np
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer
import time

# Explicitly set environment variables for docling
os.environ["DOCLING_DEVICE"] = "cuda"
os.environ["PYTORCH_DEVICE"] = "cpu"
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "0"
os.environ["OMP_NUM_THREADS"] = "1"

# Import pipeline after setting environment variables
from src.pipeline import Pipeline, max_nst_o3m_config

model = SentenceTransformer("deepvk/USER-bge-m3", device="cpu")

@retry(wait=wait_fixed(2), stop=stop_after_attempt(5))
def get_embeddings(texts: List[str]) -> List[List[float]]:
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

def create_vector_database(chunks_dir: Path, output_dir: Path = None, force_recreate: bool = True) -> None:
    """
    Создание векторной базы данных из чанков текста
    
    Args:
        chunks_dir: Путь к директории с чанками
        output_dir: Путь для сохранения базы данных ChromaDB
        force_recreate: Если True, пересоздаст коллекцию, даже если она уже существует
    """
    # Инициализация ChromaDB
    if output_dir is None:
        output_dir = chunks_dir.parent / "chroma_db"
    
    output_dir.mkdir(exist_ok=True, parents=True)
    
    chroma_client = chromadb.PersistentClient(path=str(output_dir))
    
    collection_name = "report_chunks"
    
    # Проверяем существование коллекции и удаляем её при необходимости
    try:
        existing_collections = chroma_client.list_collections()
        for collection in existing_collections:
            if collection.name == collection_name:
                if force_recreate:
                    print(f"Удаление существующей коллекции: {collection_name}")
                    chroma_client.delete_collection(collection_name)
                else:
                    print(f"Использование существующей коллекции: {collection_name}")
                    return collection
    except Exception as e:
        print(f"Ошибка при проверке коллекций: {e}")
    
    # Создание новой коллекции
    collection = chroma_client.create_collection(
        name=collection_name,
        metadata={"description": "Чанки отчетов с эмбедингами"}
    )
    
    # Загрузка и обработка чанков
    chunk_files = list(chunks_dir.glob("*.json"))
    print(f"Найдено {len(chunk_files)} файлов с чанками")
    
    batch_size = 20  # Ограничение размера пакета для API запросов
    
    all_chunks = []
    all_metadata = []
    all_ids = []
    
    # Сбор всех чанков
    for chunk_file in tqdm(chunk_files, desc="Загрузка чанков"):
        with open(chunk_file, "r", encoding="utf-8") as f:
            chunks_data = json.load(f)
            
        file_name = chunk_file.stem
        
        for i, chunk in enumerate(chunks_data["content"]["chunks"]):
            if not isinstance(chunk, dict):
                print(f"Пропуск некорректного чанка в {file_name}: {chunk}")
                continue
                
            chunk_id = f"{file_name}_{i}"
            chunk_text = chunk.get("text", "")
            chunk_page = chunk.get("page", 0)
            
            if not chunk_text:
                continue
                
            all_chunks.append(chunk_text)
            all_metadata.append({
                "filename": file_name,
                "page": chunk_page
            })
            all_ids.append(chunk_id)
    
    print(f"Всего собрано {len(all_chunks)} чанков")
    
    # Обработка чанков пакетами
    for i in tqdm(range(0, len(all_chunks), batch_size), desc="Создание эмбедингов и сохранение в ChromaDB"):
        batch_chunks = all_chunks[i:i+batch_size]
        batch_metadata = all_metadata[i:i+batch_size]
        batch_ids = all_ids[i:i+batch_size]
        
        # Получение эмбедингов
        embeddings = get_embeddings(batch_chunks)
        
        # Сохранение в ChromaDB
        collection.add(
            embeddings=embeddings,
            documents=batch_chunks,
            metadatas=batch_metadata,
            ids=batch_ids
        )
    
    print(f"База данных успешно создана в {output_dir}")
    return collection

def get_relevant_chunks(query: str, collection, top_n: int = 3) -> List[Dict]:
        """
        Get the top N relevant chunks for a given query.
        
        Args:
            query: The query string to search for.
            collection: The ChromaDB collection to search in.
            top_n: The number of top relevant chunks to return.
        
        Returns:
            A list of dictionaries containing the top N relevant chunks.
        """
        # Получение эмбединга для запроса
        query_embedding = get_embeddings([query])[0]
        
        # Поиск релевантных чанков
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_n
        )
        
        relevant_chunks = []
        document = results["documents"][0]
        metadatas = results["metadatas"][0]
        for idx in range(len(document)):
            relevant_chunks.append({
                "chunk": document[idx],
                "metadata": metadatas[idx]
            })
        
        return relevant_chunks

# Configuration
root_path = here() / "data" / "test_set"
pipeline = Pipeline(root_path, run_config=max_nst_o3m_config)

run_config = max_nst_o3m_config
subset_name = "subset.csv"
questions_file_name = "questions.json"
pdf_reports_dir_name = "pdf_reports"

def reload_all_bd():
    output_dir = here() / "data" / "test_set" / "databases" / "chroma_db"
    if (here() / "data" / "test_set" / "databases" / "chroma_db").exists():
        # Создаем клиент с указанием пути к существующей базе
        chroma_client = chromadb.PersistentClient(path=str(output_dir))
        db_collection = chroma_client.get_collection(name="report_chunks")
        print(f"База данных загружена. Количество записей: {db_collection.count()}")
    else:
        start = time.time()
        pipeline.parse_pdf_reports_sequential()
        print("parse_pdf_reports_sequential:", time.time()-start)
        start = time.time()
        pipeline.merge_reports()
        print("merge_reports:", time.time()-start)
        start = time.time()
        pipeline.export_reports_to_markdown()
        print("export_reports_to_markdown:", time.time()-start)
        start = time.time()
        pipeline.chunk_reports()
        print("chunk_reports:", time.time()-start)
        chunks_dir = here() / "data" / "test_set" / "databases" / "chunked_reports"
        db_collection = create_vector_database(chunks_dir)
        print(f"База данных создана. Количество записей: {db_collection.count()}")
    
    return db_collection


def ask_question(query, db_collection, history_chat):
    history_chat = history_chat[-5:]
    # перефразирование относительно истории
    query = paraphrasing(query, history_chat)
    
    relevant_chunks = get_relevant_chunks(query=query, collection=db_collection)
    result = pipeline.get_answer_for_company(question=query, context=relevant_chunks, history_chat=history_chat) # "Что означает термин 223-ФЗ"
    return result, relevant_chunks
    
def add_pdf(db_collection, pdf_path: str):
    """
    Обрабатывает новый PDF-файл и добавляет его чанки в существующую базу данных.
    
    Args:
        db_collection: Коллекция ChromaDB для добавления чанков
        pdf_path: Путь к PDF-файлу для обработки
    """
    import shutil
    from pathlib import Path
    
    # Проверяем существование файла
    pdf_file = Path(pdf_path)
    if not pdf_file.exists() or not pdf_file.is_file():
        raise FileNotFoundError(f"PDF-файл не найден: {pdf_path}")
        
    # Определяем пути для сохранения
    pdf_filename = pdf_file.name
    pdf_reports_dir = here() / "data" / "test_set" / "databases" / pdf_reports_dir_name
    temp_dir = here() / "data" / "test_set" / "databases" / "temp_process"
    chunks_dir = here() / "data" / "test_set" / "databases" / "chunked_reports"
    
    # Создаем временную директорию для обработки
    temp_dir.mkdir(exist_ok=True, parents=True)
    pdf_reports_dir.mkdir(exist_ok=True, parents=True)
    
    # Копируем PDF в директорию отчетов
    target_pdf_path = pdf_reports_dir / pdf_filename
    shutil.copy2(pdf_path, target_pdf_path)
    
    print(f"PDF скопирован в {target_pdf_path}")
    
    # Обрабатываем PDF с помощью pipeline
    # Создаем временный экземпляр Pipeline для обработки только этого файла
    temp_pipeline = Pipeline(temp_dir.parent, run_config=max_nst_o3m_config)
    
    # Парсим PDF в JSON
    temp_pipeline.parse_pdf_reports_sequential(single_file=target_pdf_path)
    
    # Экспортируем в markdown и чанкируем
    temp_pipeline.merge_reports()
    temp_pipeline.export_reports_to_markdown()
    temp_pipeline.chunk_reports()
    
    # Получаем созданные чанки
    new_chunks_files = list(temp_dir / "chunked_reports".glob("*.json"))
    
    if not new_chunks_files:
        print("Предупреждение: Не создано ни одного чанка из PDF")
        return
    
    batch_size = 20  # Ограничение размера пакета для API запросов
    
    # Обрабатываем каждый файл с чанками
    for chunk_file in tqdm(new_chunks_files, desc="Обработка новых чанков"):
        with open(chunk_file, "r", encoding="utf-8") as f:
            chunks_data = json.load(f)
            
        file_name = chunk_file.stem
        
        all_chunks = []
        all_metadata = []
        all_ids = []
        
        # Собираем чанки из файла
        for i, chunk in enumerate(chunks_data["content"]["chunks"]):
            if not isinstance(chunk, dict):
                print(f"Пропуск некорректного чанка в {file_name}: {chunk}")
                continue
                
            chunk_id = f"{file_name}_{i}"
            chunk_text = chunk.get("text", "")
            chunk_page = chunk.get("page", 0)
            
            if not chunk_text:
                continue
                
            all_chunks.append(chunk_text)
            all_metadata.append({
                "filename": file_name,
                "page": chunk_page
            })
            all_ids.append(chunk_id)
        
        # Обработка чанков пакетами
        for i in range(0, len(all_chunks), batch_size):
            batch_chunks = all_chunks[i:i+batch_size]
            batch_metadata = all_metadata[i:i+batch_size]
            batch_ids = all_ids[i:i+batch_size]
            
            # Получение эмбедингов
            embeddings = get_embeddings(batch_chunks)
            
            # Добавление в существующую коллекцию ChromaDB
            db_collection.add(
                embeddings=embeddings,
                documents=batch_chunks,
                metadatas=batch_metadata,
                ids=batch_ids
            )
    
    # Копируем обработанные чанки в основную директорию чанков
    for chunk_file in new_chunks_files:
        shutil.copy2(chunk_file, chunks_dir / chunk_file.name)
    
    # Удаляем временные файлы
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
        
    print(f"PDF успешно обработан и добавлен в базу данных. Количество записей в базе: {db_collection.count()}")
    return True

def add_pdf(db_collection, pdf_path: str):
    """
    Обрабатывает новый PDF-файл и добавляет его чанки в существующую базу данных.
    
    Args:
        db_collection: Коллекция ChromaDB для добавления чанков
        pdf_path: Путь к PDF-файлу для обработки
    """
    import shutil
    from pathlib import Path
    
    # Проверяем существование файла
    pdf_file = Path(pdf_path)
    if not pdf_file.exists() or not pdf_file.is_file():
        raise FileNotFoundError(f"PDF-файл не найден: {pdf_path}")
        
    # Определяем пути для сохранения
    pdf_filename = pdf_file.name
    pdf_reports_dir = here() / "data" / "test_set" / "databases" / pdf_reports_dir_name
    temp_dir = here() / "data" / "test_set" / "databases" / "temp_process"
    chunks_dir = here() / "data" / "test_set" / "databases" / "chunked_reports"
    
    # Создаем временную директорию для обработки
    temp_dir.mkdir(exist_ok=True, parents=True)
    pdf_reports_dir.mkdir(exist_ok=True, parents=True)
    
    # Копируем PDF в директорию отчетов
    target_pdf_path = pdf_reports_dir / pdf_filename
    shutil.copy2(pdf_path, target_pdf_path)
    
    print(f"PDF скопирован в {target_pdf_path}")
    
    # Обрабатываем PDF с помощью pipeline
    # Создаем временный экземпляр Pipeline для обработки только этого файла
    main_dir = here() / "uploads"
    temp_pipeline = Pipeline(main_dir, run_config=max_nst_o3m_config)
    
    # Парсим PDF в JSON
    temp_pipeline.parse_pdf_reports_sequential()
    
    # Экспортируем в markdown и чанкируем
    temp_pipeline.merge_reports()
    temp_pipeline.export_reports_to_markdown()
    temp_pipeline.chunk_reports()
    
    # Получаем созданные чанки
    # Сохраняем путь к чанкам в new_chunks_files
    new_chunks_files = list((main_dir / "databases" / "chunked_reports").glob("*.json"))
    
    if not new_chunks_files:
        print("Предупреждение: Не создано ни одного чанка из PDF")
        return
    
    batch_size = 20  # Ограничение размера пакета для API запросов
    
    # Обрабатываем каждый файл с чанками
    for chunk_file in tqdm(new_chunks_files, desc="Обработка новых чанков"):
        with open(chunk_file, "r", encoding="utf-8") as f:
            chunks_data = json.load(f)
            
        file_name = chunk_file.stem
        
        all_chunks = []
        all_metadata = []
        all_ids = []
        
        # Собираем чанки из файла
        for i, chunk in enumerate(chunks_data["content"]["chunks"]):
            if not isinstance(chunk, dict):
                print(f"Пропуск некорректного чанка в {file_name}: {chunk}")
                continue
                
            chunk_id = f"{file_name}_{i}"
            chunk_text = chunk.get("text", "")
            chunk_page = chunk.get("page", 0)
            
            if not chunk_text:
                continue
                
            all_chunks.append(chunk_text)
            all_metadata.append({
                "filename": file_name,
                "page": chunk_page
            })
            all_ids.append(chunk_id)
        
        # Обработка чанков пакетами
        for i in range(0, len(all_chunks), batch_size):
            batch_chunks = all_chunks[i:i+batch_size]
            batch_metadata = all_metadata[i:i+batch_size]
            batch_ids = all_ids[i:i+batch_size]
            
            # Получение эмбедингов
            embeddings = get_embeddings(batch_chunks)
            
            # Добавление в существующую коллекцию ChromaDB
            db_collection.add(
                embeddings=embeddings,
                documents=batch_chunks,
                metadatas=batch_metadata,
                ids=batch_ids
            )
    
    # Копируем обработанные чанки в основную директорию чанков
    # for chunk_file in new_chunks_files:
    #     shutil.copy2(chunk_file, chunks_dir / chunk_file.name)
    
    # # Удаляем временные файлы
    # if temp_dir.exists():
    #     shutil.rmtree(temp_dir)
    debug_data_path = here() / "uploads" / "debug_data"
    if debug_data_path.exists() and debug_data_path.is_dir():
        shutil.rmtree(debug_data_path)
        print(f"Папка {debug_data_path} успешно удалена.")
    else:
        print(f"Папка {debug_data_path} не существует или не является директорией.")
        
    print(f"PDF успешно обработан и добавлен в базу данных. Количество записей в базе: {db_collection.count()}")
    return True

def paraphrasing(query, history_chat):
    # создаем новый query
    # new_query = pipeline.get_answer_for_company(question=query, context=history_chat, )
    return query

# query = 'В чем суть 223-ФЗ'
# db_collection = reload_all_bd()
# result, relevant_chunks = ask_question(query, db_collection)
# print("result:", result)
# print(relevant_chunks)





# here() / "data" / "test_set" / "databases" / "chunked_reports"

# Step 5: Создание эмбедингов и сохранение в ChromaDB
# chunks_dir = here() / "data" / "test_set" / "databases" / "chunked_reports"
# db_collection = create_vector_database(chunks_dir)
# print(f"База данных с эмбедингами успешно создана. Количество записей: {db_collection.count()}")


# new_pdf_path = here() / "54321.pdf"
# answer = add_pdf(db_collection, new_pdf_path)
# print("answer:", answer)
# query = 'Что необходимо каждому поставщику?'
# result, relevant_chunks = ask_question(query, db_collection)
# print("result:", result)
