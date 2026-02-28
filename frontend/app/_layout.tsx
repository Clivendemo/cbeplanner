import React, { useEffect } from 'react';
import { Stack, useRouter, useSegments, useRootNavigationState } from 'expo-router';
import { AuthProvider, useAuth } from '../contexts/AuthContext';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { StyleSheet, View, ActivityIndicator, Text } from 'react-native';

// Auth gate component that handles navigation based on auth state
function AuthGate({ children }: { children: React.ReactNode }) {
  const { user, loading, authChecked, isAdmin } = useAuth();
  const segments = useSegments();
  const router = useRouter();
  const navigationState = useRootNavigationState();

  useEffect(() => {
    // Don't do anything until navigation is ready and auth is checked
    if (!navigationState?.key || !authChecked) return;

    const inAuthGroup = segments[0] === 'auth';
    const inAdminGroup = segments[0] === '(admin)';
    const inTeacherGroup = segments[0] === '(teacher)';
    const isIndex = segments.length === 0 || segments[0] === 'index';

    console.log('AuthGate check:', { user: user?.email, inAuthGroup, inAdminGroup, inTeacherGroup, isIndex, segments });

    if (!user) {
      // User is not authenticated
      if (!inAuthGroup && !isIndex) {
        // Redirect to login using replace to prevent back navigation issues
        console.log('Redirecting to login - no user');
        router.replace('/auth/login');
      }
    } else {
      // User is authenticated
      if (inAuthGroup || isIndex) {
        // Redirect to appropriate dashboard
        if (isAdmin) {
          console.log('Redirecting admin to admin dashboard');
          router.replace('/(admin)/dashboard');
        } else {
          console.log('Redirecting user to teacher home');
          router.replace('/(teacher)/home');
        }
      } else if (inAdminGroup && !isAdmin) {
        // Non-admin trying to access admin routes
        console.log('Non-admin trying to access admin - redirecting');
        router.replace('/(teacher)/home');
      }
    }
  }, [user, segments, authChecked, navigationState?.key, isAdmin]);

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
