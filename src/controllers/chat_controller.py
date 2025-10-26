"""
聊天会话控制器
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

from config.database import get_db
from middlewares.auth import get_current_user
from models.user import User
from repositories.chat_repository import ChatRepository
from services.chat_service import ChatService


router = APIRouter(prefix="/chat", tags=["Chat"])


class CreateSessionRequest(BaseModel):
    """创建会话请求"""
    first_message: str


class AddMessageRequest(BaseModel):
    """添加消息请求"""
    role: str  # 'user' | 'assistant'
    content: str
    mode: Optional[str] = None
    quotes: Optional[List[dict]] = None


@router.get("/sessions")
async def list_sessions(
    page: int = 1,
    page_size: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户的所有聊天会话"""
    chat_repo = ChatRepository(db)
    chat_service = ChatService(chat_repo)
    
    sessions = await chat_service.list_sessions(current_user.id, page, page_size)
    
    # 为每个会话获取统计信息
    sessions_with_stats = []
    for session in sessions:
        session_dict = session.to_dict(include_messages=False)
        # 获取统计信息
        stats = await chat_repo.get_session_stats(session.id)
        session_dict.update(stats)
        sessions_with_stats.append(session_dict)
    
    return {
        "sessions": sessions_with_stats,
        "page": page,
        "pageSize": page_size
    }


@router.post("/sessions")
async def create_session(
    request: CreateSessionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建新的聊天会话"""
    chat_repo = ChatRepository(db)
    chat_service = ChatService(chat_repo)
    
    session = await chat_service.create_or_get_session(current_user.id, request.first_message)
    
    return session.to_dict()


@router.get("/sessions/{session_id}")
async def get_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取聊天会话详情"""
    chat_repo = ChatRepository(db)
    chat_service = ChatService(chat_repo)
    
    session = await chat_service.get_session(session_id, current_user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session.to_dict()


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除聊天会话"""
    chat_repo = ChatRepository(db)
    chat_service = ChatService(chat_repo)
    
    success = await chat_service.delete_session(session_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"success": True}


@router.get("/sessions/{session_id}/messages")
async def get_messages(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取会话的所有消息"""
    chat_repo = ChatRepository(db)
    chat_service = ChatService(chat_repo)
    
    messages = await chat_service.get_messages(session_id, current_user.id)
    
    return {
        "messages": [msg.to_dict() for msg in messages]
    }


@router.post("/sessions/{session_id}/messages")
async def add_message(
    session_id: UUID,
    request: AddMessageRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """添加消息到会话"""
    chat_repo = ChatRepository(db)
    chat_service = ChatService(chat_repo)
    
    message = await chat_service.add_message(
        session_id,
        current_user.id,
        request.role,
        request.content,
        request.mode,
        request.quotes
    )
    
    if not message:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return message.to_dict()

