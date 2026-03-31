import React, { useEffect, useRef, useState } from 'react';
import { Stack, useRouter, useSegments, useRootNavigationState } from 'expo-router';
import { AuthProvider, useAuth } from '../contexts/AuthContext';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { StyleSheet, View, ActivityIndicator, Text, Platform } from 'react-native';

// Auth gate component that handles navigation based on auth state
function AuthGate({ children }: { children: React.ReactNode }) {
  const { user, loading, authChecked, isAdmin } = useAuth();
  const segments = useSegments();
  const router = useRouter();
  const navigationState = useRootNavigationState();
  const hasNavigated = useRef(false);
  const [isReady, setIsReady] = useState(false);

  // Handle navigation readiness for both web and native
  useEffect(() => {
    // On web, navigationState might not have a key immediately
    if (Platform.OS === 'web') {
      // Give a small delay for web to initialize
      const timer = setTimeout(() => setIsReady(true), 100);
      return () => clearTimeout(timer);
    } else {
      // On native, wait for navigation state
      if (navigationState?.key) {
        setIsReady(true);
      }
    }
  }, [navigationState?.key]);

  useEffect(() => {
    // Don't do anything until ready and auth is checked
    if (!isReady || !authChecked) return;

    const inAuthGroup = segments[0] === 'auth';
    const inAdminGroup = segments[0] === '(admin)';
    const inTeacherGroup = segments[0] === '(teacher)';
    const isIndex = segments.length === 0 || segments[0] === 'index';

    // Prevent double navigation
    if (hasNavigated.current) return;

    if (!user) {
      // User is not authenticated
      if (!inAuthGroup && !isIndex) {
        // Redirect to login using replace to prevent back navigation issues
        hasNavigated.current = true;
        router.replace('/auth/login');
      }
    } else {
      // User is authenticated
      if (inAuthGroup || isIndex) {
        // Redirect to appropriate dashboard
        hasNavigated.current = true;
        if (isAdmin) {
          router.replace('/(admin)/dashboard');
        } else {
          router.replace('/(teacher)/dashboard');
        }
      } else if (inAdminGroup && !isAdmin) {
        // Non-admin trying to access admin routes
        hasNavigated.current = true;
        router.replace('/(teacher)/dashboard');
      }
    }
  }, [user, segments, authChecked, isReady, isAdmin]);

  // Reset navigation flag when user changes (login/logout)
  useEffect(() => {
    hasNavigated.current = false;
  }, [user]);

  // Show loading screen while checking auth
  if (loading || !authChecked) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#6366F1" />
        <Text style={styles.loadingText}>Loading...</Text>
      </View>
    );
  }

  return <>{children}</>;
}

export default function RootLayout() {
  return (
    <GestureHandlerRootView style={styles.container}>
      <AuthProvider>
        <AuthGate>
          <Stack 
            screenOptions={{ 
              headerShown: false,
              animation: 'slide_from_right',
              gestureEnabled: true
            }}
          >
            <Stack.Screen name="index" options={{ gestureEnabled: false }} />
            <Stack.Screen name="auth/login" options={{ gestureEnabled: false }} />
            <Stack.Screen name="auth/signup" options={{ gestureEnabled: false }} />
            <Stack.Screen name="(teacher)" options={{ gestureEnabled: false }} />
            <Stack.Screen name="(admin)" options={{ gestureEnabled: false }} />
          </Stack>
        </AuthGate>
      </AuthProvider>
    </GestureHandlerRootView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F9FAFB'
  },
  loadingText: {
    marginTop: 12,
    fontSize: 14,
    color: '#6B7280'
  }
});
