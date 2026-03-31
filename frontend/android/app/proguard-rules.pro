# ==============================================================================
# PROGUARD RULES - Production Configuration
# ==============================================================================
# These rules ensure native modules work correctly in release builds
# ==============================================================================

# ==============================================================================
# REACT NATIVE CORE
# ==============================================================================
-keep class com.facebook.react.** { *; }
-keep class com.facebook.hermes.** { *; }
-keep class com.facebook.jni.** { *; }

# React Native TurboModules
-keep class com.facebook.react.turbomodule.** { *; }
-keep class com.facebook.react.bridge.** { *; }

# ==============================================================================
# REACT NATIVE REANIMATED
# ==============================================================================
-keep class com.swmansion.reanimated.** { *; }
-keep class com.swmansion.worklets.** { *; }

# ==============================================================================
# REACT NATIVE GESTURE HANDLER
# ==============================================================================
-keep class com.swmansion.gesturehandler.** { *; }

# ==============================================================================
# REACT NATIVE SCREENS
# ==============================================================================
-keep class com.swmansion.rnscreens.** { *; }

# ==============================================================================
# FIREBASE
# ==============================================================================
-keep class com.google.firebase.** { *; }
-keep class io.invertase.firebase.** { *; }
-dontwarn io.invertase.firebase.**

# ==============================================================================
# EXPO MODULES
# ==============================================================================
-keep class expo.modules.** { *; }
-keep class versioned.host.exp.exponent.** { *; }

# ==============================================================================
# OKHTTP & OKIO
# ==============================================================================
-dontwarn okhttp3.**
-dontwarn okio.**
-keep class okhttp3.** { *; }
-keep class okio.** { *; }

# ==============================================================================
# GENERAL ANDROID
# ==============================================================================
-keepattributes Signature
-keepattributes *Annotation*
-keepattributes SourceFile,LineNumberTable
-keepattributes InnerClasses,EnclosingMethod

# Keep native methods
-keepclassmembers class * {
    native <methods>;
}

# Keep Parcelables
-keepclassmembers class * implements android.os.Parcelable {
    static ** CREATOR;
}

# Keep Serializable
-keepclassmembers class * implements java.io.Serializable {
    static final long serialVersionUID;
    private static final java.io.ObjectStreamField[] serialPersistentFields;
    private void writeObject(java.io.ObjectOutputStream);
    private void readObject(java.io.ObjectInputStream);
    java.lang.Object writeReplace();
    java.lang.Object readResolve();
}

# ==============================================================================
# SUPPRESS WARNINGS
# ==============================================================================
-dontwarn org.conscrypt.**
-dontwarn org.bouncycastle.**
-dontwarn org.openjsse.**
-dontwarn javax.annotation.**
-dontwarn sun.misc.Unsafe
