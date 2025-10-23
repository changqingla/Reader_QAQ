"""Favorites API endpoints."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from config.database import get_db
from schemas.schemas import CreateFavoriteRequest, FavoritesResponse
from services.favorite_service import FavoriteService
from middlewares.auth import get_current_user
from models.user import User

router = APIRouter(prefix="/favorites", tags=["Favorites"])


@router.get("", response_model=FavoritesResponse)
async def list_favorites(
    type: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List favorites with optional filtering."""
    service = FavoriteService(db)
    items, total = await service.list_favorites(
        str(current_user.id), type, q, page, pageSize
    )
    return {"total": total, "page": page, "pageSize": pageSize, "items": items}


@router.post("")
async def create_favorite(
    request: CreateFavoriteRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add a new favorite."""
    service = FavoriteService(db)
    return await service.create_favorite(
        str(current_user.id),
        request.type,
        request.targetId,
        request.tags
    )


@router.post(":toggle")
async def toggle_favorite(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Toggle favorite on/off."""
    service = FavoriteService(db)
    return {"data": await service.toggle_favorite(
        str(current_user.id),
        request["type"],
        request["targetId"]
    )}


@router.patch("/{favoriteId}")
async def update_favorite(
    favoriteId: str,
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update favorite tags."""
    service = FavoriteService(db)
    tags = request.get("tags", [])
    return await service.update_favorite(favoriteId, str(current_user.id), tags)


@router.delete("/{favoriteId}")
async def delete_favorite(
    favoriteId: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a favorite."""
    service = FavoriteService(db)
    await service.delete_favorite(favoriteId, str(current_user.id))
    return {"success": True}

