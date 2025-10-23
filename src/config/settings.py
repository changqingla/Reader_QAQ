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
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://10.0.169.144:5173"]
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://reader:reader_dev_password@localhost:5433/reader_qaq"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    
    # Redis
    REDIS_URL: str = "redis://:reader_dev_password@localhost:6380/0"
    
    # MinIO/S3
    MINIO_ENDPOINT: str = "localhost:8999"
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
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


