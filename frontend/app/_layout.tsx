import React, { useEffect, useRef, useState } from 'react';
import { Stack, useRouter, useSegments, useRootNavigationState } from 'expo-router';
import { AuthProvider, useAuth } from '../contexts/AuthContext';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { StyleSheet, View, ActivityIndicator, Text, Platform } from 'react-native';
import { AppChrome } from '../components/AppChrome';
import { ErrorBoundary } from '../components/ErrorBoundary';

// Auth gate component that handles navigation based on auth state
function AuthGate({ children }: { children: React.ReactNode }) {
  const { user, loading, authChecked, isAdmin } = useAuth();
  const segments = useSegments();
  const router = useRouter();
  const lastUserRef = useRef<string | null>(null);
  const navigationPending = useRef(false);

  useEffect(() => {
    // Don't do anything until auth is checked
    if (!authChecked) return;
    // Prevent re-entrant navigation
    if (navigationPending.current) return;

    const inAuthGroup = segments[0] === 'auth';
    const inAdminGroup = segments[0] === '(admin)';
    const isIndex = segments.length === 0 || segments[0] === 'index';

    // Determine the target user key (null = logged out, else the user id)
    const currentUserKey = user?.id || null;
    const userChanged = currentUserKey !== lastUserRef.current;

    // Only navigate when: user state actually changed, or on initial load, or wrong route group
    const needsRedirect = userChanged || (!user && !inAuthGroup) || (user && (inAuthGroup || isIndex)) || (inAdminGroup && !isAdmin);
    if (!needsRedirect) return;

    // Small delay for web to ensure router is ready
    const timer = setTimeout(() => {
      if (navigationPending.current) return;
      navigationPending.current = true;
      lastUserRef.current = currentUserKey;

      if (!user) {
        if (!inAuthGroup) {
          router.replace('/auth/login');
        }
      } else {
        if (inAuthGroup || isIndex) {
          if (isAdmin) {
            router.replace('/(admin)/dashboard');
          } else {
            router.replace('/(teacher)/dashboard');
          }
        } else if (inAdminGroup && !isAdmin) {
          router.replace('/(teacher)/dashboard');
        }
      }

      // Reset lock after navigation settles
      setTimeout(() => { navigationPending.current = false; }, 300);
    }, Platform.OS === 'web' ? 100 : 0);

    return () => clearTimeout(timer);
  }, [user, segments, authChecked, isAdmin]);

  // Show loading screen while checking auth
  if (loading || !authChecked) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#5C6BC0" />
        <Text style={styles.loadingText}>Loading...</Text>
      </View>
    );
  }

  return <>{children}</>;
}

export default function RootLayout() {
  return (
    <GestureHandlerRootView style={styles.container}>
      <ErrorBoundary>
        <AuthProvider>
          <AppChrome>
            <AuthGate>
              <Stack 
                screenOptions={{ 
                  headerShown: false,
                  animation: 'slide_from_right',
                  gestureEnabled: true,
                  contentStyle: { backgroundColor: 'transparent' },
                }}
              >
                <Stack.Screen name="index" options={{ gestureEnabled: false }} />
                <Stack.Screen name="(teacher)" options={{ gestureEnabled: false }} />
                <Stack.Screen name="(admin)" options={{ gestureEnabled: false }} />
              </Stack>
            </AuthGate>
          </AppChrome>
        </AuthProvider>
      </ErrorBoundary>
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
    color: '#5A5A7A'
  }
});
