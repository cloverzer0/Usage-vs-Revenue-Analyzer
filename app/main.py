from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

from app.services.openai_service import OpenAIService
from app.services.stripe_service import StripeService
from app.services.aggregation_service import AggregationService
from app.models import DashboardData

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Usage vs Revenue Analyzer",
    description="Dashboard that joins usage data with billing data",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize services
openai_service = None
stripe_service = None
aggregation_service = AggregationService()

# Check if API keys are configured
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_org_id = os.getenv("OPENAI_ORG_ID")
stripe_api_key = os.getenv("STRIPE_API_KEY")

if openai_api_key and openai_api_key != "your_openai_api_key_here":
    openai_service = OpenAIService(openai_api_key, openai_org_id)

if stripe_api_key and stripe_api_key != "your_stripe_secret_key_here":
    stripe_service = StripeService(stripe_api_key)


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the dashboard HTML"""
    with open("static/index.html", "r") as f:
        return f.read()


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "openai_configured": openai_service is not None,
        "stripe_configured": stripe_service is not None
    }


@app.get("/api/dashboard", response_model=DashboardData)
async def get_dashboard_data(
    start_date: str = Query(
        None,
        description="Start date in YYYY-MM-DD format",
        example="2024-01-01"
    ),
    end_date: str = Query(
        None,
        description="End date in YYYY-MM-DD format",
        example="2024-01-31"
    )
):
    """
    Get aggregated dashboard data for the specified date range.
    
    If dates are not provided, defaults to last 30 days.
    """
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
    
    # Initialize services with sample data if not configured
    if not openai_service:
        temp_openai = OpenAIService("demo_key", "demo_org")
    else:
        temp_openai = openai_service
    
    if not stripe_service:
        temp_stripe = StripeService("demo_key")
    else:
        temp_stripe = stripe_service
    
    # Fetch data from both sources
    try:
        usage_records = temp_openai.fetch_usage_data(start_date, end_date)
        billing_records = temp_stripe.fetch_billing_data(start_date, end_date)
        
        # Aggregate data
        dashboard_data = aggregation_service.aggregate_data(usage_records, billing_records)
        
        return dashboard_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")


@app.get("/api/features")
async def get_features(
    start_date: str = Query(None),
    end_date: str = Query(None)
):
    """Get feature metrics only"""
    dashboard_data = await get_dashboard_data(start_date, end_date)
    return {
        "features": dashboard_data.feature_metrics,
        "summary": dashboard_data.summary
    }


@app.get("/api/timeseries")
async def get_timeseries(
    start_date: str = Query(None),
    end_date: str = Query(None)
):
    """Get time-series metrics only"""
    dashboard_data = await get_dashboard_data(start_date, end_date)
    return {
        "timeseries": dashboard_data.time_series
    }


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(app, host=host, port=port)
