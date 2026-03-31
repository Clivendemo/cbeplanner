# CBE Lesson Planner - Product Requirements Document

## Overview
A competency-based education lesson planning system for Kenyan teachers with M-Pesa wallet payments, Firebase authentication, and MongoDB Atlas database.

## Original Problem Statement
1. Fix the scheme of work preview for mobile - should display PDF in-app using WebView
2. Add new admin feature for curriculum PDF upload without modifying existing functionality

## Architecture
- **Frontend**: React Native (Expo) on port 3000/8081
- **Backend**: FastAPI (Python) on port 8001  
- **Database**: MongoDB
- **Auth**: Firebase Authentication
- **Payments**: Safaricom Daraja API (M-Pesa)

## Core Requirements (Static)
1. Lesson plan generation with KICD alignment
2. Schemes of work multi-step wizard with PDF generation
3. M-Pesa wallet integration for payments
4. Admin panel for curriculum management
5. 2-day lesson expiration with auto-delete

## User Personas
- **Teachers**: Create lesson plans, generate notes, download schemes of work
- **Admin**: Manage curriculum data, import CSV/PDF/Word files

## What's Been Implemented

### January 2026 - Session 2: PDF Preview & Admin Upload Feature

#### 1. Mobile PDF Preview Fix (Completed)
- Updated `schemes.tsx` to use WebView for in-app PDF display on mobile
- Added `react-native-webview` for native PDF rendering
- Full-screen modal with SafeAreaView for proper layout
- Added Share button to allow sharing PDF from modal
- Smooth loading state with ActivityIndicator
- Works on both iOS and Android devices

#### 2. Admin Curriculum PDF Upload Feature (NEW - Completed)
**Backend (`/api/admin/upload-curriculum`)**:
- New POST endpoint accepts PDF file via multipart/form-data
- Validates file type (PDF only) and size (10MB limit)
- Saves file to `backend/pdfs/` directory
- Uses AI extraction (OpenAI GPT-4o-mini) to parse curriculum data
- Extracts strands, substrands, SLOs, and activities
- Stores extracted data in MongoDB
- Moves processed file to `backend/pdfs_processed/`
- Returns success response with processing statistics

**Frontend (`curriculum-upload.tsx`)**:
- New dedicated admin page for PDF upload
- Uses `expo-document-picker` for file selection
- Shows file name and allows changing selection
- Upload button with loading state ("Processing...")
- Success card showing extracted counts (grade, subject, pages, strands, SLOs)
- Error handling with user-friendly messages
- Requirements section listing PDF specs

**Integration Notes**:
- Does NOT modify existing routes or components
- Uses existing `verify_admin` dependency for auth
- Independent tab in admin panel ("PDF Upload")
- Reuses same database schema as existing curriculum import

### January 2026 - Session 1: UI/UX Audit (Previous Session)
- Fixed login single-tap issue with keyboard handling
- Added SafeAreaView to auth screens
- Fixed navigation double-slide bug
- Updated credit system flow with profile redirect
- Added Help & Support with email to profiles
- Removed all console.log for production readiness

## Prioritized Backlog

### P0 (Critical) - Completed
- [x] Mobile PDF preview in-app display
- [x] Admin curriculum PDF upload feature

### P1 (High Priority)
- [ ] M-Pesa production verification with Safaricom
- [ ] Intermittent lesson plan generation failures investigation
- [ ] Complete grade data for all levels

### P2 (Medium Priority)
- [ ] Add unit tests for critical flows
- [ ] Implement offline mode for lesson viewing
- [ ] Add push notifications for payment confirmations

### Future Enhancements
- Share feature for educators
- Collaborative lesson planning
- Analytics dashboard for usage patterns
- Bulk PDF processing (multiple files at once)

## Technical Dependencies Added
- `pdfplumber`: PDF text extraction
- `pdfminer.six`: PDF parsing support
- `pypdfium2`: PDF rendering support
- `react-native-webview`: In-app PDF display (already installed)

## Next Tasks
1. Test PDF upload feature with actual KICD curriculum PDFs
2. Test mobile PDF preview on physical devices
3. Submit for M-Pesa production environment verification
4. Prepare Play Store listing assets
5. Build production APK/AAB using `eas build`
