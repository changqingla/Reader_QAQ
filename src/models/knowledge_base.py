"""Knowledge Base database model."""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from config.database import Base
import uuid


# 知识库分类常量
KNOWLEDGE_CATEGORIES = [
    "哲学", "经济学", "法学", "教育学", "文学", "历史学",
    "理学", "工学", "农学", "医学", "军事学", "管理学", "艺术学", "其它"
]


class KnowledgeBase(Base):
    """Knowledge Base model - supports both private and public sharing."""
    __tablename__ = "knowledge_bases"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    category = Column(String(50), nullable=False, default="其它", index=True)  # 知识库分类
    is_public = Column(Boolean, nullable=False, default=False, index=True)  # 是否公开
    subscribers_count = Column(Integer, nullable=False, default=0, index=True)  # 订阅数
    view_count = Column(Integer, nullable=False, default=0)  # 浏览量
    contents_count = Column(Integer, nullable=False, default=0)
    avatar = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_updated_at = Column(DateTime(timezone=True), nullable=True)  # 最后内容更新时间
    
    def to_dict(self, include_owner=False):
        """Convert to dictionary."""
        result = {
            "id": str(self.id),
            "name": self.name,
            "description": self.description or "",
            "category": self.category,
            "isPublic": self.is_public,
            "subscribersCount": self.subscribers_count,
            "viewCount": self.view_count,
            "contents": self.contents_count,
            "avatar": self.avatar or "/kb.png",
            "createdAt": self.created_at.strftime("%Y-%m-%d"),
            "updatedAt": self.updated_at.strftime("%Y-%m-%d"),
        }
        if include_owner:
            result["ownerId"] = str(self.owner_id)
        return result


class KnowledgeBaseSubscription(Base):
    """Knowledge Base subscription relationship."""
    __tablename__ = "kb_subscriptions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    kb_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_bases.id", ondelete="CASCADE"), nullable=False, index=True)
    subscribed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_viewed_at = Column(DateTime(timezone=True), nullable=True)
    
    __table_args__ = (
        UniqueConstraint('user_id', 'kb_id', name='uq_user_kb_subscription'),
    )
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "userId": str(self.user_id),
            "kbId": str(self.kb_id),
            "subscribedAt": self.subscribed_at.isoformat(),
            "lastViewedAt": self.last_viewed_at.isoformat() if self.last_viewed_at else None,
        }

