"""
RAG 服务配置
"""
from pydantic_settings import BaseSettings


class RAGSettings(BaseSettings):
    """RAG 服务配置"""
    
    # RAG 服务地址
    RAG_SERVICE_URL: str = "http://10.0.169.144:7792"
    
    # RAG 服务认证
    RAG_AGENT_AUTHORIZATION: str = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJTZXJ2aWNlSWQiOiJhZ2VudCIsIlNlcnZpY2VTZWNyZXQiOiJ1Wng1YXoxdyIsIlVzZXJJZCI6NDU2LCJleHAiOjE3NjIwNTA5MDUsImlhdCI6MTc2MTQ0NjEwNX0.rXD5ZaKOB_M4XVi-NKQtxaBeuRFeZZrIFQXJjHBPmYg"
    
    # LLM 配置
    LLM_MODEL_NAME: str = "qwen3-next-80b-a3b-instruct"
    LLM_MODEL_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    LLM_API_KEY: str = "sk-b87f72df32b34dd9a97b73477ef00738"
    LLM_TEMPERATURE: float = 0.7
    LLM_TOP_P: float = 0.3
    LLM_MAX_TOKENS: int = 1000
    
    # Recall 配置
    RECALL_TOP_N: int = 40
    RECALL_SIMILARITY_THRESHOLD: float = 0.01
    RECALL_VECTOR_SIMILARITY_WEIGHT: float = 0.3
    RECALL_TOP_K: int = 1024
    
    # Embedding 模型配置
    EMBED_MODEL_FACTORY: str = "Tongyi-Qianwen"
    EMBED_MODEL_NAME: str = "text-embedding-v4"
    EMBED_MODEL_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    EMBED_MODEL_API_KEY: str = "sk-8dd3264e37d3474398f8ea5dc586cd8a"
    
    # Rerank 模型配置
    RERANK_FACTORY: str = "openai"
    RERANK_MODEL_NAME: str = "bge-reranker-v2-m3"
    RERANK_BASE_URL: str = "http://10.0.1.4:8001/v1"
    RERANK_API_KEY: str = "sk-8dd3264e37d3474398f8ea5dc586cd8a"
    
    # ElasticSearch 配置
    ES_HOST: str = "http://10.0.100.36:9202"
    
    # Thinking 配置
    THINKING_MAX_SUB_QUESTIONS: int = 4
    THINKING_MAX_ITERATIONS: int = 2
    THINKING_ENABLE_QUESTION_REFINEMENT: bool = True
    
    # Tavily 配置
    TAVILY_API_KEY: str = "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"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 全局配置实例
rag_settings = RAGSettings()

