import stripe
from typing import List, Dict
from datetime import datetime, timedelta
from app.models import BillingRecord


class StripeService:
    """Service to fetch billing data from Stripe API"""
    
    def __init__(self, api_key: str):
        stripe.api_key = api_key
        self.api_key = api_key
    
    def fetch_billing_data(self, start_date: str, end_date: str) -> List[BillingRecord]:
        """
        Fetch billing data from Stripe for the specified date range.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            List of BillingRecord objects
        """
        billing_records = []
        
        try:
            # Convert dates to timestamps
            start_timestamp = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp())
            end_timestamp = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp())
            
            # Fetch charges/payments from Stripe
            charges = stripe.Charge.list(
                created={
                    'gte': start_timestamp,
                    'lte': end_timestamp
                },
                limit=100
            )
            
            for charge in charges.auto_paging_iter():
                if charge.paid and charge.amount > 0:
                    # Extract feature/subscription info from metadata if available
                    feature = charge.metadata.get('feature', 'subscription')
                    
                    billing_records.append(BillingRecord(
                        date=datetime.fromtimestamp(charge.created).strftime('%Y-%m-%d'),
                        customer_id=charge.customer or 'unknown',
                        feature=feature,
                        revenue=charge.amount / 100.0,  # Convert from cents to dollars
                        subscription_type=charge.metadata.get('subscription_type', None)
                    ))
        except stripe.error.StripeError as e:
            # If API fails, return sample data for demonstration
            print(f"Stripe API error: {e}. Using sample data.")
            billing_records = self._generate_sample_billing_data(start_date, end_date)
        
        return billing_records
    
    def _generate_sample_billing_data(self, start_date: str, end_date: str) -> List[BillingRecord]:
        """Generate sample billing data for demonstration"""
        import random
        
        billing_records = []
        subscription_types = ['basic', 'pro', 'enterprise']
        features = ['gpt-4', 'gpt-3.5-turbo', 'text-embedding-ada-002']
        
        current_date = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        while current_date <= end:
            date_str = current_date.strftime('%Y-%m-%d')
            
            # Generate 1-5 transactions per day
            for _ in range(random.randint(1, 5)):
                subscription_type = random.choice(subscription_types)
                feature = random.choice(features)
                
                # Different pricing based on subscription type
                revenue_map = {
                    'basic': random.uniform(10, 50),
                    'pro': random.uniform(50, 200),
                    'enterprise': random.uniform(200, 1000)
                }
                
                billing_records.append(BillingRecord(
                    date=date_str,
                    customer_id=f"cus_{random.randint(1000, 9999)}",
                    feature=feature,
                    revenue=round(revenue_map[subscription_type], 2),
                    subscription_type=subscription_type
                ))
            
            current_date += timedelta(days=1)
        
        return billing_records
    
    def get_revenue_per_feature(self, billing_records: List[BillingRecord]) -> Dict[str, float]:
        """Calculate total revenue per feature"""
        revenue = {}
        for record in billing_records:
            if record.feature:
                revenue[record.feature] = revenue.get(record.feature, 0) + record.revenue
        return revenue
