import { useEffect } from 'react';
import { View, ActivityIndicator, StyleSheet, TouchableOpacity, Text } from 'react-native';
import { useRouter, useSegments } from 'expo-router';
import { useAuth } from '../contexts/AuthContext';
import AsyncStorage from '@react-native-async-storage/async-storage';

export default function Index() {
  const { user, loading, signOut } = useAuth();
  const router = useRouter();
  const segments = useSegments();

  useEffect(() => {
    if (loading) return;

    console.log('Auth state:', { user: user?.email, role: user?.role, loading });

    // If no user, go to login
    if (!user) {
      console.log('No user found, redirecting to login');
      router.replace('/auth/login');
      return;
    }

    // If user exists, redirect based on role
    if (user.role === 'admin') {
      console.log('Admin user, redirecting to dashboard');
      router.replace('/(admin)/dashboard');
    } else {
      console.log('Teacher user, redirecting to home');
      router.replace('/(teacher)/home');
    }
  }, [user, loading]);

  const handleClearAndLogout = async () => {
    console.log('Clearing session...');
    await AsyncStorage.clear();
    await signOut();
    router.replace('/auth/login');
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#6366F1" />
        <Text style={styles.text}>Loading...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <ActivityIndicator size="large" color="#6366F1" />
      <Text style={styles.text}>Redirecting...</Text>
      <TouchableOpacity style={styles.button} onPress={handleClearAndLogout}>
        <Text style={styles.buttonText}>Clear Session & Logout</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F9FAFB'
  },
  text: {
    marginTop: 16,
    color: '#6B7280',
    fontSize: 14
  },
  button: {
    marginTop: 24,
    paddingHorizontal: 20,
    paddingVertical: 12,
    backgroundColor: '#EF4444',
    borderRadius: 8
  },
  buttonText: {
    color: '#FFFFFF',
    fontWeight: '600'
  }
});