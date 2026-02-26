import React from 'react';
import { View, TouchableOpacity, StyleSheet, Alert } from 'react-native';
import { Tabs, useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../../contexts/AuthContext';

// Header right component with logout button - defined outside to prevent re-renders
function AdminHeaderRight() {
  const router = useRouter();
  const { signOut } = useAuth();

  const handleLogout = () => {
    Alert.alert(
      'Sign Out',
      'Are you sure you want to sign out?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Sign Out',
          style: 'destructive',
          onPress: async () => {
            try {
              await signOut();
              setTimeout(() => {
                router.replace('/auth/login');
              }, 100);
            } catch (error) {
              console.error('Sign out error:', error);
              router.replace('/auth/login');
            }
          }
        }
      ]
    );
  };

  return (
    <View style={styles.headerRight}>
      <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
        <Ionicons name="log-out-outline" size={24} color="#FFFFFF" />
      </TouchableOpacity>
    </View>
  );
}

// Empty header for profile page
function EmptyHeader() {
  return null;
}

// Tab bar icon components - defined outside to prevent re-renders
function DashboardIcon({ color, size }: { color: string; size: number }) {
  return <Ionicons name="grid-outline" size={size} color={color} />;
}

function CurriculumIcon({ color, size }: { color: string; size: number }) {
  return <Ionicons name="school-outline" size={size} color={color} />;
}

function ProfileIcon({ color, size }: { color: string; size: number }) {
  return <Ionicons name="person-outline" size={size} color={color} />;
}

export default function AdminLayout() {
  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: '#6366F1',
        tabBarInactiveTintColor: '#9CA3AF',
        tabBarStyle: {
          backgroundColor: '#FFFFFF',
          borderTopColor: '#E5E7EB',
          height: 60,
          paddingBottom: 8
        },
        headerStyle: {
          backgroundColor: '#6366F1'
        },
        headerTintColor: '#FFFFFF',
        headerTitleStyle: {
          fontWeight: 'bold'
        },
        headerRight: AdminHeaderRight
      }}
    >
      <Tabs.Screen
        name="dashboard"
        options={{
          title: 'Dashboard',
          tabBarIcon: DashboardIcon
        }}
      />
      <Tabs.Screen
        name="curriculum"
        options={{
          title: 'Curriculum',
          tabBarIcon: CurriculumIcon
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: 'Profile',
          tabBarIcon: ProfileIcon,
          headerRight: EmptyHeader
        }}
      />
    </Tabs>
  );
}

const styles = StyleSheet.create({
  headerRight: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 16
  },
  logoutButton: {
    padding: 8,
    backgroundColor: 'rgba(255,255,255,0.2)',
    borderRadius: 8
  }
});
