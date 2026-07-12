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
import { useRouter } from 'expo-router';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

export default function AdminDashboard() {
  const { firebaseUser } = useAuth();
  const [seeding, setSeeding] = useState(false);
  const router = useRouter();

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
        <Ionicons name="shield-checkmark" size={48} color="#5C6BC0" />
        <Text style={styles.headerTitle}>Admin Dashboard</Text>
        <Text style={styles.headerSubtitle}>CBE Lesson Planner - Curriculum Management</Text>
      </View>

      <View style={styles.card}>
        <View style={styles.cardHeader}>
          <Ionicons name="information-circle" size={24} color="#5C6BC0" />
          <Text style={styles.cardTitle}>Welcome Admin!</Text>
        </View>
        <Text style={styles.cardText}>
          Use this admin panel to manage the Kenyan CBC (Competency-Based Curriculum) structure. You can add and organize:
        </Text>
        <View style={styles.list}>
          <Text style={styles.listItem}>• Grades (PP1 to Grade 9+)</Text>
          <Text style={styles.listItem}>• Subjects/Learning Areas</Text>
          <Text style={styles.listItem}>• Strands and Sub-strands</Text>
          <Text style={styles.listItem}>• Specific Learning Outcomes (SLOs)</Text>
          <Text style={styles.listItem}>• Core Competencies, Values, and PCIs</Text>
          <Text style={styles.listItem}>• Learning Activities and Assessments</Text>
        </View>
      </View>

      <View style={styles.card}>
        <View style={styles.cardHeader}>
          <Ionicons name="cloud-upload" size={24} color="#10B981" />
          <Text style={styles.cardTitle}>Data Import Features</Text>
        </View>
        <Text style={styles.cardText}>
          Import curriculum data in multiple formats:
        </Text>
        <View style={styles.list}>
          <Text style={styles.listItem}>• CSV Upload - Recommended for bulk data</Text>
          <Text style={styles.listItem}>• PDF Extraction - Extract from KICD documents</Text>
          <Text style={styles.listItem}>• Word Document (.docx) - Extract from Word files</Text>
        </View>
        <TouchableOpacity
          style={styles.importButton}
          onPress={() => router.push('/(admin)/data-import')}
        >
          <Ionicons name="cloud-upload-outline" size={20} color="#FFFFFF" />
          <Text style={styles.importButtonText}>Go to Data Import</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.card}>
        <View style={styles.cardHeader}>
          <Ionicons name="download" size={24} color="#F59E0B" />
          <Text style={styles.cardTitle}>Sample Data</Text>
        </View>
        <Text style={styles.cardText}>
          Load sample curriculum data to get started quickly. This includes:
        </Text>
        <View style={styles.list}>
          <Text style={styles.listItem}>• Sample grades and subjects</Text>
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
        <TouchableOpacity 
          style={styles.quickLink}
          onPress={() => router.push('/(admin)/curriculum')}
        >
          <View style={styles.quickLinkIcon}>
            <Ionicons name="layers" size={20} color="#5C6BC0" />
          </View>
          <Text style={styles.quickLinkText}>Manage Curriculum</Text>
          <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={styles.quickLink}
          onPress={() => router.push('/(admin)/data-import')}
        >
          <View style={styles.quickLinkIcon}>
            <Ionicons name="cloud-upload" size={20} color="#5C6BC0" />
          </View>
          <Text style={styles.quickLinkText}>Import Data</Text>
          <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />
        </TouchableOpacity>

        <TouchableOpacity 
          style={styles.quickLink}
          onPress={() => router.push('/(admin)/profile')}
        >
          <View style={styles.quickLinkIcon}>
            <Ionicons name="person" size={20} color="#5C6BC0" />
          </View>
          <Text style={styles.quickLinkText}>Admin Profile</Text>
          <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: 'transparent'
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
    color: '#1A1A3A',
    marginTop: 16
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#5A5A7A',
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
    color: '#1A1A3A',
    marginLeft: 12
  },
  cardText: {
    fontSize: 14,
    color: '#5A5A7A',
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
    color: '#1A1A3A',
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
    backgroundColor: '#F3F4FF',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12
  },
  quickLinkText: {
    flex: 1,
    fontSize: 16,
    color: '#374151',
    fontWeight: '500'
  },
  importButton: {
    flexDirection: 'row',
    backgroundColor: '#5C6BC0',
    borderRadius: 8,
    paddingVertical: 12,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    marginTop: 8
  },
  importButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600'
  }
});