"""Application configuration."""

import os
from typing import Optional


class Settings:
    """Application settings."""
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./data/usage_revenue.db"
    )
    
    # External Services
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_ORG_ID: Optional[str] = os.getenv("OPENAI_ORG_ID")
    STRIPE_API_KEY: Optional[str] = os.getenv("STRIPE_API_KEY")
    
    # Scheduler
    SYNC_INTERVAL_HOURS: int = int(os.getenv("SYNC_INTERVAL_HOURS", "1"))
    AGGREGATION_HOUR: int = int(os.getenv("AGGREGATION_HOUR", "2"))  # 2 AM
    INSIGHT_INTERVAL_HOURS: int = int(os.getenv("INSIGHT_INTERVAL_HOURS", "6"))
    
    # API
    API_VERSION: str = "2.0.0"
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:3001",
    ]
    
    # Feature Flags
    USE_DATABASE: bool = os.getenv("USE_DATABASE", "true").lower() == "true"
    ENABLE_SCHEDULER: bool = os.getenv("ENABLE_SCHEDULER", "true").lower() == "true"
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "false").lower() == "true"


settings = Settings()
