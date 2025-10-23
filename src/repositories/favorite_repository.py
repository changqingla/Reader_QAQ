"""Favorite repository for database operations."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List, Tuple
from models.favorite import Favorite


class FavoriteRepository:
    """Repository for Favorite model."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, favorite_id: str, user_id: str) -> Optional[Favorite]:
        """Get favorite by ID for specific user."""
        result = await self.db.execute(
            select(Favorite).where(Favorite.id == favorite_id, Favorite.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def list_favorites(
        self,
        user_id: str,
        favorite_type: Optional[str] = None,
        query: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Favorite], int]:
        """List favorites with pagination."""
        stmt = select(Favorite).where(Favorite.user_id == user_id)
        
        if favorite_type:
            stmt = stmt.where(Favorite.type == favorite_type)
        
        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self.db.execute(count_stmt)).scalar()
        
        # Paginate
        stmt = stmt.order_by(Favorite.created_at.desc())
        stmt = stmt.limit(page_size).offset((page - 1) * page_size)
        
        result = await self.db.execute(stmt)
        favorites = result.scalars().all()
        
        return list(favorites), total or 0
    
    async def create(
        self,
        user_id: str,
        favorite_type: str,
        target_id: str,
        tags: List[str]
    ) -> Favorite:
        """Create a new favorite."""
        favorite = Favorite(
            user_id=user_id,
            type=favorite_type,
            target_id=target_id,
            tags=tags
        )
        self.db.add(favorite)
        await self.db.commit()
        await self.db.refresh(favorite)
        return favorite
    
    async def update(self, favorite: Favorite, tags: List[str]) -> Favorite:
        """Update favorite tags."""
        favorite.tags = tags
        await self.db.commit()
        await self.db.refresh(favorite)
        return favorite
    
    async def delete(self, favorite: Favorite):
        """Delete a favorite."""
        await self.db.delete(favorite)
        await self.db.commit()
    
    async def find_existing(
        self,
        user_id: str,
        favorite_type: str,
        target_id: str
    ) -> Optional[Favorite]:
        """Find existing favorite."""
        result = await self.db.execute(
            select(Favorite).where(
                Favorite.user_id == user_id,
                Favorite.type == favorite_type,
                Favorite.target_id == target_id
            )
        )
        return result.scalar_one_or_none()

