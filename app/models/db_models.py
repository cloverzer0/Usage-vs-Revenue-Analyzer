"""Database models for the normalization and correlation layer."""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Index, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base


class User(Base):
    """User model for authentication."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Customer(Base):
    """Customer entity - maps usage + revenue to the same entity."""
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    external_customer_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    plan = Column(String, nullable=True)
    environment = Column(String, default="production")  # production, staging
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    usage_events = relationship("UsageEvent", back_populates="customer")
    revenue_events = relationship("RevenueEvent", back_populates="customer")
    daily_aggregates = relationship("DailyAggregate", back_populates="customer")
    insight_flags = relationship("InsightFlag", back_populates="customer")


class UsageEvent(Base):
    """Aggregatable usage data from various sources."""
    __tablename__ = "usage_events"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    feature = Column(String, nullable=False, index=True)
    quantity = Column(Float, nullable=False)
    unit_cost = Column(Float, default=0.0)  # Cost per unit
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    source = Column(String, default="api")  # api, webhook, prometheus, etc.
    extra_data = Column(String, nullable=True)  # JSON string for extra data

    # Relationships
    customer = relationship("Customer", back_populates="usage_events")

    __table_args__ = (
        Index('idx_usage_customer_timestamp', 'customer_id', 'timestamp'),
        Index('idx_usage_feature_timestamp', 'feature', 'timestamp'),
    )


class EventType(enum.Enum):
    """Revenue event types."""
    INVOICE = "invoice"
    CHARGE = "charge"
    REFUND = "refund"
    SUBSCRIPTION = "subscription"
    PAYMENT = "payment"


class RevenueEvent(Base):
    """Stripe-derived revenue truth."""
    __tablename__ = "revenue_events"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="usd")
    event_type = Column(Enum(EventType), nullable=False, index=True)
    external_id = Column(String, unique=True, index=True)  # Stripe ID for idempotency
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    extra_data = Column(String, nullable=True)  # JSON string for extra data

    # Relationships
    customer = relationship("Customer", back_populates="revenue_events")

    __table_args__ = (
        Index('idx_revenue_customer_timestamp', 'customer_id', 'timestamp'),
    )


class DailyAggregate(Base):
    """Pre-computed daily aggregates for efficient chart rendering."""
    __tablename__ = "daily_aggregates"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True, index=True)
    feature = Column(String, nullable=True, index=True)
    
    # Aggregated metrics
    usage_total = Column(Float, default=0.0)
    usage_count = Column(Integer, default=0)
    revenue_total = Column(Float, default=0.0)
    cost_total = Column(Float, default=0.0)
    
    # Relationships
    customer = relationship("Customer", back_populates="daily_aggregates")

    __table_args__ = (
        Index('idx_daily_date_customer', 'date', 'customer_id'),
        Index('idx_daily_date_feature', 'date', 'feature'),
    )


class SeverityType(enum.Enum):
    """Insight severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class InsightType(enum.Enum):
    """Types of insights."""
    HIGH_USAGE = "high_usage"
    LOW_REVENUE = "low_revenue"
    UNPROFITABLE_FEATURE = "unprofitable_feature"
    LEGACY_PLAN = "legacy_plan"
    THRESHOLD_EXCEEDED = "threshold_exceeded"


class InsightFlag(Base):
    """Precomputed insights for fast UI rendering."""
    __tablename__ = "insight_flags"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True, index=True)
    insight_type = Column(Enum(InsightType), nullable=False, index=True)
    severity = Column(Enum(SeverityType), nullable=False, index=True)
    category = Column(String, nullable=False)  # usage, revenue, customer, feature
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    metric_value = Column(String, nullable=True)
    is_active = Column(Integer, default=1)  # Boolean: 1 = active, 0 = resolved
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    resolved_at = Column(DateTime, nullable=True)

    # Relationships
    customer = relationship("Customer", back_populates="insight_flags")

    __table_args__ = (
        Index('idx_insight_active_severity', 'is_active', 'severity'),
    )


class ServiceConfiguration(Base):
    """Configured billing services for Airbyte integration."""
    __tablename__ = "service_configurations"

    id = Column(Integer, primary_key=True, index=True)
    service_type = Column(String, nullable=False, index=True)  # stripe, chargebee, openai, etc.
    service_category = Column(String, nullable=False, index=True)  # 'usage' or 'revenue'
    service_name = Column(String, nullable=False)  # Display name
    api_key_encrypted = Column(Text, nullable=False)  # Encrypted API credentials
    additional_config = Column(Text, nullable=True)  # JSON string for extra config
    airbyte_source_id = Column(String, nullable=True)  # Airbyte source ID
    airbyte_connection_id = Column(String, nullable=True)  # Airbyte connection ID
    status = Column(String, default="pending")  # pending, active, inactive, error
    last_sync = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_service_type_status', 'service_type', 'status'),
        Index('idx_service_category', 'service_category'),
    )

