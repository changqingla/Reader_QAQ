"""Favorite database model."""
from sqlalchemy import Column, String, DateTime, ForeignKey, CheckConstraint, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from config.database import Base
import uuid


class Favorite(Base):
    """Favorite model."""
    __tablename__ = "favorites"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String, nullable=False)
    target_id = Column(String, nullable=False)
    tags = Column(ARRAY(String), nullable=False, default=list, server_default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    __table_args__ = (
        CheckConstraint("type IN ('paper', 'knowledge')", name='check_favorite_type'),
        UniqueConstraint('user_id', 'type', 'target_id', name='uq_user_favorite'),
    )
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "type": self.type,
            "targetId": self.target_id,
            "tags": self.tags or [],
            "date": self.created_at.strftime("%Y-%m-%d"),
        }

