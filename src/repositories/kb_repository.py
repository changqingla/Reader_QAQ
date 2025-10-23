"""Knowledge Base repository for database operations."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List, Tuple
from models.knowledge_base import KnowledgeBase
from models.document import Document


class KnowledgeBaseRepository:
    """Repository for KnowledgeBase model."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, kb_id: str, owner_id: str) -> Optional[KnowledgeBase]:
        """Get knowledge base by ID for specific owner."""
        result = await self.db.execute(
            select(KnowledgeBase).where(
                KnowledgeBase.id == kb_id,
                KnowledgeBase.owner_id == owner_id
            )
        )
        return result.scalar_one_or_none()
    
    async def list_kbs(
        self,
        owner_id: str,
        query: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[KnowledgeBase], int]:
        """List knowledge bases for user."""
        stmt = select(KnowledgeBase).where(KnowledgeBase.owner_id == owner_id)
        
        if query:
            stmt = stmt.where(KnowledgeBase.name.ilike(f"%{query}%"))
        
        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self.db.execute(count_stmt)).scalar()
        
        # Paginate
        stmt = stmt.order_by(KnowledgeBase.created_at.desc())
        stmt = stmt.limit(page_size).offset((page - 1) * page_size)
        
        result = await self.db.execute(stmt)
        kbs = result.scalars().all()
        
        return list(kbs), total or 0
    
    async def create(
        self,
        owner_id: str,
        name: str,
        description: Optional[str],
        tags: List[str]
    ) -> KnowledgeBase:
        """Create a new knowledge base."""
        kb = KnowledgeBase(
            owner_id=owner_id,
            name=name,
            description=description,
            tags=tags
        )
        self.db.add(kb)
        await self.db.commit()
        await self.db.refresh(kb)
        return kb
    
    async def update(self, kb: KnowledgeBase, **kwargs) -> KnowledgeBase:
        """Update knowledge base fields."""
        for key, value in kwargs.items():
            if hasattr(kb, key) and value is not None:
                setattr(kb, key, value)
        await self.db.commit()
        await self.db.refresh(kb)
        return kb
    
    async def delete(self, kb: KnowledgeBase):
        """Delete a knowledge base."""
        await self.db.delete(kb)
        await self.db.commit()
    
    async def calculate_total_size(self, owner_id: str) -> int:
        """Calculate total storage used by user."""
        result = await self.db.execute(
            select(func.sum(Document.size)).select_from(Document).join(
                KnowledgeBase
            ).where(KnowledgeBase.owner_id == owner_id)
        )
        total = result.scalar()
        return total or 0
    
    async def increment_contents_count(self, kb_id: str, delta: int = 1):
        """Increment contents count."""
        kb = await self.db.get(KnowledgeBase, kb_id)
        if kb:
            kb.contents_count += delta
            await self.db.commit()

