"""Knowledge Base database model."""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from config.database import Base
import uuid


class KnowledgeBase(Base):
    """Knowledge Base model for user's private knowledge bases."""
    __tablename__ = "knowledge_bases"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    tags = Column(ARRAY(String), nullable=False, default=list, server_default="{}")
    contents_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description or "",
            "tags": self.tags or [],
            "contents": self.contents_count,
            "createdAt": self.created_at.strftime("%Y-%m-%d"),
        }

