import React from 'react';
import { TouchableOpacity, View, Text, StyleSheet, ActivityIndicator, Platform, ScrollView, useWindowDimensions } from 'react-native';
import { Stack, useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../../contexts/AuthContext';
import { AppLeftSidebar, AppRightSidebar } from '../../components/AppSidebars';

// Layout constants for the persistent shell (desktop only)
const LEFT_SIDEBAR_W = 180;
const MAIN_W = 950;
const RIGHT_SIDEBAR_W = 180;
const GAP = 20;
const SHELL_W = LEFT_SIDEBAR_W + MAIN_W + RIGHT_SIDEBAR_W + GAP * 2; // 1330
const SHELL_BREAKPOINT = 1280; // Below this we hide sidebars and show full-width app

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
  const { width } = useWindowDimensions();
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

  // On smaller screens, render the Stack full-bleed (no sidebars).
  if (!showSidebars) {
    return stack;
  }

  // Desktop: wrap the Stack in a centered 1330px shell with 180 / 950 / 180 columns.
  // The app itself only operates inside the central 950 column.
  return (
    <View style={styles.shellRoot}>
      {/* Decorative soft indigo background that blends with the #6366F1 header */}
      <View style={styles.shellBg} pointerEvents="none" />

      <ScrollView
        style={styles.shellScroll}
        contentContainerStyle={styles.shellScrollContent}
        showsVerticalScrollIndicator={false}
      >
        <View style={styles.shellRow}>
          {/* Left sidebar */}
          <View style={[styles.sideCol, { width: LEFT_SIDEBAR_W }]}>
            <AppLeftSidebar />
          </View>

          {/* Central app column — the Stack renders here, untouched */}
          <View style={[styles.mainCol, { width: MAIN_W }]}>
            {stack}
          </View>

          {/* Right sidebar */}
          <View style={[styles.sideCol, { width: RIGHT_SIDEBAR_W }]}>
            <AppRightSidebar />
          </View>
        </View>
      </ScrollView>
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
    backgroundColor: '#EEF2FF', // indigo-50, blends with #6366F1 header
    position: 'relative',
  },
  shellBg: {
    // Subtle layered wash — soft indigo → slate → violet
    position: 'absolute',
    top: 0, left: 0, right: 0, bottom: 0,
    backgroundColor: '#EEF2FF',
    backgroundImage: 'radial-gradient(1000px 600px at 10% 0%, #E0E7FF 0%, transparent 60%), radial-gradient(1000px 600px at 90% 100%, #F5F3FF 0%, transparent 60%), linear-gradient(180deg, #EEF2FF 0%, #F8FAFC 100%)',
  } as any,
  shellScroll: { flex: 1 },
  shellScrollContent: {
    flexGrow: 1,
    alignItems: 'center',
    paddingVertical: 24,
  },
  shellRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 20,
    width: 1330, // LEFT + GAP + MAIN + GAP + RIGHT
    maxWidth: '100%',
  },
  sideCol: {
    flexShrink: 0,
    paddingTop: 4,
  },
  mainCol: {
    flexShrink: 0,
    minHeight: '100vh' as any,
    backgroundColor: '#FFFFFF',
    borderRadius: 14,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.04,
    shadowRadius: 12,
  },
});
