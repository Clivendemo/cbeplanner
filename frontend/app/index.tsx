import { useEffect } from 'react';
import { View, ActivityIndicator, StyleSheet, TouchableOpacity, Text } from 'react-native';
import { useRouter } from 'expo-router';
import { useAuth } from '../contexts/AuthContext';
import AsyncStorage from '@react-native-async-storage/async-storage';

export default function Index() {
  const { user, loading, signOut } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading) {
      if (user) {
        console.log('User logged in, role:', user.role);
        if (user.role === 'admin') {
          router.replace('/(admin)/dashboard');
        } else {
          router.replace('/(teacher)/home');
        }
      } else {
        console.log('No user, redirecting to login');
        router.replace('/auth/login');
      }
    }
  }, [user, loading]);

  const handleClearAndLogout = async () => {
    await AsyncStorage.clear();
    await signOut();
    router.replace('/auth/login');
  };

  return (
    <View style={styles.container}>
      <ActivityIndicator size="large" color="#6366F1" />
      <Text style={styles.text}>Loading...</Text>
      {!loading && (
        <TouchableOpacity style={styles.button} onPress={handleClearAndLogout}>
          <Text style={styles.buttonText}>Clear Session & Retry</Text>
        </TouchableOpacity>
      )}
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