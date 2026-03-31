# CBE Lesson Planner - Product Requirements Document

## Overview
A competency-based education lesson planning system for Kenyan teachers with M-Pesa wallet payments, Firebase authentication, and MongoDB Atlas database.

## Original Problem Statement
Audit, debug, and improve the CBE Lesson Planner app across UI/UX, performance, responsiveness, navigation behavior, and state management to prepare for Play Store submission.

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

### January 2026 - UI/UX Audit & Performance Improvements

#### 1. Responsiveness & SafeArea Handling (Completed)
- Added `SafeAreaView` to login.tsx and signup.tsx
- Implemented proper edge handling with `edges={['top', 'left', 'right']}`
- Added `useSafeAreaInsets` for dynamic padding calculations

#### 2. Login/Signup UX Improvements (Completed)
- Wrapped in `TouchableWithoutFeedback` with `Keyboard.dismiss()` callback
- Added `keyboardShouldPersistTaps="handled"` to ScrollView
- Used `KeyboardAvoidingView` with proper behavior for iOS/Android
- Login now works on first tap without needing to dismiss keyboard first

#### 3. Navigation Double-Slide Fix (Completed)
- Added `hasNavigated` ref in AuthGate component in `_layout.tsx`
- Prevents duplicate navigation triggers after login
- Simplified `index.tsx` to just show loading (AuthGate handles redirects)
- Added user dependency reset to clear navigation flag on auth changes

#### 4. Credit System Flow (Completed)
- Updated `schemes.tsx` insufficient funds modal
- "Top Up via M-PESA" button now navigates to `/(teacher)/profile`
- Added `pendingDownload` state to track flow
- Implemented `useFocusEffect` to refresh profile and detect balance updates
- Shows success alert when balance is updated after returning from top-up

#### 5. Performance Optimization (Completed)
- Removed ALL `console.log` and `console.error` statements from:
  - `/app/frontend/app/auth/login.tsx`
  - `/app/frontend/app/auth/signup.tsx`
  - `/app/frontend/app/_layout.tsx`
  - `/app/frontend/app/(teacher)/home.tsx`
  - `/app/frontend/app/(teacher)/schemes.tsx`
  - `/app/frontend/app/(teacher)/profile.tsx`
  - `/app/frontend/app/(teacher)/lessons.tsx`
  - `/app/frontend/app/(teacher)/lesson-detail.tsx`
  - `/app/frontend/app/(teacher)/notes.tsx`
  - `/app/frontend/app/(admin)/curriculum.tsx`
  - `/app/frontend/app/(admin)/data-import.tsx`
  - `/app/frontend/app/(admin)/profile.tsx`
  - `/app/frontend/contexts/AuthContext.tsx`

#### 6. Admin Panel Quick Access (Verified)
- Quick Access links already implemented and functional:
  - Manage Curriculum → `/(admin)/curriculum`
  - Import Data → `/(admin)/data-import`
  - Admin Profile → `/(admin)/profile`

#### 7. Support Section (Completed)
- Added Help & Support menu item to `/(teacher)/profile.tsx`
- Added Help & Support menu item to `/(admin)/profile.tsx`
- Displays support email: `legitlabs@outlook.com`
- Tapping opens email client with pre-filled subject line
- Added `Linking` import for email functionality

#### 8. General UX Polish (Completed)
- Consistent SafeAreaView implementation across auth screens
- Consistent keyboard handling behavior
- Added data-testid attributes for testing

#### 9. Expo & Play Store Readiness (Completed)
- Removed all debug logs for production
- No development-only console statements
- Proper error handling maintained (without logging)

## Prioritized Backlog

### P0 (Critical) - Completed
- [x] Login single-tap issue
- [x] Navigation double-slide bug
- [x] Console log removal for production

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

## Next Tasks
1. Test on physical Android devices across screen sizes
2. Submit for M-Pesa production environment verification
3. Prepare Play Store listing assets
4. Build production APK/AAB using `eas build`
