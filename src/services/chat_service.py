"""
聊天会话服务层
"""
from typing import List, Optional
from uuid import UUID

from repositories.chat_repository import ChatRepository
from models.chat_session import ChatSession, ChatMessage


class ChatService:
    """聊天会话服务"""
    
    def __init__(self, chat_repo: ChatRepository):
        self.chat_repo = chat_repo
    
    async def create_or_get_session(self, user_id: UUID, first_message: str) -> ChatSession:
        """创建或获取聊天会话"""
        # 生成标题（取前30个字符）
        title = first_message[:30] + ("..." if len(first_message) > 30 else "")
        session = await self.chat_repo.create_session(user_id, title)
        return session
    
    async def get_session(self, session_id: UUID, user_id: UUID) -> Optional[ChatSession]:
        """获取会话（验证所有权）"""
        session = await self.chat_repo.get_session(session_id)
        if session and session.user_id == user_id:
            return session
        return None
    
    async def list_sessions(self, user_id: UUID, page: int = 1, page_size: int = 50) -> List[ChatSession]:
        """获取用户的所有会话"""
        return await self.chat_repo.list_user_sessions(user_id, page, page_size)
    
    async def delete_session(self, session_id: UUID, user_id: UUID) -> bool:
        """删除会话（验证所有权）"""
        session = await self.get_session(session_id, user_id)
        if not session:
            return False
        return await self.chat_repo.delete_session(session_id)
    
    async def add_message(
        self,
        session_id: UUID,
        user_id: UUID,
        role: str,
        content: str,
        mode: Optional[str] = None,
        quotes: Optional[List[dict]] = None
    ) -> Optional[ChatMessage]:
        """添加消息（验证所有权）"""
        session = await self.get_session(session_id, user_id)
        if not session:
            return None
        
        return await self.chat_repo.add_message(session_id, role, content, mode, quotes)
    
    async def get_messages(self, session_id: UUID, user_id: UUID) -> List[ChatMessage]:
        """获取会话消息（验证所有权）"""
        session = await self.get_session(session_id, user_id)
        if not session:
            return []
        
        return await self.chat_repo.get_session_messages(session_id)

