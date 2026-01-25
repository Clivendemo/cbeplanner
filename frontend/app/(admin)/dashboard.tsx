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
import axios from 'axios';
import { Ionicons } from '@expo/vector-icons';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

export default function AdminDashboard() {
  const { firebaseUser } = useAuth();
  const [seeding, setSeeding] = useState(false);

  const handleSeedData = async () => {
    Alert.alert(
      'Seed Sample Data',
      'This will clear existing curriculum data and load sample data. Continue?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Continue',
          onPress: async () => {
            setSeeding(true);
            try {
              if (firebaseUser) {
                const token = await firebaseUser.getIdToken();
                const response = await axios.post(
                  `${BACKEND_URL}/api/admin/seed-data`,
                  {},
                  { headers: { Authorization: `Bearer ${token}` } }
                );
                
                if (response.data.success) {
                  Alert.alert('Success', 'Sample data seeded successfully!');
                }
              }
            } catch (error: any) {
              Alert.alert('Error', error.response?.data?.detail || 'Failed to seed data');
            } finally {
              setSeeding(false);
            }
          }
        }
      ]
    );
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.header}>
        <Ionicons name="shield-checkmark" size={48} color="#6366F1" />
        <Text style={styles.headerTitle}>Admin Dashboard</Text>
        <Text style={styles.headerSubtitle}>Manage CBE Curriculum Data</Text>
      </View>

      <View style={styles.card}>
        <View style={styles.cardHeader}>
          <Ionicons name="information-circle" size={24} color="#6366F1" />
          <Text style={styles.cardTitle}>Welcome Admin!</Text>
        </View>
        <Text style={styles.cardText}>
          Use this admin panel to manage the Kenyan CBC curriculum structure. You can add and organize:
        </Text>
        <View style={styles.list}>
          <Text style={styles.listItem}>• Grades (1-6)</Text>
          <Text style={styles.listItem}>• Subjects/Learning Areas</Text>
          <Text style={styles.listItem}>• Strands and Sub-strands</Text>
          <Text style={styles.listItem}>• Specific Learning Outcomes (SLOs)</Text>
          <Text style={styles.listItem}>• Core Competencies, Values, and PCIs</Text>
          <Text style={styles.listItem}>• Learning Activities and Assessments</Text>
        </View>
      </View>

      <View style={styles.card}>
        <View style={styles.cardHeader}>
          <Ionicons name="download" size={24} color="#10B981" />
          <Text style={styles.cardTitle}>Sample Data</Text>
        </View>
        <Text style={styles.cardText}>
          Load sample curriculum data to get started quickly. This includes:
        </Text>
        <View style={styles.list}>
          <Text style={styles.listItem}>• Grades 1-6</Text>
          <Text style={styles.listItem}>• Sample subjects (Math, English, Science, etc.)</Text>
          <Text style={styles.listItem}>• Sample strands and learning outcomes</Text>
          <Text style={styles.listItem}>• Pre-configured competencies and values</Text>
        </View>
        <TouchableOpacity
          style={[styles.seedButton, seeding && styles.buttonDisabled]}
          onPress={handleSeedData}
          disabled={seeding}
        >
          {seeding ? (
            <ActivityIndicator color="#FFFFFF" />
          ) : (
            <>
              <Ionicons name="download-outline" size={20} color="#FFFFFF" />
              <Text style={styles.seedButtonText}>Load Sample Data</Text>
            </>
          )}
        </TouchableOpacity>
      </View>

      <View style={styles.quickLinks}>
        <Text style={styles.quickLinksTitle}>Quick Access</Text>
        <TouchableOpacity style={styles.quickLink}>
          <View style={styles.quickLinkIcon}>
            <Ionicons name="layers" size={20} color="#6366F1" />
          </View>
          <Text style={styles.quickLinkText}>Manage Curriculum</Text>
          <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />
        </TouchableOpacity>
        
        <TouchableOpacity style={styles.quickLink}>
          <View style={styles.quickLinkIcon}>
            <Ionicons name="people" size={20} color="#6366F1" />
          </View>
          <Text style={styles.quickLinkText}>View Users</Text>
          <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />
        </TouchableOpacity>

        <TouchableOpacity style={styles.quickLink}>
          <View style={styles.quickLinkIcon}>
            <Ionicons name="settings" size={20} color="#6366F1" />
          </View>
          <Text style={styles.quickLinkText}>Settings</Text>
          <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />
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
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#111827',
    marginTop: 16
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 4
  },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#111827',
    marginLeft: 12
  },
  cardText: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 12,
    lineHeight: 20
  },
  list: {
    marginLeft: 8
  },
  listItem: {
    fontSize: 14,
    color: '#374151',
    marginBottom: 6,
    lineHeight: 20
  },
  seedButton: {
    flexDirection: 'row',
    backgroundColor: '#10B981',
    borderRadius: 8,
    paddingVertical: 12,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    marginTop: 8
  },
  buttonDisabled: {
    opacity: 0.6
  },
  seedButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600'
  },
  quickLinks: {
    marginTop: 8
  },
  quickLinksTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 12
  },
  quickLink: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    padding: 16,
    borderRadius: 8,
    marginBottom: 8
  },
  quickLinkIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#EEF2FF',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12
  },
  quickLinkText: {
    flex: 1,
    fontSize: 16,
    color: '#374151',
    fontWeight: '500'
  }
});