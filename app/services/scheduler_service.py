"""Background scheduler for periodic data aggregation and insight computation."""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
import logging

from app.database import SessionLocal
from app.services.data_ingestion_service import DataIngestionService
from app.services.aggregation_service import AggregationService

logger = logging.getLogger(__name__)


class SchedulerService:
    """Manages scheduled tasks for data processing."""

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self._setup_jobs()

    def _setup_jobs(self):
        """Set up scheduled jobs."""
        
        # Sync data from external services every hour
        self.scheduler.add_job(
            func=self.sync_external_data,
            trigger=CronTrigger(minute=0),  # Every hour
            id='sync_external_data',
            name='Sync data from OpenAI and Stripe',
            replace_existing=True
        )

        # Materialize daily aggregates at 2 AM
        self.scheduler.add_job(
            func=self.materialize_aggregates,
            trigger=CronTrigger(hour=2, minute=0),  # Daily at 2 AM
            id='materialize_aggregates',
            name='Materialize daily aggregates',
            replace_existing=True
        )

        # Compute insights every 6 hours
        self.scheduler.add_job(
            func=self.compute_insights,
            trigger=CronTrigger(hour='*/6'),  # Every 6 hours
            id='compute_insights',
            name='Compute rule-based insights',
            replace_existing=True
        )

    async def sync_external_data(self):
        """Trigger Airbyte syncs for all configured connections."""
        logger.info("Starting Airbyte sync...")
        db = SessionLocal()
        try:
            ingestion_service = DataIngestionService(db)
            stats = await ingestion_service.sync_from_airbyte()
            logger.info(f"Sync complete: {stats['connections_synced']} connections synced, {stats['connections_failed']} failed")
            
        except Exception as e:
            logger.error(f"Error syncing Airbyte connections: {e}")
        finally:
            db.close()

    def materialize_aggregates(self):
        """Materialize daily aggregates for yesterday."""
        logger.info("Starting daily aggregate materialization...")
        db = SessionLocal()
        try:
            aggregation_service = AggregationService(db)
            
            # Materialize for yesterday
            yesterday = datetime.now() - timedelta(days=1)
            count = aggregation_service.materialize_daily_aggregates(yesterday)
            logger.info(f"Materialized {count} daily aggregates for {yesterday.date()}")
            
        except Exception as e:
            logger.error(f"Error materializing aggregates: {e}")
        finally:
            db.close()

    def compute_insights(self):
        """Compute insights."""
        logger.info("Computing insights...")
        db = SessionLocal()
        try:
            aggregation_service = AggregationService(db)
            count = aggregation_service.compute_insights()
            logger.info(f"Generated {count} new insights")
            
        except Exception as e:
            logger.error(f"Error computing insights: {e}")
        finally:
            db.close()

    def start(self):
        """Start the scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler started")

    def shutdown(self):
        """Shutdown the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")
