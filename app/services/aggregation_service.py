from typing import List, Dict
from collections import defaultdict
from datetime import datetime
from app.models import (
    UsageRecord, BillingRecord, FeatureMetrics, 
    TimeSeriesMetrics, DashboardData
)


class AggregationService:
    """Service to aggregate usage and billing data"""
    
    def aggregate_data(
        self, 
        usage_records: List[UsageRecord], 
        billing_records: List[BillingRecord]
    ) -> DashboardData:
        """
        Aggregate usage and billing data to create dashboard metrics.
        
        Args:
            usage_records: List of usage records from OpenAI
            billing_records: List of billing records from Stripe
            
        Returns:
            DashboardData with aggregated metrics
        """
        # Calculate feature-level metrics
        feature_metrics = self._calculate_feature_metrics(usage_records, billing_records)
        
        # Calculate time-series metrics
        time_series = self._calculate_time_series(usage_records, billing_records)
        
        # Calculate summary statistics
        summary = self._calculate_summary(feature_metrics, time_series)
        
        return DashboardData(
            feature_metrics=feature_metrics,
            time_series=time_series,
            summary=summary
        )
    
    def _calculate_feature_metrics(
        self, 
        usage_records: List[UsageRecord], 
        billing_records: List[BillingRecord]
    ) -> List[FeatureMetrics]:
        """Calculate metrics per feature"""
        feature_data = defaultdict(lambda: {
            'cost': 0.0, 
            'revenue': 0.0, 
            'usage_count': 0, 
            'revenue_count': 0
        })
        
        # Aggregate usage costs
        for record in usage_records:
            feature_data[record.feature]['cost'] += record.cost
            feature_data[record.feature]['usage_count'] += 1
        
        # Aggregate revenues
        for record in billing_records:
            if record.feature:
                feature_data[record.feature]['revenue'] += record.revenue
                feature_data[record.feature]['revenue_count'] += 1
        
        # Create FeatureMetrics objects
        metrics = []
        for feature, data in feature_data.items():
            net_profit = data['revenue'] - data['cost']
            metrics.append(FeatureMetrics(
                feature=feature,
                total_cost=round(data['cost'], 2),
                total_revenue=round(data['revenue'], 2),
                net_profit=round(net_profit, 2),
                usage_count=data['usage_count'],
                revenue_count=data['revenue_count']
            ))
        
        # Sort by net profit (descending)
        metrics.sort(key=lambda x: x.net_profit, reverse=True)
        
        return metrics
    
    def _calculate_time_series(
        self, 
        usage_records: List[UsageRecord], 
        billing_records: List[BillingRecord]
    ) -> List[TimeSeriesMetrics]:
        """Calculate time-series metrics for trends"""
        daily_data = defaultdict(lambda: {'cost': 0.0, 'revenue': 0.0})
        
        # Aggregate by date
        for record in usage_records:
            daily_data[record.date]['cost'] += record.cost
        
        for record in billing_records:
            daily_data[record.date]['revenue'] += record.revenue
        
        # Create TimeSeriesMetrics objects
        time_series = []
        for date, data in sorted(daily_data.items()):
            net_profit = data['revenue'] - data['cost']
            time_series.append(TimeSeriesMetrics(
                date=date,
                total_cost=round(data['cost'], 2),
                total_revenue=round(data['revenue'], 2),
                net_profit=round(net_profit, 2)
            ))
        
        return time_series
    
    def _calculate_summary(
        self, 
        feature_metrics: List[FeatureMetrics],
        time_series: List[TimeSeriesMetrics]
    ) -> Dict:
        """Calculate summary statistics"""
        total_cost = sum(m.total_cost for m in feature_metrics)
        total_revenue = sum(m.total_revenue for m in feature_metrics)
        total_profit = total_revenue - total_cost
        
        # Find most/least profitable features
        most_profitable = max(feature_metrics, key=lambda x: x.net_profit) if feature_metrics else None
        least_profitable = min(feature_metrics, key=lambda x: x.net_profit) if feature_metrics else None
        
        # Calculate profit margin
        profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
        
        # Identify outliers (features with extreme profit/loss)
        outliers = []
        if feature_metrics:
            avg_profit = total_profit / len(feature_metrics)
            for metric in feature_metrics:
                # Flag as outlier if profit deviates significantly from average
                if abs(metric.net_profit - avg_profit) > abs(avg_profit * 0.5):
                    outliers.append({
                        'feature': metric.feature,
                        'net_profit': metric.net_profit,
                        'type': 'high_profit' if metric.net_profit > avg_profit else 'high_loss'
                    })
        
        return {
            'total_cost': round(total_cost, 2),
            'total_revenue': round(total_revenue, 2),
            'total_profit': round(total_profit, 2),
            'profit_margin': round(profit_margin, 2),
            'most_profitable_feature': most_profitable.feature if most_profitable else None,
            'least_profitable_feature': least_profitable.feature if least_profitable else None,
            'outliers': outliers,
            'total_features': len(feature_metrics),
            'date_range': {
                'start': time_series[0].date if time_series else None,
                'end': time_series[-1].date if time_series else None
            }
        }
