/**
 * Auth group layout — app/auth/_layout.tsx
 *
 * Expo Router nested navigator for the auth/ group.
 * On desktop (≥ 1180px): dark AuthSideNav on left + content fills right.
 * On mobile/tablet: no sidebar, full-width stack.
 */
import React from 'react';
import { View, StyleSheet, useWindowDimensions } from 'react-native';
import { Stack } from 'expo-router';
import { AuthSideNav } from '../../components/AuthSideNav';

const LEFT_SIDEBAR_W = 240;
const GAP = 16;
const SHELL_BREAKPOINT = 1180;

export default function AuthLayout() {
  const { width } = useWindowDimensions();
  const showSidebar = width >= SHELL_BREAKPOINT;

  if (!showSidebar) {
    return <Stack screenOptions={{ headerShown: false }} />;
  }

  return (
    <View style={styles.root}>
      {/* Dark locked sidebar */}
      <View style={{ width: LEFT_SIDEBAR_W, flexShrink: 0 }}>
        <AuthSideNav />
      </View>

      {/* Content area — Stack renders the screen here */}
      <View style={styles.content}>
        <Stack screenOptions={{ headerShown: false }} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
    flexDirection: 'row',
    backgroundColor: '#F3F4FF',
    // @ts-ignore web
    backgroundImage:
      'radial-gradient(900px 500px at 8% 0%, #E0E7FF 0%, transparent 60%), linear-gradient(180deg, #F3F4FF 0%, #F8FAFC 100%)',
    padding: GAP,
    gap: GAP,
  },
  content: {
    flex: 1,
    minWidth: 0,
    borderRadius: 14,
    overflow: 'hidden',
    backgroundColor: '#F7F8FF',
    // @ts-ignore web
    boxShadow: '0 6px 24px rgba(17, 24, 39, 0.06)',
  },
});
