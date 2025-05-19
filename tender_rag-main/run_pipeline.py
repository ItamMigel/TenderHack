import os
import sys
from pathlib import Path
from pyprojroot import here
import os
import json
import pickle
from typing import List, Union
from pathlib import Path
from tqdm import tqdm

from dotenv import load_dotenv
from rank_bm25 import BM25Okapi
import chromadb
import numpy as np
from tenacity import retry, wait_fixed, stop_after_attempt

import json
import logging
from typing import List, Tuple, Dict, Union
from rank_bm25 import BM25Okapi
import pickle
from pathlib import Path
from dotenv import load_dotenv
import os
import numpy as np
from src.reranking import LLMReranker

from dataclasses import dataclass

_log = logging.getLogger(__name__)

# Explicitly set environment variables for docling
os.environ["DOCLING_DEVICE"] = "cpu"
os.environ["PYTORCH_DEVICE"] = "cpu"
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "0"
os.environ["OMP_NUM_THREADS"] = "1"

class BM25Retriever:
    def __init__(self, bm25_db_dir: Path, documents_dir: Path):
        self.bm25_db_dir = bm25_db_dir
        self.documents_dir = documents_dir
        
    def retrieve_by_company_name(self, company_name: str, query: str, top_n: int = 3, return_parent_pages: bool = False) -> List[Dict]:
        document_path = None
        for path in self.documents_dir.glob("*.json"):
            with open(path, 'r', encoding='utf-8') as f:
                doc = json.load(f)
                if doc["metainfo"]["company_name"] == company_name:
                    document_path = path
                    document = doc
                    break
                    
        if document_path is None:
            raise ValueError(f"No report found with '{company_name}' company name.")
            
        # Load corresponding BM25 index
        bm25_path = self.bm25_db_dir / f"{document['metainfo']['sha1_name']}.pkl"
        with open(bm25_path, 'rb') as f:
            bm25_index = pickle.load(f)
            
        # Get the document content and BM25 index
        document = document
        chunks = document["content"]["chunks"]
        pages = document["content"]["pages"]
        
        # Get BM25 scores for the query
        tokenized_query = query.split()
        scores = bm25_index.get_scores(tokenized_query)
        
        actual_top_n = min(top_n, len(scores))
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:actual_top_n]
        
        retrieval_results = []
        seen_pages = set()
        
        for index in top_indices:
            score = round(float(scores[index]), 4)
            chunk = chunks[index]
            parent_page = next(page for page in pages if page["page"] == chunk["page"])
            
            if return_parent_pages:
                if parent_page["page"] not in seen_pages:
                    seen_pages.add(parent_page["page"])
                    result = {
                        "distance": score,
                        "page": parent_page["page"],
                        "text": parent_page["text"]
                    }
                    retrieval_results.append(result)
            else:
                result = {
                    "distance": score,
                    "page": chunk["page"],
                    "text": chunk["text"]
                }
                retrieval_results.append(result)
        
        return retrieval_results



# class VectorRetriever:
#     def __init__(self, vector_db_dir: Path, documents_dir: Path):
#         self.vector_db_dir = vector_db_dir
#         self.documents_dir = documents_dir
#         self.chroma_client = chromadb.PersistentClient(str(vector_db_dir))
#         self.all_documents = self._load_documents()
#         self.vector_db = self._get_common_collection()
#         self.llm = self._set_up_llm()

#     def _set_up_llm(self):
#         load_dotenv()
#         llm = bit14(
#             api_key=os.getenv("bit14_API_KEY"),
#             timeout=None,
#             max_retries=2
#             )
#         return llm
    
#     @staticmethod
#     def set_up_llm():
#         load_dotenv()
#         llm = bit14(
#             api_key=os.getenv("bit14_API_KEY"),
#             timeout=None,
#             max_retries=2
#             )
#         return llm
    
#     def _get_common_collection(self):
#         """Get the common collection containing all documents."""
#         collection_name = "all_documents"
#         try:
#             return self.chroma_client.get_collection(name=collection_name)
#         except Exception as e:
#             _log.error(f"Error accessing ChromaDB collection: {e}")
#             return None

#     def _load_documents(self):
#         """Load document info from JSON files."""
#         documents = {}
#         # Get list of JSON document paths
#         all_documents_paths = list(self.documents_dir.glob('*.json'))
        
#         for document_path in all_documents_paths:
#             stem = document_path.stem
#             try:
#                 with open(document_path, 'r', encoding='utf-8') as f:
#                     document = json.load(f)
                    
#                 # Validate that the document meets the expected schema
#                 if not (isinstance(document, dict) and "metainfo" in document and "content" in document):
#                     _log.warning(f"Skipping {document_path.name}: does not match the expected schema.")
#                     continue
                
#                 company_name = document["metainfo"].get("company_name", stem)
#                 documents[company_name] = document
                
#             except Exception as e:
#                 _log.error(f"Error loading JSON from {document_path.name}: {e}")
#                 continue
                
#         return documents

#     @staticmethod
#     def get_strings_cosine_similarity(str1, str2):
#         llm = VectorRetriever.set_up_llm()
#         embeddings = llm.embeddings.create(input=[str1, str2], model="text-embedding-3-large")
#         embedding1 = embeddings.data[0].embedding
#         embedding2 = embeddings.data[1].embedding
#         similarity_score = np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))
#         similarity_score = round(similarity_score, 4)
#         return similarity_score

#     def retrieve_by_company_name(self, query: str, company_name: str = None, llm_reranking_sample_size: int = None, top_n: int = 3, return_parent_pages: bool = False) -> List[Tuple[str, float]]:
#         # Если коллекция не найдена, возвращаем пустой список
#         if self.vector_db is None:
#             _log.error("Vector database collection not found")
#             return []
            
#         # Получаем документ для извлечения страниц и чанков
#         # Даже если ищем по всей БД, нам все равно нужны данные из документа для return_parent_pages
#         if company_name and company_name in self.all_documents:
#             document = self.all_documents[company_name]
#         else:
#             # Если имя компании не указано или не найдено, используем первый документ
#             if not self.all_documents:
#                 _log.error("No documents available")
#                 return []
#             company_name = next(iter(self.all_documents.keys()))
#             document = self.all_documents[company_name]
        
#         chunks = document["content"]["chunks"]
#         pages = document["content"]["pages"]
        
#         actual_top_n = min(top_n, 1000)  # Увеличиваем лимит результатов для поиска по всей БД
        
#         # Получаем эмбеддинг для запроса
#         embedding = self.llm.embeddings.create(
#             input=query,
#             model="text-embedding-3-large"
#         )
#         embedding = embedding.data[0].embedding
        
#         # Убираем фильтрацию по company_name и ищем по всей базе данных
#         results = self.vector_db.query(
#             query_embeddings=[embedding],
#             n_results=actual_top_n,
#             include=["metadatas", "documents"]
#         )
        
#         retrieval_results = []
#         seen_pages = set()
        
#         # Обработка результатов из ChromaDB
#         distances = results.get("distances", [[]])[0]  # Получаем дистанции
#         ids = results.get("ids", [[]])[0]  # Получаем IDs
#         metadatas = results.get("metadatas", [[]])[0]  # Получаем метаданные
#         documents_text = results.get("documents", [[]])[0]  # Получаем тексты
        
#         if not ids:
#             return []
            
#         for i, (doc_id, distance, metadata, doc_text) in enumerate(zip(ids, distances, metadatas, documents_text)):
#             # Получаем метаданные
#             chunk_id = metadata.get("chunk_id", i)
#             page_num = metadata.get("page")
#             doc_company_name = metadata.get("company_name", "")
            
#             # Для возврата родительских страниц, нам нужно найти соответствующий документ
#             doc_to_use = document
#             if doc_company_name != company_name and doc_company_name in self.all_documents:
#                 doc_to_use = self.all_documents[doc_company_name]
                
#             # Находим родительскую страницу
#             try:
#                 parent_page = next(page for page in doc_to_use["content"]["pages"] if page["page"] == page_num)
#             except:
#                 # Если страница не найдена, используем текст из результата
#                 parent_page = {"page": page_num, "text": doc_text}
            
#             distance = round(float(distance), 4)
            
#             # Генерируем уникальный ключ для страницы
#             page_key = f"{doc_company_name}_{page_num}"
            
#             if return_parent_pages:
#                 if page_key not in seen_pages:
#                     seen_pages.add(page_key)
#                     result = {
#                         "distance": distance,
#                         "page": page_num,
#                         "text": parent_page["text"],
#                         "metadata": metadata
#                     }
#                     retrieval_results.append(result)
#             else:
#                 result = {
#                     "distance": distance,
#                     "page": page_num,
#                     "text": doc_text,
#                     "metadata": metadata
#                 }
#                 retrieval_results.append(result)
        
#         # Ограничиваем количество результатов до запрошенного top_n
#         return retrieval_results[:top_n]

#     def retrieve_all(self, company_name: str = None) -> List[Dict]:
#         """Retrieve all pages for a given company."""
#         # Если имя компании указано, ищем соответствующий документ
#         if company_name and company_name in self.all_documents:
#             document = self.all_documents[company_name]
#         else:
#             # Если имя компании не указано или не найдено, используем первый документ
#             if not self.all_documents:
#                 _log.error("No documents available")
#                 return []
#             company_name = next(iter(self.all_documents.keys()))
#             document = self.all_documents[company_name]
        
#         pages = document["content"]["pages"]
        
#         all_pages = []
#         for page in sorted(pages, key=lambda p: p["page"]):
#             result = {
#                 "distance": 0.5,
#                 "page": page["page"],
#                 "text": page["text"],
#                 "metadata": {"company_name": company_name, "page": page["page"], "participant": "Участник 1"}
#             }
#             all_pages.append(result)
            
#         return all_pages


# class HybridRetriever:
#     def __init__(self, vector_db_dir: Path, documents_dir: Path):
#         self.vector_retriever = VectorRetriever(vector_db_dir, documents_dir)
#         self.bm25_retriever = BM25Retriever(vector_db_dir.parent / "bm25_dbs", documents_dir)
        
#     def retrieve_by_company_name(
#         self, 
#         query: str, 
#         company_name: str = None,
#         top_n: int = 3,
#         return_parent_pages: bool = False,
#         bm25_weight: float = 0.2,
#         search_all_documents: bool = True  # Новый параметр для поиска по всем документам
#     ) -> List[Dict]:
#         # Retrieve from vector DB (по всем документам или только по указанной компании)
#         vector_results = self.vector_retriever.retrieve_by_company_name(
#             query=query,
#             company_name=company_name if not search_all_documents else None,  # Передаем None для поиска по всем документам
#             top_n=top_n * 2,  # Retrieve more results for re-ranking
#             return_parent_pages=return_parent_pages
#         )
        
#         # Retrieve from BM25 (только по указанной компании, т.к. BM25 работает только с одним документом)
#         try:
#             if company_name:
#                 bm25_results = self.bm25_retriever.retrieve_by_company_name(
#                     company_name=company_name,
#                     query=query,
#                     top_n=top_n * 2,
#                     return_parent_pages=return_parent_pages
#                 )
#             else:
#                 bm25_results = []
#         except Exception as e:
#             _log.warning(f"Error retrieving BM25 results: {e}")
#             bm25_results = []
            
#         # Combine and re-rank results 
#         all_results = {}
        
#         # Используем company_name + page как уникальный ключ
#         def get_page_key(result):
#             metadata = result.get("metadata", {})
#             doc_company_name = metadata.get("company_name", "unknown")
#             page = result["page"]
#             return f"{doc_company_name}_{page}"
        
#         # Process vector results
#         for result in vector_results:
#             page_key = get_page_key(result)
#             distance = result["distance"]
#             all_results[page_key] = {
#                 "text": result["text"],
#                 "vector_score": distance,
#                 "bm25_score": 0,
#                 "page": result["page"],
#                 "metadata": result.get("metadata", {})
#             }
            
#         # Process BM25 results
#         for result in bm25_results:
#             if company_name:
#                 # Для BM25 мы всегда знаем компанию
#                 page_key = f"{company_name}_{result['page']}"
                
#                 if page_key in all_results:
#                     all_results[page_key]["bm25_score"] = result["distance"]
#                 else:
#                     metadata = {"company_name": company_name, "page": result["page"], "participant": "Участник 1"} 
#                     all_results[page_key] = {
#                         "text": result["text"],
#                         "vector_score": 0,
#                         "bm25_score": result["distance"],
#                         "page": result["page"],
#                         "metadata": metadata
#                     }
                
#         # Calculate combined score
#         for page_key, result in all_results.items():
#             # Normalize vector score (assumes higher is better for both)
#             vector_score = result["vector_score"]
#             bm25_score = result["bm25_score"]
            
#             # Combined score
#             combined_score = (1 - bm25_weight) * vector_score + bm25_weight * bm25_score
#             result["combined_score"] = combined_score
#             result["distance"] = combined_score  # For backwards compatibility
            
#         # Sort by combined score and return top N
#         sorted_results = sorted(
#             all_results.values(), 
#             key=lambda x: x["combined_score"], 
#             reverse=True
#         )[:top_n]
        
#         return sorted_results


@dataclass
class PipelineConfig:
    def __init__(self, root_path: Path, subset_name: str = "subset.csv", questions_file_name: str = "questions.json", pdf_reports_dir_name: str = "pdf_reports", serialized: bool = False, config_suffix: str = ""):
        self.root_path = root_path
        suffix = "_ser_tab" if serialized else ""

        self.subset_path = root_path / subset_name
        self.questions_file_path = root_path / questions_file_name
        self.pdf_reports_dir = root_path / pdf_reports_dir_name
        
        self.answers_file_path = root_path / f"answers{config_suffix}.json"       
        self.debug_data_path = root_path / "debug_data"
        self.databases_path = root_path / f"databases{suffix}"
        
        self.vector_db_dir = self.databases_path / "vector_dbs"
        self.documents_dir = self.databases_path / "chunked_reports"
        self.bm25_db_path = self.databases_path / "bm25_dbs"

        self.parsed_reports_dirname = "01_parsed_reports"
        self.parsed_reports_debug_dirname = "01_parsed_reports_debug"
        self.merged_reports_dirname = f"02_merged_reports{suffix}"
        self.reports_markdown_dirname = f"03_reports_markdown{suffix}"

        self.parsed_reports_path = self.debug_data_path / self.parsed_reports_dirname
        self.parsed_reports_debug_path = self.debug_data_path / self.parsed_reports_debug_dirname
        self.merged_reports_path = self.debug_data_path / self.merged_reports_dirname
        self.reports_markdown_path = self.debug_data_path / self.reports_markdown_dirname

def _initialize_paths(root_path: Path, subset_name: str, questions_file_name: str, pdf_reports_dir_name: str, run_config) -> PipelineConfig:
        """Initialize paths configuration based on run config settings"""
        return PipelineConfig(
            root_path=root_path,
            subset_name=subset_name,
            questions_file_name=questions_file_name,
            pdf_reports_dir_name=pdf_reports_dir_name,
            serialized=run_config.use_serialized_tables,
            config_suffix=run_config.config_suffix
        )


# Import pipeline after setting environment variables
from src.pipeline import Pipeline, max_nst_o3m_config

# Configuration
root_path = here() / "data" / "test_set"
pipeline = Pipeline(root_path, run_config=max_nst_o3m_config)

run_config = max_nst_o3m_config
subset_name = "subset.csv"
questions_file_name = "questions.json"
pdf_reports_dir_name = "pdf_reports"
paths = _initialize_paths(root_path, subset_name, questions_file_name, pdf_reports_dir_name, run_config)
# Execute the pipeline steps
try:
    # Step 1: Parse PDF reports
    pipeline.parse_pdf_reports_sequential()
    
    # Step 2: Merge reports
    pipeline.merge_reports()
    
    # Step 3: Export reports to markdown for review
    pipeline.export_reports_to_markdown()
    
    # Step 4: Chunk reports
    pipeline.chunk_reports()
    
    # Step 5: Create vector databases
    pipeline.create_vector_dbs()
    retriever = VectorRetriever(
                vector_db_dir=paths.vector_db_dir,
                documents_dir=paths.documents_dir
            )
    
    # Step 6: Process questions and generate answers
    result = pipeline.get_answer_for_company(question="What 2022 highlights", retriever=retriever) # "Что означает термин 223-ФЗ"
    
    print(result)
    print("---")
    print("Pipeline executed successfully!")
except Exception as e:
    print(f"Error occurred during pipeline execution: {e}")
    sys.exit(1) 