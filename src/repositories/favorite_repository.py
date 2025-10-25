"""Favorite repository for database operations."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func, desc
from sqlalchemy.exc import IntegrityError
from typing import Optional, List, Tuple
from models.favorite import Favorite
from models.knowledge_base import KnowledgeBase
from models.document import Document
import logging

logger = logging.getLogger(__name__)


class FavoriteRepository:
    """Repository for Favorite model."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def add_favorite(
        self,
        user_id: str,
        item_type: str,
        item_id: str,
        source: str = Favorite.SOURCE_MANUAL
    ) -> Favorite:
        """Add a favorite (idempotent - returns existing if already exists)."""
        # Check if already exists
        existing = await self.get_favorite(user_id, item_type, item_id)
        if existing:
            logger.info(f"Favorite already exists: user={user_id}, type={item_type}, item={item_id}")
            return existing
        
        try:
            favorite = Favorite(
                user_id=user_id,
                item_type=item_type,
                item_id=item_id,
                source=source
            )
            self.db.add(favorite)
            await self.db.commit()
            await self.db.refresh(favorite)
            logger.info(f"Created favorite: user={user_id}, type={item_type}, item={item_id}, source={source}")
            return favorite
        except IntegrityError:
            await self.db.rollback()
            # Race condition: another request created it
            existing = await self.get_favorite(user_id, item_type, item_id)
            if existing:
                return existing
            raise
    
    async def remove_favorite(
        self,
        user_id: str,
        item_type: str,
        item_id: str
    ) -> bool:
        """Remove a favorite."""
        stmt = delete(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.item_type == item_type,
            Favorite.item_id == item_id
        )
        
        result = await self.db.execute(stmt)
        await self.db.commit()
        deleted = result.rowcount > 0
        if deleted:
            logger.info(f"Removed favorite: user={user_id}, type={item_type}, item={item_id}")
        return deleted
    
    async def get_favorite(
        self,
        user_id: str,
        item_type: str,
        item_id: str
    ) -> Optional[Favorite]:
        """Get a specific favorite."""
        result = await self.db.execute(
            select(Favorite).where(
                Favorite.user_id == user_id,
                Favorite.item_type == item_type,
                Favorite.item_id == item_id
            )
        )
        return result.scalar_one_or_none()
    
    async def list_kb_favorites(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[KnowledgeBase], int]:
        """List favorite knowledge bases with details."""
        # Count total
        count_stmt = select(func.count()).select_from(
            select(Favorite.id)
            .where(
                Favorite.user_id == user_id,
                Favorite.item_type == Favorite.ITEM_TYPE_KB
            )
            .subquery()
        )
        total = (await self.db.execute(count_stmt)).scalar()
        
        # Get favorites with KB details
        stmt = (
            select(KnowledgeBase)
            .join(
                Favorite,
                (Favorite.item_id == KnowledgeBase.id) &
                (Favorite.item_type == Favorite.ITEM_TYPE_KB)
            )
            .where(Favorite.user_id == user_id)
            .order_by(desc(Favorite.created_at))
            .limit(page_size)
            .offset((page - 1) * page_size)
        )
        
        result = await self.db.execute(stmt)
        kbs = result.scalars().all()
        
        return list(kbs), total or 0
    
    async def list_doc_favorites(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Document], int]:
        """List favorite documents with details."""
        # Count total
        count_stmt = select(func.count()).select_from(
            select(Favorite.id)
            .where(
                Favorite.user_id == user_id,
                Favorite.item_type == Favorite.ITEM_TYPE_DOC
            )
            .subquery()
        )
        total = (await self.db.execute(count_stmt)).scalar()
        
        # Get favorites with document details
        stmt = (
            select(Document)
            .join(
                Favorite,
                (Favorite.item_id == Document.id) &
                (Favorite.item_type == Favorite.ITEM_TYPE_DOC)
            )
            .where(Favorite.user_id == user_id)
            .order_by(desc(Favorite.created_at))
            .limit(page_size)
            .offset((page - 1) * page_size)
        )
        
        result = await self.db.execute(stmt)
        docs = result.scalars().all()
        
        return list(docs), total or 0
    
    async def check_favorite(
        self,
        user_id: str,
        item_type: str,
        item_id: str
    ) -> bool:
        """Check if an item is favorited."""
        favorite = await self.get_favorite(user_id, item_type, item_id)
        return favorite is not None
