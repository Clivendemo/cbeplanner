import React from 'react';
import { Tabs } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../../contexts/AuthContext';
import { View, Text, StyleSheet, ActivityIndicator } from 'react-native';

export default function AdminLayout() {
  const { user, isAdmin, loading, authChecked } = useAuth();

  // Show loading while checking auth
  if (loading || !authChecked) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#F59E0B" />
        <Text style={styles.loadingText}>Loading...</Text>
      </View>
    );
  }

  // If not admin, AuthGate will redirect — show placeholder
  if (!isAdmin) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#EF4444" />
        <Text style={styles.errorText}>Access Denied</Text>
        <Text style={styles.errorSubtext}>Redirecting...</Text>
      </View>
    );
  }

  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: '#F59E0B',
        tabBarInactiveTintColor: '#9CA3AF',
        tabBarStyle: {
          backgroundColor: '#FFFFFF',
          borderTopWidth: 1,
          borderTopColor: '#DDDDF5',
          paddingBottom: 5,
          paddingTop: 5,
          height: 60
        },
        headerStyle: {
          backgroundColor: '#F59E0B'
        },
        headerTintColor: '#FFFFFF',
        headerTitleStyle: {
          fontWeight: 'bold'
        }
      }}
    >
      <Tabs.Screen
        name="dashboard"
        options={{
          title: 'Dashboard',
          headerTitle: 'Admin Dashboard',
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="grid" size={size} color={color} />
          )
        }}
      />
      <Tabs.Screen
        name="curriculum"
        options={{
          title: 'Curriculum',
          headerTitle: 'Curriculum Management',
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="library" size={size} color={color} />
          )
        }}
      />
      <Tabs.Screen
        name="lesson-slots"
        options={{
          title: 'Lesson SLOs',
          headerTitle: 'Lesson SLO Slots',
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="layers" size={size} color={color} />
          )
        }}
      />
      <Tabs.Screen
        name="calendar"
        options={{
          title: 'Calendar',
          headerTitle: 'Calendar Events & Terms',
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="calendar" size={size} color={color} />
          )
        }}
      />
      <Tabs.Screen
        name="news"
        options={{
          title: 'News',
          headerTitle: 'News Announcements',
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="megaphone" size={size} color={color} />
          )
        }}
      />
      <Tabs.Screen
        name="data-import"
        options={{
          title: 'Import',
          headerTitle: 'Data Import',
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="cloud-upload" size={size} color={color} />
          )
        }}
      />
      <Tabs.Screen
        name="curriculum-upload"
        options={{
          title: 'PDF Upload',
          headerTitle: 'Curriculum Import',
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="document-attach" size={size} color={color} />
          )
        }}
      />
      <Tabs.Screen
        name="assessments"
        options={{
          title: 'Papers',
          headerTitle: 'Past Papers / Assessments',
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="school" size={size} color={color} />
          )
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: 'Profile',
          headerTitle: 'Admin Profile',
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="person" size={size} color={color} />
          )
        }}
      />
    </Tabs>
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
  errorText: {
    marginTop: 12,
    fontSize: 18,
    fontWeight: '600',
    color: '#EF4444'
  },
  errorSubtext: {
    marginTop: 4,
    fontSize: 14,
    color: '#5A5A7A'
  }
});
