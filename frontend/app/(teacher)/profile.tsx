import React from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Alert
} from 'react-native';
import { useAuth } from '../../contexts/AuthContext';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';

export default function Profile() {
  const { user, signOut } = useAuth();
  const router = useRouter();

  const handleSignOut = async () => {
    Alert.alert(
      'Sign Out',
      'Are you sure you want to sign out?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Sign Out',
          style: 'destructive',
          onPress: async () => {
            await signOut();
            router.replace('/auth/login');
          }
        }
      ]
    );
  };

  const handleSetAsAdmin = async () => {
    Alert.alert(
      'Set as Admin',
      'This will grant you admin privileges. Continue?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Confirm',
          onPress: async () => {
            try {
              if (firebaseUser) {
                const token = await firebaseUser.getIdToken();
                const response = await axios.post(
                  `${process.env.EXPO_PUBLIC_BACKEND_URL}/api/auth/set-admin`,
                  {},
                  { headers: { Authorization: `Bearer ${token}` } }
                );
                
                if (response.data.success) {
                  Alert.alert('Success', 'You are now an admin. Please restart the app.');
                }
              }
            } catch (error: any) {
              Alert.alert('Error', error.response?.data?.detail || 'Failed to set as admin');
            }
          }
        }
      ]
    );
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.header}>
        <View style={styles.avatarContainer}>
          <Ionicons name="person" size={48} color="#FFFFFF" />
        </View>
        <Text style={styles.email}>{user?.email}</Text>
        <View style={styles.roleBadge}>
          <Text style={styles.roleText}>{user?.role?.toUpperCase()}</Text>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Wallet</Text>
        <View style={styles.walletCard}>
          <View style={styles.walletInfo}>
            <Ionicons name="wallet" size={32} color="#6366F1" />
            <View style={styles.walletDetails}>
              <Text style={styles.balanceLabel}>Available Balance</Text>
              <Text style={styles.balanceAmount}>{user?.walletBalance} KES</Text>
            </View>
          </View>
          <TouchableOpacity style={styles.topUpButton}>
            <Text style={styles.topUpButtonText}>Top Up (M-Pesa)</Text>
          </TouchableOpacity>
          <Text style={styles.comingSoon}>M-Pesa integration coming soon</Text>
        </View>

        <View style={styles.freeLessonCard}>
          <View style={styles.freeLessonRow}>
            <Ionicons name="gift" size={24} color="#10B981" />
            <View style={styles.freeLessonInfo}>
              <Text style={styles.freeLessonLabel}>Free Lesson</Text>
              <Text style={styles.freeLessonStatus}>
                {user?.freeLessonUsed ? 'Used' : 'Available'}
              </Text>
            </View>
          </View>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Account</Text>
        
        <TouchableOpacity style={styles.menuItem}>
          <Ionicons name="information-circle-outline" size={24} color="#6B7280" />
          <Text style={styles.menuText}>About CBE Planner</Text>
          <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />
        </TouchableOpacity>

        <TouchableOpacity style={styles.menuItem}>
          <Ionicons name="help-circle-outline" size={24} color="#6B7280" />
          <Text style={styles.menuText}>Help & Support</Text>
          <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />
        </TouchableOpacity>

        <TouchableOpacity style={[styles.menuItem, styles.signOutButton]} onPress={handleSignOut}>
          <Ionicons name="log-out-outline" size={24} color="#EF4444" />
          <Text style={[styles.menuText, styles.signOutText]}>Sign Out</Text>
        </TouchableOpacity>
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
    backgroundColor: '#6366F1',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16
  },
  email: {
    fontSize: 18,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 8
  },
  roleBadge: {
    backgroundColor: '#EEF2FF',
    paddingHorizontal: 16,
    paddingVertical: 6,
    borderRadius: 16
  },
  roleText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#6366F1'
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
  walletCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12
  },
  walletInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16
  },
  walletDetails: {
    marginLeft: 16,
    flex: 1
  },
  balanceLabel: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 4
  },
  balanceAmount: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#111827'
  },
  topUpButton: {
    backgroundColor: '#10B981',
    borderRadius: 8,
    paddingVertical: 12,
    alignItems: 'center',
    marginBottom: 8
  },
  topUpButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600'
  },
  comingSoon: {
    fontSize: 12,
    color: '#9CA3AF',
    textAlign: 'center',
    fontStyle: 'italic'
  },
  freeLessonCard: {
    backgroundColor: '#ECFDF5',
    borderRadius: 12,
    padding: 16
  },
  freeLessonRow: {
    flexDirection: 'row',
    alignItems: 'center'
  },
  freeLessonInfo: {
    marginLeft: 12,
    flex: 1
  },
  freeLessonLabel: {
    fontSize: 14,
    color: '#065F46',
    marginBottom: 2
  },
  freeLessonStatus: {
    fontSize: 16,
    fontWeight: '600',
    color: '#10B981'
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
  }
});