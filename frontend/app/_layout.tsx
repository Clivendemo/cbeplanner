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
  const hasNavigated = useRef(false);

  useEffect(() => {
    // Don't do anything until auth is checked
    if (!authChecked) return;

    const inAuthGroup = segments[0] === 'auth';
    const inAdminGroup = segments[0] === '(admin)';
    const isIndex = segments.length === 0 || segments[0] === 'index';

    // Prevent double navigation
    if (hasNavigated.current) return;

    // Small delay for web to ensure router is ready
    const timer = setTimeout(() => {
      if (hasNavigated.current) return;
      
      if (!user) {
        // User is not authenticated - redirect to login if not already there
        if (!inAuthGroup) {
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
    }, Platform.OS === 'web' ? 100 : 0);

    return () => clearTimeout(timer);
  }, [user, segments, authChecked, isAdmin]);

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
