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

### Notes Generation Feature (April 2, 2026)
- **Backend**: `POST /api/notes/generate`, `GET /api/notes/{id}/preview`, `POST /api/notes/{id}/download`
- **Content**: Rich educational notes with Introduction, Main Content (concept sections with explanations, examples, applications), Key Terms, Practice Questions, Summary
- **PDF**: Clean textbook-style A4 PDF via ReportLab (Times Roman, proper headings, meta table)
- **Wallet**: KES 1 per download (first one free via `freeNotesUsed` flag), preview is free
- **Frontend**: Form with cascading dropdowns, in-app preview, download button, insufficient funds modal
- **Files**: `notes_generator.py`, `notes_pdf.py`, updated `server.py`, updated `notes.tsx`, updated `dashboard.tsx`

### Stabilization Fixes (April 1, 2026)
- Fixed double navigation (centralized in AuthGate)
- Fixed login keyboard bug (keyboardShouldPersistTaps="always")
- Removed competing navigation from index.tsx, login.tsx, signup.tsx, teacher/admin layouts
- Removed console.log statements from AuthContext
- Fixed frontend .env pointing to production instead of preview

### Previous Work
- PDF preview using WebView (mobile)
- Admin curriculum PDF upload
- Android native build setup (expo prebuild, gradle fixes)
- Web infinite loading fix
- Help & Support with email

## Key API Endpoints
- `POST /api/auth/verify` - Firebase token verification
- `GET /api/grades`, `GET /api/subjects`, `GET /api/strands`, `GET /api/substrands`, `GET /api/slos` - Curriculum data
- `POST /api/lesson-plans/generate` - Generate lesson plans
- `POST /api/schemes/generate` - Generate schemes
- `POST /api/notes/generate` - Generate study notes
- `GET /api/notes/{id}/preview` - Preview notes PDF (free)
- `POST /api/notes/{id}/download` - Download notes PDF (KES 1)
- `GET /api/notes` - List user's notes
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

## Test Data
- Grade 4 > Mathematics > Numbers > Whole Numbers (with 3 SLOs, 2 learning activities)
