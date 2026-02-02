# Usage vs Revenue Analyzer 📊

A comprehensive dashboard that joins OpenAI usage data with Stripe billing data to provide insights into feature profitability, helping teams understand which features drive revenue and which are cost centers.

## Features

- **Cost per Feature** - Track OpenAI API usage costs per feature/model
- **Revenue per Feature** - Monitor revenue attribution to features from Stripe
- **Net Profit Analysis** - Calculate and visualize profit margins over time
- **Trends & Outliers** - Identify high-performing and underperforming features
- **Interactive Dashboard** - Real-time visualizations with customizable date ranges

## Architecture

```
OpenAI Usage API ──┐
                   ├─ Aggregation Layer ──→ Metrics Store ──→ UI Dashboard
Stripe Billing API ┘
```

### Components

1. **Data Fetching Layer** (`app/services/`)
   - `openai_service.py` - Fetches usage and token cost data from OpenAI API
   - `stripe_service.py` - Fetches subscriptions, invoices, and payments from Stripe API

2. **Aggregation Layer** (`app/services/aggregation_service.py`)
   - Joins usage and billing data
   - Calculates cost per feature, revenue per feature, and net profit
   - Identifies trends and statistical outliers

3. **API Layer** (`app/main.py`)
   - RESTful API built with FastAPI
   - Provides endpoints for dashboard data, feature metrics, and time-series data

4. **UI Layer** (`static/index.html`)
   - Interactive web dashboard
   - Real-time charts using Chart.js
   - Feature breakdown table with outlier indicators

## Setup

### Prerequisites

- Python 3.8 or higher
- OpenAI API key (optional - demo data available)
- Stripe API key (optional - demo data available)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/cloverzer0/Usage-vs-Revenue-Analyzer.git
cd Usage-vs-Revenue-Analyzer
```

2. Run the setup script:
```bash
./setup.sh
```

Or manually:
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

3. Configure API keys in `.env` file:
```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_ORG_ID=your_org_id_here
STRIPE_API_KEY=your_stripe_secret_key_here
```

**Note:** The application works with sample data if API keys are not configured, perfect for testing and development.

## Usage

### Starting the Server

```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Start the server
python -m uvicorn app.main:app --reload
```

The dashboard will be available at: http://localhost:8000

### API Endpoints

- `GET /` - Dashboard UI
- `GET /api/health` - Health check and configuration status
- `GET /api/dashboard?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` - Full dashboard data
- `GET /api/features?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` - Feature metrics only
- `GET /api/timeseries?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` - Time-series data only

### Example API Call

```bash
curl "http://localhost:8000/api/dashboard?start_date=2024-01-01&end_date=2024-01-31"
```

## Dashboard Metrics

### Summary Cards
- **Total Revenue** - Sum of all Stripe payments
- **Total Cost** - Sum of all OpenAI usage costs
- **Net Profit** - Revenue minus costs
- **Profit Margin** - Percentage of revenue that is profit

### Visualizations
- **Net Profit Over Time** - Line chart showing profit trends
- **Cost vs Revenue Over Time** - Dual line chart comparing costs and revenue
- **Feature Profitability** - Bar chart comparing revenue and costs per feature

### Feature Breakdown Table
- Feature name (e.g., gpt-4, gpt-3.5-turbo)
- Total cost
- Total revenue
- Net profit
- Usage count
- Status badges for outliers (high profit ⭐ or high loss ⚠️)

## Development

### Project Structure

```
Usage-vs-Revenue-Analyzer/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── models/
│   │   └── __init__.py        # Data models (Pydantic)
│   └── services/
│       ├── openai_service.py   # OpenAI API integration
│       ├── stripe_service.py   # Stripe API integration
│       └── aggregation_service.py  # Data aggregation logic
├── static/
│   └── index.html              # Dashboard UI
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
├── setup.sh                   # Setup script
└── README.md                  # This file
```

### Adding New Features

1. Update data models in `app/models/__init__.py`
2. Extend services in `app/services/`
3. Add new API endpoints in `app/main.py`
4. Update UI in `static/index.html`

## Production Deployment

### Environment Variables

Set the following environment variables:
- `OPENAI_API_KEY` - Your OpenAI API key
- `OPENAI_ORG_ID` - Your OpenAI organization ID (optional)
- `STRIPE_API_KEY` - Your Stripe secret key
- `HOST` - Server host (default: 0.0.0.0)
- `PORT` - Server port (default: 8000)

### Running in Production

```bash
# Install production server
pip install gunicorn

# Run with Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker Deployment (Optional)

Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t usage-revenue-analyzer .
docker run -p 8000:8000 --env-file .env usage-revenue-analyzer
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details
