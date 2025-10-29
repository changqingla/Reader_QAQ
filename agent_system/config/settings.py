"""Application settings and configuration."""
from functools import lru_cache
from typing import Dict, Any

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        protected_namespaces=()  # Disable protected namespace warning
    )
    
    # ========== LLM 配置 (统一) ==========
    openai_api_key: str
    openai_api_base: str = "https://api.openai.com/v1"
    model_name: str = "Qwen/Qwen3-30B-A3B-Instruct-2507"  # 统一模型：Agent推理 + Token计算
    temperature: float = 0.3  # 统一温度：Agent推理 + 压缩摘要
    
    # ========== 上下文和 Token 管理 ==========
    max_context_tokens: int = 128000  # 模型最大上下文窗口
    direct_content_threshold: float = 0.7  # 直接内容模式阈值：文档大小 < 70% 可用tokens时直接使用
    
    # ========== Agent 配置 ==========
    enable_web_search: bool = False
    max_replan_attempts: int = 2
    execution_timeout: int = 300
    
    # Recall API Configuration
    recall_api_url: str = "http://localhost:9003/api/recall"
    recall_index_names: str = "deeprag_vectors"  # Comma-separated
    recall_doc_ids: str = ""  # Comma-separated, optional
    recall_es_host: str = "http://localhost:9200"
    recall_top_n: int = 10
    recall_similarity_threshold: float = 0.2
    recall_vector_similarity_weight: float = 0.3
    
    # Recall Model Configuration
    recall_model_factory: str = "VLLM"
    recall_model_name: str = "bge-m3"
    recall_model_base_url: str = "http://localhost:8002/v1"
    recall_api_key: str = "sk-your-api-key"
    
    # Recall Rerank Configuration (Optional)
    recall_use_rerank: bool = False
    recall_rerank_factory: str = "VLLM"
    recall_rerank_model_name: str = "bge-reranker-v2-m3"
    recall_rerank_base_url: str = "http://localhost:8001/v1"
    recall_rerank_api_key: str = "your_api_key"
    
    # Tavily Web Search Configuration
    tavily_api_key: str = ""
    tavily_max_results: int = 5
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "./logs/agent.log"
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # ========== 上下文压缩配置 ==========
    compression_threshold_ratio: float = 0.8  # 达到80%上下文时触发压缩
    compression_preserve_ratio: float = 0.3  # 保留最近30%的消息不压缩
    
    # ========== 时间窗口注入配置 ==========
    intent_recognition_turns: int = 2
    planning_turns: int = 2
    answer_generation_turns: int = 3
    execution_turns: int = 0
    
    # ========== Redis 配置（使用 Reader 项目的 Redis）==========
    redis_host: str = "localhost"
    redis_port: int = 6380  # Reader 项目的 Redis 端口
    redis_db: int = 1  # 使用 DB 1，避免与 Reader 项目的 DB 0 冲突
    redis_username: str = ""
    redis_password: str = "reader_dev_password"  # Reader 项目的 Redis 密码
    redis_socket_timeout: int = 5
    redis_socket_connect_timeout: int = 5
    session_cache_ttl: int = 3600
    message_cache_ttl: int = 1800
    
    # ========== PostgreSQL 配置（使用 Reader 项目的数据库）==========
    postgres_host: str = "localhost"
    postgres_port: int = 5433  # Reader 项目的 PostgreSQL 端口
    postgres_db: str = "reader_qaq"  # Reader 项目的数据库名
    postgres_user: str = "reader"  # Reader 项目的用户名
    postgres_password: str = "reader_dev_password"  # Reader 项目的密码
    postgres_pool_size: int = 10
    postgres_max_overflow: int = 20
    
    # ========== 性能配置 ==========
    batch_size: int = 100
    enable_cache: bool = True
    cache_read_timeout: int = 2
    
    def validate_required_fields(self) -> None:
        """Validate that all required fields are set."""
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY must be set in environment variables")
        if not self.recall_api_url:
            raise ValueError("RECALL_API_URL must be set in environment variables")
        if not self.recall_api_key:
            raise ValueError("RECALL_API_KEY must be set in environment variables")
    
    def get_recall_index_names(self) -> list:
        """Parse comma-separated index names."""
        if not self.recall_index_names:
            return []
        return [name.strip() for name in self.recall_index_names.split(",")]
    
    def get_recall_doc_ids(self) -> list:
        """Parse doc IDs - supports both JSON array and comma-separated string."""
        if not self.recall_doc_ids:
            return None
        
        # Try to parse as JSON first
        import json
        if self.recall_doc_ids.strip().startswith('['):
            try:
                return json.loads(self.recall_doc_ids)
            except json.JSONDecodeError:
                pass
        
        # Fallback to comma-separated
        return [doc_id.strip() for doc_id in self.recall_doc_ids.split(",")]
    
    # ========== 计算属性 ==========
    
    @property
    def compression_threshold_tokens(self) -> int:
        """计算压缩触发的绝对token阈值"""
        return int(self.max_context_tokens * self.compression_threshold_ratio)
    
    @property
    def redis_url(self) -> str:
        """获取Redis连接URL"""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    @property
    def postgres_url(self) -> str:
        """获取PostgreSQL连接URL"""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
    
    @property
    def injection_strategy(self) -> Dict[str, Dict[str, Any]]:
        """获取注入策略配置"""
        return {
            "intent_recognition": {
                "turn_count": self.intent_recognition_turns,
                "include_compression": True
            },
            "planning": {
                "turn_count": self.planning_turns,
                "include_compression": True
            },
            "execution": {
                "turn_count": self.execution_turns,
                "include_compression": False
            },
            "answer_generation": {
                "turn_count": self.answer_generation_turns,
                "include_compression": True
            }
        }


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    settings = Settings()
    settings.validate_required_fields()
    return settings

