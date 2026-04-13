# CBE Planner - Product Requirements Document

## Overview
A competency-based education lesson planning system for Kenyan teachers with M-Pesa wallet payments, Firebase authentication, and MongoDB Atlas database.

## Architecture
- **Frontend**: React Native (Expo) - Cross-platform (Android, Web)
- **Backend**: FastAPI (Python) on port 8001
- **Database**: MongoDB
- **Auth**: Firebase Authentication
- **Payments**: Safaricom Daraja API (M-Pesa)

## What's Been Implemented

### Core Features
- Login/Signup with Firebase Auth (keyboard handling fixed for web)
- Navigation with centralized AuthGate (no double navigation)
- Dashboard with 6 feature tiles
- Lesson Plan generation with cascading dropdowns (Grade > Subject > Strand > Substrand > SLO)
- Scheme of Work generation
- M-Pesa wallet top-up integration
- Transaction history
- Teacher profile management

### Lesson Planning Engine Extension (April 13, 2026)
- **Multi-Lesson Architecture**: Broke "1 SLO = 1 Lesson" assumption
- **DB Schema**: Added `number_of_lessons` to substrands, new `substrand_lessons` collection
- **Backend Endpoints**: GET/POST/PATCH/DELETE for substrand lessons
- **Admin UI**: Lesson configuration modal in curriculum.tsx
- **Frontend**: LessonPlanDisplay.tsx shows lesson-specific outcomes
- **PDF Generator**: Updated to render "Lesson X of Y" label and lesson-specific outcome bullets
- **Backward Compatibility**: Falls back to old SLO logic if no substrand_lessons configured

### Move Modal Fix (April 13, 2026)
- **Root Cause**: Modal used bottom-sheet pattern (justifyContent: flex-end) causing content clipping
- **Fix**: Centered modal with ScrollView body, fixed header/footer, responsive sizing
- **Styles**: New moveModalOverlay, moveModalContainer, moveModalHeader, moveModalBody, moveModalFooter
- **Features**: Overlay dismiss, close button, proper z-index, nested scroll support

### Notes Generation Feature (April 2, 2026)
- **Backend**: `POST /api/notes/generate`, `GET /api/notes/{id}/preview`, `POST /api/notes/{id}/download`
- **Content**: Rich educational notes with Introduction, Main Content, Key Terms, Practice Questions
- **PDF**: Clean textbook-style A4 PDF via ReportLab
- **Wallet**: KES 1 per download (first one free), preview is free

### Stabilization Fixes (April 1, 2026)
- Fixed double navigation (centralized in AuthGate)
- Fixed login keyboard bug
- Fixed frontend .env pointing to production instead of preview

### Previous Work
- PDF preview using WebView (mobile)
- Admin curriculum PDF upload
- Android native build setup
- Web infinite loading fix
- Help & Support with email

## Key API Endpoints
- `POST /api/auth/verify` - Firebase token verification
- `GET /api/grades`, subjects, strands, substrands, slos - Curriculum data
- `POST /api/lesson-plans/generate` - Generate lesson plans
- `GET /api/lesson-plans/{id}/pdf` - Download lesson plan PDF
- `GET /api/substrands/{id}/lessons` - Get substrand lessons
- `POST /api/substrands/{id}/lessons/generate` - Generate lesson slots
- `PATCH /api/substrand-lessons/{id}` - Update lesson outcomes
- `POST /api/schemes/generate` - Generate schemes
- `POST /api/notes/generate` - Generate study notes
- `POST /api/wallet/topup` - M-Pesa wallet top-up

## Pricing
- Lesson Plans: KES 2 each (5 free on signup)
- Notes Download: KES 1 each (first one free)
- Notes Preview: Free

## Next Tasks
1. Past Papers feature implementation
2. Android APK build testing
3. Configure release signing for Play Store
4. Production environment variable management for Vercel
5. Refactor server.py (5000+ lines) into smaller route modules

## Test Data
- Grade 4 > Mathematics > Numbers > Whole Numbers (with 3 SLOs, 2 substrand_lessons configured)

## Admin Emails
- mail2clive@gmail.com (primary)
- testadmin2026@gmail.com (test account)
