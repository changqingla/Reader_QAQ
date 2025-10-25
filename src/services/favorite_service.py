"""Favorite service business logic."""
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from repositories.favorite_repository import FavoriteRepository
from repositories.kb_repository import KnowledgeBaseRepository
from repositories.document_repository import DocumentRepository
from models.favorite import Favorite
from models.knowledge_base import KnowledgeBase
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)


class FavoriteService:
    """Service for favorite operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.favorite_repo = FavoriteRepository(db)
        self.kb_repo = KnowledgeBaseRepository(db)
        self.doc_repo = DocumentRepository(db)
    
    async def favorite_kb(
        self,
        kb_id: str,
        user_id: str,
        source: str = Favorite.SOURCE_MANUAL
    ) -> dict:
        """Favorite a knowledge base."""
        # Verify KB exists and user has access (owned or public)
        kb = await self.kb_repo.get_by_id(kb_id, user_id)
        if not kb:
            kb = await self.kb_repo.get_by_id_public(kb_id)
            if not kb:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={"error": {"code": "NOT_FOUND", "message": "Knowledge base not found or not accessible"}}
                )
        
        await self.favorite_repo.add_favorite(
            user_id,
            Favorite.ITEM_TYPE_KB,
            kb_id,
            source
        )
        logger.info(f"User {user_id} favorited KB {kb_id} (source: {source})")
        return {"success": True}
    
    async def unfavorite_kb(self, kb_id: str, user_id: str) -> dict:
        """Unfavorite a knowledge base."""
        success = await self.favorite_repo.remove_favorite(
            user_id,
            Favorite.ITEM_TYPE_KB,
            kb_id
        )
        if success:
            logger.info(f"User {user_id} unfavorited KB {kb_id}")
        return {"success": success}
    
    async def favorite_document(
        self,
        doc_id: str,
        kb_id: str,
        user_id: str
    ) -> dict:
        """Favorite a document."""
        # Verify user has access to the KB (owned or public)
        kb = await self.kb_repo.get_by_id(kb_id, user_id)
        if not kb:
            kb = await self.kb_repo.get_by_id_public(kb_id)
            if not kb:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={"error": {"code": "NOT_FOUND", "message": "Knowledge base not found or not accessible"}}
                )
        
        # Verify document exists in this KB
        doc = await self.doc_repo.get_by_id(doc_id, kb_id)
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": {"code": "NOT_FOUND", "message": "Document not found"}}
            )
        
        await self.favorite_repo.add_favorite(
            user_id,
            Favorite.ITEM_TYPE_DOC,
            doc_id
        )
        logger.info(f"User {user_id} favorited document {doc_id}")
        return {"success": True}
    
    async def unfavorite_document(self, doc_id: str, user_id: str) -> dict:
        """Unfavorite a document."""
        success = await self.favorite_repo.remove_favorite(
            user_id,
            Favorite.ITEM_TYPE_DOC,
            doc_id
        )
        if success:
            logger.info(f"User {user_id} unfavorited document {doc_id}")
        return {"success": success}
    
    async def list_favorite_kbs(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[dict], int]:
        """List favorite knowledge bases."""
        kbs, total = await self.favorite_repo.list_kb_favorites(user_id, page, page_size)
        return [kb.to_dict(include_owner=True) for kb in kbs], total
    
    async def list_favorite_docs(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[dict], int]:
        """List favorite documents with KB info."""
        docs, total = await self.favorite_repo.list_doc_favorites(user_id, page, page_size)
        
        # Enrich with KB info
        result = []
        for doc in docs:
            doc_dict = doc.to_dict()
            # Get KB info
            kb = await self.db.get(KnowledgeBase, doc.kb_id)
            if kb:
                doc_dict["kbName"] = kb.name
                doc_dict["kbAvatar"] = kb.avatar or "/kb.png"
            result.append(doc_dict)
        
        return result, total
    
    async def check_favorites(
        self,
        user_id: str,
        items: List[dict]
    ) -> dict:
        """Batch check if items are favorited."""
        result = {}
        for item in items:
            item_type = item.get("type")
            item_id = item.get("id")
            if item_type and item_id:
                is_favorited = await self.favorite_repo.check_favorite(
                    user_id,
                    item_type,
                    item_id
                )
                result[f"{item_type}:{item_id}"] = is_favorited
        return result
