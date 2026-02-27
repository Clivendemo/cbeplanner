# CBE Lesson Planner - Product Requirements Document

## Original Problem Statement
Build a production-ready Competency-Based Education (CBE) lesson planning system for Kenyan teachers with:
- M-Pesa wallet integration for payments
- 5 free lesson plans on signup, then KES 2 per plan
- Firebase authentication
- MongoDB Atlas database
- Deployment to Render (backend) and Vercel (frontend)

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
- Dockerfile configured with `$PORT` environment variable (Render default: 10000)
- Health check endpoints: `GET /health` (simple) and `GET /api/health` (detailed)
- `.env.example` with all required variables documented
- Start command: `uvicorn server:app --host 0.0.0.0 --port $PORT`

## Key Files
- `backend/server.py` - Main FastAPI application
- `backend/mpesa_service.py` - M-Pesa integration
- `backend/Dockerfile` - Production-ready Docker configuration for Render
- `frontend/app/(teacher)/home.tsx` - Main lesson generation UI
- `frontend/app/(teacher)/profile.tsx` - Wallet & M-Pesa UI

## Known Issues
1. **Expo Go Instability (P1):** User reported app crashes on mobile. May need further debugging.
2. **English PDF Data (P2):** English curriculum PDF extraction failed; data not imported.

## Important Notes
- **M-Pesa is in SANDBOX mode.** `MPESA_CALLBACK_URL` must be updated with production URL after deployment.
- Render sets `$PORT` automatically - Dockerfile is configured to use it.

## Render Deployment Steps
1. Push code to GitHub
2. Create new Web Service on Render
3. Connect to GitHub repository
4. Set environment variables in Render dashboard
5. Deploy (Render auto-detects Dockerfile)
6. Update `MPESA_CALLBACK_URL` with Render URL

## Next Steps / Backlog
- [ ] Deploy backend to Render
- [ ] Deploy frontend to Vercel
- [ ] Test with production M-Pesa credentials
- [ ] Debug Expo Go stability issues (if still occurring)
- [ ] Import English curriculum data (requires OCR)
