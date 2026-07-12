import React from 'react';
import { TouchableOpacity, View, Text, StyleSheet, ActivityIndicator, Platform, useWindowDimensions } from 'react-native';
import { Stack, useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../../contexts/AuthContext';
import { TeacherSideNav } from '../../components/TeacherSideNav';

// Layout constants for the persistent shell (desktop only).
// LEFT_SIDEBAR_W is the dark TeacherSideNav (formerly the AppLeftSidebar
// at 180 px) — wider now so menu labels never truncate.
const LEFT_SIDEBAR_W = 240;
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
        <ActivityIndicator size="large" color="#5C6BC0" />
        <Text style={styles.loadingText}>Loading...</Text>
      </View>
    );
  }

  // If no user, AuthGate will redirect — show placeholder
  if (!user) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#5C6BC0" />
        <Text style={styles.loadingText}>Redirecting...</Text>
      </View>
    );
  }

  const stack = (
    <Stack
      screenOptions={{
        headerStyle: {
          backgroundColor: '#283593'
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

  // Mobile/tablet: Stack covers the full viewport. Sidebar widgets used
  // to render below the page — now the dashboard hosts them inline in
  // its main pane, so we just render the stack full-width and trust each
  // route to lay out its own content.
  if (!showSidebars) {
    return (
      <View style={[styles.mobileRoot, { flex: 1 }]}>
        {stack}
      </View>
    );
  }

  // Desktop: wrap the Stack in a centered, responsive shell.
  // Left column hosts the dark persistent TeacherSideNav. The right
  // sidebar was retired — its widgets (Useful Links, Teacher's Corner,
  // Support) now live on the dashboard's main pane so the central column
  // can use the full remaining width.
  return (
    <View style={styles.shellRoot}>
      <View style={styles.shellRow}>
        {/* Left sidebar — persistent dark nav */}
        <View style={[styles.sideCol, { width: LEFT_SIDEBAR_W }]}>
          <TeacherSideNav />
        </View>

        {/* Central app column — flexes to fill all remaining space */}
        <View style={[styles.mainCol]}>
          {stack}
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
    color: '#5A5A7A'
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
    backgroundColor: '#F3F4FF', // indigo-50, blends with #5C6BC0 header
    // @ts-ignore web-only CSS: soft indigo wash
    backgroundImage:
      'radial-gradient(900px 500px at 8% 0%, #E0E7FF 0%, transparent 60%), radial-gradient(900px 500px at 92% 100%, #F3F4FF 0%, transparent 60%), linear-gradient(180deg, #F3F4FF 0%, #F8FAFC 100%)',
  },
  shellRow: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'stretch',
    gap: GAP,
    paddingHorizontal: GAP,
    paddingVertical: GAP,
  },
  sideCol: {
    flexShrink: 0,
    paddingTop: 4,
  },
  mainCol: {
    flex: 1,
    minWidth: 0, // allow the flex child to shrink below its content width
    backgroundColor: '#FFFFFF',
    borderRadius: 14,
    borderWidth: 1,
    borderColor: '#DDDDF5',
    overflow: 'hidden',
    // @ts-ignore web-only subtle shadow
    boxShadow: '0 6px 24px rgba(17, 24, 39, 0.06)',
  },

  // Mobile/tablet shell (below 1180px): Stack is viewport-height, sidebars below
  mobileRoot: {
    flex: 1,
    backgroundColor: '#F3F4FF',
    // @ts-ignore web-only CSS
    backgroundImage:
      'radial-gradient(900px 500px at 8% 0%, #E0E7FF 0%, transparent 60%), linear-gradient(180deg, #F3F4FF 0%, #F8FAFC 100%)',
  },
  mobileSidebars: {
    padding: 16,
    gap: 14,
  },
});
