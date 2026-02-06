"""Service for ingesting and normalizing data from external sources."""
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging

from app.models.db_models import Customer, UsageEvent, RevenueEvent, EventType

logger = logging.getLogger(__name__)


class DataIngestionService:
    """Handles ingestion of usage and revenue data into the database."""

    def __init__(self, db: Session):
        self.db = db

    def ingest_usage_data(self, usage_records: List[Dict[str, Any]]) -> int:
        """
        Ingest usage data from third-party sources.
        
        Args:
            usage_records: List of usage records with structure:
                {
                    'customer_id': str,
                    'customer_name': str,
                    'feature': str,
                    'quantity': float,
                    'unit_cost': float,
                    'timestamp': datetime,
                    'source': str
                }
        
        Returns:
            Number of records ingested
        """
        ingested = 0
        
        for record in usage_records:
            try:
                # Get or create customer
                customer = self._get_or_create_customer(
                    external_id=record['customer_id'],
                    name=record.get('customer_name', record['customer_id']),
                    plan=record.get('plan', 'Unknown')
                )

                # Create usage event
                usage_event = UsageEvent(
                    customer_id=customer.id,
                    feature=record['feature'],
                    quantity=record['quantity'],
                    unit_cost=record.get('unit_cost', 0.0),
                    timestamp=record.get('timestamp', datetime.utcnow()),
                    source=record.get('source', 'api')
                )
                
                self.db.add(usage_event)
                ingested += 1
                
            except Exception as e:
                logger.error(f"Error ingesting usage record: {e}")
                continue

        self.db.commit()
        return ingested

    def ingest_revenue_data(self, revenue_records: List[Dict[str, Any]]) -> int:
        """
        Ingest revenue data from Stripe or other third-party sources.
        
        Args:
            revenue_records: List of revenue records with structure:
                {
                    'customer_id': str,
                    'customer_name': str,
                    'amount': float,
                    'currency': str,
                    'event_type': str,
                    'external_id': str,
                    'timestamp': datetime
                }
        
        Returns:
            Number of records ingested
        """
        ingested = 0
        
        for record in revenue_records:
            try:
                # Check for duplicate (idempotency)
                existing = self.db.query(RevenueEvent).filter(
                    RevenueEvent.external_id == record['external_id']
                ).first()
                
                if existing:
                    continue

                # Get or create customer
                customer = self._get_or_create_customer(
                    external_id=record['customer_id'],
                    name=record.get('customer_name', record['customer_id'])
                )

                # Create revenue event
                revenue_event = RevenueEvent(
                    customer_id=customer.id,
                    amount=record['amount'],
                    currency=record.get('currency', 'usd'),
                    event_type=EventType[record['event_type'].upper()],
                    external_id=record['external_id'],
                    timestamp=record.get('timestamp', datetime.utcnow())
                )
                
                self.db.add(revenue_event)
                ingested += 1
                
            except Exception as e:
                logger.error(f"Error ingesting revenue record: {e}")
                continue

        self.db.commit()
        return ingested

    def _get_or_create_customer(self, external_id: str, name: str, plan: str = None) -> Customer:
        """Get existing customer or create new one."""
        customer = self.db.query(Customer).filter(
            Customer.external_customer_id == external_id
        ).first()

        if not customer:
            customer = Customer(
                external_customer_id=external_id,
                name=name,
                plan=plan or 'Unknown'
            )
            self.db.add(customer)
            self.db.flush()  # Get the ID without committing

        return customer

    async def sync_from_airbyte(self) -> Dict[str, int]:
        """
        Trigger syncs for all configured Airbyte connections.
        
        With Airbyte architecture:
        1. This triggers Airbyte to pull data from sources
        2. Airbyte writes directly to our database tables
        3. Returns sync statistics
        
        Returns:
            Dict with sync statistics per connection
        """
        from app.services.airbyte_service import airbyte_service
        
        stats = {
            'connections_synced': 0,
            'connections_failed': 0,
            'total_records': 0
        }

        try:
            # Get all Airbyte connections
            connections = await airbyte_service.list_connections()
            
            for connection in connections:
                try:
                    connection_id = connection.get('connectionId')
                    if not connection_id:
                        continue
                    
                    # Trigger sync
                    job_info = await airbyte_service.trigger_sync(connection_id)
                    
                    if job_info.get('status') == 'running':
                        stats['connections_synced'] += 1
                        logger.info(f"Triggered sync for connection {connection_id}")
                    else:
                        stats['connections_failed'] += 1
                        logger.warning(f"Failed to sync connection {connection_id}")
                        
                except Exception as e:
                    stats['connections_failed'] += 1
                    logger.error(f"Error syncing connection: {e}")
                    
        except Exception as e:
            logger.error(f"Error listing Airbyte connections: {e}")
        
        return stats
    
    def get_sync_statistics(self, start_date: str, end_date: str) -> Dict[str, int]:
        """
        Get statistics on data ingested between dates.
        Useful for monitoring data pipeline health.
        """
        try:
            start_dt = datetime.fromisoformat(start_date)
            end_dt = datetime.fromisoformat(end_date)
            
            # Count usage events
            usage_count = self.db.query(UsageEvent).filter(
                UsageEvent.timestamp >= start_dt,
                UsageEvent.timestamp <= end_dt
            ).count()
            
            # Count revenue events
            revenue_count = self.db.query(RevenueEvent).filter(
                RevenueEvent.timestamp >= start_dt,
                RevenueEvent.timestamp <= end_dt
            ).count()
            
            # Count customers
            customer_count = self.db.query(Customer).count()
            
            return {
                'usage_events': usage_count,
                'revenue_events': revenue_count,
                'total_customers': customer_count,
                'date_range': f"{start_date} to {end_date}"
            }
            
        except Exception as e:
            logger.error(f"Error getting sync statistics: {e}")
            return {
                'usage_events': 0,
                'revenue_events': 0,
                'total_customers': 0,
                'error': str(e)
            }
