# CBE Lesson Planner - Product Requirements Document

## Original Problem Statement
Build a production-ready Competency-Based Education (CBE) lesson planning system for Kenyan teachers with:
- M-Pesa wallet integration for payments
- 5 free lesson plans on signup, then KES 2 per plan
- Firebase authentication
- MongoDB Atlas database
- Deployment to Render (backend) and Vercel (frontend)

## User Personas
- **Teachers:** Primary users who create lesson plans, notes, and schemes of work
- **Admin (mail2clive@gmail.com):** Manages curriculum data, imports, and system settings

## Core Requirements
1. Curriculum data management (CRUD for grades, subjects, strands, substrands, SLOs)
2. Lesson plan generation from curriculum data
3. M-Pesa payment integration for wallet top-up
4. 2-day lesson plan expiration with auto-delete
5. Production-hardened security (HSTS, CSP, rate limiting)
6. Admin panel with bulk edit, reorder, import tools

## What's Been Implemented

### Core Features (DONE)
- **User Authentication:** Firebase-based signup/login with JWT verification
- **Wallet System:** M-Pesa STK Push integration (production credentials)
- **Business Logic:** 5 free lessons on signup, KES 2 per subsequent plan
- **Lesson Plan Generator:** Duration-aware lesson plans (25-80 min)
- **Notes Generator:** Duration-aware teaching notes
- **Schemes of Work Generator:** Term-based curriculum planning
- **Admin Role:** Role-based access control (mail2clive@gmail.com only)

### Admin Panel (DONE)
- Move items (strands, substrands, SLOs) with cascade
- Bulk add (text/table input modes)
- Bulk editing & reordering
- Data import system (CSV/PDF/Word)
- Import history tracking
- **Auto-refresh:** Data auto-refreshes after add/edit/delete/reorder operations
- **Back buttons:** Navigation back buttons on subjects, strands, substrands, SLOs pages

### Data Import Features (DONE - Dec 2026)
- **CSV Upload:** Download template, upload filled CSV, preview and import
- **PDF Extraction:** Upload KICD curriculum PDFs, AI extracts structure
- **Word Document Extraction (NEW):** Upload .docx files, extract from paragraphs and tables
- **Import History:** Track all import operations

### Lesson Plan Viewing & Expiration (DONE - Feb 2026)
- **Lesson Detail Page:** `lesson-detail.tsx` displays full lesson plan using `LessonPlanDisplay` component
- **Navigation:** Clicking lesson card navigates to detail page
- **2-Day Expiration:** Plans auto-expire after 2 days via MongoDB TTL index
- **Expiration Badges:** Color-coded badges (green/orange/red) showing time remaining
- **Delete:** Users can manually delete lesson plans
- **Admin Cleanup:** `POST /api/admin/cleanup-expired-plans` for manual cleanup

### Production Hardening (DONE - Feb 2026)
- **Security Headers:** HSTS, CSP, X-Frame-Options, X-Content-Type-Options, Permissions-Policy, Referrer-Policy
- **Rate Limiting:** IP-based rate limiting middleware (auth: 10/min, payment: 5/min, default: 100/min)
- **Request Logging:** All API requests logged with method, path, status, duration
- **Input Validation:** Phone number, amount, email validators
- **Idempotency:** Duplicate payment prevention
- **Transaction Locking:** Race condition prevention for wallet operations
- **IP Whitelisting:** Safaricom IP validation for M-Pesa callbacks
- **CORS Cleanup:** Removed duplicate CORS middleware, single properly-configured instance

### M-Pesa Integration (DONE - production credentials configured)
- STK Push initiation with split-shortcode (BusinessShortCode: 4978540, PartyB: 8336258)
- Callback handling with IP whitelisting
- Payment status polling
- Wallet ledger (source of truth) with atomic balance updates

### Curriculum Data Seeding (DONE - Dec 2026)
- **Grade 1:** Mathematics, Environmental Activities, Creative Activities, CRE (33 strands, 79 substrands)
- **Grade 10:** French, German, Indigenous Language, Mandarin, Power Mechanics
- **Seeding Script:** `python seed_curriculum.py --all` imports all extracted JSON data
- **Data Integrity:** All SLO mappings linked to competencies, values, PCIs

### Session Management (DONE - Feb 2026)
- "Remember Me" checkbox (unchecked by default)
- Persistent sessions via AsyncStorage when checked
- 20-minute inactivity timeout when unchecked
- Auto-redirect to teacher dashboard on login

### UI/UX Improvements (DONE)
- SLO selection dropdown (replaced radio buttons)
- Wallet balance auto-refresh on dashboard focus
- Free lessons badge shows correct remaining count

### Mobile Navigation Improvements (DONE - Dec 2026)
- **Gesture Navigation:** Enabled horizontal swipe to go back on all screens
- **Back Buttons:** Custom back buttons in header for consistent navigation
- **Animation:** Improved slide animation (250ms duration)
- **iOS Full-screen Gesture:** Enabled for smoother navigation on iOS

### About Section (DONE - Mar 2026)
- **About Modal:** Added comprehensive About section to teacher profile page
- **Content:** App introduction, target users (Teachers, Administrators), key features, benefits, mission statement
- **Features Highlighted:** Lesson Plan Generator, Study Notes Generator, Schemes of Work, Structured Curriculum Mapping, Competency & Values Integration
- **Developer Credit:** LEGIT LAB branding with version info

## Architecture
- **Backend:** FastAPI (Python) on port 8001
- **Frontend:** React Native (Expo) on port 3000
- **Database:** MongoDB (DB_NAME: cbeplanner)
- **Auth:** Firebase
- **Payments:** Safaricom Daraja API (M-Pesa)

## Key Files
- `/app/backend/server.py` - Main FastAPI application
- `/app/backend/curriculum_import.py` - CSV/PDF/Word import utilities
- `/app/backend/seed_curriculum.py` - Database seeding script
- `/app/frontend/app/(admin)/curriculum.tsx` - Admin curriculum management
- `/app/frontend/app/(admin)/data-import.tsx` - Data import UI
- `/app/frontend/app/(teacher)/dashboard.tsx` - Teacher dashboard

## Key API Endpoints
- `POST /api/auth/verify` - Firebase token verification
- `GET /api/lesson-plans` - List user's active lesson plans
- `GET /api/lesson-plans/{id}` - Get single lesson plan detail
- `POST /api/lesson-plans/generate` - Generate new lesson plan
- `DELETE /api/lesson-plans/{id}` - Delete lesson plan
- `POST /api/admin/cleanup-expired-plans` - Admin cleanup of expired plans
- `POST /api/payments/mpesa/initiate` - Initiate M-Pesa STK Push
- `POST /api/payments/mpesa/callback` - M-Pesa callback
- `GET /api/payments/mpesa/status/{id}` - Payment status check
- `POST /api/admin/import/extract-pdf` - Extract curriculum from PDF
- `POST /api/admin/import/extract-docx` - Extract curriculum from Word document

## Pending Issues
- **M-Pesa Production:** User reports it's now sorted (needs verification on production)
- **Lesson Plan Generation Failures:** Intermittent "button does nothing" on production
- **Grade 8 Data:** May be incomplete or inaccurate (P2)
- **Grade 1 Data Incomplete:** English & Kiswahili extraction blocked (broken PDF links)

## Backlog / Future Tasks
- Download Lesson Plan as PDF
- Refactor `curriculum.tsx` (3000+ lines → smaller components)
- Full codebase audit (remove dead code)
- API versioning (`/api/v1/...`)
- Backend testing suite (unit & integration)
- Lock down CORS for production (set ENVIRONMENT=production on Render)
- Grade 8 data audit
- Admin bulk import API for curriculum data
- "Share" feature for educators
