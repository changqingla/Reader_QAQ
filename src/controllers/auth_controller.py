"""Authentication API endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_db
from schemas.schemas import LoginRequest, RegisterRequest, AuthResponse, UserProfile
from services.auth_service import AuthService
from middlewares.auth import get_current_user
from models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """User login endpoint."""
    service = AuthService(db)
    token, user_data = await service.login(request.email, request.password)
    return {"token": token, "user": user_data}


@router.post("/register", response_model=AuthResponse)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """User registration endpoint."""
    service = AuthService(db)
    token, user_data = await service.register(request.email, request.password, request.name)
    return {"token": token, "user": user_data}


@router.get("/me", response_model=UserProfile)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    """Get current user profile."""
    return current_user.to_dict()

