"""
聊天会话模型
"""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from config.database import Base


class ChatSession(Base):
    """聊天会话"""
    __tablename__ = "chat_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False)  # 会话标题（通常是第一条消息的摘要）
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关系（使用 lazy loading）
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan", lazy="select")
    user = relationship("User", back_populates="chat_sessions", lazy="select")

    def to_dict(self, include_messages=False):
        """转换为字典"""
        result = {
            "id": str(self.id),
            "title": self.title,
            "lastMessage": "",
            "timestamp": self._format_timestamp(self.updated_at),
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat(),
            "messageCount": 0
        }
        
        # 只在明确需要时才访问关系属性
        if include_messages:
            try:
                messages_list = list(self.messages)
                if messages_list:
                    last_message = messages_list[-1]
                    result["lastMessage"] = last_message.content[:50]
                    result["messageCount"] = len(messages_list)
            except:
                pass
        
        return result
    
    @staticmethod
    def _format_timestamp(dt: datetime) -> str:
        """格式化时间戳为相对时间"""
        now = datetime.utcnow()
        diff = now - dt
        
        if diff.days > 7:
            return f"{diff.days} 天前"
        elif diff.days > 0:
            return f"{diff.days} 天前"
        elif diff.seconds >= 3600:
            hours = diff.seconds // 3600
            return f"{hours} 小时前"
        elif diff.seconds >= 60:
            minutes = diff.seconds // 60
            return f"{minutes} 分钟前"
        else:
            return "刚刚"


class ChatMessage(Base):
    """聊天消息"""
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # 'user' | 'assistant'
    content = Column(Text, nullable=False)
    mode = Column(String(20), nullable=True)  # 'deep' | 'search'
    quotes = Column(Text, nullable=True)  # JSON 格式的引用信息
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 关系
    session = relationship("ChatSession", back_populates="messages")

    def to_dict(self):
        """转换为字典"""
        import json
        return {
            "id": str(self.id),
            "role": self.role,
            "content": self.content,
            "mode": self.mode,
            "quotes": json.loads(self.quotes) if self.quotes else [],
            "createdAt": self.created_at.isoformat()
        }

