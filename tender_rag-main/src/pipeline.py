from dataclasses import dataclass
from pathlib import Path
from pyprojroot import here
import logging
import os
import json
import pandas as pd

from src.pdf_parsing import PDFParser
from src.parsed_reports_merging import PageTextPreparation
from src.text_splitter import TextSplitter
# from src.ingestion import VectorDBIngestor
from src.ingestion import BM25Ingestor
from src.questions_processing import QuestionsProcessor
# from src.tables_serialization import TableSerializer
# from src.retrieval import VectorRetriever, HybridRetriever
from src.api_requests import APIProcessor

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

@dataclass
class RunConfig:
    use_serialized_tables: bool = False
    parent_document_retrieval: bool = False
    use_vector_dbs: bool = True
    use_bm25_db: bool = False
    llm_reranking: bool = False
    llm_reranking_sample_size: int = 30
    top_n_retrieval: int = 10
    parallel_requests: int = 10
    team_email: str = "79250515615@yandex.com"
    submission_name: str = "Ilia_Ris vDB + SO CoT"
    pipeline_details: str = ""
    submission_file: bool = True
    full_context: bool = False
    api_provider: str = "bit14"
    answering_model: str = "14bit"
    config_suffix: str = ""

class Pipeline:
    def __init__(self, root_path: Path, subset_name: str = "subset.csv", questions_file_name: str = "questions.json", pdf_reports_dir_name: str = "pdf_reports", run_config: RunConfig = RunConfig()):
        self.run_config = run_config
        self.paths = self._initialize_paths(root_path, subset_name, questions_file_name, pdf_reports_dir_name)
        self._convert_json_to_csv_if_needed()
        api_provider="bit14"
        self.bit14_processor = APIProcessor(provider=api_provider)
        self.answering_model = "bit14"
        self.new_challenge_pipeline = True
        

    def _initialize_paths(self, root_path: Path, subset_name: str, questions_file_name: str, pdf_reports_dir_name: str) -> PipelineConfig:
        """Initialize paths configuration based on run config settings"""
        return PipelineConfig(
            root_path=root_path,
            subset_name=subset_name,
            questions_file_name=questions_file_name,
            pdf_reports_dir_name=pdf_reports_dir_name,
            serialized=self.run_config.use_serialized_tables,
            config_suffix=self.run_config.config_suffix
        )

    def _convert_json_to_csv_if_needed(self):
        """
        Checks if subset.json exists in root dir and subset.csv is absent.
        If so, converts the JSON to CSV format.
        """
        json_path = self.paths.root_path / "subset.json"
        csv_path = self.paths.root_path / "subset.csv"
        
        if json_path.exists() and not csv_path.exists():
            try:
                with open(json_path, 'r') as f:
                    data = json.load(f)
                
                df = pd.DataFrame(data)
                
                df.to_csv(csv_path, index=False)
                
            except Exception as e:
                print(f"Error converting JSON to CSV: {str(e)}")

# Docling automatically downloads some models from huggingface when first used
# I wanted to download them prior to running the pipeline and created this crutch
    @staticmethod
    def download_docling_models(): 
        logging.basicConfig(level=logging.DEBUG)
        parser = PDFParser(output_dir=here())
        os.environ["DOCLING_DEVICE"] = "cpu"  # Принудительно использовать CPU
        parser.parse_and_export(input_doc_paths=[here() / "src/dummy_report.pdf"])

    def parse_pdf_reports_sequential(self, pdf_reports_dir=None, parsed_reports_path=None):
        logging.basicConfig(level=logging.DEBUG)
        
        if pdf_reports_dir == None:
            pdf_parser = PDFParser(
                output_dir=self.paths.parsed_reports_path,
                csv_metadata_path=self.paths.subset_path,
                num_threads=1
            )
            pdf_parser.debug_data_path = self.paths.parsed_reports_debug_path
            pdf_parser.parse_and_export(doc_dir=self.paths.pdf_reports_dir)
        else:
            pdf_parser = PDFParser(
                output_dir=parsed_reports_path,
                csv_metadata_path=self.paths.subset_path,
                num_threads=1
            )
            pdf_parser.debug_data_path = self.paths.parsed_reports_debug_path
            pdf_parser.parse_and_export(doc_dir=Path(file_path.parent))
        print(f"PDF reports parsed and saved to {self.paths.parsed_reports_path}")

    def parse_pdf_reports_parallel(self, chunk_size: int = 2, max_workers: int = 10):
        """Parse PDF reports in parallel using multiple processes.
        
        Args:
            chunk_size: Number of PDFs to process in each worker
            num_workers: Number of parallel worker processes to use
        """
        logging.basicConfig(level=logging.DEBUG)
        
        pdf_parser = PDFParser(
            output_dir=self.paths.parsed_reports_path,
            csv_metadata_path=self.paths.subset_path
        )
        pdf_parser.debug_data_path = self.paths.parsed_reports_debug_path

        input_doc_paths = list(self.paths.pdf_reports_dir.glob("*.pdf"))
        
        pdf_parser.parse_and_export_parallel(
            input_doc_paths=input_doc_paths,
            optimal_workers=max_workers,
            chunk_size=chunk_size
        )
        print(f"PDF reports parsed and saved to {self.paths.parsed_reports_path}")

    # def serialize_tables(self, max_workers: int = 10):
    #     """Process tables in files using parallel threading"""
    #     serializer = TableSerializer()
    #     serializer.process_directory_parallel(
    #         self.paths.parsed_reports_path,
    #         max_workers=max_workers
    #     )

    def merge_reports(self, parsed_reports_path=None, merged_reports_path=None):
        """Merge complex JSON reports into a simpler structure with a list of pages, where all text blocks are combined into a single string."""
        ptp = PageTextPreparation(use_serialized_tables=self.run_config.use_serialized_tables)
        if parsed_reports_path == None:
            _ = ptp.process_reports(
                reports_dir=self.paths.parsed_reports_path,
                output_dir=self.paths.merged_reports_path
            )
        else:
            _ = ptp.process_reports(
                reports_dir=parsed_reports_path,
                output_dir=merged_reports_path
            )
        print(f"Reports saved to {self.paths.merged_reports_path}")

    def export_reports_to_markdown(self, parsed_reports_path=None, reports_markdown_path=None):
        """Export processed reports to markdown format for review."""
        ptp = PageTextPreparation(use_serialized_tables=self.run_config.use_serialized_tables)
        if parsed_reports_path == None:
            ptp.export_to_markdown(
                reports_dir=self.paths.parsed_reports_path,
                output_dir=self.paths.reports_markdown_path
            )
            print(f"Reports saved to {self.paths.reports_markdown_path}")
        else:
            ptp.export_to_markdown(
                reports_dir=parsed_reports_path,
                output_dir=reports_markdown_path
            )
            print(f"Reports saved to {reports_markdown_path}")
        

    def chunk_reports(self, include_serialized_tables: bool = False, merged_reports_path=None):
        """Split processed reports into smaller chunks for better processing."""
        text_splitter = TextSplitter()
        
        serialized_tables_dir = None
        if include_serialized_tables:
            serialized_tables_dir = self.paths.parsed_reports_path
        
        if merged_reports_path==None:
            text_splitter.split_all_reports(
                self.paths.merged_reports_path,
                self.paths.documents_dir,
                serialized_tables_dir
            )
        else:
            text_splitter.split_all_reports(
                merged_reports_path,
                self.paths.documents_dir, # 
                serialized_tables_dir
            )
        print(f"Chunked reports saved to {self.paths.documents_dir}")

    def create_vector_dbs(self):
        """Create vector databases from chunked reports."""
        input_dir = self.paths.documents_dir
        output_dir = self.paths.vector_db_dir
        
        # vdb_ingestor = VectorDBIngestor()
        # vdb_ingestor._process_report(input_dir, output_dir)
        # print(f"Vector databases created in {output_dir}")
    
    def create_bm25_db(self):
        """Create BM25 database from chunked reports."""
        input_dir = self.paths.documents_dir
        output_file = self.paths.bm25_db_path
        
        bm25_ingestor = BM25Ingestor()
        bm25_ingestor.process_reports(input_dir, output_file)
        print(f"BM25 database created at {output_file}")
    
    def parse_pdf_reports(self, parallel: bool = True, chunk_size: int = 2, max_workers: int = 10):
        if parallel:
            self.parse_pdf_reports_parallel(chunk_size=chunk_size, max_workers=max_workers)
        else:
            self.parse_pdf_reports_sequential()
    
    def process_parsed_reports(self):
        """Process already parsed PDF reports through the pipeline:
        1. Merge to simpler JSON structure
        2. Export to markdown
        3. Chunk the reports
        4. Create vector databases
        """
        print("Starting reports processing pipeline...")
        
        print("Step 1: Merging reports...")
        self.merge_reports()
        
        print("Step 2: Exporting reports to markdown...")
        self.export_reports_to_markdown()
        
        print("Step 3: Chunking reports...")
        self.chunk_reports()
        
        print("Step 4: Creating vector databases...")
        self.create_vector_dbs()
        
        print("Reports processing pipeline completed successfully!")
        
    def _get_next_available_filename(self, base_path: Path) -> Path:
        """
        Returns the next available filename by adding a numbered suffix if the file exists.
        Example: If answers.json exists, returns answers_01.json, etc.
        """
        if not base_path.exists():
            return base_path
            
        stem = base_path.stem
        suffix = base_path.suffix
        parent = base_path.parent
        
        counter = 1
        while True:
            new_filename = f"{stem}_{counter:02d}{suffix}"
            new_path = parent / new_filename
            
            if not new_path.exists():
                return new_path
            counter += 1
    
    def _format_retrieval_results(self, retrieval_results) -> str:
        """Format vector retrieval results into RAG context string"""
        if not retrieval_results:
            return ""
        
        context_parts = []
        for result in retrieval_results:
            page_number = result['page']
            text = result['text']
            context_parts.append(f'Text retrieved from page {page_number}: \n"""\n{text}\n"""')
            
        return "\n\n---\n\n".join(context_parts)
    
    def _validate_page_references(self, claimed_pages: list, retrieval_results: list, min_pages: int = 2, max_pages: int = 8) -> list:
        """
        Validate that all page numbers mentioned in the LLM's answer are actually from the retrieval results.
        If fewer than min_pages valid references remain, add top pages from retrieval results.
        """
        if claimed_pages is None:
            claimed_pages = []
        
        retrieved_pages = [result['page'] for result in retrieval_results]
        
        validated_pages = [page for page in claimed_pages if page in retrieved_pages]
        
        if len(validated_pages) < len(claimed_pages):
            removed_pages = set(claimed_pages) - set(validated_pages)
            print(f"Warning: Removed {len(removed_pages)} hallucinated page references: {removed_pages}")
        
        if len(validated_pages) < min_pages and retrieval_results:
            existing_pages = set(validated_pages)
            
            for result in retrieval_results:
                page = result['page']
                if page not in existing_pages:
                    validated_pages.append(page)
                    existing_pages.add(page)
                    
                    if len(validated_pages) >= min_pages:
                        break
        
        if len(validated_pages) > max_pages:
            print(f"Trimming references from {len(validated_pages)} to {max_pages} pages")
            validated_pages = validated_pages[:max_pages]
        
        return validated_pages
    
    def _extract_references(self, pages_list: list, company_name: str) -> list:
        # Load companies data
        company_sha1 = company_name  # По умолчанию используем имя компании как идентификатор
        
        # Пробуем найти SHA1 в subset.csv, если он есть
        if hasattr(self, 'companies_df') and self.companies_df is not None:
            matching_rows = self.companies_df[self.companies_df['company_name'] == company_name]
            if not matching_rows.empty:
                company_sha1 = matching_rows.iloc[0]['sha1']
        
        refs = []
        for page in pages_list:
            refs.append({"pdf_sha1": company_sha1, "page_index": page})
        return refs
    
    def get_new_query(self, question: str, context):

        context = "\n".join(["user:" + i[0] + "\n" + "assistent:" + i[1] for i in context])
        answer_dict = self.bit14_processor.get_answer_from_rag_context(
            question=question,
            rag_context=context,
            model=self.answering_model
        )
        return answer_dict
    
    def get_answer_for_company(self, question: str, context, history_chat) -> dict:
        # if self.run_config.llm_reranking:
        #     retriever = HybridRetriever(
        #         vector_db_dir=self.paths.vector_db_dir,
        #         documents_dir=self.paths.documents_dir
        #     )
        # else:
        #     retriever = VectorRetriever(
        #         vector_db_dir=self.paths.vector_db_dir,
        #         documents_dir=self.paths.documents_dir
        #     )
    
        # retrieval_results = retriever.retrieve_by_company_name(
        #     query=question,
        #     llm_reranking_sample_size=self.run_config.llm_reranking_sample_size,
        #     top_n=self.run_config.top_n_retrieval,
        #     return_parent_pages=self.run_config.parent_document_retrieval
        # )
        
        # if not retrieval_results:
        #     raise ValueError("No relevant context found")
        
        # rag_context = self._format_retrieval_results(retrieval_results)
        # print("rag_context:", rag_context)
        context = "\n---\n".join([i["chunk"] for i in context])
        str_history_chat = "\n".join(["user: " + i[0] + "\n" + "assistant: " + i[1] for i in history_chat])
        answer_dict = self.bit14_processor.get_answer_from_rag_context(
            question=question,
            rag_context=context,
            model=self.answering_model,
            history_chat=str_history_chat
        )
        return answer_dict


    def process_questions(self):
        processor = QuestionsProcessor(
            vector_db_dir=self.paths.vector_db_dir,
            documents_dir=self.paths.documents_dir,
            questions_file_path=self.paths.questions_file_path,
            new_challenge_pipeline=True,
            subset_path=self.paths.subset_path,
            parent_document_retrieval=self.run_config.parent_document_retrieval, # 
            llm_reranking=self.run_config.llm_reranking, #
            llm_reranking_sample_size=self.run_config.llm_reranking_sample_size, #
            top_n_retrieval=self.run_config.top_n_retrieval, #
            parallel_requests=self.run_config.parallel_requests, #
            api_provider=self.run_config.api_provider,
            answering_model=self.run_config.answering_model,
            full_context=self.run_config.full_context #       
        )
        
        output_path = self._get_next_available_filename(self.paths.answers_file_path)
        
        _ = processor.process_all_questions(
            output_path=output_path,
            submission_file=self.run_config.submission_file,
            team_email=self.run_config.team_email,
            submission_name=self.run_config.submission_name,
            pipeline_details=self.run_config.pipeline_details
        )
        print(f"Answers saved to {output_path}")


preprocess_configs = {"ser_tab": RunConfig(use_serialized_tables=True),
                      "no_ser_tab": RunConfig(use_serialized_tables=False)}

base_config = RunConfig(
    parallel_requests=10,
    submission_name="Ilia Ris v.0",
    pipeline_details="Custom pdf parsing + vDB + Router + SO CoT; llm = bit14",
    config_suffix="_base"
)

parent_document_retrieval_config = RunConfig(
    parent_document_retrieval=True,
    parallel_requests=20,
    submission_name="Ilia Ris v.1",
    pipeline_details="Custom pdf parsing + vDB + Router + Parent Document Retrieval + SO CoT; llm = bit14",
    answering_model="bit14-2024-08-06",
    config_suffix="_pdr"
)

max_config = RunConfig(
    use_serialized_tables=True,
    parent_document_retrieval=True,
    llm_reranking=True,
    parallel_requests=20,
    submission_name="Ilia Ris v.2",
    pipeline_details="Custom pdf parsing + table serialization + vDB + Router + Parent Document Retrieval + reranking + SO CoT; llm = bit14",
    answering_model="bit14-2024-08-06",
    config_suffix="_max"
)

max_no_ser_tab_config = RunConfig(
    use_serialized_tables=False,
    parent_document_retrieval=True,
    llm_reranking=True,
    parallel_requests=20,
    submission_name="Ilia Ris v.3",
    pipeline_details="Custom pdf parsing + vDB + Router + Parent Document Retrieval + reranking + SO CoT; llm = bit14",
    answering_model="bit14-2024-08-06",
    config_suffix="_max_no_ser_tab"
)

max_nst_o3m_config = RunConfig(
    use_serialized_tables=False,
    parent_document_retrieval=True,
    llm_reranking=True,
    parallel_requests=25,
    submission_name="Ilia Ris v.4",
    pipeline_details="Custom pdf parsing + vDB + Router + Parent Document Retrieval + reranking + SO CoT; llm = o3-mini",
    answering_model="o3-mini-2025-01-31",
    config_suffix="_max_nst_o3m"
)

max_st_o3m_config = RunConfig(
    use_serialized_tables=True,
    parent_document_retrieval=True,
    llm_reranking=True,
    parallel_requests=25,
    submission_name="Ilia Ris v.5",
    pipeline_details="Custom pdf parsing + tables serialization + Router + vDB + Parent Document Retrieval + reranking + SO CoT; llm = o3-mini",
    answering_model="o3-mini-2025-01-31",
    config_suffix="_max_st_o3m"
)

ibm_llama70b_config = RunConfig(
    use_serialized_tables=False,
    parent_document_retrieval=True,
    llm_reranking=False,
    parallel_requests=10,
    submission_name="Ilia Ris v.6",
    pipeline_details="Custom pdf parsing + vDB + Router + Parent Document Retrieval + SO CoT + SO reparser; IBM WatsonX llm = llama-3.3-70b-instruct",
    api_provider="ibm",
    answering_model="meta-llama/llama-3-3-70b-instruct",
    config_suffix="_ibm_llama70b"
)

ibm_llama8b_config = RunConfig(
    use_serialized_tables=False,
    parent_document_retrieval=True,
    llm_reranking=False,
    parallel_requests=10,
    submission_name="Ilia Ris v.7",
    pipeline_details="Custom pdf parsing + vDB + Router + Parent Document Retrieval + SO CoT + SO reparser; IBM WatsonX llm = llama-3.1-8b-instruct",
    api_provider="ibm",
    answering_model="meta-llama/llama-3-1-8b-instruct",
    config_suffix="_ibm_llama8b"
)

gemini_thinking_config = RunConfig(
    use_serialized_tables=False,
    parent_document_retrieval=True,
    llm_reranking=False,
    parallel_requests=1,
    full_context=True,
    submission_name="Ilia Ris v.8",
    pipeline_details="Custom pdf parsing + Full Context + Router + SO CoT + SO reparser; llm = gemini-2.0-flash-thinking-exp-01-21",
    api_provider="gemini",
    answering_model="gemini-2.0-flash-thinking-exp-01-21",
    config_suffix="_gemini_thinking_fc"
)

gemini_flash_config = RunConfig(
    use_serialized_tables=False,
    parent_document_retrieval=True,
    llm_reranking=False,
    parallel_requests=1,
    full_context=True,
    submission_name="Ilia Ris v.9",
    pipeline_details="Custom pdf parsing + Full Context + Router + SO CoT + SO reparser; llm = gemini-2.0-flash",
    api_provider="gemini",
    answering_model="gemini-2.0-flash",
    config_suffix="_gemini_flash_fc"
)

max_nst_o3m_config_big_context = RunConfig(
    use_serialized_tables=False,
    parent_document_retrieval=True,
    llm_reranking=True,
    parallel_requests=5,
    llm_reranking_sample_size=36,
    top_n_retrieval=14,
    submission_name="Ilia Ris v.10",
    pipeline_details="Custom pdf parsing + vDB + Router + Parent Document Retrieval + reranking + SO CoT; llm = o3-mini; top_n = 14; topn for rerank = 36",
    answering_model="o3-mini-2025-01-31",
    config_suffix="_max_nst_o3m_bc"
)

ibm_llama70b_config_big_context = RunConfig(
    use_serialized_tables=False,
    parent_document_retrieval=True,
    llm_reranking=True,
    parallel_requests=5,
    llm_reranking_sample_size=36,
    top_n_retrieval=14,
    submission_name="Ilia Ris v.11",
    pipeline_details="Custom pdf parsing + vDB + Router + Parent Document Retrieval + reranking + SO CoT; llm = llama-3.3-70b-instruct; top_n = 14; topn for rerank = 36",
    api_provider="ibm",
    answering_model="meta-llama/llama-3-3-70b-instruct",
    config_suffix="_ibm_llama70b_bc"
)

gemini_thinking_config_big_context = RunConfig(
    use_serialized_tables=False,
    parent_document_retrieval=True,
    parallel_requests=1,
    top_n_retrieval=30,
    submission_name="Ilia Ris v.12",
    pipeline_details="Custom pdf parsing + vDB + Router + Parent Document Retrieval + SO CoT; llm = gemini-2.0-flash-thinking-exp-01-21; top_n = 30;",
    api_provider="gemini",
    answering_model="gemini-2.0-flash-thinking-exp-01-21",
    config_suffix="_gemini_thinking_bc"
)

configs = {"base": base_config,
           "pdr": parent_document_retrieval_config,
           "max": max_config, 
           "max_no_ser_tab": max_no_ser_tab_config,
           "max_nst_o3m": max_nst_o3m_config, # This configuration returned the best results
           "max_st_o3m": max_st_o3m_config,
           "ibm_llama70b": ibm_llama70b_config, # This one won't work, because ibm api was avaliable only while contest was running
           "ibm_llama8b": ibm_llama8b_config, # This one won't work, because ibm api was avaliable only while contest was running
           "gemini_thinking": gemini_thinking_config}


if __name__ == "__main__":
    root_path = here() / "data" / "test_set"
    pipeline = Pipeline(root_path, run_config=max_nst_o3m_config)
    
    
    # This method parses pdf reports into a jsons. It creates jsons in the debug/data_01_parsed_reports. These jsons used in the next steps. 
    # It also stores raw output of docling in debug/data_01_parsed_reports_debug, these jsons contain a LOT of metadata, and not used anywhere
    pipeline.parse_pdf_reports_sequential() 
    
    
    # This method should be called only if you want run configs with serialized tables
    # It modifies the jsons in the debug/data_01_parsed_reports, adding a new field "serialized_table" to each table
    # pipeline.serialize_tables(max_workers=5) 
    
    
    # This method converts jsons from the debug/data_01_parsed_reports into much simpler jsons, that is a list of pages in markdown
    # New jsons can be found in debug/data_02_merged_reports
    # pipeline.merge_reports() 


    # This method exports the reports into plain markdown format. They used only for review and for full text search config: gemini_thinking_config
    # New files can be found in debug/data_03_reports_markdown
    # pipeline.export_reports_to_markdown() 
    

    # This method splits the reports into chunks, that are used for vectorization
    # New jsons can be found in databases/chunked_reports
    # pipeline.chunk_reports() 
    
    
    # This method creates vector databases from the chunked reports
    # New files can be found in databases/vector_dbs
    # pipeline.create_vector_dbs() 
    
    
    # This method processes the questions and answers
    # Questions processing logic depends on the run_config
    # pipeline.process_questions() 