"""Knowledge Base API endpoints."""
from fastapi import APIRouter, Depends, Query, UploadFile, File, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from config.database import get_db
from middlewares.auth import get_current_user
from models.user import User
from services.kb_service import KnowledgeBaseService
from services.document_service import DocumentService
from services.search_service import SearchService

router = APIRouter(prefix="/kb", tags=["Knowledge Base"])


@router.get("")
async def list_knowledge_bases(
    q: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List user's knowledge bases."""
    service = KnowledgeBaseService(db)
    items, total = await service.list_kbs(str(current_user.id), q, page, pageSize)
    return {
        "total": total,
        "page": page,
        "pageSize": pageSize,
        "items": items
    }


@router.post("")
async def create_knowledge_base(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new knowledge base."""
    service = KnowledgeBaseService(db)
    return await service.create_kb(
        str(current_user.id),
        request["name"],
        request.get("description"),
        request.get("tags", [])
    )


@router.patch("/{kbId}")
async def update_knowledge_base(
    kbId: str,
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update knowledge base."""
    service = KnowledgeBaseService(db)
    return await service.update_kb(kbId, str(current_user.id), **request)


@router.delete("/{kbId}")
async def delete_knowledge_base(
    kbId: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete knowledge base."""
    service = KnowledgeBaseService(db)
    await service.delete_kb(kbId, str(current_user.id))
    return {"success": True}


@router.get("/quota")
async def get_quota(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get storage quota."""
    service = KnowledgeBaseService(db)
    return await service.get_quota(str(current_user.id))


@router.post("/{kbId}/documents")
async def upload_document(
    kbId: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload document to knowledge base."""
    service = DocumentService(db)
    return await service.upload_document(kbId, str(current_user.id), file, background_tasks)


@router.get("/{kbId}/documents")
async def list_documents(
    kbId: str,
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List documents in knowledge base."""
    service = DocumentService(db)
    items, total = await service.list_documents(kbId, str(current_user.id), page, pageSize)
    return {"total": total, "page": page, "pageSize": pageSize, "items": items}


@router.get("/{kbId}/documents/{docId}/status")
async def get_document_status(
    kbId: str,
    docId: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get document processing status."""
    service = DocumentService(db)
    return await service.get_document_status(docId, kbId, str(current_user.id))


@router.delete("/{kbId}/documents/{docId}")
async def delete_document(
    kbId: str,
    docId: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a document."""
    service = DocumentService(db)
    await service.delete_document(docId, kbId, str(current_user.id))
    return {"success": True}


@router.post("/{kbId}/chat/messages")
async def chat_with_kb(
    kbId: str,
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Search in knowledge base (retrieve relevant chunks).
    Note: LLM answer generation is not implemented yet.
    """
    service = SearchService(db)
    question = request.get("question", "")
    top_n = request.get("top_n", 10)
    
    search_results = await service.search_in_kb(
        kbId,
        str(current_user.id),
        question,
        top_n=top_n
    )
    
    # Return search results (without LLM-generated answer)
    return {
        "messageId": "search_" + str(hash(question)),
        "references": search_results["references"],
        "answer": "检索完成，找到相关内容（LLM问答功能暂未实现）"
    }
