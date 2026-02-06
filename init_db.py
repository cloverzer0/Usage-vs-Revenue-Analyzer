#!/usr/bin/env python3
"""Database initialization script."""

import sys
import os
import asyncio
from datetime import datetime, timedelta

# Add app directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.database import init_db, SessionLocal
from app.services.data_ingestion_service import DataIngestionService
from app.services.aggregation_service import AggregationService


async def main():
    print("Initializing database...")
    
    # Create tables
    init_db()
    print("Database tables created")
    
    # Create a session
    db = SessionLocal()
    
    try:
        print("\nℹ️  Airbyte Integration:")
        print("   - Configure services through the Settings UI")
        print("   - Airbyte will automatically sync data to the database")
        print("   - Use POST /api/sync to trigger manual syncs")
        
        print("\nMaterializing initial aggregates...")
        aggregation_service = AggregationService(db)
        agg_count = aggregation_service.materialize_daily_aggregates(datetime.now())
        print(f"   - Created {agg_count} aggregate records")
        
        print("\nComputing insights...")
        insight_count = aggregation_service.compute_insights()
        print(f"   - Generated {insight_count} insights")
        
        print("\nDatabase initialization complete!")
        print(f"\n📊 Summary:")
        print(f"   - Daily aggregates: {agg_count}")
        print(f"   - Active insights: {insight_count}")
        print(f"\n🚀 Next steps:")
        print(f"   1. Start the backend: python -m uvicorn app.main:app --reload --port 8000")
        print(f"   2. Start the frontend: cd frontend && npm run dev")
        print(f"   3. Visit http://localhost:3002 and login")
        print(f"   4. Configure services in Settings")
        
    except Exception as e:
        print(f"\n❌ Error during initialization: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
