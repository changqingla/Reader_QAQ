"""Main agent class for orchestrating the workflow."""
import time
import uuid
from typing import Dict, Any, Optional, List

from langchain_openai import ChatOpenAI

from .state import AgentState, IntentType
from .nodes import AgentNodes
from .graph import create_agent_graph
from ..tools import create_recall_tool, create_web_search_tool
from ..utils.logger import get_logger
from config import get_settings

# 上下文管理模块 - 强制依赖
from context.session_manager import SessionManager
from context.session_storage import SessionStorage

logger = get_logger(__name__)


class IntelligentAgent:
    """
    Main intelligent agent for processing user queries.
    
    This agent orchestrates the entire workflow from intent recognition
    to answer generation.
    """
    
    def __init__(self):
        """Initialize the intelligent agent with configuration from settings."""
        self.settings = get_settings()
        logger.info("Initializing IntelligentAgent...")
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=self.settings.model_name,
            temperature=self.settings.temperature,
            openai_api_key=self.settings.openai_api_key,
            openai_api_base=self.settings.openai_api_base
        )
        logger.info(f"LLM initialized: {self.settings.model_name}")
        
        # Initialize Recall tool with HTTP API
        self.recall_tool = create_recall_tool(
            api_url=self.settings.recall_api_url,
            index_names=self.settings.get_recall_index_names(),
            es_host=self.settings.recall_es_host,
            model_base_url=self.settings.recall_model_base_url,
            api_key=self.settings.recall_api_key,
            doc_ids=self.settings.get_recall_doc_ids(),
            top_n=self.settings.recall_top_n,
            similarity_threshold=self.settings.recall_similarity_threshold,
            vector_similarity_weight=self.settings.recall_vector_similarity_weight,
            model_factory=self.settings.recall_model_factory,
            model_name=self.settings.recall_model_name,
            use_rerank=self.settings.recall_use_rerank,
            rerank_factory=self.settings.recall_rerank_factory if self.settings.recall_use_rerank else None,
            rerank_model_name=self.settings.recall_rerank_model_name if self.settings.recall_use_rerank else None,
            rerank_base_url=self.settings.recall_rerank_base_url if self.settings.recall_use_rerank else None,
            rerank_api_key=self.settings.recall_rerank_api_key if self.settings.recall_use_rerank else None
        )
        logger.info("Recall tool initialized with HTTP API")
        
        # Initialize Web search tool
        self.web_search_tool = None
        if self.settings.enable_web_search and self.settings.tavily_api_key:
            self.web_search_tool = create_web_search_tool(
                api_key=self.settings.tavily_api_key,
                max_results=self.settings.tavily_max_results
            )
            logger.info("Web search tool initialized with Tavily")
        else:
            logger.info("Web search tool disabled or API key not provided")
        
        # Initialize nodes
        self.agent_nodes = AgentNodes(
            llm=self.llm,
            recall_tool=self.recall_tool,
            web_search_tool=self.web_search_tool
        )
        
        # Initialize session manager (强制依赖)
        storage = SessionStorage()
        self.session_manager = SessionManager(storage)
        logger.info("Session manager initialized at agent level")
        
        # Create graph
        self.graph = create_agent_graph(self.agent_nodes)
        logger.info("Agent graph created")
        
        logger.info("IntelligentAgent initialization complete")
    
    def process_query(
        self,
        user_query: str,
        mode_type: Optional[str] = None,
        enable_web_search: Optional[bool] = None,
        deep_thinking: bool = False,
        session_id: Optional[str] = None,
        content: Optional[str] = None,
        force_recall: bool = False,
        recall_index_names: Optional[List[str]] = None,
        recall_doc_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Process a user query through the agent workflow.
        
        Args:
            user_query: The user's question or request
            mode_type: Optional task type override
            enable_web_search: Optional override for web search enablement
            deep_thinking: Enable deep thinking mode with QA pairs
            session_id: Optional session ID for multi-turn conversation (auto-loads history if exists)
            content: Optional full document content (for small documents)
            force_recall: If True, always use recall even when content is small
            recall_index_names: Optional list of index names for recall (overrides environment)
            recall_doc_ids: Optional list of document IDs for recall (overrides environment)
            
        Returns:
            Result dictionary containing the final answer and metadata
        """
        start_time = time.time()
        
        # 🔑 如果用户未提供session_id，自动生成一个
        if session_id is None:
            session_id = str(uuid.uuid4())
            logger.info(f"No session_id provided, generated new: {session_id}")
        
        logger.info(f"Processing query [session: {session_id}]: {user_query[:100]}...")
        
        # ========================================================================
        # Session Management: 先加载会话状态，用于计算可用tokens
        # ========================================================================
        session = self.session_manager.get_or_create_session(session_id=session_id)
        session_id = str(session.session_id)
        logger.info(f"Using session: {session_id}")
        
        # 🔑 直接使用 session.total_token_count（已经正确维护）
        # 包含：压缩摘要tokens + 保留消息tokens（不包括已压缩的原始消息）
        session_tokens = session.total_token_count
        
        # 加载session历史（用于context injection）
        session_messages = self.session_manager.get_conversation_history(session_id)
        session_history = session_messages if session_messages else None
        
        if session_messages:
            logger.info(f"Loaded session history: {len(session_messages)} messages, {session_tokens} tokens")
        
        # ========================================================================
        # 🔑 自动计算当前可用上下文长度
        # ========================================================================
        from context.token_counter import calculate_tokens
        
        # 1. 计算当前查询的tokens
        query_tokens = calculate_tokens(user_query, self.settings.model_name)
        
        # 2. 预估系统提示词tokens（根据任务类型粗略估计）
        estimated_system_tokens = 2000  # 提示词+规划等系统消息
        
        # 3. 预留给回答的tokens
        reserved_answer_tokens = 4000  # 预留给助手回答
        
        # 4. 计算当前可用上下文
        # 公式：可用 = 最大上下文 - (历史tokens + 当前问题 + 系统提示 + 预留回答)
        max_context_tokens = self.settings.max_context_tokens
        used_tokens = session_tokens + query_tokens + estimated_system_tokens + reserved_answer_tokens
        available_tokens = max(0, max_context_tokens - used_tokens)
        
        logger.info("=" * 60)
        logger.info("📊 当前上下文使用情况")
        logger.info("=" * 60)
        logger.info(f"最大上下文: {max_context_tokens:,} tokens")
        logger.info(f"会话历史: {session_tokens:,} tokens (压缩摘要 + 保留消息)")
        logger.info(f"当前问题: {query_tokens:,} tokens")
        logger.info(f"系统提示: {estimated_system_tokens:,} tokens (估计)")
        logger.info(f"预留回答: {reserved_answer_tokens:,} tokens")
        logger.info(f"已使用: {used_tokens:,} tokens ({(used_tokens/max_context_tokens)*100:.1f}%)")
        logger.info(f"剩余可用: {available_tokens:,} tokens ({(available_tokens/max_context_tokens)*100:.1f}%)")
        logger.info("=" * 60)
        
        # ========================================================================
        # 🔑 Check if direct content mode should be used
        # ========================================================================
        use_direct_content_mode = False
        direct_content_value = None
        content_tokens = None
        
        if content and not force_recall:
            from ..utils import should_use_direct_content
            
            # 使用自动计算的可用tokens
            should_use, token_count = should_use_direct_content(
                content=content,
                available_tokens=available_tokens,
                threshold=self.settings.direct_content_threshold,
                model=self.settings.model_name
            )
            
            if should_use:
                use_direct_content_mode = True
                direct_content_value = content
                content_tokens = token_count
                logger.info("=" * 60)
                logger.info("✅ 启用直接内容模式（跳过 recall）")
                logger.info(f"   文档 Token 数: {token_count:,}")
                logger.info(f"   可用 Token 数: {available_tokens:,}")
                logger.info(f"   使用比例: {(token_count/available_tokens)*100:.1f}%")
                logger.info("=" * 60)
            else:
                logger.info("=" * 60)
                logger.info("⚠️ 文档过大，使用 recall 模式")
                logger.info(f"   文档 Token 数: {token_count:,}")
                logger.info(f"   可用 Token 数: {available_tokens:,}")
                logger.info(f"   使用比例: {(token_count/available_tokens)*100:.1f}%")
                logger.info(f"   阈值: {self.settings.direct_content_threshold*100:.0f}%")
                logger.info("=" * 60)
        elif content and force_recall:
            logger.info("⚠️ 提供了 content 但设置了 force_recall=True，将使用 recall 模式")
        
        # 🔑 关键修复：不在这里保存user消息，而是在workflow结束时保存
        # 这样可以避免当前user消息被包含在"历史"中
        # user_message_saved标志设为False，让answer_generation_node保存
        user_message_saved = False
        logger.debug(f"User message will be saved after processing (session {session_id})")
        
        # Prepare initial state
        initial_state: AgentState = {
            "user_query": user_query,
            "mode_type": IntentType(mode_type) if mode_type else None,
            "enable_web_search": enable_web_search if enable_web_search is not None else self.settings.enable_web_search,
            "deep_thinking": deep_thinking,
            "detected_intent": None,
            "plan": None,
            "current_step_index": 0,
            "replan_count": 0,
            "execution_results": [],
            "collected_information": "",
            "qa_pairs": [],
            "is_information_sufficient": False,
            "analysis_result": None,
            "final_answer": "",
            "messages": [],  # Empty messages (not used with SessionManager)
            # Session management
            "session_id": session_id,
            "session_history": session_history,  # Injected session history (from SessionManager)
            "session_tokens": session_tokens,
            "_user_message_saved": user_message_saved,  # Internal flag to avoid duplicate saving
            # Metadata
            "start_time": start_time,
            "error": None,
            # Direct content mode
            "direct_content": direct_content_value,
            "use_direct_content": use_direct_content_mode,
            "content_token_count": content_tokens,
            # Recall configuration (dynamic overrides)
            "recall_index_names": recall_index_names,
            "recall_doc_ids": recall_doc_ids
        }
        
        try:
            # Execute the graph with recursion limit
            config = {
                "configurable": {"thread_id": session_id},
                "recursion_limit": 50  # Increase from default 25
            }
            result = self.graph.invoke(initial_state, config=config)
            
            execution_time = time.time() - start_time
            logger.info(f"Query processed successfully in {execution_time:.2f}s")
            
            # Get session statistics
            session = self.session_manager.load_session(session_id)
            compression_threshold = self.settings.compression_threshold_tokens
            tokens_remaining = max(0, compression_threshold - session.total_token_count)
            
            session_stats = {
                "session_total_tokens": session.total_token_count,
                "session_message_count": session.message_count,
                "compression_threshold": compression_threshold,
                "tokens_until_compression": tokens_remaining
            }
            logger.debug(f"Session stats: {session.total_token_count}/{compression_threshold} tokens, {tokens_remaining} remaining")
            
            # Extract key information
            response = {
                "success": True,
                "session_id": session_id,
                "detected_intent": result["detected_intent"].value if result.get("detected_intent") else None,
                "plan": result.get("plan"),
                "execution_results": result.get("execution_results", []),
                "analysis": result.get("analysis_result"),
                "final_answer": result.get("final_answer", ""),
                "execution_time": execution_time,
                "error": result.get("error"),
                **session_stats  # Add session statistics
            }
            
            return response
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Error processing query: {str(e)}", exc_info=True)
            
            return {
                "success": False,
                "session_id": session_id,
                "error": str(e),
                "execution_time": execution_time,
                "final_answer": f"处理请求时发生错误: {str(e)}"
            }
    
    def get_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get the conversation history for a session.
        
        Args:
            session_id: Session ID to retrieve history for
            
        Returns:
            List of message dictionaries
        """
        messages = self.session_manager.get_conversation_history(session_id)
        if not messages:
            return []
        
        history = []
        for msg in messages:
            history.append({
                "role": msg.role,
                "content": msg.content,
                "type": msg.message_type.value,
                "token_count": msg.token_count,
                "created_at": msg.created_at.isoformat(),
                "is_compressed": msg.is_compressed
            })
        logger.debug(f"Retrieved {len(history)} messages from SessionManager")
        return history
    
    def clear_conversation(self, session_id: str) -> bool:
        """
        Clear the conversation history for a session.
        
        Args:
            session_id: Session ID to clear
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # This would require implementing a clear method in the checkpointer
            # For now, just log the action
            logger.info(f"Conversation clearing requested for session: {session_id}")
            logger.warning("Full conversation clearing not implemented - start a new session instead")
            return False
        except Exception as e:
            logger.error(f"Failed to clear conversation: {str(e)}")
            return False
    
    async def aprocess_query(
        self,
        user_query: str,
        mode_type: Optional[str] = None,
        enable_web_search: Optional[bool] = None,
        deep_thinking: bool = False,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Async version of process_query.
        
        Args:
            user_query: The user's question or request
            mode_type: Optional task type override
            enable_web_search: Optional override for web search enablement
            deep_thinking: Enable deep thinking mode with QA pairs
            session_id: Optional session ID for multi-turn conversation
            
        Returns:
            Result dictionary containing the final answer and metadata
        """
        # For now, call the sync version
        # In production, implement true async execution
        return self.process_query(user_query, mode_type, enable_web_search, deep_thinking, session_id)


def create_agent() -> IntelligentAgent:
    """
    Factory function to create a configured IntelligentAgent.
    
    The agent is configured via environment variables and settings.
    
    Returns:
        Configured IntelligentAgent instance
    """
    return IntelligentAgent()

