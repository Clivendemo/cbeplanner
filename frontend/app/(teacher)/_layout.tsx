import React from 'react';
import { TouchableOpacity, View, Text, StyleSheet } from 'react-native';
import { Stack, useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../../contexts/AuthContext';

// Profile button component for header
const ProfileButton = () => {
  const router = useRouter();
  const { user } = useAuth();
  
  return (
    <TouchableOpacity 
      style={styles.profileButton}
      onPress={() => router.push('/(teacher)/profile')}
    >
      <View style={styles.profileIconContainer}>
        <Ionicons name="person-circle" size={28} color="#FFFFFF" />
      </View>
    </TouchableOpacity>
  );
};

// Wallet badge for header
const WalletBadge = () => {
  const { user } = useAuth();
  
  return (
    <View style={styles.walletBadge}>
      <Ionicons name="wallet-outline" size={14} color="#FFFFFF" />
      <Text style={styles.walletText}>{user?.walletBalance || 0} KES</Text>
    </View>
  );
};

export default function TeacherLayout() {
  return (
    <Stack
      screenOptions={{
        headerStyle: {
          backgroundColor: '#6366F1'
        },
        headerTintColor: '#FFFFFF',
        headerTitleStyle: {
          fontWeight: 'bold'
        },
        headerRight: () => (
          <View style={styles.headerRight}>
            <WalletBadge />
            <ProfileButton />
          </View>
        )
      }}
    >
      <Stack.Screen
        name="dashboard"
        options={{
          title: 'CBE Planner',
          headerShown: true
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
          headerRight: () => null // Hide profile button on profile page
        }}
      />
      <Stack.Screen
        name="schemes"
        options={{
          title: 'Schemes of Work'
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
}

const styles = StyleSheet.create({
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
  }
});
