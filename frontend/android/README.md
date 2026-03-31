# Android Build Guide - Production Ready

This document explains how to build the Android app after pulling from Git.

## Prerequisites

1. **Android Studio** (Arctic Fox 2020.3.1 or later)
2. **Java JDK 17** (required for React Native)
3. **Node.js** (v18 or later) - Must be in system PATH
4. **Yarn** - Package manager

## First-Time Setup

### 1. Install Dependencies

```bash
cd frontend
yarn install
```

### 2. Configure Android SDK

Create/edit `frontend/android/local.properties`:

```properties
# Windows
sdk.dir=C\:\\Users\\YOUR_USERNAME\\AppData\\Local\\Android\\Sdk

# macOS
sdk.dir=/Users/YOUR_USERNAME/Library/Android/sdk

# Linux
sdk.dir=/home/YOUR_USERNAME/Android/Sdk
```

### 3. Open in Android Studio

1. Open Android Studio
2. File > Open
3. Select `frontend/android` folder
4. Wait for Gradle sync to complete

## Building the APK

### Option 1: Android Studio (Recommended)

1. Open `frontend/android` in Android Studio
2. Wait for Gradle sync (first time takes longer)
3. Build > Build Bundle(s) / APK(s) > Build APK(s)
4. APK location: `android/app/build/outputs/apk/release/app-release.apk`

### Option 2: Command Line

```bash
cd frontend/android

# Windows
gradlew.bat assembleRelease

# macOS/Linux
./gradlew assembleRelease
```

## Building AAB (For Play Store)

```bash
cd frontend/android

# Windows
gradlew.bat bundleRelease

# macOS/Linux
./gradlew bundleRelease
```

AAB location: `android/app/build/outputs/bundle/release/app-release.aab`

## Release Signing (Production)

### 1. Generate Keystore

```bash
keytool -genkeypair -v -storetype PKCS12 \
  -keystore release.keystore \
  -alias cbe-planner \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000
```

### 2. Configure Signing

Add to `frontend/android/local.properties`:

```properties
RELEASE_STORE_FILE=../keystore/release.keystore
RELEASE_STORE_PASSWORD=your_password
RELEASE_KEY_ALIAS=cbe-planner
RELEASE_KEY_PASSWORD=your_password
```

## Troubleshooting

### "SDK location not found"
- Create `local.properties` with your SDK path
- Or set `ANDROID_HOME` environment variable

### "Node not found" / Settings.gradle errors
1. Ensure Node.js is installed: `node --version`
2. Add Node.js to system PATH
3. Restart Android Studio

### Build errors after pulling
1. Clean project: Build > Clean Project
2. Invalidate caches: File > Invalidate Caches / Restart
3. Re-sync Gradle: File > Sync Project with Gradle Files

### CMake / NDK errors
This project is configured to avoid CMake compilation. If you see CMake errors:
1. Ensure `newArchEnabled=false` in `gradle.properties`
2. Run `yarn install` to ensure correct package versions

## Architecture

- **Build Architecture**: ARM64 only (covers 95%+ of modern devices)
- **JavaScript Engine**: Hermes (faster, smaller APK)
- **Min SDK**: 24 (Android 7.0)
- **Target SDK**: 35 (Android 15)

## Files Overview

| File | Purpose |
|------|---------|
| `build.gradle` (root) | Project-wide configuration |
| `app/build.gradle` | App module configuration |
| `gradle.properties` | Build settings and flags |
| `settings.gradle` | Module inclusion and plugins |
| `local.properties` | Machine-specific paths (not in Git) |
| `proguard-rules.pro` | Code obfuscation rules |

---

**Developed by LEGIT LAB**
