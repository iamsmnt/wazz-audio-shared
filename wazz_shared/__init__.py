"""
Wazz Audio Shared Library

This package contains shared code used by both the API service and Worker service.
"""

__version__ = "1.0.0"

# Import commonly used components for easier access
from .config import SharedSettings, get_shared_settings
from .database import Base, get_db, SessionLocal, engine
from .models import User, AudioProcessingJob, GuestSession, UserUsageStats, TokenBlacklist
from . import usage_tracking

__all__ = [
    "SharedSettings",
    "get_shared_settings",
    "Base",
    "get_db",
    "SessionLocal",
    "engine",
    "User",
    "AudioProcessingJob",
    "GuestSession",
    "UserUsageStats",
    "TokenBlacklist",
    "usage_tracking",
]
