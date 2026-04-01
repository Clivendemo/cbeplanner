# CBE Planner - Product Requirements Document

## Overview
A competency-based education lesson planning system for Kenyan teachers with M-Pesa wallet payments, Firebase authentication, and MongoDB Atlas database.

## Architecture
- **Frontend**: React Native (Expo) - Cross-platform (Android, Web)
- **Backend**: FastAPI (Python) on port 8001
- **Database**: MongoDB
- **Auth**: Firebase Authentication
- **Payments**: Safaricom Daraja API (M-Pesa)

## Android Build Configuration (Production-Ready)

### Versions Locked
- **Gradle**: 8.10.2
- **Android Gradle Plugin**: 8.7.3
- **Kotlin**: 1.9.24
- **NDK**: 26.1.10909125
- **Build Tools**: 35.0.0
- **Compile SDK**: 35
- **Target SDK**: 35
- **Min SDK**: 24

### Key Settings
- `newArchEnabled`: false (prevents CMake/reanimated issues)
- `hermesEnabled`: true (better performance)
- `reactNativeArchitectures`: arm64-v8a (modern devices)
- BuildConfig enabled for all modules

### Files Modified
1. `android/build.gradle` - Root project configuration
2. `android/app/build.gradle` - App module configuration
3. `android/gradle.properties` - Build settings
4. `android/settings.gradle` - Cross-platform compatible
5. `android/proguard-rules.pro` - Native module rules
6. `android/gradle/wrapper/gradle-wrapper.properties` - Gradle version
7. `app.json` - Expo configuration
8. `babel.config.js` - Reanimated plugin

## Build Instructions

### First Time Setup
1. `cd frontend && yarn install`
2. Create `android/local.properties` with SDK path
3. Open `android/` in Android Studio
4. Wait for Gradle sync

### Building APK
- Android Studio: Build > Build Bundle(s)/APK(s) > Build APK(s)
- Command Line: `cd android && gradlew assembleRelease`

### Building AAB (Play Store)
- `cd android && gradlew bundleRelease`

## What's Been Implemented
- Login/Signup with keyboard handling (web-compatible)
- Navigation with auth state management (centralized in AuthGate)
- Credit system flow with profile redirect
- PDF preview using WebView (mobile)
- Admin curriculum PDF upload
- Help & Support with email
- Lesson plan generation with dropdown cascading (Grade > Subject > Strand > Substrand > SLO)
- Scheme of Work generation with topic selection, breaks, double lessons
- M-Pesa wallet top-up integration
- Transaction history
- Dashboard with 6 feature tiles

## Stabilization Fixes (April 2026)
1. Fixed double navigation: Centralized all redirects in AuthGate (_layout.tsx)
2. Fixed login keyboard bug: keyboardShouldPersistTaps changed to "always"
3. Removed competing navigation from index.tsx, login.tsx, signup.tsx, teacher layout, admin layout
4. Removed console.log statements from AuthContext for production
5. Fixed frontend .env pointing to production instead of preview backend
6. Fixed web infinite loading by serving static Expo web export

## Next Tasks
1. Test Android build on Windows machine
2. Configure release signing
3. Submit to Play Store
4. Production environment variable management for Vercel deployment
