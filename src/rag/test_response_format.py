"""
测试 RAG 服务的响应格式
分别测试深度思考模式和联网搜索模式
"""
import asyncio
import logging
import json
import httpx
from .config import rag_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_deep_thinking_mode():
    """测试深度思考模式的响应格式"""
    
    logger.info("\n" + "=" * 80)
    logger.info("测试 1: 深度思考模式 (thinking=true)")
    logger.info("=" * 80)
    
    url = f"{rag_settings.RAG_SERVICE_URL}/conversation"
    
    request_data = {
        "mode": "chat",
        "session_id": "test-deep-001",
        "messages": [
            {"role": "user", "content": "介绍一下杭州"}
        ],
        "llm": {
            "model_name": rag_settings.LLM_MODEL_NAME,
            "model_url": rag_settings.LLM_MODEL_URL,
            "api_key": rag_settings.LLM_API_KEY,
            "temperature": 0.7,
            "top_p": 0.3,
            "max_tokens": 500
        },
        "recall": {
            "index_names": ["test-index"],
            "es_host": rag_settings.ES_HOST,
            "top_n": 8,
            "similarity_threshold": 0.2,
            "vector_similarity_weight": 0.3,
            "top_k": 1024,
            "model_factory": rag_settings.EMBED_MODEL_FACTORY,
            "model_name": rag_settings.EMBED_MODEL_NAME,
            "model_base_url": rag_settings.EMBED_MODEL_BASE_URL,
            "model_api_key": rag_settings.EMBED_MODEL_API_KEY,
            "rerank_factory": rag_settings.RERANK_FACTORY,
            "rerank_model_name": rag_settings.RERANK_MODEL_NAME,
            "rerank_base_url": rag_settings.RERANK_BASE_URL,
            "rerank_api_key": rag_settings.RERANK_API_KEY
        },
        "thinking": {
            "max_sub_questions": 4,
            "max_iterations": 2,
            "enable_question_refinement": True
        },
        "knowledge_base": True,
        "tavily": False,
        "show_quote": True,
        "stream": True
    }
    
    logger.info(f"\n📡 请求 URL: {url}")
    logger.info(f"💭 深度思考: 启用")
    logger.info("\n开始接收响应...\n")
    logger.info("-" * 80)
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                url,
                json=request_data,
                headers={
                    "AgentAuthorization": f"Bearer {rag_settings.RAG_AGENT_AUTHORIZATION.replace('Bearer ', '')}",
                    "Content-Type": "application/json"
                }
            ) as response:
                response.raise_for_status()
                
                chunk_count = 0
                async for line in response.aiter_lines():
                    if not line.strip() or not line.startswith("data: "):
                        continue
                    
                    data = line[6:]  # Remove "data: " prefix
                    
                    if data == "[DONE]":
                        logger.info("\n\n✅ 收到 [DONE] 标记")
                        break
                    
                    try:
                        chunk_data = json.loads(data)
                        chunk_count += 1
                        
                        # 打印原始响应格式
                        logger.info(f"\n📦 Chunk {chunk_count}:")
                        logger.info(f"   原始数据: {json.dumps(chunk_data, ensure_ascii=False, indent=2)}")
                        
                    except json.JSONDecodeError as e:
                        logger.warning(f"无法解析 JSON: {data}")
                
                logger.info(f"\n\n📊 总共收到 {chunk_count} 个数据块")
                
    except Exception as e:
        logger.error(f"\n❌ 错误: {e}", exc_info=True)


async def test_search_mode():
    """测试联网搜索模式的响应格式"""
    
    logger.info("\n\n" + "=" * 80)
    logger.info("测试 2: 联网搜索模式 (tavily=true)")
    logger.info("=" * 80)
    
    url = f"{rag_settings.RAG_SERVICE_URL}/conversation"
    
    request_data = {
        "mode": "search",
        "session_id": "test-search-001",
        "messages": [
            {"role": "user", "content": "今天的天气怎么样"}
        ],
        "llm": {
            "model_name": rag_settings.LLM_MODEL_NAME,
            "model_url": rag_settings.LLM_MODEL_URL,
            "api_key": rag_settings.LLM_API_KEY,
            "temperature": 0.7,
            "top_p": 0.3,
            "max_tokens": 500
        },
        "recall": {
            "index_names": ["test-index"],
            "es_host": rag_settings.ES_HOST,
            "top_n": 8,
            "similarity_threshold": 0.2,
            "vector_similarity_weight": 0.3,
            "top_k": 1024,
            "model_factory": rag_settings.EMBED_MODEL_FACTORY,
            "model_name": rag_settings.EMBED_MODEL_NAME,
            "model_base_url": rag_settings.EMBED_MODEL_BASE_URL,
            "model_api_key": rag_settings.EMBED_MODEL_API_KEY,
            "rerank_factory": rag_settings.RERANK_FACTORY,
            "rerank_model_name": rag_settings.RERANK_MODEL_NAME,
            "rerank_base_url": rag_settings.RERANK_BASE_URL,
            "rerank_api_key": rag_settings.RERANK_API_KEY
        },
        "thinking": {
            "max_sub_questions": 4,
            "max_iterations": 2,
            "enable_question_refinement": True
        },
        "knowledge_base": False,
        "tavily": True,
        "tavily_api_key": rag_settings.TAVILY_API_KEY,
        "show_quote": True,
        "stream": True
    }
    
    logger.info(f"\n📡 请求 URL: {url}")
    logger.info(f"🔍 联网搜索: 启用")
    logger.info("\n开始接收响应...\n")
    logger.info("-" * 80)
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                url,
                json=request_data,
                headers={
                    "AgentAuthorization": f"Bearer {rag_settings.RAG_AGENT_AUTHORIZATION.replace('Bearer ', '')}",
                    "Content-Type": "application/json"
                }
            ) as response:
                response.raise_for_status()
                
                chunk_count = 0
                async for line in response.aiter_lines():
                    if not line.strip() or not line.startswith("data: "):
                        continue
                    
                    data = line[6:]  # Remove "data: " prefix
                    
                    if data == "[DONE]":
                        logger.info("\n\n✅ 收到 [DONE] 标记")
                        break
                    
                    try:
                        chunk_data = json.loads(data)
                        chunk_count += 1
                        
                        # 打印原始响应格式
                        logger.info(f"\n📦 Chunk {chunk_count}:")
                        logger.info(f"   原始数据: {json.dumps(chunk_data, ensure_ascii=False, indent=2)}")
                        
                    except json.JSONDecodeError as e:
                        logger.warning(f"无法解析 JSON: {data}")
                
                logger.info(f"\n\n📊 总共收到 {chunk_count} 个数据块")
                
    except Exception as e:
        logger.error(f"\n❌ 错误: {e}", exc_info=True)


async def main():
    """主函数"""
    
    logger.info("\n🧪 开始测试 RAG 服务响应格式")
    logger.info(f"📡 服务地址: {rag_settings.RAG_SERVICE_URL}")
    
    # 测试深度思考模式
    await test_deep_thinking_mode()
    
    # 等待一下
    await asyncio.sleep(2)
    
    # 测试联网搜索模式
    await test_search_mode()
    
    logger.info("\n\n" + "=" * 80)
    logger.info("✅ 测试完成！请查看上面的响应格式")
    logger.info("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())

