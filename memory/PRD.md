# CBE Lesson Planner - Product Requirements Document

## Original Problem Statement
Build a production-ready Competency-Based Education (CBE) lesson planning system for Kenyan teachers with:
- M-Pesa wallet integration for payments
- 5 free lesson plans on signup, then KES 2 per plan
- Firebase authentication
- MongoDB Atlas database
- Deployment to Railway (backend) and Vercel (frontend)

## What's Been Implemented

### Core Features (DONE)
- **User Authentication:** Firebase-based signup/login with JWT verification
- **Wallet System:** M-Pesa STK Push integration (SANDBOX mode)
- **Business Logic:** 5 free lessons on signup, KES 2 per subsequent plan
- **Lesson Plan Generator:** Duration-aware lesson plans (25-80 min)
- **Notes Generator:** Duration-aware teaching notes
- **Schemes of Work Generator:** Term-based curriculum planning
- **Admin Role:** Role-based access control for admin endpoints

### Database (DONE)
- MongoDB Atlas connection configured
- Wallet ledger for atomic, idempotent transactions
- Database indexes for performance

### Deployment Prep (DONE - Dec 2025)
- Dockerfile configured with `$PORT` environment variable
- `railway.toml` with health check configuration
- Health check endpoint at `/api/health`
- `.env.example` with all required variables documented
- `RAILWAY_DEPLOYMENT.md` guide created

## Key Files
- `backend/server.py` - Main FastAPI application
- `backend/mpesa_service.py` - M-Pesa integration
- `backend/Dockerfile` - Production-ready Docker configuration
- `backend/railway.toml` - Railway deployment config
- `backend/RAILWAY_DEPLOYMENT.md` - Deployment instructions
- `frontend/app/(teacher)/home.tsx` - Main lesson generation UI
- `frontend/app/(teacher)/profile.tsx` - Wallet & M-Pesa UI

## Known Issues
1. **Expo Go Instability (P1):** User reported app crashes on mobile. May need further debugging.
2. **English PDF Data (P2):** English curriculum PDF extraction failed; data not imported.

## Important Notes
- **M-Pesa is in SANDBOX mode.** `MPESA_CALLBACK_URL` must be updated with production URL after deployment.
- Railway sets `$PORT` automatically - Dockerfile is configured to use it.

## Deployment Checklist
1. Push code to GitHub
2. Connect repo to Railway
3. Set all environment variables in Railway dashboard
4. Update `MPESA_CALLBACK_URL` with Railway URL
5. Deploy frontend to Vercel with backend URL

## Next Steps / Backlog
- [ ] Test on Railway with production M-Pesa credentials
- [ ] Deploy frontend to Vercel
- [ ] Debug Expo Go stability issues (if still occurring)
- [ ] Import English curriculum data (requires OCR)
