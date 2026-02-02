"""Shared configuration settings for all Wazz Audio services"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class SharedSettings(BaseSettings):
    """
    Shared settings used by both API service and Worker service

    These settings can be overridden via environment variables or .env file
    """

    # =========================================================================
    # Application Settings
    # =========================================================================
    app_name: str = "Whazz Audio"
    debug: bool = True
    environment: str = "development"  # development, staging, production

    # =========================================================================
    # Database Settings - PostgreSQL
    # =========================================================================
    database_url: str = "postgresql://postgres:postgres@localhost:5432/whazz_audio"

    # Alternative: Individual PostgreSQL settings
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "whazz_audio"

    # =========================================================================
    # Message Broker Settings - RabbitMQ
    # =========================================================================
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672//"
    rabbitmq_host: str = "localhost"
    rabbitmq_port: int = 5672
    rabbitmq_user: str = "guest"
    rabbitmq_password: str = "guest"
    rabbitmq_vhost: str = "/"

    # Celery settings
    celery_broker_url: str = "amqp://guest:guest@localhost:5672//"
    celery_result_backend: str = "db+postgresql://postgres:postgres@localhost:5432/whazz_audio"

    # =========================================================================
    # Object Storage Settings - S3/MinIO
    # =========================================================================
    # Set use_local_storage=True to use local filesystem instead of S3/MinIO
    use_local_storage: bool = True  # Toggle between local and S3 storage

    # S3/MinIO configuration
    s3_endpoint_url: str = "http://localhost:9000"  # MinIO endpoint
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_bucket_name: str = "wazz-audio"
    s3_region: str = "us-east-1"
    s3_use_ssl: bool = False  # Set True for production S3

    # For AWS S3, set s3_endpoint_url to None and configure:
    # s3_endpoint_url: str = None  # Uses default AWS S3
    # s3_access_key: str = "YOUR_AWS_ACCESS_KEY"
    # s3_secret_key: str = "YOUR_AWS_SECRET_KEY"
    # s3_region: str = "us-east-1"
    # s3_use_ssl: bool = True

    # =========================================================================
    # File Storage Settings
    # =========================================================================
    # Local storage paths (used when use_local_storage=True)
    upload_dir: str = "./uploads"
    output_dir: str = "./processed_audio"

    # File validation
    max_file_size_mb: int = 100
    allowed_audio_formats: List[str] = [".wav", ".mp3", ".flac", ".m4a", ".ogg"]
    file_expiry_hours: int = 24  # Auto-delete files after 24 hours

    # =========================================================================
    # Audio Processing Settings
    # =========================================================================
    clearvoice_model_name: str = "MossFormer2_SE_48K"
    processing_timeout_seconds: int = 3600  # 1 hour max

    # Worker settings
    worker_concurrency: int = 2  # Number of concurrent tasks per worker
    worker_max_tasks_per_child: int = 10  # Restart worker after N tasks (prevent memory leaks)

    # =========================================================================
    # Security Settings (API Service specific, but shared for consistency)
    # =========================================================================
    secret_key: str = "94fb8603af544370a40ab4eac0de704715d6c688d51e7a60960f1c276975bb81"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # =========================================================================
    # CORS Settings (API Service specific)
    # =========================================================================
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:5173",
    ]

    # =========================================================================
    # Email Settings (API Service specific)
    # =========================================================================
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_use_tls: bool = True
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""
    frontend_url: str = "http://localhost:5173"
    require_email_verification: bool = True

    # =========================================================================
    # Logging Settings
    # =========================================================================
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    log_format: str = "json"  # json or text

    class Config:
        env_file = ".env"
        case_sensitive = False
        env_prefix = ""  # No prefix for environment variables


@lru_cache()
def get_shared_settings() -> SharedSettings:
    """
    Get cached settings instance

    This function is cached to ensure only one settings instance is created
    and reused across the application.

    Returns:
        SharedSettings: The cached settings instance
    """
    return SharedSettings()
