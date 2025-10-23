"""External services client for document processing."""
import httpx
from typing import Dict, List, Optional, Any
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

# HTTP client with timeout
http_client = httpx.AsyncClient(timeout=30.0)


class MineruService:
    """Client for Mineru document conversion service."""
    
    @staticmethod
    async def convert_document(file_data: bytes, filename: str) -> Dict[str, Any]:
        """
        Convert PDF/Office document to Markdown using Mineru.
        
        Args:
            file_data: File binary data
            filename: Original filename
        
        Returns:
            Response with task_id
        """
        try:
            files = {'file': (filename, file_data)}
            response = await http_client.post(
                f"{settings.MINERU_BASE_URL}/process-async/",
                files=files
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get("code") != 0:
                raise Exception(f"Mineru conversion failed: {result.get('message')}")
            
            return result["data"]
        
        except Exception as e:
            logger.error(f"Mineru conversion error: {e}")
            raise
    
    @staticmethod
    async def get_task_status(task_id: str) -> Dict[str, Any]:
        """Get Mineru task status."""
        try:
            response = await http_client.get(
                f"{settings.MINERU_BASE_URL}/task/{task_id}"
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get("code") != 0:
                raise Exception(f"Failed to get task status: {result.get('message')}")
            
            return result["data"]
        
        except Exception as e:
            logger.error(f"Get Mineru task status error: {e}")
            raise
    
    @staticmethod
    async def get_content(task_id: str) -> str:
        """Get converted content from Mineru."""
        try:
            response = await http_client.get(
                f"{settings.MINERU_BASE_URL}/task/{task_id}/content"
            )
            response.raise_for_status()
            result = response.json()
            
            if result.get("code") != 0:
                raise Exception(f"Failed to get content: {result.get('message')}")
            
            return result["data"]["content"]
        
        except Exception as e:
            logger.error(f"Get Mineru content error: {e}")
            raise


class DocumentProcessService:
    """Client for document processing service (chunking, embedding, storage)."""
    
    @staticmethod
    async def parse_document(
        file_path: str,
        document_id: str,
        index_name: str,
        filename: str
    ) -> Dict[str, Any]:
        """
        Parse document: chunk + embed + store to ES.
        
        Args:
            file_path: Path to markdown file
            document_id: Document ID
            index_name: ES index name
            filename: Original filename
        
        Returns:
            Response with task_id
        """
        try:
            # Read file content
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            files = {'file': (filename, file_data)}
            data = {
                'model_factory': settings.EMBEDDING_MODEL_FACTORY,
                'model_name': settings.EMBEDDING_MODEL_NAME,
                'base_url': settings.EMBEDDING_BASE_URL,
                'index_name': index_name,
                'document_id': document_id,
                'parser_type': settings.DEFAULT_PARSER_TYPE,
                'chunk_token_num': str(settings.DEFAULT_CHUNK_TOKEN_NUM),
                'es_host': settings.ES_HOST,
            }
            
            if settings.EMBEDDING_API_KEY:
                data['api_key'] = settings.EMBEDDING_API_KEY
            
            response = await http_client.post(
                f"{settings.DOC_PROCESS_BASE_URL}/api/parse-document",
                files=files,
                data=data
            )
            response.raise_for_status()
            result = response.json()
            
            if not result.get("success"):
                raise Exception(f"Document parsing failed: {result.get('message')}")
            
            return result["data"]
        
        except Exception as e:
            logger.error(f"Document parsing error: {e}")
            raise
    
    @staticmethod
    async def get_task_status(task_id: str) -> Dict[str, Any]:
        """Get document processing task status."""
        try:
            response = await http_client.get(
                f"{settings.DOC_PROCESS_BASE_URL}/api/task-status/{task_id}"
            )
            response.raise_for_status()
            result = response.json()
            
            if not result.get("success"):
                raise Exception(f"Failed to get task status: {result.get('message')}")
            
            return result
        
        except Exception as e:
            logger.error(f"Get task status error: {e}")
            raise
    
    @staticmethod
    async def search_chunks(
        question: str,
        index_names: List[str],
        doc_ids: List[str],
        top_n: int = None,
        use_rerank: bool = False
    ) -> Dict[str, Any]:
        """
        Search chunks using vector similarity.
        
        Args:
            question: User question
            index_names: List of ES index names
            doc_ids: List of document IDs to search in
            top_n: Number of results to return
            use_rerank: Whether to use reranking
        
        Returns:
            Search results with chunks
        """
        try:
            top_n = top_n or settings.DEFAULT_TOP_N
            
            payload = {
                "question": question,
                "index_names": index_names,
                "doc_ids": doc_ids,
                "es_host": settings.ES_HOST,
                "top_n": top_n,
                "similarity_threshold": settings.SIMILARITY_THRESHOLD,
                "vector_similarity_weight": settings.VECTOR_SIMILARITY_WEIGHT,
                "model_factory": settings.EMBEDDING_MODEL_FACTORY,
                "model_name": settings.EMBEDDING_MODEL_NAME,
                "model_base_url": settings.EMBEDDING_BASE_URL,
            }
            
            if settings.EMBEDDING_API_KEY:
                payload["api_key"] = settings.EMBEDDING_API_KEY
            
            if use_rerank:
                payload.update({
                    "rerank_factory": settings.RERANK_FACTORY,
                    "rerank_model_name": settings.RERANK_MODEL_NAME,
                    "rerank_base_url": settings.RERANK_BASE_URL,
                })
                if settings.RERANK_API_KEY:
                    payload["rerank_api_key"] = settings.RERANK_API_KEY
            
            response = await http_client.post(
                f"{settings.DOC_PROCESS_BASE_URL}/api/recall",
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            
            if not result.get("success"):
                raise Exception(f"Search failed: {result.get('message')}")
            
            return result["data"]
        
        except Exception as e:
            logger.error(f"Search chunks error: {e}")
            raise
    
    @staticmethod
    async def delete_document_from_es(document_id: str, index_name: str) -> Dict[str, Any]:
        """
        Delete document chunks from Elasticsearch.
        
        Args:
            document_id: Document ID
            index_name: ES index name
        
        Returns:
            Deletion result
        """
        try:
            payload = {
                "document_id": document_id,
                "index_name": index_name,
                "es_host": settings.ES_HOST
            }
            
            response = await http_client.post(
                f"{settings.DOC_PROCESS_BASE_URL}/api/delete-document",
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            
            if not result.get("success"):
                raise Exception(f"ES deletion failed: {result.get('message')}")
            
            return result["data"]
        
        except Exception as e:
            logger.error(f"Delete from ES error: {e}")
            raise
    
    @staticmethod
    async def list_chunks(
        document_id: str,
        index_name: str,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        List document chunks.
        
        Args:
            document_id: Document ID
            index_name: ES index name
            page: Page number
            page_size: Items per page
        
        Returns:
            Chunks list
        """
        try:
            payload = {
                "document_id": document_id,
                "es_host": settings.ES_HOST,
                "index_name": index_name,
                "page": page,
                "page_size": page_size
            }
            
            response = await http_client.post(
                f"{settings.DOC_PROCESS_BASE_URL}/api/chunk-list",
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            
            if not result.get("success"):
                raise Exception(f"List chunks failed: {result.get('message')}")
            
            return result["data"]
        
        except Exception as e:
            logger.error(f"List chunks error: {e}")
            raise


async def close_http_client():
    """Close HTTP client on shutdown."""
    await http_client.aclose()

