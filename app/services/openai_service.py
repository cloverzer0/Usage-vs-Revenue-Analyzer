import os
from typing import List, Dict
from datetime import datetime, timedelta
from openai import OpenAI
from app.models import UsageRecord


class OpenAIService:
    """Service to fetch usage data from OpenAI API"""
    
    def __init__(self, api_key: str, org_id: str = None):
        self.client = OpenAI(api_key=api_key, organization=org_id)
        self.api_key = api_key
        self.org_id = org_id
    
    def fetch_usage_data(self, start_date: str, end_date: str) -> List[UsageRecord]:
        """
        Fetch usage data from OpenAI for the specified date range.
        
        Note: This is a simplified implementation. In production, you would
        call the actual OpenAI usage API endpoints. As of now, OpenAI doesn't
        have a public usage API, so this returns sample data for demonstration.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            List of UsageRecord objects
        """
        # Sample data for demonstration
        # In production, you would integrate with OpenAI's usage tracking
        usage_records = []
        
        # Generate sample data for demonstration
        models = ['gpt-4', 'gpt-3.5-turbo', 'text-embedding-ada-002']
        token_costs = {
            'gpt-4': 0.00003,  # $0.03 per 1K tokens (average of input/output)
            'gpt-3.5-turbo': 0.000002,  # $0.002 per 1K tokens
            'text-embedding-ada-002': 0.0000001  # $0.0001 per 1K tokens
        }
        
        current_date = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Generate sample usage for each day
        import random
        while current_date <= end:
            date_str = current_date.strftime('%Y-%m-%d')
            for model in models:
                tokens = random.randint(10000, 500000)
                cost = tokens * token_costs[model]
                
                usage_records.append(UsageRecord(
                    date=date_str,
                    feature=model,
                    tokens_used=tokens,
                    cost=round(cost, 2)
                ))
            
            current_date += timedelta(days=1)
        
        return usage_records
    
    def get_cost_per_feature(self, usage_records: List[UsageRecord]) -> Dict[str, float]:
        """Calculate total cost per feature"""
        costs = {}
        for record in usage_records:
            costs[record.feature] = costs.get(record.feature, 0) + record.cost
        return costs
