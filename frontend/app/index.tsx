import { useEffect } from 'react';
import { View, ActivityIndicator, StyleSheet, Text, Platform } from 'react-native';
import { useRouter } from 'expo-router';
import { useAuth } from '../contexts/AuthContext';

export default function Index() {
  const { user, authChecked, isAdmin } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // Once auth is checked, redirect appropriately
    if (authChecked) {
      if (user) {
        if (isAdmin) {
          router.replace('/(admin)/dashboard');
        } else {
          router.replace('/(teacher)/dashboard');
        }
      } else {
        router.replace('/auth/login');
      }
    }
  }, [authChecked, user, isAdmin]);

  // Fallback redirect for web if auth takes too long
  useEffect(() => {
    if (Platform.OS === 'web') {
      const timer = setTimeout(() => {
        if (!authChecked) {
          console.log('Index: Fallback redirect to login');
          router.replace('/auth/login');
        }
      }, 4000);
      return () => clearTimeout(timer);
    }
  }, [authChecked]);

  return (
    <View style={styles.container}>
      <ActivityIndicator size="large" color="#6366F1" />
      <Text style={styles.text}>Loading CBE Planner...</Text>
      <Text style={styles.subtext}>Developed by LEGIT LAB</Text>
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
  subtext: {
    marginTop: 8,
    color: '#9CA3AF',
    fontSize: 12
  }
});
