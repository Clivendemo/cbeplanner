/**
 * AuthSideNav — a locked preview of the teacher navigation shown on all
 * auth screens (login, signup, reset-password).
 *
 * Every item is visually inactive and carries a lock badge. Tapping any
 * item scrolls the centre column back to the login / sign-up form so the
 * user understands they need to sign in first.
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

type MenuItem = {
  title: string;
  icon: string;
};

const COLORS = {
  sidebarBg: '#111827',
  sidebarText: '#6B7280',   // dimmed — not yet unlocked
  sidebarIcon: '#4B5563',   // dimmed
  divider: '#1F2937',
  lockIcon: '#374151',
  hoverBg: '#1F2937',
  brandText: '#E5E7EB',
};

const MENU_ITEMS: MenuItem[] = [
  { title: 'Dashboard',         icon: 'grid-outline' },
  { title: 'Schemes of Work',   icon: 'calendar-outline' },
  { title: 'My Schemes',        icon: 'albums-outline' },
  { title: 'Create Lesson Plan',icon: 'document-text-outline' },
  { title: 'My Lesson Plans',   icon: 'folder-open-outline' },
  { title: 'Generate Notes',    icon: 'create-outline' },
  { title: 'Revision Papers',   icon: 'school-outline' },
  { title: 'Profile',           icon: 'person-circle-outline' },
];

interface AuthSideNavProps {
  /** Call this to scroll / focus the auth form when a locked item is tapped */
  onLockedPress?: () => void;
}

export function AuthSideNav({ onLockedPress }: AuthSideNavProps) {
  const router = useRouter();
  const pathname = usePathname();
  const isSignup = pathname?.includes('signup');

  const handlePress = () => {
    if (onLockedPress) {
      onLockedPress();
    }
  };

  return (
    <View style={styles.sidebar} data-testid="auth-side-nav">
      {/* Brand row */}
      <View style={styles.brandRow}>
        <Ionicons name="menu" size={20} color={COLORS.brandText} />
        <Text style={styles.brandText}>CBE Planner</Text>
      </View>

      {/* Sign-in prompt chip */}
      <TouchableOpacity
        style={styles.signInChip}
        onPress={() => router.replace('/auth/login')}
        activeOpacity={0.8}
      >
        <Ionicons name="log-in-outline" size={14} color="#FFFFFF" />
        <Text style={styles.signInChipText}>
          {isSignup ? 'Already have an account?' : 'Sign in to unlock'}
        </Text>
      </TouchableOpacity>

      <View style={styles.divider} />

      {/* Locked menu items */}
      <ScrollView style={{ flex: 1 }} showsVerticalScrollIndicator={false}>
        {MENU_ITEMS.map((item) => (
          <TouchableOpacity
            key={item.title}
            style={styles.menuItem}
            onPress={handlePress}
            activeOpacity={0.6}
          >
            <Ionicons
              name={item.icon as any}
              size={18}
              color={COLORS.sidebarIcon}
              style={styles.menuIcon}
            />
            <Text style={styles.menuLabel} numberOfLines={1}>
              {item.title}
            </Text>
            <Ionicons
              name="lock-closed"
              size={11}
              color={COLORS.lockIcon}
            />
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Bottom hint */}
      <View style={styles.hintBox}>
        <Text style={styles.hintText}>
          Sign in or create a free account to access all features.
        </Text>
      </View>
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
    color: COLORS.brandText,
    fontSize: 16,
    fontWeight: '700',
    letterSpacing: 0.3,
  },
  signInChip: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#5C6BC0',
    borderRadius: 8,
    paddingVertical: 8,
    paddingHorizontal: 12,
    marginTop: 6,
    marginHorizontal: 4,
    gap: 6,
  },
  signInChipText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '600',
    flex: 1,
  },
  divider: {
    height: 1,
    backgroundColor: COLORS.divider,
    marginVertical: 12,
  },
  menuItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 11,
    paddingHorizontal: 14,
    borderRadius: 8,
    marginBottom: 2,
  },
  menuIcon: { marginRight: 14 },
  menuLabel: {
    flex: 1,
    fontSize: 14,
    fontWeight: '400',
    color: COLORS.sidebarText,
  },
  hintBox: {
    marginTop: 8,
    padding: 10,
    backgroundColor: '#1F2937',
    borderRadius: 8,
  },
  hintText: {
    fontSize: 11,
    color: '#6B7280',
    lineHeight: 16,
    textAlign: 'center',
  },
});
