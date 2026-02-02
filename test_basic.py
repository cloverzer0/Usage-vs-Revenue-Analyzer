"""
Simple tests for the Usage vs Revenue Analyzer API
"""
import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from app.services.openai_service import OpenAIService
from app.services.stripe_service import StripeService
from app.services.aggregation_service import AggregationService


def test_openai_service():
    """Test OpenAI service data generation"""
    service = OpenAIService("demo_key", "demo_org")
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    records = service.fetch_usage_data(start_date, end_date)
    
    assert len(records) > 0, "Should generate usage records"
    assert all(hasattr(r, 'date') for r in records), "All records should have date"
    assert all(hasattr(r, 'feature') for r in records), "All records should have feature"
    assert all(hasattr(r, 'cost') for r in records), "All records should have cost"
    
    print(f"✓ OpenAI service test passed - Generated {len(records)} records")


def test_stripe_service():
    """Test Stripe service data generation"""
    service = StripeService("demo_key")
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    records = service.fetch_billing_data(start_date, end_date)
    
    assert len(records) > 0, "Should generate billing records"
    assert all(hasattr(r, 'date') for r in records), "All records should have date"
    assert all(hasattr(r, 'revenue') for r in records), "All records should have revenue"
    
    print(f"✓ Stripe service test passed - Generated {len(records)} records")


def test_aggregation_service():
    """Test aggregation service"""
    openai_service = OpenAIService("demo_key", "demo_org")
    stripe_service = StripeService("demo_key")
    aggregation_service = AggregationService()
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    usage_records = openai_service.fetch_usage_data(start_date, end_date)
    billing_records = stripe_service.fetch_billing_data(start_date, end_date)
    
    dashboard_data = aggregation_service.aggregate_data(usage_records, billing_records)
    
    assert len(dashboard_data.feature_metrics) > 0, "Should have feature metrics"
    assert len(dashboard_data.time_series) > 0, "Should have time series data"
    assert dashboard_data.summary is not None, "Should have summary data"
    assert 'total_cost' in dashboard_data.summary, "Summary should include total_cost"
    assert 'total_revenue' in dashboard_data.summary, "Summary should include total_revenue"
    assert 'total_profit' in dashboard_data.summary, "Summary should include total_profit"
    
    print(f"✓ Aggregation service test passed")
    print(f"  - Features: {len(dashboard_data.feature_metrics)}")
    print(f"  - Time series points: {len(dashboard_data.time_series)}")
    print(f"  - Total Revenue: ${dashboard_data.summary['total_revenue']:.2f}")
    print(f"  - Total Cost: ${dashboard_data.summary['total_cost']:.2f}")
    print(f"  - Net Profit: ${dashboard_data.summary['total_profit']:.2f}")


def test_profit_calculations():
    """Test that profit calculations are correct"""
    openai_service = OpenAIService("demo_key", "demo_org")
    stripe_service = StripeService("demo_key")
    aggregation_service = AggregationService()
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    usage_records = openai_service.fetch_usage_data(start_date, end_date)
    billing_records = stripe_service.fetch_billing_data(start_date, end_date)
    
    dashboard_data = aggregation_service.aggregate_data(usage_records, billing_records)
    
    # Verify profit = revenue - cost
    calculated_profit = dashboard_data.summary['total_revenue'] - dashboard_data.summary['total_cost']
    assert abs(calculated_profit - dashboard_data.summary['total_profit']) < 0.01, \
        "Profit should equal revenue minus cost"
    
    # Verify feature metrics sum to totals
    feature_cost_sum = sum(f.total_cost for f in dashboard_data.feature_metrics)
    feature_revenue_sum = sum(f.total_revenue for f in dashboard_data.feature_metrics)
    
    assert abs(feature_cost_sum - dashboard_data.summary['total_cost']) < 0.01, \
        "Feature costs should sum to total cost"
    assert abs(feature_revenue_sum - dashboard_data.summary['total_revenue']) < 0.01, \
        "Feature revenues should sum to total revenue"
    
    print(f"✓ Profit calculation test passed")


if __name__ == "__main__":
    print("Running Usage vs Revenue Analyzer Tests\n")
    
    try:
        test_openai_service()
        test_stripe_service()
        test_aggregation_service()
        test_profit_calculations()
        
        print("\n✅ All tests passed!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
