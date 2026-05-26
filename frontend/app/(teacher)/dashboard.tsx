import React, { useCallback } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  useWindowDimensions,
} from 'react-native';
import { useRouter, usePathname } from 'expo-router';
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
// pushes the existing expo-router route used by the legacy tile grid.

type MenuItem = {
  title: string;
  icon: string;
  route: string;
  badge?: string;
};

// Mobile breakpoint: on narrow screens the dark sidebar stacks on top of
// the main pane as a full-width vertical column.
const MOBILE_BREAKPOINT = 768;

// Theme colours for the dark editorial style modelled on the reference UI.
const COLORS = {
  sidebarBg: '#111827',     // charcoal — softer than pure black, icons stay readable
  sidebarBgHover: '#1F2937',
  sidebarText: '#E5E7EB',
  sidebarIcon: '#9CA3AF',
  activeBg: '#FFFFFF',
  activeText: '#111827',
  activeIcon: '#1E293B',
  divider: '#1F2937',
  mainBg: '#FFFFFF',
  mainTextPrimary: '#111827',
  mainTextSecondary: '#6B7280',
  pillBg: '#F3F4F6',
  pillText: '#374151',
  hintBg: '#FFF7ED',
  hintBorder: '#FED7AA',
  hintText: '#7C2D12',
  hintAccent: '#E65100',
};

export default function Dashboard() {
  const router = useRouter();
  const pathname = usePathname();
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
    { title: 'Schemes of Work', icon: 'calendar-outline', route: '/(teacher)/schemes' },
    { title: 'My Schemes', icon: 'albums-outline', route: '/(teacher)/my-schemes' },
    {
      title: 'Create Lesson Plan',
      icon: 'document-text-outline',
      route: '/(teacher)/home',
      badge: freeLessonsRemaining > 0 ? `${freeLessonsRemaining}` : undefined,
    },
    { title: 'My Lesson Plans', icon: 'folder-open-outline', route: '/(teacher)/lessons' },
    { title: 'Generate Notes', icon: 'create-outline', route: '/(teacher)/notes' },
    { title: 'Revision Papers', icon: 'school-outline', route: '/(teacher)/revision' },
    { title: 'Profile', icon: 'person-circle-outline', route: '/(teacher)/profile' },
  ];

  // Active-route detection — if the user is browsing /(teacher)/schemes,
  // the Schemes of Work row gets the white-pill treatment. Dashboard is
  // not in the menu, so on /(teacher)/dashboard nothing is active.
  const isActive = (route: string) => {
    if (!pathname) return false;
    // Strip the leading group "(teacher)" since expo-router resolves it
    // away in the pathname. Compare on the trailing segment.
    const normalize = (p: string) => p.replace('/(teacher)', '');
    return normalize(pathname) === normalize(route);
  };

  const SideMenu = (
    <View
      style={[
        styles.sidebar,
        isMobile ? styles.sidebarMobile : styles.sidebarDesktop,
      ]}
      data-testid="dashboard-sidebar"
    >
      {/* Brand header */}
      <View style={styles.brandRow}>
        <Ionicons name="menu" size={20} color={COLORS.sidebarText} />
        <Text style={styles.brandText}>CBE Planner</Text>
      </View>

      <View style={styles.brandDivider} />

      {/* Menu items */}
      <View style={isMobile ? null : styles.menuList}>
        {menuItems.map((item) => {
          const active = isActive(item.route);
          return (
            <TouchableOpacity
              key={item.route}
              style={[styles.menuItem, active && styles.menuItemActive]}
              onPress={() => router.push(item.route as any)}
              activeOpacity={0.7}
              data-testid={`dashboard-menu-${item.title.toLowerCase().replace(/\s+/g, '-')}`}
              testID={`dashboard-menu-${item.title.toLowerCase().replace(/\s+/g, '-')}`}
            >
              <Ionicons
                name={item.icon as any}
                size={18}
                color={active ? COLORS.activeIcon : COLORS.sidebarIcon}
                style={styles.menuIcon}
              />
              <Text
                style={[styles.menuLabel, active && styles.menuLabelActive]}
                numberOfLines={1}
              >
                {item.title}
              </Text>
              {item.badge && (
                <View style={[styles.menuBadge, active && styles.menuBadgeActive]}>
                  <Text style={[styles.menuBadgeText, active && styles.menuBadgeTextActive]}>
                    {item.badge}
                  </Text>
                </View>
              )}
            </TouchableOpacity>
          );
        })}
      </View>
    </View>
  );

  const WelcomePane = (
    <ScrollView
      style={styles.mainPane}
      contentContainerStyle={styles.mainContent}
      showsVerticalScrollIndicator={false}
    >
      {/* Greeting block */}
      <View style={styles.greetingBlock}>
        <Text style={styles.greetingHello}>Welcome back,</Text>
        <Text style={styles.greetingName}>
          {user?.firstName || ''} {user?.lastName || ''}
        </Text>
        {!!user?.schoolName && (
          <View style={styles.schoolPill}>
            <Ionicons name="business-outline" size={13} color={COLORS.pillText} />
            <Text style={styles.schoolPillText}>{user.schoolName}</Text>
          </View>
        )}
      </View>

      <View style={styles.thinDivider} />

      {/* Stats row */}
      <View style={styles.statsRow}>
        <View style={styles.statCard}>
          <Ionicons name="wallet-outline" size={20} color={COLORS.mainTextPrimary} />
          <Text style={styles.statValue}>KES {user?.walletBalance ?? 0}</Text>
          <Text style={styles.statLabel}>Wallet Balance</Text>
        </View>
        <View style={styles.statCard}>
          <Ionicons name="checkmark-circle-outline" size={20} color={COLORS.mainTextPrimary} />
          <Text style={styles.statValue}>
            {freeLessonsRemaining > 0 ? `${freeLessonsRemaining} Left` : 'Used'}
          </Text>
          <Text style={styles.statLabel}>Free Lessons</Text>
        </View>
      </View>

      {/* Hint card */}
      <View style={styles.hintCard}>
        <Ionicons name="bulb-outline" size={18} color={COLORS.hintAccent} />
        <Text style={styles.hintText}>
          Pick a section from the menu to get started. Need help?{'  '}
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
        {/* On desktop the persistent dark nav lives in the global teacher
            shell (_layout.tsx). Embedding it again here would render two
            sidebars side-by-side. Mobile widths skip the shell sidebar,
            so the dashboard still renders the menu inline for those
            users. */}
        {isMobile && SideMenu}
        {WelcomePane}
      </View>
    </SafeAreaView>
  );
}

// ---------------------------------------------------------------------------
// Styles
// ---------------------------------------------------------------------------

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.mainBg },

  // Layout shell
  layout: { flex: 1 },
  layoutDesktop: { flexDirection: 'row' },
  layoutMobile: { flexDirection: 'column' },

  // Sidebar
  sidebar: {
    backgroundColor: COLORS.sidebarBg,
    paddingVertical: 14,
    paddingHorizontal: 12,
  },
  sidebarDesktop: { width: 260, minHeight: '100%' },
  sidebarMobile: { width: '100%' },

  // Brand header
  brandRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 10,
    paddingHorizontal: 8,
  },
  brandText: {
    marginLeft: 12,
    color: COLORS.sidebarText,
    fontSize: 16,
    fontWeight: '700',
    letterSpacing: 0.3,
  },
  brandDivider: {
    height: 1,
    backgroundColor: COLORS.divider,
    marginVertical: 10,
  },

  // Menu
  menuList: {},
  menuItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 11,
    paddingHorizontal: 14,
    borderRadius: 8,
    marginBottom: 2,
    backgroundColor: 'transparent',
  },
  menuItemActive: {
    backgroundColor: COLORS.activeBg,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.06,
    shadowRadius: 2,
    elevation: 1,
  },
  menuIcon: { marginRight: 14 },
  menuLabel: {
    flex: 1,
    fontSize: 14,
    fontWeight: '500',
    color: COLORS.sidebarText,
  },
  menuLabelActive: { color: COLORS.activeText, fontWeight: '700' },
  menuBadge: {
    paddingHorizontal: 7,
    paddingVertical: 1,
    borderRadius: 999,
    backgroundColor: '#E65100',
    minWidth: 20,
    alignItems: 'center',
  },
  menuBadgeActive: { backgroundColor: '#FED7AA' },
  menuBadgeText: { color: '#FFFFFF', fontSize: 10, fontWeight: '700' },
  menuBadgeTextActive: { color: '#7C2D12' },

  // Main pane
  mainPane: { flex: 1, backgroundColor: COLORS.mainBg },
  mainContent: { paddingHorizontal: 40, paddingVertical: 32, maxWidth: 880 },

  // Greeting
  greetingBlock: { marginBottom: 18 },
  greetingHello: {
    fontSize: 13,
    color: COLORS.mainTextSecondary,
    marginBottom: 2,
    textTransform: 'uppercase',
    letterSpacing: 1,
  },
  greetingName: {
    fontSize: 28,
    fontWeight: '700',
    color: COLORS.mainTextPrimary,
    marginBottom: 8,
  },
  schoolPill: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: COLORS.pillBg,
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 999,
    alignSelf: 'flex-start',
  },
  schoolPillText: {
    marginLeft: 6,
    fontSize: 12,
    fontWeight: '600',
    color: COLORS.pillText,
  },

  thinDivider: {
    height: 1,
    backgroundColor: '#E5E7EB',
    marginVertical: 24,
  },

  // Stats
  statsRow: {
    flexDirection: 'row',
    gap: 16,
    marginBottom: 24,
    flexWrap: 'wrap',
  },
  statCard: {
    flex: 1,
    minWidth: 200,
    backgroundColor: COLORS.mainBg,
    borderRadius: 10,
    padding: 18,
    alignItems: 'flex-start',
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  statValue: {
    fontSize: 20,
    fontWeight: '700',
    color: COLORS.mainTextPrimary,
    marginTop: 8,
  },
  statLabel: {
    fontSize: 12,
    color: COLORS.mainTextSecondary,
    marginTop: 2,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },

  // Hint card
  hintCard: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    backgroundColor: COLORS.hintBg,
    borderColor: COLORS.hintBorder,
    borderWidth: 1,
    borderRadius: 10,
    padding: 14,
    gap: 10,
  },
  hintText: {
    flex: 1,
    fontSize: 13,
    color: COLORS.hintText,
    lineHeight: 19,
  },
  hintLink: {
    color: COLORS.hintAccent,
    fontWeight: '700',
    textDecorationLine: 'underline',
  },
});
