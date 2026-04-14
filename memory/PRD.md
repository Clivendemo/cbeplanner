# CBE Planner - Product Requirements Document

## Overview
A competency-based education lesson planning system for Kenyan teachers with M-Pesa wallet payments, Firebase authentication, and MongoDB Atlas database.

## Architecture
- **Frontend**: React Native (Expo) - Cross-platform (Android, Web)
- **Backend**: FastAPI (Python) on port 8001
- **Database**: MongoDB (Motor async)
- **Auth**: Firebase Authentication
- **Payments**: Safaricom Daraja API (M-Pesa)

## Production Hardening (April 14, 2026)

### Section 1 — Critical Bug Fixes
- Removed duplicate `app.include_router(api_router)` at end of server.py
- Removed hardcoded secrets (Firebase API Key, JWT Secret) — now fail-fast in production if missing
- M-Pesa passkey: sandbox default kept for dev, required in production
- Admin emails now loaded from `ADMIN_EMAILS` env var (comma-separated)
- Removed duplicate `GET /admin/slo-mappings/{slo_id}` route (kept richer version with `exists` field)
- Fixed `database.py` broken `property()` call
- Fixed scheme download race condition: replaced `$set` with atomic `$inc` + `wallet_ledger` entry
- Added refund-on-failure for lesson plan generation (wraps content gen in try/except)

### Section 2 — Security Hardening
- M-Pesa callback: added shared secret validation (`MPESA_CALLBACK_SECRET` header)
- Added `validate_object_id()` helper for clean 400 on malformed IDs
- Admin init endpoint now requires `ADMIN_BOOTSTRAP_SECRET` header
- Email masking in auth logs improved (full domain masking)

### Section 3 — Curriculum Density Fix
- Scheme of Work `generate_scheme_v2` now uses `number_of_lessons` from substrands
- Substrand with `number_of_lessons=6` and 2 SLOs generates 6 rows (SLOs cycle)
- Falls back to SLO count if `number_of_lessons` not set
- Added `lessonInSubstrand` and `totalLessonsInSubstrand` to scheme lesson rows
- `admin_update_substrand` now uses partial update (only sets non-None fields)

### Section 4 — Payment & Wallet Integrity
- Scheme download now creates `wallet_ledger` entry + atomic `$inc` deduction
- Lesson plan charge syncs `wallets` collection alongside `users.walletBalance`
- PDF failure → refund + ledger rollback + wallets collection rollback

### Section 5 — UX Improvements
- `/api/wallet/balance` now returns `freeLessonsRemaining` and `currency`
- `verify_token` user auto-creation now includes `freeLessonsRemaining` and creates wallet entry
- Friendly 404 messages for missing curriculum data
- Added `api_error()` helper for standardized error responses

### Section 6 — Cleanup
- Removed 13 unused packages from requirements.txt (stripe, boto3, HuggingFace, linting tools)
- Moved 7 seed/extract scripts to `backend/scripts/seed/`
- Added `pdfs_processed/` and `scripts/seed/` to `.gitignore`
- Seed script generator now saves `number_of_lessons` on substrands

## What's Been Implemented

### Core Features
- Login/Signup with Firebase Auth
- Dashboard with 6 feature tiles
- Lesson Plan generation with cascading dropdowns
- Scheme of Work generation (with number_of_lessons support)
- M-Pesa wallet top-up integration
- Notes Generation module

### Multi-Lesson Architecture
- `number_of_lessons` field on substrands
- `substrand_lessons` collection for lesson-specific outcomes
- PDF generator renders "Lesson X of Y" and specific outcomes
- Backward compatibility with SLO-only fallback

### Admin Features
- Curriculum CRUD with move modal (centered, scrollable, responsive)
- Bulk add/edit operations
- SLO mapping management
- Relationship repair endpoint
- Dynamic strand/substrand fetching in move modal

## Key API Endpoints
- `POST /api/auth/verify` - Firebase token verification
- `GET /api/wallet/balance` - Quick balance check with free lessons remaining
- `POST /api/lesson-plans/generate` - Generate lesson plans (with refund on failure)
- `POST /api/schemes/download` - Download scheme PDF (KES 15, atomic payment)
- `POST /api/admin/repair-relationships` - Check/fix orphaned curriculum data
- `GET /api/substrands/{id}/lessons` - Get substrand lesson config

## Pricing
- Lesson Plans: KES 2 each (5 free on signup)
- Notes Download: KES 1 each (first one free)
- Scheme Download: KES 15
- Notes Preview: Free

## Environment Variables Required for Production
See Section 7 in the hardening spec for full list.

## Next Tasks
1. Firebase Admin SDK integration (Section 2.1 — deferred: requires service account JSON)
2. Past Papers feature
3. Android APK build testing
4. Refactor server.py into smaller route modules
