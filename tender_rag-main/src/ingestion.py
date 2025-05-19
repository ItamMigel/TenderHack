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


class BM25Ingestor:
    def __init__(self):
        pass

    def create_bm25_index(self, chunks: List[str]) -> BM25Okapi:
        """Create a BM25 index from a list of text chunks."""
        tokenized_chunks = [chunk.split() for chunk in chunks]
        return BM25Okapi(tokenized_chunks)
    
    def process_reports(self, all_reports_dir: Path, output_dir: Path):
        """Process all reports and save individual BM25 indices.
        
        Args:
            all_reports_dir (Path): Directory containing the JSON report files
            output_dir (Path): Directory where to save the BM25 indices
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        all_report_paths = list(all_reports_dir.glob("*.json"))

        for report_path in tqdm(all_report_paths, desc="Processing reports for BM25"):
            # Load the report
            with open(report_path, 'r', encoding='utf-8') as f:
                report_data = json.load(f)
                
            # Extract text chunks and create BM25 index
            text_chunks = [chunk['text'] for chunk in report_data['content']['chunks']]
            bm25_index = self.create_bm25_index(text_chunks)
            
            # Save BM25 index
            sha1_name = report_data["metainfo"]["sha1_name"]
            output_file = output_dir / f"{sha1_name}.pkl"
            with open(output_file, 'wb') as f:
                pickle.dump(bm25_index, f)
                
        print(f"Processed {len(all_report_paths)} reports")

# class VectorDBIngestor:
#     def __init__(self):
#         self.llm = self._set_up_llm()

#     def _set_up_llm(self):
#         load_dotenv()
#         llm = bit14(
#             api_key=os.getenv("bit14_API_KEY"),
#             timeout=None,
#             max_retries=2
#         )
#         return llm

#     @retry(wait=wait_fixed(20), stop=stop_after_attempt(2))
#     def _get_embeddings(self, text: Union[str, List[str]], model: str = "text-embedding-3-large") -> List[float]:
#         if isinstance(text, str) and not text.strip():
#             raise ValueError("Input text cannot be an empty string.")
        
#         if isinstance(text, list):
#             text_chunks = [text[i:i + 1024] for i in range(0, len(text), 1024)]
#         else:
#             text_chunks = [text]

#         embeddings = []
#         for chunk in text_chunks:
#             response = self.llm.embeddings.create(input=chunk, model=model)
#             embeddings.extend([embedding.embedding for embedding in response.data])
        
#         return embeddings

#     def _create_chroma_collection(self, client, collection_name):
#         """Create or get a ChromaDB collection."""
#         try:
#             return client.get_collection(name=collection_name)
#         except:
#             return client.create_collection(name=collection_name)
    
#     def _process_report(self, report: dict, chroma_client):
#         """Process a report and add its chunks to a ChromaDB collection."""
#         chunks = report['content']['chunks']
#         text_chunks = [chunk['text'] for chunk in chunks]
#         sha1_name = report["metainfo"]["sha1_name"]
#         collection_name = f"collection_{sha1_name}"
        
#         # Create or get collection
#         collection = self._create_chroma_collection(chroma_client, collection_name)
        
#         # Get embeddings
#         embeddings = self._get_embeddings(text_chunks)
        
#         # Add documents to collection
#         ids = [str(i) for i in range(len(text_chunks))]
        
#         # Создаем метаданные для каждого чанка
#         metadatas = []
#         for i, chunk in enumerate(chunks):
#             metadata = {
#                 "chunk_id": i,
#                 "sha1_name": sha1_name,
#                 "page": chunk["page"],  # Добавляем номер страницы
#                 "file": sha1_name,      # Добавляем имя файла
#                 "participant": "Участник 1"  # Добавляем участника
#             }
#             metadatas.append(metadata)
        
#         collection.add(
#             documents=text_chunks,
#             embeddings=embeddings,
#             ids=ids,
#             metadatas=metadatas
#         )
        
#         return collection

#     def process_reports(self, all_reports_dir: Path, output_dir: Path):
#         """Process all reports and create a single ChromaDB collection with all documents.
        
#         Args:
#             all_reports_dir (Path): Directory containing the JSON report files
#             output_dir (Path): Directory where to save the ChromaDB database
#         """
#         output_dir.mkdir(parents=True, exist_ok=True)
#         all_report_paths = list(all_reports_dir.glob("*.json"))
        
#         # Initialize ChromaDB client
#         chroma_client = chromadb.PersistentClient(str(output_dir))
        
#         # Create a single collection for all documents
#         collection_name = "all_documents"
#         try:
#             # Пробуем получить существующую коллекцию
#             try:
#                 collection = chroma_client.get_collection(name=collection_name)
#                 # Удаляем коллекцию, если она существует
#                 chroma_client.delete_collection(name=collection_name)
#                 print(f"Existing collection '{collection_name}' deleted")
#             except Exception as e:
#                 # Коллекции нет, просто продолжаем
#                 pass
                
#             # Создаем новую коллекцию
#             collection = chroma_client.create_collection(name=collection_name)
#             print(f"Created new collection '{collection_name}'")
            
#             # Process all documents and add them to the single collection
#             total_chunks = 0
#             for report_path in tqdm(all_report_paths, desc="Processing reports"):
#                 with open(report_path, 'r', encoding='utf-8') as file:
#                     report_data = json.load(file)
                    
#                 # Process document and add to the common collection
#                 chunks_added = self._add_report_to_collection(report_data, collection)
#                 total_chunks += chunks_added

#             print(f"Processed {len(all_report_paths)} reports with {total_chunks} total chunks to ChromaDB at {output_dir}")
#         except Exception as e:
#             print(f"Error processing reports: {e}")
#             raise

#     def _add_report_to_collection(self, report: dict, collection):
#         """Add report chunks to the common collection."""
#         chunks = report['content']['chunks']
#         text_chunks = [chunk['text'] for chunk in chunks]
#         sha1_name = report["metainfo"]["sha1_name"]
#         company_name = report["metainfo"].get("company_name", sha1_name)
        
#         if not text_chunks:
#             return 0
            
#         # Get embeddings
#         embeddings = self._get_embeddings(text_chunks)
        
#         # Create unique IDs by combining document name and chunk index
#         ids = [f"{sha1_name}_{i}" for i in range(len(text_chunks))]
        
#         # Создаем метаданные для каждого чанка
#         metadatas = []
#         for i, chunk in enumerate(chunks):
#             metadata = {
#                 "chunk_id": i,
#                 "sha1_name": sha1_name,
#                 "company_name": company_name,
#                 "page": chunk["page"],  # Номер страницы
#                 "file": sha1_name,      # Имя файла
#                 "participant": "Участник 1"  # Участник
#             }
#             metadatas.append(metadata)
        
#         # Add documents to collection
#         collection.add(
#             documents=text_chunks,
#             embeddings=embeddings,
#             ids=ids,
#             metadatas=metadatas
#         )
        
#         return len(text_chunks)