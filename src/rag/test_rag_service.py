"""
RAG 服务连接测试脚本
"""
import asyncio
import logging
from .config import rag_settings
from .schemas import (
    RAGChatRequest, ChatMessage, LLMConfig, 
    RecallConfig, ThinkingConfig
)
from .client import rag_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_rag_connection():
    """测试 RAG 服务连通性"""
    
    logger.info("=" * 60)
    logger.info("RAG 服务连接测试")
    logger.info("=" * 60)
    
    # 构建测试请求
    request = RAGChatRequest(
        mode="chat",
        session_id="test-session-001",
        messages=[
            ChatMessage(role="user", content="你好，请介绍一下你自己")
        ],
        llm=LLMConfig(
            model_name=rag_settings.LLM_MODEL_NAME,
            model_url=rag_settings.LLM_MODEL_URL,
            api_key=rag_settings.LLM_API_KEY,
            temperature=rag_settings.LLM_TEMPERATURE,
            top_p=rag_settings.LLM_TOP_P,
            max_tokens=rag_settings.LLM_MAX_TOKENS
        ),
        recall=RecallConfig(
            index_names=["test-index"],
            es_host=rag_settings.ES_HOST,
            top_n=rag_settings.RECALL_TOP_N,
            similarity_threshold=rag_settings.RECALL_SIMILARITY_THRESHOLD,
            vector_similarity_weight=rag_settings.RECALL_VECTOR_SIMILARITY_WEIGHT,
            top_k=rag_settings.RECALL_TOP_K,
            model_factory=rag_settings.EMBED_MODEL_FACTORY,
            model_name=rag_settings.EMBED_MODEL_NAME,
            model_base_url=rag_settings.EMBED_MODEL_BASE_URL,
            model_api_key=rag_settings.EMBED_MODEL_API_KEY,
            rerank_factory=rag_settings.RERANK_FACTORY,
            rerank_model_name=rag_settings.RERANK_MODEL_NAME,
            rerank_base_url=rag_settings.RERANK_BASE_URL,
            rerank_api_key=rag_settings.RERANK_API_KEY
        ),
        thinking=ThinkingConfig(
            max_sub_questions=rag_settings.THINKING_MAX_SUB_QUESTIONS,
            max_iterations=rag_settings.THINKING_MAX_ITERATIONS,
            enable_question_refinement=rag_settings.THINKING_ENABLE_QUESTION_REFINEMENT
        ),
        knowledge_base=True,
        tavily=False,
        show_quote=True,
        stream=True
    )
    
    logger.info(f"\n📡 RAG 服务地址: {rag_settings.RAG_SERVICE_URL}")
    logger.info(f"💬 测试消息: {request.messages[0].content}")
    logger.info(f"🤖 LLM 模型: {rag_settings.LLM_MODEL_NAME}")
    logger.info("\n开始测试流式响应...")
    logger.info("-" * 60)
    
    try:
        # 测试流式响应
        response_content = ""
        chunk_count = 0
        
        async for chunk in rag_client.stream_chat_completion(request):
            chunk_count += 1
            
            if chunk.type == "token":
                response_content += chunk.content
                print(chunk.content, end="", flush=True)
            elif chunk.type == "quote":
                logger.info(f"\n\n📖 引用: {chunk.quote}")
            elif chunk.type == "error":
                logger.error(f"\n\n❌ 错误: {chunk.content}")
                break
            elif chunk.type == "done":
                logger.info("\n\n✅ 流式响应完成")
                break
        
        logger.info("-" * 60)
        logger.info(f"\n📊 统计:")
        logger.info(f"  - 收到 {chunk_count} 个数据块")
        logger.info(f"  - 响应长度: {len(response_content)} 字符")
        logger.info("\n✅ RAG 服务连接成功！")
        logger.info("=" * 60)
        
        return True
    
    except Exception as e:
        logger.error(f"\n❌ RAG 服务连接失败: {e}", exc_info=True)
        logger.info("=" * 60)
        return False


async def main():
    """主函数"""
    success = await test_rag_connection()
    
    if success:
        logger.info("\n🎉 测试通过！RAG 服务可以正常使用。")
    else:
        logger.error("\n⚠️ 测试失败！请检查:")
        logger.error("  1. RAG 服务是否运行")
        logger.error("  2. 网络连接是否正常")
        logger.error("  3. 配置参数是否正确")


if __name__ == "__main__":
    asyncio.run(main())

