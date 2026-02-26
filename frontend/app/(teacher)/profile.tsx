import React, { useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator
} from 'react-native';
import { useAuth } from '../../contexts/AuthContext';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import axios from 'axios';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

export default function Profile() {
  const { user, firebaseUser, signOut, refreshProfile } = useAuth();
  const router = useRouter();
  const [resetting, setResetting] = useState(false);
  const [becomingAdmin, setBecomingAdmin] = useState(false);

  const handleResetTrial = async () => {
    setResetting(true);
    try {
      const token = await firebaseUser?.getIdToken();
      await axios.post(
        `${BACKEND_URL}/api/profile/reset-free-trial`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );
      await refreshProfile();
      Alert.alert('Success', 'Free trial reset and 100 KES added to wallet!');
    } catch (error) {
      Alert.alert('Error', 'Failed to reset trial');
    } finally {
      setResetting(false);
    }
  };

  const handleBecomeAdmin = async () => {
    Alert.alert(
      'Become Admin',
      'This will give you admin access to manage curriculum data. Continue?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Continue',
          onPress: async () => {
            setBecomingAdmin(true);
            try {
              const token = await firebaseUser?.getIdToken();
              await axios.post(
                `${BACKEND_URL}/api/profile/become-admin`,
                {},
                { headers: { Authorization: `Bearer ${token}` } }
              );
              Alert.alert('Success', 'You are now an admin! The app will redirect you to the admin panel.', [
                {
                  text: 'OK',
                  onPress: () => {
                    refreshProfile();
                    router.replace('/(admin)/dashboard');
                  }
                }
              ]);
            } catch (error) {
              Alert.alert('Error', 'Failed to become admin');
            } finally {
              setBecomingAdmin(false);
            }
          }
        }
      ]
    );
  };

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
            try {
              await signOut();
              // Use setTimeout to ensure state is cleared before navigation
              setTimeout(() => {
                router.replace('/auth/login');
              }, 100);
            } catch (error) {
              console.error('Sign out error:', error);
              // Still try to navigate even if signOut fails
              router.replace('/auth/login');
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
        <Text style={styles.name}>{user?.firstName} {user?.lastName}</Text>
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

        <View style={styles.freeNotesCard}>
          <View style={styles.freeLessonRow}>
            <Ionicons name="gift" size={24} color="#3B82F6" />
            <View style={styles.freeLessonInfo}>
              <Text style={styles.freeLessonLabel}>Free Notes</Text>
              <Text style={styles.freeNotesStatus}>
                {user?.freeNotesUsed ? 'Used' : 'Available'}
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

        <TouchableOpacity 
          style={[styles.menuItem, styles.resetButton]} 
          onPress={handleResetTrial}
          disabled={resetting}
        >
          {resetting ? (
            <ActivityIndicator size="small" color="#6366F1" />
          ) : (
            <Ionicons name="refresh-outline" size={24} color="#6366F1" />
          )}
          <Text style={[styles.menuText, styles.resetText]}>
            {resetting ? 'Resetting...' : 'Reset Free Trial (Test)'}
          </Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={[styles.menuItem, styles.adminButton]} 
          onPress={handleBecomeAdmin}
          disabled={becomingAdmin}
        >
          {becomingAdmin ? (
            <ActivityIndicator size="small" color="#F59E0B" />
          ) : (
            <Ionicons name="shield-checkmark-outline" size={24} color="#F59E0B" />
          )}
          <Text style={[styles.menuText, styles.adminText]}>
            {becomingAdmin ? 'Processing...' : 'Access Admin Panel'}
          </Text>
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
  name: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#111827',
    marginBottom: 4
  },
  email: {
    fontSize: 14,
    color: '#6B7280',
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
    padding: 16,
    marginBottom: 12
  },
  freeNotesCard: {
    backgroundColor: '#DBEAFE',
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
  freeNotesStatus: {
    fontSize: 16,
    fontWeight: '600',
    color: '#3B82F6'
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
  resetButton: {
    marginTop: 8,
    backgroundColor: '#EEF2FF'
  },
  resetText: {
    color: '#6366F1'
  },
  adminButton: {
    marginTop: 8,
    backgroundColor: '#FEF3C7'
  },
  adminText: {
    color: '#F59E0B'
  }
});