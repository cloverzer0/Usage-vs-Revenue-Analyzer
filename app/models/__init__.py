from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class UsageRecord(BaseModel):
    """Represents OpenAI usage data"""
    date: str
    feature: str  # e.g., 'gpt-4', 'gpt-3.5-turbo', 'embeddings'
    tokens_used: int
    cost: float  # in USD


class BillingRecord(BaseModel):
    """Represents Stripe billing data"""
    date: str
    customer_id: str
    feature: Optional[str] = None  # can be derived from subscription metadata
    revenue: float  # in USD
    subscription_type: Optional[str] = None


class FeatureMetrics(BaseModel):
    """Aggregated metrics per feature"""
    feature: str
    total_cost: float
    total_revenue: float
    net_profit: float
    usage_count: int
    revenue_count: int


class TimeSeriesMetrics(BaseModel):
    """Time-series metrics for trends"""
    date: str
    total_cost: float
    total_revenue: float
    net_profit: float


class DashboardData(BaseModel):
    """Complete dashboard data"""
    feature_metrics: List[FeatureMetrics]
    time_series: List[TimeSeriesMetrics]
    summary: dict
