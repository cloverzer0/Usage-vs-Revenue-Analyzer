# Usage vs Revenue Analyzer

A modern analytics dashboard that correlates usage data with revenue data, providing actionable insights into profitability and customer behavior. Built with FastAPI, Next.js, and Airbyte for seamless data integration.

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+

### Installation

1. **Clone and setup backend:**
```bash
git clone <your-repo>
cd Usage-vs-Revenue-Analyzer
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Setup frontend:**
```bash
cd frontend
npm install
```

### Running the Application

**Terminal 1 - Backend:**
```bash
source venv/bin/activate
python -m uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Access the dashboard:** http://localhost:3000

## 📊 Features

### Multi-Service Integration
Connect multiple data sources through a unified interface:

**Usage Services** (Track API consumption, compute, storage):
- OpenAI, Anthropic, AWS CloudWatch, Datadog
- Custom Usage APIs

**Revenue Services** (Track payments and subscriptions):
- Stripe, Chargebee, Paddle, Recurly, Braintree
- Custom Revenue APIs

### Key Capabilities
- ✅ **Airbyte Integration**: Automated data pipelines with 300+ connectors
- ✅ **Encrypted Credentials**: Secure storage using Fernet encryption
- ✅ **Real-time Sync**: Background jobs for hourly data synchronization
- ✅ **Pre-computed Metrics**: Materialized aggregates for 90% faster queries
- ✅ **Smart Insights**: Automated alerts for anomalies and opportunities
- ✅ **Modern UI**: Built with Next.js 14, TypeScript, and Tailwind CSS

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│          Service Integrations                    │
│  Usage: OpenAI, AWS, Datadog                    │
│  Revenue: Stripe, Chargebee, Paddle             │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│         Airbyte Data Pipelines                   │
│  • Incremental sync with state management       │
│  • Error handling and retries                   │
│  • 300+ pre-built connectors                    │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│          SQLite Database                         │
│  • customers (normalized entities)               │
│  • usage_events (raw usage records)              │
│  • revenue_events (raw billing records)          │
│  • daily_aggregates (pre-computed metrics)       │
│  • insight_flags (automated alerts)              │
│  • service_configurations (encrypted creds)      │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│         Background Scheduler                     │
│  • Hourly: Data sync from services              │
│  • Daily: Aggregate computation                  │
│  • 6-hourly: Insight generation                  │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│          FastAPI Backend (Port 8000)             │
│  • RESTful API endpoints                         │
│  • CORS-enabled for frontend                     │
│  • Automatic OpenAPI documentation               │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────┐
│        Next.js Frontend (Port 3002)              │
│  • Server-side rendering                         │
│  • TypeScript for type safety                    │
│  • shadcn/ui component library                   │
│  • Recharts for data visualization               │
└─────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
Usage-vs-Revenue-Analyzer/
├── app/
│   ├── main.py                      # FastAPI application
│   ├── database.py                  # Database connection & models
│   ├── models/
│   │   ├── __init__.py
│   │   └── db_models.py             # SQLAlchemy models
│   └── services/
│       ├── aggregation_service.py   # In-memory aggregation
│       ├── aggregation_db_service.py # Database aggregation
│       ├── data_ingestion_service.py # Data normalization
│       ├── scheduler_service.py     # Background jobs
│       └── airbyte_service.py       # Airbyte integration
├── frontend/
│   ├── app/
│   │   └── page.tsx                 # Main dashboard
│   ├── components/
│   │   ├── navigation.tsx           # Top navigation bar
│   │   ├── kpi-cards.tsx            # Metric cards
│   │   ├── dual-axis-chart.tsx      # Usage vs revenue chart
│   │   ├── breakdown-tabs.tsx       # Customer/feature tabs
│   │   ├── drilldown-panel.tsx      # Detailed data view
│   │   ├── insights-section.tsx     # Automated insights
│   │   ├── dynamic-settings-dialog.tsx # Service configuration
│   │   └── airbyte-connections.tsx  # Pipeline status
│   └── lib/
│       ├── api.ts                   # API client functions
│       └── types.ts                 # TypeScript interfaces
├── data/
│   └── usage_revenue.db             # SQLite database
├── requirements.txt                 # Python dependencies
└── README.md
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Required for encryption
ENCRYPTION_KEY=<generate-with-fernet>

# Optional: Control features
ENABLE_SCHEDULER=true
USE_DATABASE=true
```

**Generate encryption key:**
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Adding Services

1. Click **Settings** button in the dashboard
2. Select **Category** (Usage or Revenue)
3. Choose **Service Type** from the dropdown
4. Enter **Credentials** (encrypted automatically)
5. Click **Add Service** to create Airbyte pipeline

## 📊 Database Schema

### Core Tables

**customers**
- Normalized customer entities with deduplication
- Tracks plan, environment, and metadata

**usage_events**
- Raw usage records from APIs
- Indexed by customer_id and timestamp
- Stores feature, quantity, unit_cost

**revenue_events**
- Raw billing records from payment providers
- Indexed by customer_id and timestamp
- Tracks invoices, charges, refunds

**daily_aggregates**
- Pre-computed daily metrics by customer and feature
- Dramatically improves query performance
- Automatically updated by scheduler

**insight_flags**
- Rule-based alerts and recommendations
- Categories: unprofitable customers, usage anomalies, upsell opportunities

**service_configurations**
- Encrypted API credentials
- Tracks Airbyte source/connection IDs
- Service status and last sync timestamps

## 🔌 API Endpoints

### Dashboard Data
- `GET /api/dashboard` - Aggregated metrics for date range
- `GET /api/customers` - List all customers with metrics
- `GET /api/health` - Health check

### Service Management
- `GET /api/services` - List configured services
- `POST /api/services` - Add new service with Airbyte pipeline
- `DELETE /api/services/{id}` - Remove service
- `POST /api/test-service` - Validate credentials

### Airbyte Integration
- `GET /api/airbyte/connections` - List all data pipelines
- `POST /api/airbyte/sync/{id}` - Trigger manual sync
- `GET /api/airbyte/status/{id}` - Get sync status



## 🎯 Key Features Explained

### Automated Insights
The system analyzes data patterns and generates actionable insights:
- **Unprofitable Customers**: Revenue < usage costs
- **Usage Anomalies**: Sudden spikes or drops in consumption
- **Upsell Opportunities**: High usage with low-tier plans

### Background Scheduler
APScheduler runs automated tasks:
- **Hourly**: Sync data from configured services
- **Daily**: Compute aggregated metrics
- **6-hourly**: Generate and update insights

### Airbyte Integration
Optional integration for production data pipelines:
- 300+ pre-built connectors
- Incremental sync with state tracking
- Built-in error handling and retries
- Use Airbyte Cloud or self-hosted

## 🚀 Deployment

### Backend (FastAPI)
```bash
# Production server
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend (Next.js)
```bash
cd frontend
npm run build
npm start
```

### Database
- Development: SQLite (included)
- Production: PostgreSQL recommended
  - Update `DATABASE_URL` in `database.py`
  - Migrate schema with SQLAlchemy

## 🧪 Development

### Adding New Services
1. Add service definition to `frontend/components/dynamic-settings-dialog.tsx`
2. Add connector ID mapping to `app/services/airbyte_service.py`
3. Add validation rules to `/api/test-service` endpoint

### Database Management
```bash
# View database
sqlite3 data/usage_revenue.db

# List tables
.tables

# Query customers
SELECT * FROM customers LIMIT 5;

# View aggregates
SELECT * FROM daily_aggregates ORDER BY date DESC LIMIT 10;
```

### Testing
```bash
# Backend tests
source venv/bin/activate
pytest

# Frontend development
cd frontend
npm run dev     # Development server
npm run build   # Production build
npm run lint    # ESLint check
```

## 📝 License

MIT License - see LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

---

**Built with:** FastAPI • Next.js • TypeScript • Tailwind CSS • Airbyte • SQLite • Recharts

4. Ensure all tests pass
5. Submit a pull request

## 🐛 Troubleshooting

### Database locked error
```bash
# Stop all processes
pkill -f uvicorn
pkill -f python

# Remove lock
rm data/usage_revenue.db-journal
```

### Scheduler not starting
Check `ENABLE_SCHEDULER=true` in `.env`

### No data in dashboard
```bash
# Manually trigger sync
curl -X POST "http://localhost:8000/api/sync"
```

### Frontend not connecting to API
Verify CORS settings in [app/main.py](app/main.py) include `http://localhost:3000`

---

**Version**: 2.0.0  
**Last Updated**: February 2024
