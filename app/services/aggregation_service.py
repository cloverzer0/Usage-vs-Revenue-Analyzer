"""Aggregation service for usage and revenue data."""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

from app.models.db_models import (
    Customer, UsageEvent, RevenueEvent, DailyAggregate,
    InsightFlag, SeverityType, InsightType
)

logger = logging.getLogger(__name__)


class AggregationService:
    """Service for aggregating usage and revenue data from the database."""

    def __init__(self, db: Session):
        self.db = db

    def materialize_daily_aggregates(self, date: datetime) -> int:
        """
        Pre-compute daily aggregates for efficient querying.
        This runs periodically (e.g., nightly) to update the aggregates table.
        
        Args:
            date: Date to materialize aggregates for
            
        Returns:
            Number of aggregates created
        """
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        created = 0

        # Aggregate by customer
        customer_aggregates = self.db.query(
            UsageEvent.customer_id,
            func.sum(UsageEvent.quantity).label('usage_total'),
            func.count(UsageEvent.id).label('usage_count'),
            func.sum(UsageEvent.quantity * UsageEvent.unit_cost).label('cost_total')
        ).filter(
            and_(
                UsageEvent.timestamp >= start_of_day,
                UsageEvent.timestamp < end_of_day
            )
        ).group_by(UsageEvent.customer_id).all()

        for agg in customer_aggregates:
            # Get revenue for this customer
            revenue = self.db.query(
                func.sum(RevenueEvent.amount)
            ).filter(
                and_(
                    RevenueEvent.customer_id == agg.customer_id,
                    RevenueEvent.timestamp >= start_of_day,
                    RevenueEvent.timestamp < end_of_day
                )
            ).scalar() or 0.0

            # Check if aggregate already exists
            existing = self.db.query(DailyAggregate).filter(
                and_(
                    DailyAggregate.date == start_of_day,
                    DailyAggregate.customer_id == agg.customer_id,
                    DailyAggregate.feature.is_(None)
                )
            ).first()

            if existing:
                existing.usage_total = agg.usage_total
                existing.usage_count = agg.usage_count
                existing.cost_total = agg.cost_total
                existing.revenue_total = revenue
            else:
                daily_agg = DailyAggregate(
                    date=start_of_day,
                    customer_id=agg.customer_id,
                    usage_total=agg.usage_total,
                    usage_count=agg.usage_count,
                    cost_total=agg.cost_total,
                    revenue_total=revenue
                )
                self.db.add(daily_agg)
                created += 1

        # Aggregate by feature
        feature_aggregates = self.db.query(
            UsageEvent.feature,
            func.sum(UsageEvent.quantity).label('usage_total'),
            func.count(UsageEvent.id).label('usage_count'),
            func.sum(UsageEvent.quantity * UsageEvent.unit_cost).label('cost_total')
        ).filter(
            and_(
                UsageEvent.timestamp >= start_of_day,
                UsageEvent.timestamp < end_of_day
            )
        ).group_by(UsageEvent.feature).all()

        for agg in feature_aggregates:
            existing = self.db.query(DailyAggregate).filter(
                and_(
                    DailyAggregate.date == start_of_day,
                    DailyAggregate.customer_id.is_(None),
                    DailyAggregate.feature == agg.feature
                )
            ).first()

            if existing:
                existing.usage_total = agg.usage_total
                existing.usage_count = agg.usage_count
                existing.cost_total = agg.cost_total
            else:
                daily_agg = DailyAggregate(
                    date=start_of_day,
                    feature=agg.feature,
                    usage_total=agg.usage_total,
                    usage_count=agg.usage_count,
                    cost_total=agg.cost_total
                )
                self.db.add(daily_agg)
                created += 1

        self.db.commit()
        return created

    def compute_insights(self) -> int:
        """
        Compute rule-based insights and store them as flags.
        
        Returns:
            Number of insights generated
        """
        # Clear old insights
        self.db.query(InsightFlag).filter(InsightFlag.is_active == 1).update(
            {'is_active': 0, 'resolved_at': datetime.utcnow()}
        )

        insights_created = 0

        # Insight 1: High usage, low revenue customers
        high_usage_customers = self.db.query(
            Customer.id,
            Customer.name,
            func.sum(UsageEvent.quantity).label('total_usage'),
            func.sum(RevenueEvent.amount).label('total_revenue')
        ).join(
            UsageEvent, Customer.id == UsageEvent.customer_id
        ).outerjoin(
            RevenueEvent, Customer.id == RevenueEvent.customer_id
        ).group_by(
            Customer.id, Customer.name
        ).having(
            and_(
                func.sum(UsageEvent.quantity) > 10000,
                func.coalesce(func.sum(RevenueEvent.amount), 0) < 100
            )
        ).all()

        for customer in high_usage_customers:
            insight = InsightFlag(
                customer_id=customer.id,
                insight_type=InsightType.LOW_REVENUE,
                severity=SeverityType.CRITICAL,
                category='customer',
                title='High Usage, Low Revenue',
                message=f'{customer.name} has high usage ({int(customer.total_usage):,}) but low revenue (${customer.total_revenue or 0:.2f})',
                metric_value=f'Revenue/Unit: ${(customer.total_revenue or 0) / customer.total_usage:.4f}',
                is_active=1
            )
            self.db.add(insight)
            insights_created += 1

        # Insight 2: Unprofitable features
        last_30_days = datetime.utcnow() - timedelta(days=30)
        
        unprofitable_features = self.db.query(
            DailyAggregate.feature,
            func.sum(DailyAggregate.cost_total).label('total_cost'),
            func.sum(DailyAggregate.revenue_total).label('total_revenue')
        ).filter(
            and_(
                DailyAggregate.feature.isnot(None),
                DailyAggregate.date >= last_30_days
            )
        ).group_by(
            DailyAggregate.feature
        ).having(
            func.sum(DailyAggregate.cost_total) > func.sum(DailyAggregate.revenue_total)
        ).all()

        for feature in unprofitable_features:
            loss = feature.total_cost - (feature.total_revenue or 0)
            insight = InsightFlag(
                insight_type=InsightType.UNPROFITABLE_FEATURE,
                severity=SeverityType.CRITICAL if loss > 1000 else SeverityType.WARNING,
                category='feature',
                title='Unprofitable Feature',
                message=f'Feature "{feature.feature}" costs ${feature.total_cost:.2f} but generates ${feature.total_revenue or 0:.2f}',
                metric_value=f'Loss: ${loss:.2f}',
                is_active=1
            )
            self.db.add(insight)
            insights_created += 1

        # Insight 3: Legacy plan usage
        legacy_customers = self.db.query(Customer).filter(
            Customer.plan.like('%legacy%')
        ).count()

        if legacy_customers > 0:
            insight = InsightFlag(
                insight_type=InsightType.LEGACY_PLAN,
                severity=SeverityType.WARNING,
                category='usage',
                title='Legacy Plan Usage',
                message=f'{legacy_customers} customer(s) on legacy plans',
                metric_value=f'{legacy_customers} customers',
                is_active=1
            )
            self.db.add(insight)
            insights_created += 1

        self.db.commit()
        return insights_created

    def get_dashboard_data(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Get aggregated dashboard data from the database.
        This is much more efficient than in-memory aggregation.
        """
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)

        # Get time series data from daily aggregates
        time_series = self.db.query(
            DailyAggregate.date,
            func.sum(DailyAggregate.usage_total).label('usage_total'),
            func.sum(DailyAggregate.cost_total).label('cost_total'),
            func.sum(DailyAggregate.revenue_total).label('revenue_total')
        ).filter(
            and_(
                DailyAggregate.date >= start_dt,
                DailyAggregate.date <= end_dt,
                DailyAggregate.customer_id.isnot(None)  # Only customer aggregates
            )
        ).group_by(DailyAggregate.date).order_by(DailyAggregate.date).all()

        # Get feature metrics
        feature_metrics = self.db.query(
            DailyAggregate.feature,
            func.sum(DailyAggregate.usage_total).label('usage_count'),
            func.sum(DailyAggregate.cost_total).label('total_cost'),
            func.sum(DailyAggregate.revenue_total).label('revenue')
        ).filter(
            and_(
                DailyAggregate.date >= start_dt,
                DailyAggregate.date <= end_dt,
                DailyAggregate.feature.isnot(None)
            )
        ).group_by(DailyAggregate.feature).all()

        # Calculate summary
        total_usage_cost = sum(ts.cost_total for ts in time_series)
        total_revenue = sum(ts.revenue_total for ts in time_series)
        total_profit = total_revenue - total_usage_cost
        profit_margin_pct = (total_profit / total_revenue * 100) if total_revenue > 0 else 0

        return {
            'summary': {
                'total_usage_cost': total_usage_cost,
                'total_revenue': total_revenue,
                'total_profit': total_profit,
                'profit_margin_percentage': profit_margin_pct,
                'date_range': {
                    'start': start_date,
                    'end': end_date
                }
            },
            'time_series': [
                {
                    'date': ts.date.strftime('%Y-%m-%d'),
                    'usage_cost': ts.cost_total,
                    'revenue': ts.revenue_total,
                    'profit': ts.revenue_total - ts.cost_total
                }
                for ts in time_series
            ],
            'feature_metrics': [
                {
                    'feature_name': fm.feature,
                    'usage_count': int(fm.usage_count),
                    'total_cost': fm.total_cost,
                    'revenue': fm.revenue or 0,
                    'profit_margin': ((fm.revenue or 0) - fm.total_cost) / (fm.revenue or 1) * 100
                }
                for fm in feature_metrics
            ]
        }

    def get_active_insights(self) -> List[Dict[str, Any]]:
        """Get all active insights."""
        insights = self.db.query(InsightFlag).filter(
            InsightFlag.is_active == 1
        ).order_by(
            InsightFlag.severity.desc(),
            InsightFlag.created_at.desc()
        ).all()

        return [
            {
                'id': str(insight.id),
                'type': insight.severity.value,
                'category': insight.category,
                'title': insight.title,
                'description': insight.message,
                'metric': insight.metric_value
            }
            for insight in insights
        ]
