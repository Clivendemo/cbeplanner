import React, { useCallback } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  useWindowDimensions,
} from 'react-native';
import { useRouter } from 'expo-router';
import { useAuth } from '../../contexts/AuthContext';
import { Ionicons } from '@expo/vector-icons';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useFocusEffect } from '@react-navigation/native';

// ---------------------------------------------------------------------------
// Sidebar navigation items
// ---------------------------------------------------------------------------
//
// Order, labels and destinations are intentionally fixed — these are the
// seven top-level pages a teacher reaches from the dashboard. Each row
// pushes the existing expo-router route used by the legacy tile grid so
// the rest of the app is unaffected.

type MenuItem = {
  title: string;
  icon: string;
  color: string;
  route: string;
  badge?: string;
};

// Mobile breakpoint: on narrow screens the sidebar collapses to a single
// vertical column above the welcome pane (no overlay, no hamburger).
const MOBILE_BREAKPOINT = 768;

export default function Dashboard() {
  const router = useRouter();
  const { user, refreshProfile } = useAuth();
  const { width } = useWindowDimensions();
  const isMobile = width < MOBILE_BREAKPOINT;

  // Refresh wallet/free-lesson counters every time the dashboard regains
  // focus (e.g. returning here after a top-up or a generation).
  useFocusEffect(
    useCallback(() => {
      refreshProfile();
    }, []),
  );

  const freeLessonsRemaining = user?.freeLessonsRemaining ?? 0;

  const menuItems: MenuItem[] = [
    {
      title: 'Schemes of Work',
      icon: 'calendar',
      color: '#5C6BC0',
      route: '/(teacher)/schemes',
    },
    {
      title: 'My Schemes',
      icon: 'albums',
      color: '#5C6BC0',
      route: '/(teacher)/my-schemes',
    },
    {
      title: 'Create Lesson Plan',
      icon: 'document-text',
      color: '#5C6BC0',
      route: '/(teacher)/home',
      badge: freeLessonsRemaining > 0 ? `${freeLessonsRemaining} Free` : undefined,
    },
    {
      title: 'My Lesson Plans',
      icon: 'folder-open',
      color: '#F59E0B',
      route: '/(teacher)/lessons',
    },
    {
      title: 'Generate Notes',
      icon: 'create',
      color: '#10B981',
      route: '/(teacher)/notes',
    },
    {
      title: 'Revision Papers',
      icon: 'school',
      color: '#EF4444',
      route: '/(teacher)/revision',
    },
    {
      title: 'Profile',
      icon: 'person-circle',
      color: '#06B6D4',
      route: '/(teacher)/profile',
    },
  ];

  const SideMenu = (
    <View
      style={[
        styles.sidebar,
        isMobile ? styles.sidebarMobile : styles.sidebarDesktop,
      ]}
      data-testid="dashboard-sidebar"
    >
      <Text style={styles.sidebarHeading}>Workspace</Text>
      {menuItems.map((item) => (
        <TouchableOpacity
          key={item.route}
          style={styles.menuItem}
          onPress={() => router.push(item.route as any)}
          activeOpacity={0.7}
          data-testid={`dashboard-menu-${item.title.toLowerCase().replace(/\s+/g, '-')}`}
          testID={`dashboard-menu-${item.title.toLowerCase().replace(/\s+/g, '-')}`}
        >
          <View style={[styles.menuIcon, { backgroundColor: item.color + '18' }]}>
            <Ionicons name={item.icon as any} size={18} color={item.color} />
          </View>
          <Text style={styles.menuLabel} numberOfLines={1}>
            {item.title}
          </Text>
          {item.badge && (
            <View style={[styles.menuBadge, { backgroundColor: item.color }]}>
              <Text style={styles.menuBadgeText}>{item.badge}</Text>
            </View>
          )}
          <Ionicons
            name="chevron-forward"
            size={16}
            color="#94A3B8"
            style={styles.menuChevron}
          />
        </TouchableOpacity>
      ))}
    </View>
  );

  const WelcomePane = (
    <ScrollView
      style={styles.welcomePane}
      contentContainerStyle={styles.welcomeContent}
      showsVerticalScrollIndicator={false}
    >
      {/* Greeting */}
      <View style={styles.greetingBlock}>
        <Text style={styles.greetingHello}>Welcome back,</Text>
        <Text style={styles.greetingName}>
          {user?.firstName || ''} {user?.lastName || ''}
        </Text>
        {!!user?.schoolName && (
          <View style={styles.schoolPill}>
            <Ionicons name="business" size={13} color="#5C6BC0" />
            <Text style={styles.schoolPillText}>{user.schoolName}</Text>
          </View>
        )}
      </View>

      {/* Stats row */}
      <View style={styles.statsRow}>
        <View style={styles.statCard}>
          <Ionicons name="wallet" size={20} color="#5C6BC0" />
          <Text style={styles.statValue}>KES {user?.walletBalance ?? 0}</Text>
          <Text style={styles.statLabel}>Wallet Balance</Text>
        </View>
        <View style={styles.statCard}>
          <Ionicons name="checkmark-circle" size={20} color="#10B981" />
          <Text style={styles.statValue}>
            {freeLessonsRemaining > 0 ? `${freeLessonsRemaining} Left` : 'Used'}
          </Text>
          <Text style={styles.statLabel}>Free Lessons</Text>
        </View>
      </View>

      {/* Hint card */}
      <View style={styles.hintCard}>
        <Ionicons name="bulb-outline" size={18} color="#E65100" />
        <Text style={styles.hintText}>
          Pick a section from the menu to get started. Need help?
          {'  '}
          <Text
            style={styles.hintLink}
            onPress={() => router.push('/(teacher)/profile' as any)}
          >
            Visit Profile
          </Text>{' '}
          for support.
        </Text>
      </View>
    </ScrollView>
  );

  return (
    <SafeAreaView style={styles.container} edges={['bottom']}>
      <View
        style={[
          styles.layout,
          isMobile ? styles.layoutMobile : styles.layoutDesktop,
        ]}
      >
        {SideMenu}
        {WelcomePane}
      </View>
    </SafeAreaView>
  );
}

// ---------------------------------------------------------------------------
// Styles
// ---------------------------------------------------------------------------

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F3F4FF' },

  // Layout shell
  layout: { flex: 1 },
  layoutDesktop: { flexDirection: 'row' },
  layoutMobile: { flexDirection: 'column' },

  // Sidebar
  sidebar: {
    backgroundColor: '#FFFFFF',
    borderRightWidth: 1,
    borderRightColor: '#E5E7EB',
    paddingVertical: 16,
    paddingHorizontal: 12,
  },
  sidebarDesktop: { width: 260 },
  sidebarMobile: {
    width: '100%',
    borderRightWidth: 0,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  sidebarHeading: {
    fontSize: 11,
    fontWeight: '700',
    color: '#64748B',
    textTransform: 'uppercase',
    letterSpacing: 0.6,
    marginBottom: 10,
    marginLeft: 8,
  },
  menuItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 10,
    paddingHorizontal: 10,
    borderRadius: 8,
    marginBottom: 4,
    backgroundColor: 'transparent',
  },
  menuIcon: {
    width: 32,
    height: 32,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  menuLabel: {
    flex: 1,
    fontSize: 14,
    fontWeight: '600',
    color: '#1E293B',
  },
  menuBadge: {
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 10,
    marginRight: 6,
  },
  menuBadgeText: {
    color: '#FFFFFF',
    fontSize: 10,
    fontWeight: '700',
  },
  menuChevron: { marginLeft: 4 },

  // Welcome pane
  welcomePane: { flex: 1, backgroundColor: '#F3F4FF' },
  welcomeContent: { padding: 20 },
  greetingBlock: { marginBottom: 20 },
  greetingHello: { fontSize: 14, color: '#64748B', marginBottom: 4 },
  greetingName: { fontSize: 24, fontWeight: '800', color: '#1E293B' },
  schoolPill: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 8,
    paddingVertical: 4,
    paddingHorizontal: 10,
    borderRadius: 999,
    backgroundColor: '#E0E7FF',
    alignSelf: 'flex-start',
  },
  schoolPillText: {
    marginLeft: 6,
    fontSize: 12,
    fontWeight: '600',
    color: '#3730A3',
  },

  // Stats
  statsRow: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 20,
    flexWrap: 'wrap',
  },
  statCard: {
    flex: 1,
    minWidth: 140,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    alignItems: 'flex-start',
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  statValue: { fontSize: 18, fontWeight: '700', color: '#1E293B', marginTop: 6 },
  statLabel: { fontSize: 12, color: '#64748B', marginTop: 2 },

  // Hint card
  hintCard: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    backgroundColor: '#FFF7ED',
    borderColor: '#FED7AA',
    borderWidth: 1,
    borderRadius: 12,
    padding: 14,
    gap: 10,
  },
  hintText: {
    flex: 1,
    fontSize: 13,
    color: '#7C2D12',
    lineHeight: 18,
  },
  hintLink: {
    color: '#E65100',
    fontWeight: '700',
    textDecorationLine: 'underline',
  },
});
