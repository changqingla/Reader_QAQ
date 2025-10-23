"""Document service business logic."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status, UploadFile
from repositories.kb_repository import KnowledgeBaseRepository
from repositories.document_repository import DocumentRepository
from utils.minio_client import upload_file, delete_file
from utils.external_services import MineruService, DocumentProcessService
from utils.es_utils import get_user_es_index
from models.document import Document
from config.settings import settings
from typing import List, Tuple, Optional
import os
import logging
import asyncio

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for document operations."""
    
    # Supported file extensions
    PDF_EXTENSIONS = {'.pdf'}
    MARKDOWN_EXTENSIONS = {'.md', '.markdown', '.txt'}
    OFFICE_EXTENSIONS = {'.docx', '.xlsx', '.pptx'}
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.kb_repo = KnowledgeBaseRepository(db)
        self.doc_repo = DocumentRepository(db)
    
    def _get_file_extension(self, filename: str) -> str:
        """Get file extension in lowercase."""
        return os.path.splitext(filename)[1].lower()
    
    def _needs_mineru_conversion(self, filename: str) -> bool:
        """Check if file needs Mineru conversion."""
        ext = self._get_file_extension(filename)
        return ext in self.PDF_EXTENSIONS
    
    async def upload_document(
        self,
        kb_id: str,
        user_id: str,
        file: UploadFile,
        background_tasks
    ) -> dict:
        """
        Upload document and trigger processing.
        
        Complete flow:
        1. Upload to MinIO
        2. Create document record
        3. If PDF: convert with Mineru
        4. Process document (chunk + embed + store to ES)
        5. Background task to poll status
        """
        # Verify KB ownership
        kb = await self.kb_repo.get_by_id(kb_id, user_id)
        if not kb:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": {"code": "NOT_FOUND", "message": "Knowledge base not found"}}
            )
        
        # Read file
        file_data = await file.read()
        file_size = len(file_data)
        
        # Upload to MinIO
        object_name = f"kb/{user_id}/{kb_id}/{file.filename}"
        try:
            file_path = await upload_file(object_name, file_data, file.content_type)
        except Exception as e:
            logger.error(f"MinIO upload failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"error": {"code": "INTERNAL_ERROR", "message": f"File upload failed: {e}"}}
            )
        
        # Create document record
        document = await self.doc_repo.create(
            kb_id=kb_id,
            name=file.filename,
            size=file_size,
            source="upload",
            file_path=file_path
        )
        
        # Get user's ES index name (user-level, not KB-level)
        user_es_index = get_user_es_index(user_id)
        logger.info(f"Using ES index: {user_es_index} for user {user_id}")
        
        # Start background processing using FastAPI BackgroundTasks
        logger.info(f"Starting background processing for document {document.id} ({file.filename})")
        background_tasks.add_task(
            self._process_document_pipeline,
            str(document.id),
            user_es_index,
            file_data,
            file.filename
        )
        
        return {
            "id": str(document.id),
            "name": document.name,
            "status": document.status
        }
    
    async def _process_document_pipeline(
        self,
        doc_id: str,
        es_index_name: str,
        file_data: bytes,
        filename: str
    ):
        """
        Background task to process document through complete pipeline.
        
        Pipeline:
        1. Convert with Mineru (if PDF)
        2. Parse document (chunk + embed + store)
        3. Update status
        """
        # Import here to avoid circular dependency
        from config.database import AsyncSessionLocal
        from repositories.document_repository import DocumentRepository
        from repositories.kb_repository import KnowledgeBaseRepository
        
        # Create new DB session for background task
        async with AsyncSessionLocal() as db:
            doc_repo = DocumentRepository(db)
            kb_repo = KnowledgeBaseRepository(db)
            
            # Get document
            result = await db.execute(
                select(Document).where(Document.id == doc_id)
            )
            doc = result.scalar_one_or_none()
            if not doc:
                logger.error(f"Document {doc_id} not found in background task")
                return
            
            logger.info(f"[Doc {doc_id}] Background task started for {filename}")
        
            try:
                markdown_content = None
                
                # Step 1: Convert with Mineru if needed
                if self._needs_mineru_conversion(filename):
                    logger.info(f"[Doc {doc_id}] PDF detected, calling Mineru for conversion")
                    await doc_repo.update_status(doc, Document.STATUS_PROCESSING)
                
                    try:
                        logger.info(f"[Doc {doc_id}] Calling Mineru API...")
                        mineru_result = await MineruService.convert_document(file_data, filename)
                        task_id = mineru_result["task_id"]
                        logger.info(f"[Doc {doc_id}] Mineru task created: {task_id}")
                        
                        await doc_repo.update_status(
                            doc,
                            Document.STATUS_PROCESSING,
                            mineru_task_id=task_id
                        )
                        
                        # Poll Mineru status
                        logger.info(f"[Doc {doc_id}] Polling Mineru task status...")
                        markdown_content = await self._poll_mineru_task(task_id)
                        logger.info(f"[Doc {doc_id}] Mineru conversion completed, got {len(markdown_content)} chars")
                        
                    except Exception as e:
                        logger.error(f"[Doc {doc_id}] Mineru conversion failed: {e}")
                        await doc_repo.update_status(
                            doc,
                            Document.STATUS_FAILED,
                            error_message=f"Conversion failed: {e}"
                        )
                        return
                else:
                    # For markdown/text files, use directly
                    logger.info(f"[Doc {doc_id}] Markdown/text file, using directly")
                    markdown_content = file_data.decode('utf-8')
                
                # Step 2: Parse document (chunk + embed + store to ES)
                await doc_repo.update_status(doc, Document.STATUS_CHUNKING)
            
                # Save markdown to temp file for processing
                temp_file_path = f"/tmp/{doc_id}.md"
                with open(temp_file_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                
                # Use .md filename for parse_document
                md_filename = os.path.splitext(filename)[0] + '.md'
                logger.info(f"[Doc {doc_id}] Saved MD file to {temp_file_path}, will use filename: {md_filename}")
                
                try:
                    logger.info(f"[Doc {doc_id}] Calling document processing service...")
                    parse_result = await DocumentProcessService.parse_document(
                        temp_file_path,
                        str(doc_id),
                        es_index_name,
                        md_filename
                    )
                    task_id = parse_result["task_id"]
                    logger.info(f"[Doc {doc_id}] Parse task created: {task_id}")
                    
                    await doc_repo.update_status(
                        doc,
                        Document.STATUS_EMBEDDING,
                        parse_task_id=task_id
                    )
                    
                    # Poll parsing status
                    logger.info(f"[Doc {doc_id}] Polling parse task status...")
                    await self._poll_parse_task(doc, task_id, doc_repo)
                    logger.info(f"[Doc {doc_id}] Document processing completed successfully!")
                    
                finally:
                    # Clean up temp file
                    if os.path.exists(temp_file_path):
                        os.remove(temp_file_path)
                
                # Increment KB contents count
                await kb_repo.increment_contents_count(doc.kb_id)
                
            except Exception as e:
                logger.error(f"Document processing pipeline failed for {doc_id}: {e}")
                await doc_repo.update_status(
                    doc,
                    Document.STATUS_FAILED,
                    error_message=str(e)
                )
    
    async def _poll_mineru_task(self, task_id: str, max_attempts: int = 60) -> str:
        """Poll Mineru task until completion."""
        for _ in range(max_attempts):
            await asyncio.sleep(5)  # Wait 5 seconds
            
            try:
                task_status = await MineruService.get_task_status(task_id)
                status = task_status["status"]
                
                if status == "completed":
                    return await MineruService.get_content(task_id)
                elif status == "failed":
                    raise Exception(f"Mineru task failed: {task_status.get('message')}")
            
            except Exception as e:
                logger.warning(f"Error polling Mineru task {task_id}: {e}")
        
        raise Exception("Mineru task timeout")
    
    async def _poll_parse_task(self, doc: Document, task_id: str, doc_repo, max_attempts: int = 60):
        """Poll document parsing task until completion."""
        for _ in range(max_attempts):
            await asyncio.sleep(5)  # Wait 5 seconds
            
            try:
                task_status = await DocumentProcessService.get_task_status(task_id)
                status = task_status["status"]
                
                if status == "completed":
                    # Get chunk count from task data
                    chunk_count = task_status.get("data", {}).get("total_chunks", 0)
                    await doc_repo.update_status(
                        doc,
                        Document.STATUS_READY,
                        chunk_count=chunk_count
                    )
                    logger.info(f"Document {doc.id} processing completed with {chunk_count} chunks")
                    return
                
                elif status == "failed":
                    await doc_repo.update_status(
                        doc,
                        Document.STATUS_FAILED,
                        error_message=task_status.get("message", "Processing failed")
                    )
                    return
            
            except Exception as e:
                logger.warning(f"Error polling parse task {task_id}: {e}")
        
        await doc_repo.update_status(doc, Document.STATUS_FAILED, error_message="Processing timeout")
    
    async def list_documents(
        self,
        kb_id: str,
        user_id: str,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[dict], int]:
        """List documents in knowledge base."""
        # Verify KB ownership
        kb = await self.kb_repo.get_by_id(kb_id, user_id)
        if not kb:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": {"code": "NOT_FOUND", "message": "Knowledge base not found"}}
            )
        
        documents, total = await self.doc_repo.list_documents(kb_id, page, page_size)
        return [doc.to_dict() for doc in documents], total
    
    async def get_document_status(self, doc_id: str, kb_id: str, user_id: str) -> dict:
        """Get document processing status."""
        # Verify KB ownership
        kb = await self.kb_repo.get_by_id(kb_id, user_id)
        if not kb:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": {"code": "NOT_FOUND", "message": "Knowledge base not found"}}
            )
        
        doc = await self.doc_repo.get_by_id(doc_id, kb_id)
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": {"code": "NOT_FOUND", "message": "Document not found"}}
            )
        
        return {
            "status": doc.status,
            "errorMessage": doc.error_message,
            "chunkCount": doc.chunk_count
        }
    
    async def delete_document(self, doc_id: str, kb_id: str, user_id: str):
        """Delete document from KB, MinIO, and ES."""
        # Verify KB ownership
        kb = await self.kb_repo.get_by_id(kb_id, user_id)
        if not kb:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": {"code": "NOT_FOUND", "message": "Knowledge base not found"}}
            )
        
        doc = await self.doc_repo.get_by_id(doc_id, kb_id)
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": {"code": "NOT_FOUND", "message": "Document not found"}}
            )
        
        # Get user's ES index name
        user_es_index = get_user_es_index(user_id)
        
        # Delete from ES (using user-level index)
        if doc.status == Document.STATUS_READY:
            try:
                await DocumentProcessService.delete_document_from_es(str(doc.id), user_es_index)
            except Exception as e:
                logger.warning(f"Failed to delete from ES: {e}")
        
        # Delete from MinIO
        if doc.file_path:
            try:
                object_name = doc.file_path.replace(f"{settings.MINIO_BUCKET}/", "")
                await delete_file(object_name)
            except Exception as e:
                logger.warning(f"Failed to delete from MinIO: {e}")
        
        # Delete from DB
        await self.doc_repo.delete(doc)
        
        # Decrement KB contents count
        await self.kb_repo.increment_contents_count(kb_id, -1)
        
        logger.info(f"Deleted document: {doc_id}")

