"""Knowledge Base repository for database operations."""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import Optional, List, Tuple
from models.knowledge_base import KnowledgeBase, KNOWLEDGE_CATEGORIES
from models.document import Document
from datetime import datetime, timedelta


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
    
    async def get_by_id_public(self, kb_id: str) -> Optional[KnowledgeBase]:
        """Get public knowledge base by ID (no owner check)."""
        result = await self.db.execute(
            select(KnowledgeBase).where(
                KnowledgeBase.id == kb_id,
                KnowledgeBase.is_public == True
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
        category: str = "其它"
    ) -> KnowledgeBase:
        """Create a new knowledge base."""
        # Validate category
        if category not in KNOWLEDGE_CATEGORIES:
            category = "其它"
        
        kb = KnowledgeBase(
            owner_id=owner_id,
            name=name,
            description=description,
            category=category
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
            kb.last_updated_at = datetime.utcnow()
            await self.db.commit()
    
    async def toggle_public(self, kb: KnowledgeBase) -> KnowledgeBase:
        """Toggle public status of a knowledge base."""
        kb.is_public = not kb.is_public
        await self.db.commit()
        await self.db.refresh(kb)
        return kb
    
    async def increment_view_count(self, kb_id: str):
        """Increment view count."""
        kb = await self.db.get(KnowledgeBase, kb_id)
        if kb:
            kb.view_count += 1
            await self.db.commit()
    
    async def list_public_kbs(
        self,
        category: Optional[str] = None,
        query: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[KnowledgeBase], int]:
        """List public knowledge bases."""
        stmt = select(KnowledgeBase).where(KnowledgeBase.is_public == True)
        
        if category:
            stmt = stmt.where(KnowledgeBase.category == category)
        
        if query:
            stmt = stmt.where(
                KnowledgeBase.name.ilike(f"%{query}%") | 
                KnowledgeBase.description.ilike(f"%{query}%")
            )
        
        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self.db.execute(count_stmt)).scalar()
        
        # Paginate and order by subscribers
        stmt = stmt.order_by(desc(KnowledgeBase.subscribers_count), desc(KnowledgeBase.created_at))
        stmt = stmt.limit(page_size).offset((page - 1) * page_size)
        
        result = await self.db.execute(stmt)
        kbs = result.scalars().all()
        
        return list(kbs), total or 0
    
    async def list_featured_kbs(
        self,
        page: int = 1,
        page_size: int = 30
    ) -> Tuple[List[KnowledgeBase], int]:
        """List featured knowledge bases (2025年度精选)."""
        stmt = select(KnowledgeBase).where(KnowledgeBase.is_public == True)
        
        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self.db.execute(count_stmt)).scalar()
        
        # 排序算法：订阅数 40% + 文档数 20% + 浏览量 10%
        # SQLAlchemy expression for weighted score
        stmt = stmt.order_by(
            desc(
                KnowledgeBase.subscribers_count * 0.4 + 
                func.least(KnowledgeBase.contents_count, 50) * 0.2 +
                KnowledgeBase.view_count * 0.1
            )
        )
        stmt = stmt.limit(page_size).offset((page - 1) * page_size)
        
        result = await self.db.execute(stmt)
        kbs = result.scalars().all()
        
        return list(kbs), total or 0
    
    async def get_categories_stats(self) -> List[dict]:
        """Get statistics for each category."""
        result = await self.db.execute(
            select(
                KnowledgeBase.category,
                func.count(KnowledgeBase.id).label('count'),
                func.sum(KnowledgeBase.subscribers_count).label('subscribers')
            )
            .where(KnowledgeBase.is_public == True)
            .group_by(KnowledgeBase.category)
            .order_by(desc('subscribers'))
        )
        
        stats = []
        for row in result.all():
            stats.append({
                "category": row.category,
                "count": row.count,
                "subscribers": row.subscribers or 0
            })
        
        return stats

