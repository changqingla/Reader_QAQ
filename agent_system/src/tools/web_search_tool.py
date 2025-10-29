"""Web search tool using Tavily API."""
from typing import Optional
from langchain.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
from tavily import TavilyClient

from ..utils.logger import get_logger

logger = get_logger(__name__)


class WebSearchTool(BaseTool):
    """
    Tool for searching information from the internet using Tavily.
    
    Tavily provides real-time web search optimized for LLM applications.
    """
    
    name: str = "web_search"
    description: str = """从互联网搜索最新信息。

使用场景：
- 获取最新资讯
- 查找公开数据
- 了解行业动态
- 获取实时信息

输入：搜索查询文本（query）
输出：搜索结果摘要
"""
    
    api_key: str
    max_results: int = 5
    
    class Config:
        arbitrary_types_allowed = True
    
    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """
        Execute web search using Tavily.
        
        Args:
            query: Search query
            run_manager: Callback manager for the tool run
            
        Returns:
            Formatted search results
        """
        try:
            logger.info(f"Executing Tavily web search with query: {query[:100]}...")
            
            # Initialize Tavily client
            client = TavilyClient(api_key=self.api_key)
            
            # Perform search
            response = client.search(
                query=query,
                max_results=self.max_results
            )
            
            if not response:
                logger.warning(f"No results found for query: {query}")
                return "未找到相关信息。"
            
            # Extract results
            results = response.get("results", [])
            
            if not results:
                logger.warning(f"No results in Tavily response for query: {query}")
                return "未找到相关信息。"
            
            # Format results
            formatted_results = []
            
            for i, result in enumerate(results, 1):
                title = result.get("title", "N/A")
                url = result.get("url", "N/A")
                content = result.get("content", "")
                score = result.get("score", 0)
                
                result_str = f"【结果 {i}】"
                result_str += f"\n标题：{title}"
                result_str += f"\n来源：{url}"
                if score:
                    result_str += f"\n相关度：{score:.4f}"
                result_str += f"\n内容：{content}\n"
                
                formatted_results.append(result_str)
            
            # Add query context if available
            answer = response.get("answer", "")
            result_text = ""
            
            if answer:
                result_text += f"\n概要回答：\n{answer}\n\n"
            
            result_text += (
                f"搜索结果 (共 {len(results)} 条)\n"
                + "="*50 + "\n"
                + "\n".join(formatted_results)
            )
            
            logger.info(f"Web search completed. Found {len(results)} results.")
            
            return result_text
            
        except Exception as e:
            error_msg = f"Error during Tavily web search: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise RuntimeError(error_msg)
    
    async def _arun(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """
        Async execute web search.
        
        Args:
            query: Search query
            run_manager: Callback manager for the tool run
            
        Returns:
            Formatted search results
        """
        # For now, use synchronous version
        # Tavily client supports async, can implement later
        return self._run(query, run_manager)


def create_web_search_tool(
    api_key: str,
    max_results: int = 5
) -> WebSearchTool:
    """
    Factory function to create a configured WebSearchTool.
    
    Args:
        api_key: Tavily API key
        max_results: Maximum number of search results to return
        
    Returns:
        Configured WebSearchTool instance
    """
    if not api_key:
        raise ValueError("Tavily API key cannot be empty")
    
    return WebSearchTool(api_key=api_key, max_results=max_results)
