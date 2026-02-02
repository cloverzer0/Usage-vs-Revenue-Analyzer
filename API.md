# API Documentation

## Base URL
```
http://localhost:8000
```

## Endpoints

### Health Check
Check the health status and configuration of the application.

**Endpoint:** `GET /api/health`

**Response:**
```json
{
  "status": "healthy",
  "openai_configured": true,
  "stripe_configured": true
}
```

---

### Get Dashboard Data
Retrieve complete dashboard data including feature metrics, time series, and summary statistics.

**Endpoint:** `GET /api/dashboard`

**Query Parameters:**
- `start_date` (optional): Start date in YYYY-MM-DD format. Default: 30 days ago
- `end_date` (optional): End date in YYYY-MM-DD format. Default: today

**Example Request:**
```bash
curl "http://localhost:8000/api/dashboard?start_date=2024-01-01&end_date=2024-01-31"
```

**Response:**
```json
{
  "feature_metrics": [
    {
      "feature": "gpt-4",
      "total_cost": 236.59,
      "total_revenue": 10225.25,
      "net_profit": 9988.66,
      "usage_count": 31,
      "revenue_count": 25
    }
  ],
  "time_series": [
    {
      "date": "2024-01-01",
      "total_cost": 10.13,
      "total_revenue": 2637.34,
      "net_profit": 2627.21
    }
  ],
  "summary": {
    "total_cost": 254.47,
    "total_revenue": 23984.91,
    "total_profit": 23730.44,
    "profit_margin": 98.94,
    "most_profitable_feature": "gpt-4",
    "least_profitable_feature": "gpt-3.5-turbo",
    "outliers": [
      {
        "feature": "gpt-4",
        "net_profit": 9988.66,
        "type": "high_profit"
      }
    ],
    "total_features": 3,
    "date_range": {
      "start": "2024-01-01",
      "end": "2024-01-31"
    }
  }
}
```

---

### Get Feature Metrics
Retrieve feature-level metrics only.

**Endpoint:** `GET /api/features`

**Query Parameters:**
- `start_date` (optional): Start date in YYYY-MM-DD format
- `end_date` (optional): End date in YYYY-MM-DD format

**Example Request:**
```bash
curl "http://localhost:8000/api/features?start_date=2024-01-01&end_date=2024-01-31"
```

**Response:**
```json
{
  "features": [
    {
      "feature": "gpt-4",
      "total_cost": 236.59,
      "total_revenue": 10225.25,
      "net_profit": 9988.66,
      "usage_count": 31,
      "revenue_count": 25
    }
  ],
  "summary": {
    "total_cost": 254.47,
    "total_revenue": 23984.91,
    "total_profit": 23730.44,
    "profit_margin": 98.94
  }
}
```

---

### Get Time Series Data
Retrieve time-series metrics only.

**Endpoint:** `GET /api/timeseries`

**Query Parameters:**
- `start_date` (optional): Start date in YYYY-MM-DD format
- `end_date` (optional): End date in YYYY-MM-DD format

**Example Request:**
```bash
curl "http://localhost:8000/api/timeseries?start_date=2024-01-01&end_date=2024-01-31"
```

**Response:**
```json
{
  "timeseries": [
    {
      "date": "2024-01-01",
      "total_cost": 10.13,
      "total_revenue": 2637.34,
      "net_profit": 2627.21
    },
    {
      "date": "2024-01-02",
      "total_cost": 8.45,
      "total_revenue": 1543.22,
      "net_profit": 1534.77
    }
  ]
}
```

---

## Data Models

### FeatureMetrics
```json
{
  "feature": "string",           // Feature name (e.g., "gpt-4")
  "total_cost": "float",          // Total cost in USD
  "total_revenue": "float",       // Total revenue in USD
  "net_profit": "float",          // Net profit (revenue - cost)
  "usage_count": "integer",       // Number of usage records
  "revenue_count": "integer"      // Number of revenue records
}
```

### TimeSeriesMetrics
```json
{
  "date": "string",               // Date in YYYY-MM-DD format
  "total_cost": "float",          // Total cost for the day
  "total_revenue": "float",       // Total revenue for the day
  "net_profit": "float"           // Net profit for the day
}
```

### Summary
```json
{
  "total_cost": "float",
  "total_revenue": "float",
  "total_profit": "float",
  "profit_margin": "float",       // Percentage
  "most_profitable_feature": "string",
  "least_profitable_feature": "string",
  "outliers": [
    {
      "feature": "string",
      "net_profit": "float",
      "type": "string"            // "high_profit" or "high_loss"
    }
  ],
  "total_features": "integer",
  "date_range": {
    "start": "string",
    "end": "string"
  }
}
```

---

## Error Responses

### 400 Bad Request
Invalid date format or parameters.

```json
{
  "detail": "Invalid date format. Use YYYY-MM-DD"
}
```

### 500 Internal Server Error
Server error while processing request.

```json
{
  "detail": "Error fetching data: <error message>"
}
```

---

## Integration Examples

### Python
```python
import requests

response = requests.get(
    "http://localhost:8000/api/dashboard",
    params={
        "start_date": "2024-01-01",
        "end_date": "2024-01-31"
    }
)
data = response.json()
print(f"Total Profit: ${data['summary']['total_profit']}")
```

### JavaScript
```javascript
fetch('http://localhost:8000/api/dashboard?start_date=2024-01-01&end_date=2024-01-31')
  .then(response => response.json())
  .then(data => {
    console.log(`Total Profit: $${data.summary.total_profit}`);
  });
```

### cURL
```bash
# Get last 30 days of data
curl "http://localhost:8000/api/dashboard"

# Get specific date range
curl "http://localhost:8000/api/dashboard?start_date=2024-01-01&end_date=2024-01-31"

# Get only feature metrics
curl "http://localhost:8000/api/features?start_date=2024-01-01&end_date=2024-01-31"
```
