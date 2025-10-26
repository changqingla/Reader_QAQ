"""
聊天会话数据访问层
"""
from typing import List, Optional, Dict
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from sqlalchemy.orm import joinedload
import json

from models.chat_session import ChatSession, ChatMessage


class ChatRepository:
    """聊天会话仓储"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_session(self, user_id: UUID, title: str) -> ChatSession:
        """创建聊天会话"""
        session = ChatSession(
            user_id=user_id,
            title=title
        )
        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)
        return session
    
    async def get_session(self, session_id: UUID) -> Optional[ChatSession]:
        """获取聊天会话"""
        stmt = select(ChatSession).where(ChatSession.id == session_id).options(
            joinedload(ChatSession.messages)
        )
        result = await self.db.execute(stmt)
        return result.unique().scalar_one_or_none()
    
    async def list_user_sessions(
        self, 
        user_id: UUID, 
        page: int = 1, 
        page_size: int = 50
    ) -> List[ChatSession]:
        """获取用户的所有聊天会话"""
        stmt = (
            select(ChatSession)
            .where(ChatSession.user_id == user_id)
            .order_by(desc(ChatSession.updated_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def update_session_title(self, session_id: UUID, title: str) -> Optional[ChatSession]:
        """更新会话标题"""
        session = await self.get_session(session_id)
        if not session:
            return None
        
        session.title = title
        await self.db.commit()
        await self.db.refresh(session)
        return session
    
    async def delete_session(self, session_id: UUID) -> bool:
        """删除聊天会话"""
        session = await self.get_session(session_id)
        if not session:
            return False
        
        await self.db.delete(session)
        await self.db.commit()
        return True
    
    async def add_message(
        self,
        session_id: UUID,
        role: str,
        content: str,
        mode: Optional[str] = None,
        quotes: Optional[List[dict]] = None
    ) -> ChatMessage:
        """添加消息到会话"""
        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            mode=mode,
            quotes=json.dumps(quotes) if quotes else None
        )
        self.db.add(message)
        
        # 更新会话的 updated_at
        session = await self.get_session(session_id)
        if session:
            session.updated_at = message.created_at
        
        await self.db.commit()
        await self.db.refresh(message)
        return message
    
    async def get_session_messages(self, session_id: UUID) -> List[ChatMessage]:
        """获取会话的所有消息"""
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_session_stats(self, session_id: UUID) -> Dict:
        """获取会话统计信息（消息数量和最后一条消息）"""
        # 获取消息数量
        count_stmt = select(func.count(ChatMessage.id)).where(ChatMessage.session_id == session_id)
        count_result = await self.db.execute(count_stmt)
        message_count = count_result.scalar() or 0
        
        # 获取最后一条消息
        last_msg_stmt = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(desc(ChatMessage.created_at))
            .limit(1)
        )
        last_msg_result = await self.db.execute(last_msg_stmt)
        last_message = last_msg_result.scalar_one_or_none()
        
        return {
            "messageCount": message_count,
            "lastMessage": last_message.content[:50] if last_message else ""
        }

