# Deployment Guide

This application consists of two parts:
1. **Frontend** (Next.js) → Deploy to Vercel
2. **Backend** (FastAPI) → Deploy to Railway, Render, or Fly.io

## Step 1: Deploy Backend to Railway

### Prerequisites
- GitHub account
- Railway account (https://railway.app)

### Steps

1. **Create a GitHub repository** (if not already done):
   ```bash
   cd /Users/muktar/Desktop/Mine/Usage-vs-Revenue-Analyzer
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

2. **Deploy to Railway**:
   - Go to https://railway.app
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Railway will auto-detect Python and use `railway.toml` config

3. **Set Environment Variables** in Railway dashboard:
   ```
   SECRET_KEY=<generate-with-openssl-rand-hex-32>
   DATABASE_URL=sqlite:///./data/usage_revenue.db
   ENABLE_SCHEDULER=true
   FRONTEND_URL=https://your-frontend.vercel.app
   ```

4. **Get your Railway backend URL**:
   - After deployment, Railway will give you a URL like: `https://your-app.railway.app`
   - Copy this URL

5. **Update CORS in backend**:
   - Add your Vercel URL to allowed origins in `app/main.py`

## Step 2: Deploy Frontend to Vercel

### Prerequisites
- Vercel account (https://vercel.com)
- Backend URL from Railway

### Steps

1. **Update frontend environment**:
   ```bash
   cd frontend
   # Edit .env.production and add your Railway backend URL
   ```

2. **Deploy to Vercel**:
   
   **Option A: Via CLI**
   ```bash
   npm install -g vercel
   cd frontend
   vercel
   ```

   **Option B: Via GitHub**
   - Go to https://vercel.com
   - Click "New Project" → "Import Git Repository"
   - Select your repository
   - Set **Root Directory** to `frontend`
   - Add environment variable:
     - `NEXT_PUBLIC_API_URL` = Your Railway backend URL
   - Deploy

3. **Configure Environment Variables in Vercel**:
   - Go to Project Settings → Environment Variables
   - Add:
     ```
     NEXT_PUBLIC_API_URL = https://your-backend.railway.app
     ```

## Step 3: Update Backend CORS

After getting your Vercel frontend URL, update `app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "https://your-frontend.vercel.app",  # Add your Vercel URL
        "https://*.vercel.app"  # Allow all preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Commit and push to trigger redeployment on Railway.

## Step 4: Database Setup

For production, consider upgrading from SQLite:

### Option 1: PostgreSQL on Railway
1. Add PostgreSQL to your Railway project
2. Update `DATABASE_URL` environment variable
3. Update `app/database.py` to use PostgreSQL connection string

### Option 2: Keep SQLite (simpler for MVP)
- SQLite will persist on Railway's volume
- Good enough for small-scale applications

## Verification

1. Visit your Vercel URL: `https://your-frontend.vercel.app`
2. Try logging in with: demo@example.com / demo123
3. Check that dashboard loads data from backend

## Troubleshooting

### CORS errors
- Ensure your Vercel URL is in backend's allowed origins
- Check that `allow_credentials=True` is set

### 401 Unauthorized
- Check that `SECRET_KEY` matches between deployments
- Verify JWT tokens are being sent correctly

### Database errors
- Check Railway logs for database connection issues
- Ensure `data/` directory exists and is writable

## Alternative: Deploy Backend to Render

If you prefer Render over Railway:

1. Create `render.yaml`:
   ```yaml
   services:
     - type: web
       name: usage-revenue-api
       env: python
       buildCommand: "pip install -r requirements.txt"
       startCommand: "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
   ```

2. Deploy to Render following similar steps

## Security Checklist

Before going to production:

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Set `DEBUG=False` if you add debug mode
- [ ] Review and restrict CORS origins
- [ ] Enable HTTPS (automatic on Vercel/Railway)
- [ ] Set up proper database backups
- [ ] Review and update password policies
- [ ] Add rate limiting for auth endpoints
- [ ] Set up monitoring and logging

## Environment Variables Reference

### Backend (Railway/Render)
```
SECRET_KEY=<strong-random-key>
DATABASE_URL=sqlite:///./data/usage_revenue.db
ENABLE_SCHEDULER=true
FRONTEND_URL=https://your-frontend.vercel.app
AIRBYTE_API_URL=http://localhost:8006/api/v1  (optional)
AIRBYTE_WORKSPACE_ID=  (optional)
```

### Frontend (Vercel)
```
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```
