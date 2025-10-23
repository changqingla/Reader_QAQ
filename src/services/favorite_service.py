"""Favorite service business logic."""
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from repositories.favorite_repository import FavoriteRepository
from typing import List, Tuple, Optional


class FavoriteService:
    """Service for favorite operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.favorite_repo = FavoriteRepository(db)
    
    async def list_favorites(
        self,
        user_id: str,
        favorite_type: Optional[str] = None,
        query: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[dict], int]:
        """List favorites for user."""
        favorites, total = await self.favorite_repo.list_favorites(
            user_id, favorite_type, query, page, page_size
        )
        
        # TODO: Enrich with actual paper/knowledge data from respective tables
        items = []
        for fav in favorites:
            item = {
                **fav.to_dict(),
                "title": f"Mock {fav.type} {fav.target_id}",
                "description": "Description from source table (TODO)",
            }
            items.append(item)
        
        return items, total
    
    async def create_favorite(
        self,
        user_id: str,
        favorite_type: str,
        target_id: str,
        tags: List[str]
    ) -> dict:
        """Create a new favorite."""
        # Check if already exists
        existing = await self.favorite_repo.find_existing(user_id, favorite_type, target_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"error": {"code": "CONFLICT", "message": "Already favorited"}}
            )
        
        favorite = await self.favorite_repo.create(user_id, favorite_type, target_id, tags)
        return {"id": str(favorite.id)}
    
    async def toggle_favorite(
        self,
        user_id: str,
        favorite_type: str,
        target_id: str
    ) -> dict:
        """Toggle favorite (add if not exists, remove if exists)."""
        existing = await self.favorite_repo.find_existing(user_id, favorite_type, target_id)
        
        if existing:
            await self.favorite_repo.delete(existing)
            return {"id": None, "active": False}
        else:
            favorite = await self.favorite_repo.create(user_id, favorite_type, target_id, [])
            return {"id": str(favorite.id), "active": True}
    
    async def update_favorite(
        self,
        favorite_id: str,
        user_id: str,
        tags: List[str]
    ) -> dict:
        """Update favorite tags."""
        favorite = await self.favorite_repo.get_by_id(favorite_id, user_id)
        if not favorite:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": {"code": "NOT_FOUND", "message": "Favorite not found"}}
            )
        
        await self.favorite_repo.update(favorite, tags)
        return {"success": True}
    
    async def delete_favorite(self, favorite_id: str, user_id: str):
        """Delete a favorite."""
        favorite = await self.favorite_repo.get_by_id(favorite_id, user_id)
        if not favorite:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": {"code": "NOT_FOUND", "message": "Favorite not found"}}
            )
        await self.favorite_repo.delete(favorite)

