"""
RAG 服务层
"""
import logging
from typing import AsyncGenerator, List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from .client import rag_client
from .config import rag_settings
from .schemas import (
    ChatRequest, RAGChatRequest, ChatMessage, 
    LLMConfig, RecallConfig, ThinkingConfig, StreamChunk
)
from repositories.kb_repository import KnowledgeBaseRepository
from repositories.document_repository import DocumentRepository
from utils.es_utils import get_user_es_index

logger = logging.getLogger(__name__)


class RAGService:
    """RAG 服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.kb_repo = KnowledgeBaseRepository(db)
        self.doc_repo = DocumentRepository(db)
    
    async def _get_es_index_names(self, user_id: UUID) -> List[str]:
        """
        获取用户的 ES 索引名称
        
        注意：每个用户一个索引，所有知识库的文档都在同一个索引中
        
        Args:
            user_id: 用户ID
            
        Returns:
            List[str]: ES 索引名称列表（实际只有一个）
        """
        # 使用用户级别的索引，格式: {user_id}_reader
        user_index = get_user_es_index(str(user_id))
        return [user_index]
    
    async def _get_doc_ids(
        self, 
        kb_id: Optional[str] = None, 
        doc_ids: Optional[List[str]] = None
    ) -> Optional[List[str]]:
        """
        获取文档ID列表
        
        Args:
            kb_id: 知识库ID（可选）
            doc_ids: 明确指定的文档ID列表（可选）
            
        Returns:
            Optional[List[str]]: 文档ID列表，None 表示不限制
        """
        if doc_ids:
            # 如果明确指定了文档ID，直接返回
            return doc_ids
        
        if kb_id:
            # 如果指定了知识库，返回该知识库下的所有文档ID
            try:
                kb_uuid = UUID(kb_id)
                docs = await self.doc_repo.list_by_kb(kb_uuid)
                return [str(doc.id) for doc in docs]
            except Exception as e:
                logger.warning(f"Failed to get doc IDs for kb {kb_id}: {e}")
                return None
        
        # 不限制文档范围
        return None
    
    def _build_llm_config(self) -> LLMConfig:
        """构建 LLM 配置"""
        return LLMConfig(
            model_name=rag_settings.LLM_MODEL_NAME,
            model_url=rag_settings.LLM_MODEL_URL,
            api_key=rag_settings.LLM_API_KEY,
            temperature=rag_settings.LLM_TEMPERATURE,
            top_p=rag_settings.LLM_TOP_P,
            max_tokens=rag_settings.LLM_MAX_TOKENS
        )
    
    def _build_recall_config(
        self,
        index_names: List[str],
        doc_ids: Optional[List[str]] = None
    ) -> RecallConfig:
        """构建召回配置"""
        return RecallConfig(
            index_names=index_names,
            es_host=rag_settings.ES_HOST,
            top_n=rag_settings.RECALL_TOP_N,
            similarity_threshold=rag_settings.RECALL_SIMILARITY_THRESHOLD,
            vector_similarity_weight=rag_settings.RECALL_VECTOR_SIMILARITY_WEIGHT,
            top_k=rag_settings.RECALL_TOP_K,
            doc_ids=doc_ids,
            model_factory=rag_settings.EMBED_MODEL_FACTORY,
            model_name=rag_settings.EMBED_MODEL_NAME,
            model_base_url=rag_settings.EMBED_MODEL_BASE_URL,
            model_api_key=rag_settings.EMBED_MODEL_API_KEY,
            rerank_factory=rag_settings.RERANK_FACTORY,
            rerank_model_name=rag_settings.RERANK_MODEL_NAME,
            rerank_base_url=rag_settings.RERANK_BASE_URL,
            rerank_api_key=rag_settings.RERANK_API_KEY
        )
    
    def _build_thinking_config(self) -> ThinkingConfig:
        """构建思考配置"""
        return ThinkingConfig(
            max_sub_questions=rag_settings.THINKING_MAX_SUB_QUESTIONS,
            max_iterations=rag_settings.THINKING_MAX_ITERATIONS,
            enable_question_refinement=rag_settings.THINKING_ENABLE_QUESTION_REFINEMENT
        )
    
    async def chat_stream(
        self,
        request: ChatRequest,
        user_id: UUID
    ) -> AsyncGenerator[StreamChunk, None]:
        """
        流式聊天
        
        Args:
            request: 前端聊天请求
            user_id: 用户ID
            
        Yields:
            StreamChunk: 流式响应块
        """
        try:
            # 1. 获取用户的 ES 索引名称（每个用户一个索引）
            index_names = await self._get_es_index_names(user_id)
            
            # 2. 获取文档ID列表（用于限制检索范围）
            # 如果指定了 kb_id 或 doc_ids，则限制在这些文档范围内
            doc_ids = await self._get_doc_ids(request.kb_id, request.doc_ids)
            
            # 3. 构建配置
            llm_config = self._build_llm_config()
            recall_config = self._build_recall_config(index_names, doc_ids)
            thinking_config = self._build_thinking_config()
            
            # 4. 构建消息列表（当前只发送单条消息，未来可以支持历史）
            messages = [
                ChatMessage(role="user", content=request.message)
            ]
            
            # 5. 构建 RAG 请求
            # 前端 mode: "deep" | "search"
            # RAG 服务 mode: "chat" | "think"
            # - deep模式: mode="chat", knowledge_base=True, tavily=False
            # - search模式: mode="chat", knowledge_base=False, tavily=True
            rag_request = RAGChatRequest(
                mode="chat",  # RAG服务只支持 "chat" 或 "think"，这里使用 "chat"
                session_id=request.session_id,
                messages=messages,
                llm=llm_config,
                recall=recall_config,
                thinking=thinking_config,
                knowledge_base=(request.mode == "deep"),  # 深度思考模式启用知识库
                tavily=(request.mode == "search"),  # 联网搜索模式启用 Tavily
                tavily_api_key=rag_settings.TAVILY_API_KEY if request.mode == "search" else None,
                show_quote=False,
                stream=True
            )
            
            logger.info(f"RAG request: session_id={request.session_id}, mode={request.mode}, kb_id={request.kb_id}")
            
            # 6. 调用 RAG 服务
            async for chunk in rag_client.stream_chat_completion(rag_request):
                yield chunk
        
        except Exception as e:
            logger.error(f"Error in chat_stream: {e}")
            yield StreamChunk(
                type="error",
                content=f"Chat error: {str(e)}"
            )
