"""Knowledge Base service business logic."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from repositories.kb_repository import KnowledgeBaseRepository
from repositories.document_repository import DocumentRepository
from repositories.kb_subscription_repository import KBSubscriptionRepository
from utils.external_services import DocumentProcessService
from utils.es_utils import get_user_es_index
from typing import List, Tuple, Optional
import logging
import uuid

logger = logging.getLogger(__name__)


class KnowledgeBaseService:
    """Service for knowledge base operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.kb_repo = KnowledgeBaseRepository(db)
        self.doc_repo = DocumentRepository(db)
        self.subscription_repo = KBSubscriptionRepository(db)
    
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
    
    async def get_kb_info(self, kb_id: str, user_id: str) -> dict:
        """Get knowledge base info (supports both owned and public KBs)."""
        # Try to get as owner first
        kb = await self.kb_repo.get_by_id(kb_id, user_id)
        is_owner = kb is not None
        
        # If not owner, try to get as public KB
        if not kb:
            kb = await self.kb_repo.get_by_id_public(kb_id)
            if not kb:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={"error": {"code": "NOT_FOUND", "message": "Knowledge base not found or not accessible"}}
                )
        
        # Check if user is subscribed (if not owner)
        is_subscribed = False
        if not is_owner:
            subscription = await self.subscription_repo.get_subscription(user_id, kb_id)
            is_subscribed = subscription is not None
        
        # Serialize BEFORE any database operations that might expire the object
        result = kb.to_dict(include_owner=True)
        result["isOwner"] = is_owner
        result["isSubscribed"] = is_subscribed
        
        # Update view count and last_viewed_at for subscribed users (after serialization)
        if not is_owner and is_subscribed:
            await self.kb_repo.increment_view_count(kb_id)
            await self.subscription_repo.update_last_viewed(user_id, kb_id)
        
        return result
    
    async def create_kb(
        self,
        user_id: str,
        name: str,
        description: Optional[str],
        category: str = "其它"
    ) -> dict:
        """Create a new knowledge base."""
        kb = await self.kb_repo.create(user_id, name, description, category)
        logger.info(f"Created knowledge base: {kb.id} with category: {category}")
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
    
    async def upload_avatar(
        self,
        kb_id: str,
        user_id: str,
        file_data: bytes,
        filename: str,
        content_type: str
    ) -> dict:
        """Upload knowledge base avatar."""
        from utils.minio_client import upload_file
        import os
        
        # Verify KB ownership
        kb = await self.kb_repo.get_by_id(kb_id, user_id)
        if not kb:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": {"code": "NOT_FOUND", "message": "Knowledge base not found"}}
            )
        
        # Get file extension
        ext = os.path.splitext(filename)[1].lower()
        if ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": {"code": "VALIDATION_ERROR", "message": "Invalid image format"}}
            )
        
        # Upload to MinIO
        object_name = f"kb_avatars/{user_id}/{kb_id}{ext}"
        file_path = await upload_file(object_name, file_data, content_type)
        
        # Generate presigned URL for access (valid for 7 days)
        from utils.minio_client import get_file_url
        avatar_url = get_file_url(object_name, expires_seconds=7*24*3600)
        
        # Update KB avatar with presigned URL
        await self.kb_repo.update(kb, avatar=avatar_url)
        
        logger.info(f"Updated KB {kb_id} avatar: {avatar_url}")
        return {"avatarUrl": avatar_url}
    
    # ============ Public Sharing & Subscription Features ============
    
    async def toggle_public(self, kb_id: str, user_id: str) -> dict:
        """Toggle public status of a knowledge base."""
        kb = await self.kb_repo.get_by_id(kb_id, user_id)
        if not kb:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": {"code": "NOT_FOUND", "message": "Knowledge base not found"}}
            )
        
        kb = await self.kb_repo.toggle_public(kb)
        logger.info(f"KB {kb_id} public status: {kb.is_public}")
        return {
            "isPublic": kb.is_public,
            "subscribersCount": kb.subscribers_count
        }
    
    async def subscribe_kb(self, kb_id: str, user_id: str) -> dict:
        """Subscribe to a public knowledge base."""
        # Check if KB exists and is public
        kb = await self.kb_repo.get_by_id_public(kb_id)
        if not kb:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": {"code": "NOT_FOUND", "message": "Public knowledge base not found"}}
            )
        
        # Cannot subscribe to own KB
        if str(kb.owner_id) == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": {"code": "VALIDATION_ERROR", "message": "Cannot subscribe to your own knowledge base"}}
            )
        
        # Subscribe
        await self.subscription_repo.subscribe(user_id, kb_id)
        logger.info(f"User {user_id} subscribed to KB {kb_id}")
        
        # Auto-favorite when subscribing
        from services.favorite_service import FavoriteService
        from models.favorite import Favorite
        favorite_service = FavoriteService(self.db)
        try:
            await favorite_service.favorite_kb(
                kb_id,
                user_id,
                source=Favorite.SOURCE_SUBSCRIPTION
            )
            logger.info(f"Auto-favorited KB {kb_id} for user {user_id}")
        except Exception as e:
            logger.warning(f"Failed to auto-favorite KB {kb_id}: {e}")
        
        # Return updated count
        kb = await self.kb_repo.get_by_id_public(kb_id)
        return {"subscribersCount": kb.subscribers_count}
    
    async def unsubscribe_kb(self, kb_id: str, user_id: str) -> dict:
        """Unsubscribe from a knowledge base."""
        success = await self.subscription_repo.unsubscribe(user_id, kb_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": {"code": "NOT_FOUND", "message": "Subscription not found"}}
            )
        
        logger.info(f"User {user_id} unsubscribed from KB {kb_id}")
        
        # Auto-remove favorite if it was from subscription
        from services.favorite_service import FavoriteService
        from models.favorite import Favorite
        favorite_service = FavoriteService(self.db)
        try:
            # Convert string IDs to UUID
            user_uuid = uuid.UUID(user_id) if isinstance(user_id, str) else user_id
            kb_uuid = uuid.UUID(kb_id) if isinstance(kb_id, str) else kb_id
            
            # Check if favorite exists and is from subscription
            favorite = await self.db.execute(
                select(Favorite).where(
                    Favorite.user_id == user_uuid,
                    Favorite.item_type == Favorite.ITEM_TYPE_KB,
                    Favorite.item_id == kb_uuid,
                    Favorite.source == Favorite.SOURCE_SUBSCRIPTION
                )
            )
            fav = favorite.scalar_one_or_none()
            if fav:
                await favorite_service.unfavorite_kb(kb_id, user_id)
                logger.info(f"Auto-removed favorite KB {kb_id} for user {user_id}")
        except Exception as e:
            logger.warning(f"Failed to auto-remove favorite KB {kb_id}: {e}")
        
        # Return updated count
        kb = await self.kb_repo.get_by_id_public(kb_id)
        return {"subscribersCount": kb.subscribers_count if kb else 0}
    
    async def check_subscription(self, kb_id: str, user_id: str) -> dict:
        """Check if user is subscribed to a knowledge base."""
        subscription = await self.subscription_repo.get_subscription(user_id, kb_id)
        return {
            "isSubscribed": subscription is not None,
            "subscribedAt": subscription.subscribed_at.isoformat() if subscription else None
        }
    
    async def list_user_subscriptions(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[dict], int]:
        """List all knowledge bases subscribed by a user."""
        kbs, total = await self.subscription_repo.list_user_subscriptions(user_id, page, page_size)
        return [kb.to_dict(include_owner=True) for kb in kbs], total
    
    async def list_public_kbs(
        self,
        category: Optional[str] = None,
        query: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[dict], int]:
        """List public knowledge bases."""
        kbs, total = await self.kb_repo.list_public_kbs(category, query, page, page_size)
        return [kb.to_dict(include_owner=True) for kb in kbs], total
    
    async def list_featured_kbs(
        self,
        page: int = 1,
        page_size: int = 30
    ) -> Tuple[List[dict], int]:
        """List featured knowledge bases (2025年度精选)."""
        kbs, total = await self.kb_repo.list_featured_kbs(page, page_size)
        return [kb.to_dict(include_owner=True) for kb in kbs], total
    
    async def get_categories_stats(self) -> List[dict]:
        """Get statistics for each category."""
        return await self.kb_repo.get_categories_stats()

