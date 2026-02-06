from fastapi import FastAPI, HTTPException, Query, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.services.aggregation_service import AggregationService
from app.services.data_ingestion_service import DataIngestionService
from app.services.scheduler_service import SchedulerService
from app.services.airbyte_service import AirbyteService, airbyte_service
from app.models import DashboardData
from app.database import get_db, init_db
from app.auth import (
    get_password_hash, 
    authenticate_user, 
    create_access_token, 
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.models.db_models import User

# Load environment variables
load_dotenv()

# Initialize database
init_db()

# Configuration
ENABLE_SCHEDULER = os.getenv("ENABLE_SCHEDULER", "true").lower() == "true"
USE_DATABASE = os.getenv("USE_DATABASE", "true").lower() == "true"

# Initialize FastAPI app
app = FastAPI(
    title="Usage vs Revenue Analyzer",
    description="Dashboard that joins usage data with billing data",
    version="2.0.0"
)

# Add CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3002"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for auth
class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: str = None

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str = None
    is_active: bool

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Initialize scheduler only if enabled
scheduler_service = SchedulerService() if ENABLE_SCHEDULER else None


# ==================== AUTH ENDPOINTS ====================

@app.post("/api/auth/register", response_model=Token)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email or username already registered"
        )
    
    # Create new user
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create access token with user.id as string (JWT requires string subject)
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "is_active": user.is_active
        }
    }


@app.post("/api/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login user and return JWT token."""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password"
        )
    
    # Create access token with user.id as string (JWT requires string subject)
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "is_active": user.is_active
        }
    }


@app.get("/api/auth/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_active_user)):
    """Get current user info."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active
    }


# Initialize scheduler only if enabled


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    # Initialize Airbyte
    try:
        await airbyte_service.initialize()
        print("✅ Airbyte service initialized")
    except Exception as e:
        print(f"⚠️  Airbyte initialization failed: {str(e)}")
    
    # Start the scheduler for background tasks
    if ENABLE_SCHEDULER and scheduler_service:
        scheduler_service.start()
        print("✅ Background scheduler started")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    if ENABLE_SCHEDULER and scheduler_service:
        scheduler_service.shutdown()
        print("✅ Background scheduler stopped")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "2.0.0"}

@app.get("/api/health")
async def api_health_check():
    """API health check endpoint for frontend"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/health")
async def api_health_check():
    """API health check endpoint for frontend"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/dashboard")
async def get_dashboard_data(
    request: Request,
    start_date: str = Query(None),
    end_date: str = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get aggregated dashboard data for the specified date range.
    Now powered by the database layer for efficient querying.
    
    If dates are not provided, defaults to last 30 days.
    """
    # Debug: Log authorization header
    auth_header = request.headers.get('Authorization')
    print(f"🔍 Dashboard request - Auth header: {auth_header[:50] if auth_header else 'NONE'}")
    
    # Default to last 30 days if not specified
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
    if not start_date:
        start = datetime.now() - timedelta(days=30)
        start_date = start.strftime('%Y-%m-%d')
    
    # Validate dates
    try:
        datetime.strptime(start_date, '%Y-%m-%d')
        datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    try:
        # Use database aggregation service
        aggregation_service = AggregationService(db)
        dashboard_data = aggregation_service.get_dashboard_data(start_date, end_date)
        
        return dashboard_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")


@app.get("/api/features")
async def get_features(
    start_date: str = Query(None),
    end_date: str = Query(None),
    db: Session = Depends(get_db)
):
    """Get feature metrics only"""
    dashboard_data = await get_dashboard_data(start_date, end_date, db)
    return {
        "features": dashboard_data['feature_metrics'],
        "summary": dashboard_data['summary']
    }


@app.get("/api/timeseries")
async def get_timeseries(
    start_date: str = Query(None),
    end_date: str = Query(None),
    db: Session = Depends(get_db)
):
    """Get time-series metrics only"""
    dashboard_data = await get_dashboard_data(start_date, end_date, db)
    return {
        "timeseries": dashboard_data['time_series']
    }


@app.get("/api/insights")
async def get_insights(db: Session = Depends(get_db)):
    """Get active rule-based insights."""
    try:
        aggregation_service = AggregationService(db)
        insights = aggregation_service.get_active_insights()
        return {"insights": insights}
    except Exception as e:
        return {"insights": [], "error": str(e)}


@app.post("/api/sync")
async def trigger_sync(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Manually trigger Airbyte sync for all configured connections."""
    try:
        ingestion_service = DataIngestionService(db)
        stats = await ingestion_service.sync_from_airbyte()
        
        # Materialize aggregates
        aggregation_service = AggregationService(db)
        agg_count = aggregation_service.materialize_daily_aggregates(datetime.now())
        
        # Compute insights
        insight_count = aggregation_service.compute_insights()
        
        return {
            "status": "success",
            "connections_synced": stats['connections_synced'],
            "connections_failed": stats['connections_failed'],
            "aggregates_created": agg_count,
            "insights_generated": insight_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


@app.get("/api/customers")
async def get_customers(
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get list of customers with their metrics."""
    from app.models.db_models import Customer, UsageEvent, RevenueEvent
    from sqlalchemy import func
    
    try:
        customers = db.query(
            Customer.id,
            Customer.external_customer_id,
            Customer.name,
            Customer.plan,
            func.sum(UsageEvent.quantity).label('total_usage'),
            func.sum(RevenueEvent.amount).label('total_revenue')
        ).outerjoin(
            UsageEvent, Customer.id == UsageEvent.customer_id
        ).outerjoin(
            RevenueEvent, Customer.id == RevenueEvent.customer_id
        ).group_by(
            Customer.id,
            Customer.external_customer_id,
            Customer.name,
            Customer.plan
        ).limit(limit).all()
        
        return {
            "customers": [
                {
                    "id": c.id,
                    "external_id": c.external_customer_id,
                    "name": c.name,
                    "plan": c.plan,
                    "usage": float(c.total_usage or 0),
                    "revenue": float(c.total_revenue or 0),
                    "revenue_per_unit": float(c.total_revenue or 0) / float(c.total_usage or 1)
                }
                for c in customers
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching customers: {str(e)}")


@app.post("/api/test-service")
async def test_service_connection(request: dict):
    """Test service credentials (validation only - Airbyte handles actual connections)."""
    service_type = request.get('service_type')
    credentials = request.get('credentials', {})
    
    if not service_type or not credentials:
        raise HTTPException(status_code=400, detail="service_type and credentials required")
    
    # Basic validation - Airbyte will do the real connection test
    required_fields = {
        'stripe': ['api_key'],
        'openai': ['api_key'],
        'chargebee': ['api_key', 'site'],
        'paddle': ['api_key', 'vendor_id'],
        'recurly': ['api_key', 'subdomain'],
        'braintree': ['merchant_id', 'public_key', 'private_key'],
        'anthropic': ['api_key'],
        'aws': ['access_key_id', 'secret_access_key', 'region'],
        'datadog': ['api_key', 'app_key'],
    }
    
    fields = required_fields.get(service_type, ['api_key'])
    missing = [f for f in fields if not credentials.get(f)]
    
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing required fields: {', '.join(missing)}")
    
    return {"success": True, "message": f"{service_type.title()} credentials validated"}


@app.post("/api/settings")
async def save_settings(request: dict):
    """Save API settings - deprecated, use /api/services instead."""
    return {
        "success": True,
        "message": "Please use /api/services endpoint to add integrations",
        "deprecated": True
    }


@app.get("/api/airbyte/connections")
async def list_airbyte_connections():
    """List all Airbyte connections."""
    try:
        connections = airbyte_service.list_connections()
        return {"success": True, "connections": connections}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list connections: {str(e)}")


@app.post("/api/airbyte/sync/{connection_id}")
async def trigger_airbyte_sync(connection_id: str):
    """Manually trigger an Airbyte sync."""
    try:
        success = airbyte_service.trigger_sync(connection_id)
        if success:
            return {"success": True, "message": f"Sync triggered for connection {connection_id}"}
        else:
            raise HTTPException(status_code=500, detail="Failed to trigger sync")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


@app.get("/api/airbyte/status/{connection_id}")
async def get_airbyte_connection_status(connection_id: str):
    """Get status of an Airbyte connection."""
    try:
        status = airbyte_service.get_connection_status(connection_id)
        return {"success": True, "status": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


@app.get("/api/services")
async def list_services(db: Session = Depends(get_db)):
    """List all configured services."""
    from app.models.db_models import ServiceConfiguration
    import json
    
    try:
        services = db.query(ServiceConfiguration).all()
        return {
            "services": [
                {
                    "id": str(svc.id),
                    "service_type": svc.service_type,
                    "service_category": svc.service_category,
                    "service_name": svc.service_name,
                    "status": svc.status,
                    "airbyte_source_id": svc.airbyte_source_id,
                    "airbyte_connection_id": svc.airbyte_connection_id,
                    "last_sync": svc.last_sync.isoformat() if svc.last_sync else None,
                }
                for svc in services
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list services: {str(e)}")


@app.post("/api/services")
async def add_service(request: dict, db: Session = Depends(get_db)):
    """Add a new billing service and create Airbyte connection."""
    from app.models.db_models import ServiceConfiguration
    import json
    from cryptography.fernet import Fernet
    
    service_category = request.get('service_category', 'revenue')  # Default to revenue for backward compatibility
    service_type = request.get('service_type')
    service_name = request.get('service_name')
    credentials = request.get('credentials', {})
    
    if not service_type or not credentials:
        raise HTTPException(status_code=400, detail="service_type and credentials required")
    
    try:
        # Simple encryption (in production, use proper key management)
        key = os.getenv("ENCRYPTION_KEY", Fernet.generate_key()).encode() if isinstance(os.getenv("ENCRYPTION_KEY", Fernet.generate_key()), str) else Fernet.generate_key()
        cipher = Fernet(key)
        encrypted_credentials = cipher.encrypt(json.dumps(credentials).encode()).decode()
        
        # Create database record
        service_config = ServiceConfiguration(
            service_category=service_category,
            service_type=service_type,
            service_name=service_name or service_type.title(),
            api_key_encrypted=encrypted_credentials,
            additional_config=json.dumps(credentials),
            status="pending"
        )
        db.add(service_config)
        db.commit()
        db.refresh(service_config)
        
        # Create Airbyte source
        source_id = airbyte_service.create_generic_source(
            service_type=service_type,
            service_name=service_name or service_type.title(),
            credentials=credentials
        )
        
        if source_id:
            # Create destination and connection
            db_path = os.path.abspath("data/usage_revenue.db")
            dest_id = airbyte_service.create_database_destination(db_path)
            
            if dest_id:
                conn_id = airbyte_service.create_connection(source_id, dest_id)
                
                # Update service config
                service_config.airbyte_source_id = source_id
                service_config.airbyte_connection_id = conn_id
                service_config.status = "active" if conn_id else "error"
                db.commit()
                
                return {
                    "success": True,
                    "message": f"Service '{service_name}' added successfully with Airbyte pipeline",
                    "service_id": service_config.id,
                    "airbyte_connection_id": conn_id
                }
        
        service_config.status = "error"
        db.commit()
        return {
            "success": False,
            "message": f"Service added but Airbyte connection failed",
            "service_id": service_config.id
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to add service: {str(e)}")


@app.delete("/api/services/{service_id}")
async def delete_service(service_id: int, db: Session = Depends(get_db)):
    """Delete a configured service."""
    from app.models.db_models import ServiceConfiguration
    
    try:
        service = db.query(ServiceConfiguration).filter(ServiceConfiguration.id == service_id).first()
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        db.delete(service)
        db.commit()
        
        return {"success": True, "message": "Service deleted"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete service: {str(e)}")


@app.post("/api/test-service")
async def test_service_connection(request: dict):
    """Test connection to a billing service."""
    service_type = request.get('service_type')
    credentials = request.get('credentials', {})
    
    # Simple validation - in production, actually test the API
    if not credentials.get('api_key'):
        raise HTTPException(status_code=400, detail="API key required")
    
    try:
        # Here you would make actual API calls to test the connection
        # For now, just validate the format
        if service_type == 'stripe':
            if not credentials['api_key'].startswith('sk_'):
                return {"success": False, "message": "Invalid Stripe API key format"}
        
        return {"success": True, "message": f"{service_type.title()} connection test successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Connection test failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(app, host=host, port=port)
