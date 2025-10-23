"""Knowledge Base service business logic."""
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from repositories.kb_repository import KnowledgeBaseRepository
from repositories.document_repository import DocumentRepository
from utils.external_services import DocumentProcessService
from utils.es_utils import get_user_es_index
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class KnowledgeBaseService:
    """Service for knowledge base operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.kb_repo = KnowledgeBaseRepository(db)
        self.doc_repo = DocumentRepository(db)
    
    async def list_kbs(
        self,
        user_id: str,
        query: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[dict], int]:
        """List knowledge bases for user."""
        kbs, total = await self.kb_repo.list_kbs(user_id, query, page, page_size)
        return [kb.to_dict() for kb in kbs], total
    
    async def get_kb(self, kb_id: str, user_id: str) -> dict:
        """Get knowledge base details."""
        kb = await self.kb_repo.get_by_id(kb_id, user_id)
        if not kb:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": {"code": "NOT_FOUND", "message": "Knowledge base not found"}}
            )
        return kb.to_dict()
    
    async def create_kb(
        self,
        user_id: str,
        name: str,
        description: Optional[str],
        tags: List[str]
    ) -> dict:
        """Create a new knowledge base."""
        kb = await self.kb_repo.create(user_id, name, description, tags)
        logger.info(f"Created knowledge base: {kb.id}")
        return {"id": str(kb.id)}
    
    async def update_kb(
        self,
        kb_id: str,
        user_id: str,
        **kwargs
    ) -> dict:
        """Update knowledge base."""
        kb = await self.kb_repo.get_by_id(kb_id, user_id)
        if not kb:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": {"code": "NOT_FOUND", "message": "Knowledge base not found"}}
            )
        
        await self.kb_repo.update(kb, **kwargs)
        return {"success": True}
    
    async def delete_kb(self, kb_id: str, user_id: str):
        """Delete knowledge base and all its documents."""
        kb = await self.kb_repo.get_by_id(kb_id, user_id)
        if not kb:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": {"code": "NOT_FOUND", "message": "Knowledge base not found"}}
            )
        
        # Get user's ES index name
        user_index = get_user_es_index(user_id)
        
        # Get all documents for cleanup
        documents, _ = await self.doc_repo.list_documents(kb_id)
        
        # Delete from ES (using user-level index)
        for doc in documents:
            try:
                await DocumentProcessService.delete_document_from_es(
                    str(doc.id),
                    user_index
                )
            except Exception as e:
                logger.warning(f"Failed to delete doc {doc.id} from ES: {e}")
        
        # Delete KB (will cascade delete documents in DB)
        await self.kb_repo.delete(kb)
        logger.info(f"Deleted knowledge base: {kb_id}")
    
    async def get_quota(self, user_id: str) -> dict:
        """Get storage quota for user."""
        used_bytes = await self.kb_repo.calculate_total_size(user_id)
        return {
            "usedBytes": used_bytes,
            "limitBytes": 500000000000  # 500GB, should be configurable per user
        }

