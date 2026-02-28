import React from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Alert,
  Platform
} from 'react-native';
import { useAuth } from '../../contexts/AuthContext';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';

export default function AdminProfile() {
  const { user, signOut, isAdmin } = useAuth();
  const router = useRouter();

  const handleSignOut = async () => {
    if (Platform.OS === 'web') {
      const confirmed = window.confirm('Are you sure you want to sign out?');
      if (confirmed) {
        try {
          await signOut();
          router.replace('/auth/login');
        } catch (error) {
          console.error('Sign out error:', error);
          router.replace('/auth/login');
        }
      }
    } else {
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
    }
  };

  // Extra safety check - redirect if not admin
  if (!isAdmin) {
    router.replace('/(teacher)/home');
    return null;
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.header}>
        <View style={styles.avatarContainer}>
          <Ionicons name="shield-checkmark" size={48} color="#FFFFFF" />
        </View>
        <Text style={styles.name}>{user?.firstName} {user?.lastName}</Text>
        <Text style={styles.email}>{user?.email}</Text>
        <View style={styles.adminBadge}>
          <Ionicons name="star" size={12} color="#F59E0B" />
          <Text style={styles.adminText}>ADMINISTRATOR</Text>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Admin Menu</Text>
        
        <TouchableOpacity 
          style={styles.menuItem}
          onPress={() => router.push('/(admin)/dashboard')}
        >
          <Ionicons name="grid-outline" size={24} color="#6366F1" />
          <Text style={styles.menuText}>Dashboard</Text>
          <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />
        </TouchableOpacity>

        <TouchableOpacity 
          style={styles.menuItem}
          onPress={() => router.push('/(admin)/curriculum')}
        >
          <Ionicons name="library-outline" size={24} color="#10B981" />
          <Text style={styles.menuText}>Curriculum Management</Text>
          <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />
        </TouchableOpacity>

        <TouchableOpacity 
          style={styles.menuItem}
          onPress={() => router.push('/(admin)/users')}
        >
          <Ionicons name="people-outline" size={24} color="#8B5CF6" />
          <Text style={styles.menuText}>User Management</Text>
          <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />
        </TouchableOpacity>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Account</Text>
        
        <TouchableOpacity 
          style={styles.menuItem}
          onPress={() => router.push('/(teacher)/home')}
        >
          <Ionicons name="home-outline" size={24} color="#6B7280" />
          <Text style={styles.menuText}>Switch to Teacher View</Text>
          <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />
        </TouchableOpacity>

        <TouchableOpacity 
          style={[styles.menuItem, styles.signOutButton]} 
          onPress={handleSignOut}
        >
          <Ionicons name="log-out-outline" size={24} color="#EF4444" />
          <Text style={[styles.menuText, styles.signOutText]}>Sign Out</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.developerCredit}>
        <Text style={styles.developerText}>Developed by LEGIT LAB</Text>
        <Text style={styles.versionText}>Admin Panel v1.0.0</Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB'
  },
  content: {
    padding: 16
  },
  header: {
    alignItems: 'center',
    paddingVertical: 32,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    marginBottom: 24
  },
  avatarContainer: {
    width: 96,
    height: 96,
    borderRadius: 48,
    backgroundColor: '#F59E0B',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16
  },
  name: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#111827',
    marginBottom: 4
  },
  email: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 12
  },
  adminBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FEF3C7',
    paddingHorizontal: 16,
    paddingVertical: 6,
    borderRadius: 16,
    gap: 6
  },
  adminText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#92400E'
  },
  section: {
    marginBottom: 24
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 12
  },
  menuItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    padding: 16,
    borderRadius: 8,
    marginBottom: 8
  },
  menuText: {
    flex: 1,
    marginLeft: 12,
    fontSize: 16,
    color: '#374151'
  },
  signOutButton: {
    marginTop: 8
  },
  signOutText: {
    color: '#EF4444'
  },
  developerCredit: {
    alignItems: 'center',
    paddingVertical: 20
  },
  developerText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#6366F1'
  },
  versionText: {
    fontSize: 11,
    color: '#9CA3AF',
    marginTop: 4
  }
});
