"""Application configuration settings."""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "Reader QAQ API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_PREFIX: str = "/api"
    CORS_ORIGINS: List[str] = [
        "http://localhost:3003",
        "http://10.0.169.144:3003",
        "http://39.183.168.206:30003",  # 公网前端地址
        "*"  # 允许所有来源（生产环境建议移除）
    ]
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://reader:reader_dev_password@10.0.169.144:5433/reader_qaq"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    
    # Redis
    REDIS_URL: str = "redis://:reader_dev_password@10.0.169.144:6380/0"
    
    # MinIO/S3
    MINIO_ENDPOINT: str = "10.0.169.144:8999"  # 内网地址，用于服务器上传下载
    MINIO_PUBLIC_ENDPOINT: str = "10.0.169.144:8999"  # 开发环境直接访问；生产环境改为 "nginx"
    # MINIO_PUBLIC_ENDPOINT: str = "nginx"
    MINIO_ACCESS_KEY: str = "reader"
    MINIO_SECRET_KEY: str = "reader_dev_password"
    MINIO_BUCKET: str = "reader-uploads"
    MINIO_SECURE: bool = False
    
    # Authentication
    SECRET_KEY: str = "your-secret-key-change-in-production-please-use-random-string"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # Upload Limits
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # External Services - Document Processing
    MINERU_BASE_URL: str = "http://10.0.1.9:7788"
    DOC_PROCESS_BASE_URL: str = "http://10.0.169.144:7791"
    
    # Elasticsearch
    ES_HOST: str = "http://10.0.100.36:9201"
    
    # Embedding Model Configuration
    EMBEDDING_MODEL_FACTORY: str = "VLLM"
    EMBEDDING_MODEL_NAME: str = "bge-m3"
    EMBEDDING_BASE_URL: str = "http://10.0.1.4:8002/v1"
    EMBEDDING_API_KEY: str = ""  # Optional
    
    # Rerank Model Configuration (Optional)
    RERANK_FACTORY: str = "VLLM"
    RERANK_MODEL_NAME: str = "bge-reranker-v2-m3"
    RERANK_BASE_URL: str = "http://10.0.1.4:8001/v1"
    RERANK_API_KEY: str = ""  # Optional
    
    # Document Processing
    DEFAULT_CHUNK_TOKEN_NUM: int = 512
    DEFAULT_PARSER_TYPE: str = "general"  # general/qa/table
    
    # Search Configuration
    DEFAULT_TOP_N: int = 10
    SIMILARITY_THRESHOLD: float = 0.2
    VECTOR_SIMILARITY_WEIGHT: float = 0.3
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


