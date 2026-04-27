import React from 'react';
import { TouchableOpacity, View, Text, StyleSheet, ActivityIndicator, Platform, useWindowDimensions, ScrollView } from 'react-native';
import { Stack, useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../../contexts/AuthContext';
import { AppLeftSidebar, AppRightSidebar } from '../../components/AppSidebars';

// Layout constants for the persistent shell (desktop only)
const LEFT_SIDEBAR_W = 180;
const MAIN_W = 950;
const RIGHT_SIDEBAR_W = 180;
const GAP = 16;
const SHELL_BREAKPOINT = 1180; // Below this we hide sidebars and show full-width app

// Header Right component - defined outside to prevent re-renders
function HeaderRight() {
  const router = useRouter();
  const { user } = useAuth();
  
  return (
    <View style={styles.headerRight}>
      <View style={styles.walletBadge}>
        <Ionicons name="wallet-outline" size={14} color="#FFFFFF" />
        <Text style={styles.walletText}>{user?.walletBalance || 0} KES</Text>
      </View>
      <TouchableOpacity 
        style={styles.profileButton}
        onPress={() => router.push('/(teacher)/profile')}
      >
        <View style={styles.profileIconContainer}>
          <Ionicons name="person-circle" size={28} color="#FFFFFF" />
        </View>
      </TouchableOpacity>
    </View>
  );
}

// Custom back button for consistent navigation
function HeaderBack() {
  const router = useRouter();
  
  return (
    <TouchableOpacity 
      style={styles.backButton}
      onPress={() => router.back()}
      hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
    >
      <Ionicons name="arrow-back" size={24} color="#FFFFFF" />
    </TouchableOpacity>
  );
}

// Empty header for profile page
function EmptyHeader() {
  return null;
}

export default function TeacherLayout() {
  const { user, loading, authChecked } = useAuth();
  const { width, height } = useWindowDimensions();
  const showSidebars = width >= SHELL_BREAKPOINT;

  // Show loading while checking auth
  if (loading || !authChecked) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#6366F1" />
        <Text style={styles.loadingText}>Loading...</Text>
      </View>
    );
  }

  // If no user, AuthGate will redirect — show placeholder
  if (!user) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#6366F1" />
        <Text style={styles.loadingText}>Redirecting...</Text>
      </View>
    );
  }

  const stack = (
    <Stack
      screenOptions={{
        headerStyle: {
          backgroundColor: '#6366F1'
        },
        headerTintColor: '#FFFFFF',
        headerTitleStyle: {
          fontWeight: 'bold'
        },
        headerRight: HeaderRight,
        headerLeft: HeaderBack,
        animation: 'slide_from_right',
        gestureEnabled: true,
        gestureDirection: 'horizontal',
        // Improve animation performance
        animationDuration: 250,
        // Better gesture settings for mobile
        fullScreenGestureEnabled: Platform.OS === 'ios',
        contentStyle: { backgroundColor: '#FFFFFF' },
      }}
    >
      <Stack.Screen
        name="dashboard"
        options={{
          title: 'CBE Planner',
          headerShown: true,
          gestureEnabled: false,
          headerLeft: EmptyHeader // No back button on dashboard
        }}
      />
      <Stack.Screen
        name="home"
        options={{
          title: 'Create Lesson Plan'
        }}
      />
      <Stack.Screen
        name="notes"
        options={{
          title: 'Generate Notes'
        }}
      />
      <Stack.Screen
        name="lessons"
        options={{
          title: 'My Lesson Plans'
        }}
      />
      <Stack.Screen
        name="profile"
        options={{
          title: 'My Profile',
          headerRight: EmptyHeader
        }}
      />
      <Stack.Screen
        name="schemes"
        options={{
          title: 'Schemes of Work'
        }}
      />
      <Stack.Screen
        name="my-schemes"
        options={{
          title: 'My Schemes'
        }}
      />
      <Stack.Screen
        name="scheme-detail"
        options={{
          title: 'Scheme of Work'
        }}
      />
      <Stack.Screen
        name="lesson-detail"
        options={{
          title: 'Lesson Plan'
        }}
      />
      <Stack.Screen
        name="revision"
        options={{
          title: 'Revision Papers'
        }}
      />
    </Stack>
  );

  // Mobile/tablet: Stack covers the full viewport. Sidebars sit below in an
  // outer scroll so users can swipe up to see them.
  if (!showSidebars) {
    return (
      <ScrollView
        style={styles.mobileRoot}
        contentContainerStyle={{ flexGrow: 1 }}
        showsVerticalScrollIndicator={false}
      >
        <View style={{ height, backgroundColor: '#FFFFFF' }}>
          {stack}
        </View>
        <View style={styles.mobileSidebars}>
          <AppLeftSidebar />
          <AppRightSidebar />
        </View>
      </ScrollView>
    );
  }

  // Desktop: wrap the Stack in a centered, responsive shell.
  // Left & right sidebars are fixed 180px. Main column grows/shrinks with the
  // viewport so content always fits without horizontal scroll or zooming.
  return (
    <View style={styles.shellRoot}>
      <View style={styles.shellRow}>
        {/* Left sidebar */}
        <View style={[styles.sideCol, { width: LEFT_SIDEBAR_W }]}>
          <AppLeftSidebar />
        </View>

        {/* Central app column — flexes to fill available space up to MAIN_W */}
        <View style={[styles.mainCol]}>
          {stack}
        </View>

        {/* Right sidebar */}
        <View style={[styles.sideCol, { width: RIGHT_SIDEBAR_W }]}>
          <AppRightSidebar />
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
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
  },
  headerRight: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 8
  },
  profileButton: {
    padding: 4
  },
  profileIconContainer: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: 'rgba(255,255,255,0.2)',
    justifyContent: 'center',
    alignItems: 'center'
  },
  walletBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.2)',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
    marginRight: 10
  },
  walletText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '600',
    marginLeft: 4
  },
  backButton: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    marginLeft: 4
  },

  // ===== Persistent shell (desktop only) =====
  shellRoot: {
    flex: 1,
    backgroundColor: 'transparent', // body bg shows through (royal blue gradient)
  },
  shellRow: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'stretch',
    justifyContent: 'center',
    gap: GAP,
    paddingHorizontal: GAP,
    paddingVertical: GAP,
  },
  // Side columns now feel like 3D panels lifted off the page —
  // glass background + multi-layer shadow + cyan rim-light on the top edge
  // catches the navy "ambient light" and crisps the 3D feel.
  sideCol: {
    flexShrink: 0,
    paddingTop: 4,
    backgroundColor: 'rgba(255, 255, 255, 0.96)',
    borderRadius: 14,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.6)',
    // @ts-ignore web-only shadow stack — cyan rim + deep navy drop
    boxShadow:
      '0 1.5px 0 rgba(125, 211, 252, 0.55) inset,' +
      ' 0 1px 0 rgba(255,255,255,0.85) inset,' +
      ' 0 18px 36px -10px rgba(3, 16, 42, 0.60),' +
      ' 0 8px 16px -8px rgba(3, 16, 42, 0.45),' +
      ' 0 2px 4px rgba(3, 16, 42, 0.22)',
    // @ts-ignore web-only — graceful slow lift
    transition: 'transform 220ms ease, box-shadow 220ms ease',
  },
  mainCol: {
    flex: 1,
    maxWidth: MAIN_W,
    minWidth: 0,
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.6)',
    overflow: 'hidden',
    // @ts-ignore web-only — main panel sits highest, brightest cyan rim
    boxShadow:
      '0 2px 0 rgba(125, 211, 252, 0.6) inset,' +
      ' 0 1px 0 rgba(255,255,255,0.95) inset,' +
      ' 0 28px 56px -12px rgba(3, 16, 42, 0.70),' +
      ' 0 14px 28px -10px rgba(3, 16, 42, 0.55),' +
      ' 0 4px 8px rgba(3, 16, 42, 0.25)',
  },

  // Mobile/tablet shell (below 1180px): Stack is viewport-height, sidebars below
  mobileRoot: {
    flex: 1,
    backgroundColor: 'transparent',
  },
  mobileSidebars: {
    padding: 16,
    gap: 14,
  },
});
