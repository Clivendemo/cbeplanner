/**
 * TeacherSideNav — the persistent dark navigation column shown on every
 * teacher route at desktop widths (>= SHELL_BREAKPOINT in _layout.tsx).
 *
 * Visual reference: the "Contrast" component-library sidebar the user
 * shared on 2026-05-25 — charcoal background, light-grey icons + labels,
 * active row breaks out as a white pill with dark text.
 *
 * Wired up via expo-router's `usePathname` so the active highlight tracks
 * the user as they navigate. All routes match those previously used by
 * the dashboard tile grid — no route renames.
 */
import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
} from 'react-native';
import { useRouter, usePathname } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../contexts/AuthContext';

type MenuItem = {
  title: string;
  icon: string;
  route: string;
  badge?: string;
};

const COLORS = {
  sidebarBg: '#111827',
  sidebarText: '#E5E7EB',
  sidebarIcon: '#9CA3AF',
  activeBg: '#FFFFFF',
  activeText: '#111827',
  activeIcon: '#1E293B',
  divider: '#1F2937',
};

export function TeacherSideNav() {
  const router = useRouter();
  const pathname = usePathname();
  const { user } = useAuth();
  const freeLessonsRemaining = user?.freeLessonsRemaining ?? 0;

  const menuItems: MenuItem[] = [
    {
      title: 'Dashboard',
      icon: 'grid-outline',
      route: '/(teacher)/dashboard',
    },
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

  const isActive = (route: string) => {
    if (!pathname) return false;
    // Strip the leading group "(teacher)" since expo-router resolves it
    // away in the pathname.
    const normalize = (p: string) => p.replace('/(teacher)', '');
    const normalizedPath = normalize(pathname);
    const normalizedRoute = normalize(route);
    if (normalizedPath === normalizedRoute) return true;
    // Treat detail screens as part of their parent (e.g.
    // /scheme-detail counts as Schemes of Work being active).
    if (normalizedRoute === '/schemes' && normalizedPath === '/scheme-detail') return true;
    if (normalizedRoute === '/my-schemes' && normalizedPath === '/scheme-detail') return true;
    if (normalizedRoute === '/lessons' && normalizedPath === '/lesson-detail') return true;
    return false;
  };

  return (
    <View style={styles.sidebar} data-testid="teacher-side-nav">
      <View style={styles.brandRow}>
        <Ionicons name="menu" size={20} color={COLORS.sidebarText} />
        <Text style={styles.brandText}>CBE Planner</Text>
      </View>

      <View style={styles.brandDivider} />

      <ScrollView style={{ flex: 1 }} showsVerticalScrollIndicator={false}>
        {menuItems.map((item) => {
          const active = isActive(item.route);
          const slug = item.title.toLowerCase().replace(/\s+/g, '-');
          return (
            <TouchableOpacity
              key={item.route}
              style={[styles.menuItem, active && styles.menuItemActive]}
              onPress={() => router.push(item.route as any)}
              activeOpacity={0.7}
              data-testid={`teacher-nav-${slug}`}
              testID={`teacher-nav-${slug}`}
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
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  sidebar: {
    flex: 1,
    backgroundColor: COLORS.sidebarBg,
    paddingVertical: 14,
    paddingHorizontal: 12,
  },
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
});
