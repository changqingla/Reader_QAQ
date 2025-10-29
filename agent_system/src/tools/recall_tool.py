"""Document retrieval tool using remote HTTP API."""
import json
import requests
from typing import Dict, Any, List, Optional
from langchain.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun

from ..utils.logger import get_logger

logger = get_logger(__name__)


class RecallTool(BaseTool):
    """
    Tool for retrieving information from remote document knowledge base via HTTP API.
    
    This tool calls a remote recall service that performs vector search and optional reranking.
    """
    
    name: str = "recall"
    description: str = """从文档知识库中检索相关信息。

使用场景：
- 查找内部文档
- 检索历史记录
- 获取规范、标准文档
- 查询产品信息、技术文档等

输入：检索查询文本（query）
输出：相关文档片段
"""
    
    # API configuration
    api_url: str
    index_names: List[str]
    doc_ids: Optional[List[str]] = None
    es_host: str
    top_n: int = 10
    similarity_threshold: float = 0.2
    vector_similarity_weight: float = 0.3
    
    # Model configuration
    model_factory: str = "VLLM"
    model_name: str = "bge-m3"
    model_base_url: str
    api_key: str
    
    # Rerank configuration (optional)
    use_rerank: bool = False
    rerank_factory: Optional[str] = None
    rerank_model_name: Optional[str] = None
    rerank_base_url: Optional[str] = None
    rerank_api_key: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True
    
    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
        index_names: Optional[List[str]] = None,
        doc_ids: Optional[List[str]] = None
    ) -> str:
        """
        Execute document retrieval via HTTP API.
        
        Args:
            query: Search query
            run_manager: Callback manager for the tool run
            index_names: Optional override for index names
            doc_ids: Optional override for document IDs
            
        Returns:
            Formatted search results
        """
        try:
            # Use provided parameters or fall back to instance defaults
            final_index_names = index_names if index_names is not None else self.index_names
            final_doc_ids = doc_ids if doc_ids is not None else self.doc_ids
            
            logger.info(f"Executing recall with query: {query[:100]}...")
            logger.info(f"Using index_names: {final_index_names}")
            if final_doc_ids:
                logger.info(f"Using doc_ids: {final_doc_ids}")
            
            # Prepare request payload
            payload = {
                "question": query,
                "index_names": final_index_names,
                "es_host": self.es_host,
                "top_n": self.top_n,
                "similarity_threshold": self.similarity_threshold,
                "vector_similarity_weight": self.vector_similarity_weight,
                "model_factory": self.model_factory,
                "model_name": self.model_name,
                "model_base_url": self.model_base_url,
                "api_key": self.api_key
            }
            
            # Add optional doc_ids if provided
            if final_doc_ids:
                payload["doc_ids"] = final_doc_ids
            
            # Add rerank configuration if enabled
            if self.use_rerank and self.rerank_model_name:
                payload.update({
                    "rerank_factory": self.rerank_factory,
                    "rerank_model_name": self.rerank_model_name,
                    "rerank_base_url": self.rerank_base_url,
                    "rerank_api_key": self.rerank_api_key
                })
            
            logger.info(f"Calling recall API: {self.api_url}")
            logger.info(f"Payload: {json.dumps(payload, ensure_ascii=False, indent=2)}")
            
            # Make HTTP request
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Log full API response for debugging
            logger.info(f"Recall API full response: {json.dumps(result, ensure_ascii=False, indent=2)[:1000]}...")
            
            # Check if request was successful
            if not result.get("success"):
                error_msg = result.get("message", "Unknown error")
                logger.error(f"Recall API returned error: {error_msg}")
                logger.error(f"Full response: {result}")
                return f"检索失败: {error_msg}"
            
            # Extract chunks from response
            data = result.get("data", {})
            chunks = data.get("chunks", [])
            
            logger.info(f"Recall API response - success: {result.get('success')}, total: {data.get('total')}, chunks: {len(chunks)}")
            
            if not chunks:
                logger.error(f"❌ No chunks returned despite total={data.get('total')}")
                logger.error(f"Possible cause: All results filtered by similarity_threshold={self.similarity_threshold}")
                logger.error(f"API message: {result.get('message')}")
                
                # Show what was filtered out
                if data.get('total', 0) > 0:
                    logger.error(f"⚠️  Found {data.get('total')} results but all filtered by threshold")
                    logger.error(f"Consider: 1) Lower similarity_threshold, 2) Use more specific query, 3) Check if rerank is working")
                return "未找到相关信息。"
            
            # Format results
            formatted_results = []
            total = data.get("total", len(chunks))
            
            logger.info(f"Found {len(chunks)} chunks from total {total} results")
            
            for i, chunk in enumerate(chunks, 1):
                doc_name = chunk.get("docnm_kwd", "Unknown")
                content = chunk.get("content_with_weight", "")
                similarity = chunk.get("similarity", 0)
                page_nums = chunk.get("page_num_int", [])
                chunk_id = chunk.get("chunk_id", "")
                
                result_str = f"【文档 {i}】"
                result_str += f"\n来源：{doc_name}"
                if page_nums:
                    result_str += f" (第{page_nums[0]}页)"
                # 不显示相似度（按用户修改意图）
                result_str += f"\n内容：{content}\n"
                
                formatted_results.append(result_str)
            
            # 记录元数据
            if data.get("rerank_used"):
                logger.info(f"使用重排序模型: {data.get('rerank_model')}")
            
            logger.info(f"Recall completed successfully. Processing time: {result.get('processing_time', 0):.2f}s")
            logger.info(f"Returning {len(formatted_results)} formatted chunks")
            
            # 返回格式化的文档列表（不包含额外的装饰字符）
            return "\n".join(formatted_results)
            
        except requests.exceptions.Timeout:
            error_msg = "Recall API request timeout"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        except requests.exceptions.RequestException as e:
            error_msg = f"Recall API request failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"Error during recall: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise RuntimeError(error_msg)
    
    async def _arun(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """
        Async execute document retrieval.
        
        Args:
            query: Search query
            run_manager: Callback manager for the tool run
            
        Returns:
            Formatted search results
        """
        # For now, use synchronous version
        # In production, implement async requests with httpx
        return self._run(query, run_manager)


def create_recall_tool(
    api_url: str,
    index_names: List[str],
    es_host: str,
    model_base_url: str,
    api_key: str,
    doc_ids: Optional[List[str]] = None,
    top_n: int = 10,
    similarity_threshold: float = 0.2,
    vector_similarity_weight: float = 0.3,
    model_factory: str = "VLLM",
    model_name: str = "bge-m3",
    use_rerank: bool = False,
    rerank_factory: Optional[str] = None,
    rerank_model_name: Optional[str] = None,
    rerank_base_url: Optional[str] = None,
    rerank_api_key: Optional[str] = None
) -> RecallTool:
    """
    Factory function to create a configured RecallTool.
    
    Args:
        api_url: URL of the recall API endpoint
        index_names: List of index names to search
        es_host: Elasticsearch host URL
        model_base_url: Base URL for the embedding model
        api_key: API key for the embedding model
        doc_ids: Optional list of document IDs to filter
        top_n: Number of results to return
        similarity_threshold: Minimum similarity threshold
        vector_similarity_weight: Weight for vector similarity
        model_factory: Model factory type (default: "VLLM")
        model_name: Name of the embedding model
        use_rerank: Whether to use reranking
        rerank_factory: Rerank model factory
        rerank_model_name: Name of the rerank model
        rerank_base_url: Base URL for the rerank model
        rerank_api_key: API key for the rerank model
        
    Returns:
        Configured RecallTool instance
    """
    return RecallTool(
        api_url=api_url,
        index_names=index_names,
        doc_ids=doc_ids,
        es_host=es_host,
        top_n=top_n,
        similarity_threshold=similarity_threshold,
        vector_similarity_weight=vector_similarity_weight,
        model_factory=model_factory,
        model_name=model_name,
        model_base_url=model_base_url,
        api_key=api_key,
        use_rerank=use_rerank,
        rerank_factory=rerank_factory,
        rerank_model_name=rerank_model_name,
        rerank_base_url=rerank_base_url,
        rerank_api_key=rerank_api_key
    )
