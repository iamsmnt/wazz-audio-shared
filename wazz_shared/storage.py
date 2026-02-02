"""
Unified storage client for both local filesystem and S3/MinIO

This module provides a single interface that works with either:
- Local filesystem storage (for development/testing)
- S3/MinIO object storage (for production)

Toggle between them using the use_local_storage setting in config.
"""

import os
import shutil
from typing import BinaryIO, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class StorageClient:
    """
    Unified storage interface supporting both local filesystem and S3/MinIO

    Usage:
        storage = StorageClient(settings)
        storage.upload_file('/path/to/file.wav', 'uploads/file.wav')
        storage.download_file('uploads/file.wav', '/path/to/destination.wav')
        url = storage.get_file_url('uploads/file.wav')
    """

    def __init__(self, settings):
        """
        Initialize storage client

        Args:
            settings: SharedSettings instance
        """
        self.settings = settings
        self.use_local = settings.use_local_storage

        if self.use_local:
            # Local filesystem mode
            self.base_path = Path("./storage")
            self.base_path.mkdir(exist_ok=True)
            logger.info(f"Storage: Using LOCAL filesystem at {self.base_path}")
        else:
            # S3/MinIO mode
            try:
                import boto3
                from botocore.client import Config
                from botocore.exceptions import ClientError

                self.s3_client = boto3.client(
                    's3',
                    endpoint_url=settings.s3_endpoint_url,
                    aws_access_key_id=settings.s3_access_key,
                    aws_secret_access_key=settings.s3_secret_key,
                    region_name=settings.s3_region,
                    config=Config(signature_version='s3v4'),
                    use_ssl=settings.s3_use_ssl
                )
                self.bucket = settings.s3_bucket_name

                # Create bucket if not exists
                try:
                    self.s3_client.head_bucket(Bucket=self.bucket)
                    logger.info(f"Storage: Using S3/MinIO bucket '{self.bucket}'")
                except ClientError:
                    try:
                        self.s3_client.create_bucket(Bucket=self.bucket)
                        logger.info(f"Storage: Created S3/MinIO bucket '{self.bucket}'")
                    except ClientError as e:
                        logger.error(f"Failed to create bucket: {e}")
                        raise

            except ImportError:
                raise ImportError(
                    "boto3 is required for S3 storage. "
                    "Install it with: pip install boto3"
                )

    def upload_file(self, file_path: str, object_key: str) -> None:
        """
        Upload file to storage

        Args:
            file_path: Local path to file
            object_key: Storage key/path (e.g., 'uploads/file.wav')

        Raises:
            FileNotFoundError: If source file doesn't exist
            Exception: If upload fails
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Source file not found: {file_path}")

        if self.use_local:
            # Local filesystem: copy file
            dest_path = self.base_path / object_key
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, dest_path)
            logger.debug(f"Uploaded to local storage: {object_key}")
        else:
            # S3/MinIO: upload file
            self.s3_client.upload_file(file_path, self.bucket, object_key)
            logger.debug(f"Uploaded to S3: {object_key}")

    def upload_fileobj(self, file_obj: BinaryIO, object_key: str) -> None:
        """
        Upload file-like object to storage

        Args:
            file_obj: File-like object (must support read())
            object_key: Storage key/path

        Raises:
            Exception: If upload fails
        """
        if self.use_local:
            # Local filesystem: write from file object
            dest_path = self.base_path / object_key
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            with open(dest_path, 'wb') as f:
                shutil.copyfileobj(file_obj, f)
            logger.debug(f"Uploaded to local storage: {object_key}")
        else:
            # S3/MinIO: upload file object
            self.s3_client.upload_fileobj(file_obj, self.bucket, object_key)
            logger.debug(f"Uploaded to S3: {object_key}")

    def download_file(self, object_key: str, file_path: str) -> None:
        """
        Download file from storage

        Args:
            object_key: Storage key/path
            file_path: Local destination path

        Raises:
            FileNotFoundError: If object doesn't exist
            Exception: If download fails
        """
        if self.use_local:
            # Local filesystem: copy file
            src_path = self.base_path / object_key
            if not src_path.exists():
                raise FileNotFoundError(f"Object not found: {object_key}")

            # Create destination directory
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            shutil.copy2(src_path, file_path)
            logger.debug(f"Downloaded from local storage: {object_key}")
        else:
            # S3/MinIO: download file
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            self.s3_client.download_file(self.bucket, object_key, file_path)
            logger.debug(f"Downloaded from S3: {object_key}")

    def get_file_url(self, object_key: str, expiration: int = 3600) -> str:
        """
        Generate URL for file access

        Args:
            object_key: Storage key/path
            expiration: URL expiration time in seconds (for S3 presigned URLs)

        Returns:
            File URL (presigned for S3, local path for filesystem)

        Note:
            For local storage, returns a file:// URL or path.
            For production, you'd typically serve files through a web server.
        """
        if self.use_local:
            # Local filesystem: return file path
            # In production, you'd map this to a web-accessible URL
            file_path = self.base_path / object_key
            return f"file://{file_path.absolute()}"
        else:
            # S3/MinIO: generate presigned URL
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': object_key},
                ExpiresIn=expiration
            )
            return url

    def delete_file(self, object_key: str) -> None:
        """
        Delete file from storage

        Args:
            object_key: Storage key/path

        Raises:
            Exception: If deletion fails
        """
        if self.use_local:
            # Local filesystem: delete file
            file_path = self.base_path / object_key
            if file_path.exists():
                file_path.unlink()
                logger.debug(f"Deleted from local storage: {object_key}")
            else:
                logger.warning(f"File not found for deletion: {object_key}")
        else:
            # S3/MinIO: delete object
            try:
                self.s3_client.delete_object(Bucket=self.bucket, Key=object_key)
                logger.debug(f"Deleted from S3: {object_key}")
            except Exception as e:
                logger.error(f"Failed to delete from S3: {e}")
                raise

    def file_exists(self, object_key: str) -> bool:
        """
        Check if file exists in storage

        Args:
            object_key: Storage key/path

        Returns:
            True if file exists, False otherwise
        """
        if self.use_local:
            # Local filesystem: check file existence
            file_path = self.base_path / object_key
            return file_path.exists()
        else:
            # S3/MinIO: check object existence
            try:
                self.s3_client.head_object(Bucket=self.bucket, Key=object_key)
                return True
            except:
                return False

    def get_file_size(self, object_key: str) -> int:
        """
        Get file size in bytes

        Args:
            object_key: Storage key/path

        Returns:
            File size in bytes

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        if self.use_local:
            # Local filesystem: get file size
            file_path = self.base_path / object_key
            if not file_path.exists():
                raise FileNotFoundError(f"Object not found: {object_key}")
            return file_path.stat().st_size
        else:
            # S3/MinIO: get object size
            response = self.s3_client.head_object(Bucket=self.bucket, Key=object_key)
            return response['ContentLength']

    def list_files(self, prefix: str = "") -> list:
        """
        List files in storage with given prefix

        Args:
            prefix: Key prefix to filter (e.g., 'uploads/')

        Returns:
            List of object keys
        """
        if self.use_local:
            # Local filesystem: list files
            search_path = self.base_path / prefix
            if not search_path.exists():
                return []

            files = []
            for item in search_path.rglob('*'):
                if item.is_file():
                    # Get relative path from base_path
                    rel_path = item.relative_to(self.base_path)
                    files.append(str(rel_path))
            return files
        else:
            # S3/MinIO: list objects
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket,
                Prefix=prefix
            )
            if 'Contents' not in response:
                return []
            return [obj['Key'] for obj in response['Contents']]


def get_storage_client(settings=None):
    """
    Get storage client instance

    Args:
        settings: Optional SharedSettings instance. If not provided, will create one.

    Returns:
        StorageClient instance
    """
    if settings is None:
        from .config import get_shared_settings
        settings = get_shared_settings()

    return StorageClient(settings)
