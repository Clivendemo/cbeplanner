# Railway Deployment Guide

## Quick Deploy (Recommended)

1. **Create Railway Account**: https://railway.app
2. **Create New Project**: Click "New Project" → "Deploy from GitHub repo"
3. **Connect Repository**: Select your GitHub repository
4. **Set Environment Variables** in Railway Dashboard:

```env
# Required
MONGODB_URI=mongodb+srv://<user>:<pass>@<cluster>.mongodb.net/?retryWrites=true&w=majority
DB_NAME=cbeplanner

# Firebase (Required for auth)
FIREBASE_PROJECT_ID=cbeplanner
FIREBASE_API_KEY=your-firebase-api-key

# Security
JWT_SECRET=your-secure-random-string

# M-Pesa (Required for payments)
MPESA_CONSUMER_KEY=your-consumer-key
MPESA_CONSUMER_SECRET=your-consumer-secret
MPESA_SHORTCODE=174379
MPESA_PASSKEY=your-passkey
MPESA_CALLBACK_URL=https://YOUR-RAILWAY-URL/api/payments/mpesa/callback
MPESA_ENV=sandbox  # Change to 'production' for live

# CORS (Add your frontend URL)
CORS_ORIGINS=https://your-frontend.vercel.app

# Environment
ENVIRONMENT=production
LOG_LEVEL=INFO
```

5. **Deploy**: Railway will auto-detect the Dockerfile and deploy

## Post-Deployment

1. Get your Railway URL (e.g., `https://your-app.up.railway.app`)
2. Update `MPESA_CALLBACK_URL` with your actual Railway URL
3. Update frontend `.env` with the Railway backend URL

## Health Check

Test your deployment:
```bash
curl https://your-app.up.railway.app/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "environment": "production",
  "database": "connected",
  "version": "1.0.0"
}
```

## Notes

- Railway automatically sets the `PORT` environment variable
- The Dockerfile is configured to use `$PORT`
- Health check endpoint: `/api/health`
