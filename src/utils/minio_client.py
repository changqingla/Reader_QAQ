"""MinIO client for object storage operations."""
from minio import Minio
from minio.error import S3Error
from io import BytesIO
from typing import Optional
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

# Initialize MinIO client
minio_client = Minio(
    settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=settings.MINIO_SECURE
)


def ensure_bucket_exists():
    """Ensure the default bucket exists."""
    try:
        if not minio_client.bucket_exists(settings.MINIO_BUCKET):
            minio_client.make_bucket(settings.MINIO_BUCKET)
            logger.info(f"Created bucket: {settings.MINIO_BUCKET}")
    except S3Error as e:
        logger.error(f"Error ensuring bucket exists: {e}")
        raise


async def upload_file(object_name: str, file_data: bytes, content_type: str = "application/octet-stream") -> str:
    """
    Upload file to MinIO.
    
    Args:
        object_name: Object name in MinIO (e.g., 'kb/user_id/filename.pdf')
        file_data: File data as bytes
        content_type: MIME type of the file
    
    Returns:
        Object path in MinIO
    """
    try:
        ensure_bucket_exists()
        
        file_stream = BytesIO(file_data)
        file_size = len(file_data)
        
        minio_client.put_object(
            settings.MINIO_BUCKET,
            object_name,
            file_stream,
            file_size,
            content_type=content_type
        )
        
        logger.info(f"Uploaded file: {object_name} ({file_size} bytes)")
        return f"{settings.MINIO_BUCKET}/{object_name}"
    
    except S3Error as e:
        logger.error(f"Error uploading file {object_name}: {e}")
        raise Exception(f"Failed to upload file: {e}")


async def download_file(object_name: str) -> bytes:
    """
    Download file from MinIO.
    
    Args:
        object_name: Object name in MinIO
    
    Returns:
        File data as bytes
    """
    try:
        response = minio_client.get_object(settings.MINIO_BUCKET, object_name)
        data = response.read()
        response.close()
        response.release_conn()
        return data
    
    except S3Error as e:
        logger.error(f"Error downloading file {object_name}: {e}")
        raise Exception(f"Failed to download file: {e}")


async def delete_file(object_name: str):
    """
    Delete file from MinIO.
    
    Args:
        object_name: Object name in MinIO
    """
    try:
        minio_client.remove_object(settings.MINIO_BUCKET, object_name)
        logger.info(f"Deleted file: {object_name}")
    
    except S3Error as e:
        logger.error(f"Error deleting file {object_name}: {e}")
        raise Exception(f"Failed to delete file: {e}")


def get_file_url(object_name: str, expires_seconds: int = 3600) -> str:
    """
    Get presigned URL for file access.
    
    Args:
        object_name: Object name in MinIO
        expires_seconds: URL expiration time in seconds
    
    Returns:
        Presigned URL
    """
    try:
        url = minio_client.presigned_get_object(
            settings.MINIO_BUCKET,
            object_name,
            expires=expires_seconds
        )
        return url
    
    except S3Error as e:
        logger.error(f"Error generating presigned URL for {object_name}: {e}")
        raise Exception(f"Failed to generate URL: {e}")

