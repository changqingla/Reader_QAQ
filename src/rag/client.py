"""
RAG 服务客户端
"""
import httpx
import logging
from typing import AsyncGenerator
from .config import rag_settings
from .schemas import RAGChatRequest, StreamChunk

logger = logging.getLogger(__name__)


class RAGClient:
    """RAG 服务客户端"""
    
    def __init__(self):
        self.base_url = rag_settings.RAG_SERVICE_URL
        self.auth_header = {
            "AgentAuthorization": rag_settings.RAG_AGENT_AUTHORIZATION
        }
    
    async def stream_chat_completion(
        self,
        request: RAGChatRequest
    ) -> AsyncGenerator[StreamChunk, None]:
        """
        流式聊天完成
        
        Args:
            request: RAG 聊天请求
            
        Yields:
            StreamChunk: 流式响应块
        """
        url = f"{self.base_url}/conversation"
        
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                async with client.stream(
                    "POST",
                    url,
                    json=request.model_dump(),
                    headers={
                        **self.auth_header,
                        "Content-Type": "application/json"
                    }
                ) as response:
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        if not line.strip():
                            continue
                        
                        # SSE 格式: data: {...}
                        if line.startswith("data: "):
                            data = line[6:]  # 去掉 "data: "
                            
                            if data == "[DONE]":
                                yield StreamChunk(type="done", content="")
                                break
                            
                            try:
                                # 解析 JSON
                                import json
                                chunk_data = json.loads(data)
                                
                                # 转换外部服务格式到 StreamChunk 格式
                                # 外部服务格式: {"event": "...", "data": {...}}
                                # 我们的格式: {"type": "...", "content": "..."}
                                event = chunk_data.get("event", "")
                                event_data = chunk_data.get("data", {})
                                
                                if event == "start":
                                    # 开始事件，跳过
                                    continue
                                elif event == "recalling":
                                    # 正在召回知识，跳过
                                    continue
                                elif event == "recall_complete":
                                    # 召回完成，跳过
                                    continue
                                elif event == "generating":
                                    # 正在生成回答，跳过
                                    continue
                                elif event == "content_chunk":
                                    # 内容块事件，包含生成的文本
                                    yield StreamChunk(
                                        type="token",
                                        content=event_data.get("content", "")
                                    )
                                elif event == "complete":
                                    # 完成事件，包含引用信息
                                    retrieved_chunks = event_data.get("retrieved_chunks", {})
                                    
                                    # 将检索到的chunks转换为quote格式
                                    for chunk_id, chunk_info in retrieved_chunks.items():
                                        quote_data = {
                                            "source": chunk_info.get("document_name", ""),
                                            "content": chunk_info.get("content", "")[:200] + "...",  # 截断太长的内容
                                            "url": chunk_info.get("url", "")
                                        }
                                        yield StreamChunk(
                                            type="quote",
                                            content="",
                                            quote=quote_data
                                        )
                                    
                                    # 发送完成标记
                                    yield StreamChunk(
                                        type="done",
                                        content=""
                                    )
                                elif event == "error":
                                    # 错误事件
                                    yield StreamChunk(
                                        type="error",
                                        content=event_data.get("message", "Unknown error")
                                    )
                                else:
                                    # 其他未知事件类型，记录日志
                                    logger.debug(f"Unknown event type: {event}, data: {event_data}")
                                    
                            except json.JSONDecodeError as e:
                                logger.warning(f"Failed to parse chunk: {data}, error: {e}")
                                continue
        
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e}")
            yield StreamChunk(
                type="error",
                content=f"RAG service error: {e.response.status_code}"
            )
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            yield StreamChunk(
                type="error",
                content=f"Failed to connect to RAG service: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            yield StreamChunk(
                type="error",
                content=f"Unexpected error: {str(e)}"
            )
    
    async def chat_completion(
        self,
        request: RAGChatRequest
    ) -> dict:
        """
        非流式聊天完成（用于测试）
        
        Args:
            request: RAG 聊天请求
            
        Returns:
            dict: 响应数据
        """
        url = f"{self.base_url}/conversation"
        
        # 修改为非流式
        request_dict = request.model_dump()
        request_dict["stream"] = False
        
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.post(
                    url,
                    json=request_dict,
                    headers={
                        **self.auth_header,
                        "Content-Type": "application/json"
                    }
                )
                response.raise_for_status()
                return response.json()
        
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e}")
            raise Exception(f"RAG service error: {e.response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise Exception(f"Failed to connect to RAG service: {str(e)}")


# 全局客户端实例
rag_client = RAGClient()

