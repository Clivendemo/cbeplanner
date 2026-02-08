import { useEffect } from 'react';
import { View, ActivityIndicator, StyleSheet, Text } from 'react-native';
import { useRouter } from 'expo-router';
import { useAuth } from '../contexts/AuthContext';

export default function Index() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (loading) return;

    // Small delay to ensure auth state is fully settled
    const timeout = setTimeout(() => {
      if (!user) {
        console.log('No user, going to login');
        router.replace('/auth/login');
      } else if (user.role === 'admin') {
        console.log('Admin user, going to dashboard');
        router.replace('/(admin)/dashboard');
      } else {
        console.log('Teacher user, going to dashboard');
        router.replace('/(teacher)/dashboard');
      }
    }, 100);

    return () => clearTimeout(timeout);
  }, [user, loading]);

  return (
    <View style={styles.container}>
      <ActivityIndicator size="large" color="#6366F1" />
      <Text style={styles.text}>Loading CBE Planner...</Text>
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
  }
});
