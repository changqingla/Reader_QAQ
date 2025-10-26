"""
RAG API 控制器
"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from config.database import get_db
from middlewares.auth import get_current_user
from models.user import User
from .schemas import ChatRequest, StreamChunk
from .service import RAGService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rag", tags=["RAG"])


@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    流式聊天接口
    
    Args:
        request: 聊天请求
        current_user: 当前用户
        db: 数据库会话
        
    Returns:
        StreamingResponse: SSE 流式响应
    """
    try:
        # 创建 RAG 服务
        rag_service = RAGService(db)
        
        # 定义生成器函数
        async def generate():
            try:
                async for chunk in rag_service.chat_stream(request, current_user.id):
                    # SSE 格式: data: {JSON}\n\n
                    yield f"data: {chunk.model_dump_json()}\n\n"
                
                # 发送结束标记
                yield "data: [DONE]\n\n"
            
            except Exception as e:
                logger.error(f"Stream error: {e}", exc_info=True)
                error_chunk = StreamChunk(
                    type="error",
                    content=str(e)
                )
                yield f"data: {error_chunk.model_dump_json()}\n\n"
        
        # 返回流式响应
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # 禁用 Nginx 缓冲
            }
        )
    
    except Exception as e:
        logger.error(f"Failed to start chat stream: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "service": "RAG"}

