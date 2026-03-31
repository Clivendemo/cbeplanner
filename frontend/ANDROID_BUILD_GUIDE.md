# CBE Planner - Android Studio APK Generation Guide

## Prerequisites

1. **Android Studio** (Arctic Fox 2020.3.1 or later)
2. **Java JDK 17** or later
3. **Android SDK** with:
   - Build Tools 35.0.0
   - SDK Platform 35
   - NDK 27.1.12297006

## Project Setup

### 1. Open in Android Studio

1. Open Android Studio
2. Select **"Open"** or **"Open an Existing Project"**
3. Navigate to `/app/frontend/android`
4. Click **"OK"** to open the project

### 2. Sync Gradle

- Android Studio should automatically sync Gradle files
- If not, click **"Sync Project with Gradle Files"** button or
- Go to **File > Sync Project with Gradle Files**

### 3. Configure SDK Path

If prompted, set your Android SDK location in `local.properties`:

```properties
sdk.dir=/path/to/your/Android/Sdk
```

## Building APK

### Debug APK (For Testing)

1. **Using Android Studio:**
   - Go to **Build > Build Bundle(s) / APK(s) > Build APK(s)**
   - Wait for build to complete
   - Click "locate" in the notification to find the APK
   - APK location: `android/app/build/outputs/apk/debug/app-debug.apk`

2. **Using Command Line:**
   ```bash
   cd android
   ./gradlew assembleDebug
   ```

### Release APK (For Distribution)

1. **Generate Signing Key** (if you don't have one):
   ```bash
   keytool -genkeypair -v -storetype PKCS12 -keystore release.keystore -alias cbe-planner -keyalg RSA -keysize 2048 -validity 10000
   ```

2. **Configure Signing in `android/app/build.gradle`:**
   
   Add to `signingConfigs`:
   ```gradle
   release {
       storeFile file('release.keystore')
       storePassword 'your-store-password'
       keyAlias 'cbe-planner'
       keyPassword 'your-key-password'
   }
   ```

   Update `buildTypes.release`:
   ```gradle
   release {
       signingConfig signingConfigs.release
       // ... rest of config
   }
   ```

3. **Build Release APK:**
   ```bash
   cd android
   ./gradlew assembleRelease
   ```
   
   APK location: `android/app/build/outputs/apk/release/app-release.apk`

### App Bundle (For Play Store)

```bash
cd android
./gradlew bundleRelease
```

Bundle location: `android/app/build/outputs/bundle/release/app-release.aab`

## Alternative: EAS Build

For cloud builds without Android Studio:

```bash
# Install EAS CLI
npm install -g eas-cli

# Login to Expo
eas login

# Build APK for testing
eas build --platform android --profile apk

# Build AAB for Play Store
eas build --platform android --profile production
```

## Troubleshooting

### Common Issues

1. **Gradle sync fails:**
   - Delete `android/.gradle` and `android/app/build` folders
   - File > Invalidate Caches / Restart

2. **SDK not found:**
   - Create `android/local.properties` with `sdk.dir=/path/to/sdk`

3. **NDK version mismatch:**
   - Install required NDK via SDK Manager
   - Or set `ndkVersion` in `android/build.gradle`

4. **Out of memory:**
   Add to `android/gradle.properties`:
   ```properties
   org.gradle.jvmargs=-Xmx4096m -XX:MaxMetaspaceSize=1024m
   ```

### Clean Build

```bash
cd android
./gradlew clean
./gradlew assembleDebug
```

## App Configuration

- **Package Name:** `com.legitlab.cbeplanner`
- **Version:** 1.0.0 (versionCode: 1)
- **Min SDK:** 24 (Android 7.0)
- **Target SDK:** 35 (Android 15)

## Backend URL Configuration

The app connects to the backend via environment variables in `eas.json`:

- **Development:** `http://localhost:8001`
- **Production:** `https://cbeplanner.onrender.com`

To change the backend URL, update the `.env` file before building:

```
EXPO_PUBLIC_BACKEND_URL=https://your-backend-url.com
```

## Testing the APK

1. Enable "Install from Unknown Sources" on your Android device
2. Transfer the APK to your device
3. Tap the APK file to install
4. Open "CBE Plan" app

## Play Store Submission

1. Build the AAB (not APK) for Play Store
2. Create a developer account at [Google Play Console](https://play.google.com/console)
3. Create a new app
4. Upload the AAB file
5. Complete store listing, content rating, and pricing
6. Submit for review

---

**Developed by LEGIT LAB**

## Troubleshooting Build Errors

### "Task :react-native-screens:clean FAILED" or similar clean errors

**Solution:** Skip the clean task and build directly:

```bash
# In Android Studio terminal or command line:
cd android
./gradlew assembleRelease -x clean

# Or for debug build:
./gradlew assembleDebug -x clean
```

**Alternative:** In Android Studio:
1. Go to **File > Invalidate Caches / Restart**
2. Delete the `android/.gradle` folder manually
3. Delete the `android/app/build` folder manually
4. Rebuild without clean: **Build > Rebuild Project**

### If issues persist:

1. Close Android Studio
2. Delete these folders:
   - `android/.gradle`
   - `android/app/build`
   - `android/build`
   - `~/.gradle/caches` (global Gradle cache)
3. Reopen Android Studio
4. Let Gradle sync
5. Build APK directly (don't clean first)
