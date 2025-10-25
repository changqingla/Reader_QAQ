"""Authentication service business logic."""
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from repositories.user_repository import UserRepository
from repositories.note_repository import NoteFolderRepository
from repositories.kb_repository import KnowledgeBaseRepository
from utils.security import verify_password, get_password_hash, create_access_token
from typing import Tuple


class AuthService:
    """Service for authentication operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
    
    async def login(self, email: str, password: str) -> Tuple[str, dict]:
        """Login user and return token."""
        user = await self.user_repo.get_by_email(email)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": {"code": "NOT_FOUND", "message": "账号未注册"}}
            )
        
        if not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": {"code": "UNAUTHORIZED", "message": "密码不正确"}}
            )
        
        # Create access token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        return access_token, user.to_dict()
    
    async def register(self, email: str, password: str, name: str) -> Tuple[str, dict]:
        """Register new user."""
        # Check if user already exists
        existing = await self.user_repo.get_by_email(email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"error": {"code": "CONFLICT", "message": "Email already registered"}}
            )
        
        # Hash password
        password_hash = get_password_hash(password)
        
        # Create user
        user = await self.user_repo.create(email, password_hash, name)
        
        # Create default folders for new user
        folder_repo = NoteFolderRepository(self.db)
        default_folders = ["学习", "工作", "生活"]
        for folder_name in default_folders:
            await folder_repo.create(str(user.id), folder_name)
        
        # Create default knowledge base for new user
        kb_repo = KnowledgeBaseRepository(self.db)
        await kb_repo.create(
            owner_id=str(user.id),
            name="我的知识库",
            description="这是您的第一个知识库，您可以在这里上传和管理文档",
            tags=[]
        )
        
        # Create access token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        return access_token, user.to_dict()

