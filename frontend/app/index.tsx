import { useEffect } from 'react';
import { View, ActivityIndicator, StyleSheet, Text } from 'react-native';
import { useRouter } from 'expo-router';
import { useAuth } from '../contexts/AuthContext';

export default function Index() {
  const { user, loading, authChecked, isAdmin } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // Wait until auth is fully checked
    if (!authChecked) return;

    // Small delay to ensure auth state is fully settled
    const timeout = setTimeout(() => {
      if (!user) {
        console.log('Index: No user, redirecting to login');
        router.replace('/auth/login');
      } else if (isAdmin) {
        console.log('Index: Admin user, going to admin dashboard');
        router.replace('/(admin)/dashboard');
      } else {
        console.log('Index: Teacher user, going to teacher home');
        router.replace('/(teacher)/home');
      }
    }, 100);

    return () => clearTimeout(timeout);
  }, [user, authChecked, isAdmin]);

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
