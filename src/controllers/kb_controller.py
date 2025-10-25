"""Knowledge Base API endpoints."""
from fastapi import APIRouter, Depends, Query, UploadFile, File, BackgroundTasks, HTTPException, status
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
        request.get("category", "其它")
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


@router.get("/{kbId}/info")
async def get_knowledge_base_info(
    kbId: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get knowledge base info (supports both owned and public KBs)."""
    service = KnowledgeBaseService(db)
    return await service.get_kb_info(kbId, str(current_user.id))


@router.get("/quota")
async def get_quota(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get storage quota."""
    service = KnowledgeBaseService(db)
    return await service.get_quota(str(current_user.id))


@router.post("/{kbId}/avatar")
async def upload_kb_avatar(
    kbId: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload knowledge base avatar image."""
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "VALIDATION_ERROR", "message": "Only image files are allowed"}}
        )
    
    # Read file
    file_data = await file.read()
    
    # Upload avatar
    service = KnowledgeBaseService(db)
    return await service.upload_avatar(
        kbId,
        str(current_user.id),
        file_data,
        file.filename,
        file.content_type
    )


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


@router.get("/{kbId}/documents/{docId}/url")
async def get_document_url(
    kbId: str,
    docId: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get presigned URL for document file."""
    service = DocumentService(db)
    return await service.get_document_url(docId, kbId, str(current_user.id))


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


# ============ Public Sharing & Subscription Features ============

@router.post("/{kbId}/toggle-public")
async def toggle_kb_public(
    kbId: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Toggle public status of a knowledge base."""
    service = KnowledgeBaseService(db)
    return await service.toggle_public(kbId, str(current_user.id))


@router.post("/{kbId}/subscribe")
async def subscribe_to_kb(
    kbId: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Subscribe to a public knowledge base."""
    service = KnowledgeBaseService(db)
    return await service.subscribe_kb(kbId, str(current_user.id))


@router.delete("/{kbId}/subscribe")
async def unsubscribe_from_kb(
    kbId: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Unsubscribe from a knowledge base."""
    service = KnowledgeBaseService(db)
    return await service.unsubscribe_kb(kbId, str(current_user.id))


@router.get("/{kbId}/subscription-status")
async def check_kb_subscription(
    kbId: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Check if user is subscribed to a knowledge base."""
    service = KnowledgeBaseService(db)
    return await service.check_subscription(kbId, str(current_user.id))


@router.get("/subscriptions/list")
async def list_my_subscriptions(
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all knowledge bases subscribed by current user."""
    service = KnowledgeBaseService(db)
    items, total = await service.list_user_subscriptions(str(current_user.id), page, pageSize)
    return {
        "total": total,
        "page": page,
        "pageSize": pageSize,
        "items": items
    }


@router.get("/public/list")
async def list_public_knowledge_bases(
    category: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List public knowledge bases (knowledge square)."""
    service = KnowledgeBaseService(db)
    items, total = await service.list_public_kbs(category, q, page, pageSize)
    return {
        "total": total,
        "page": page,
        "pageSize": pageSize,
        "items": items
    }


@router.get("/featured/list")
async def list_featured_knowledge_bases(
    page: int = Query(1, ge=1),
    pageSize: int = Query(30, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List featured knowledge bases (2025年度精选)."""
    service = KnowledgeBaseService(db)
    items, total = await service.list_featured_kbs(page, pageSize)
    return {
        "total": total,
        "page": page,
        "pageSize": pageSize,
        "items": items
    }


@router.get("/categories/stats")
async def get_kb_categories_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get statistics for each knowledge base category."""
    service = KnowledgeBaseService(db)
    return {"categories": await service.get_categories_stats()}
