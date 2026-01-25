import React from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

export default function Curriculum() {
  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.header}>
        <Ionicons name="school" size={48} color="#6366F1" />
        <Text style={styles.headerTitle}>Curriculum Management</Text>
        <Text style={styles.headerSubtitle}>Detailed CRUD interface coming soon</Text>
      </View>

      <View style={styles.infoCard}>
        <Ionicons name="construct" size={32} color="#F59E0B" />
        <Text style={styles.infoTitle}>Under Development</Text>
        <Text style={styles.infoText}>
          The full curriculum management interface with detailed CRUD operations for all entities is under development.
        </Text>
        <Text style={styles.infoText}>
          For now, use the Dashboard to load sample data and the backend API for advanced management.
        </Text>
      </View>

      <View style={styles.featuresList}>
        <Text style={styles.featuresTitle}>Coming Soon:</Text>
        <View style={styles.featureItem}>
          <Ionicons name="checkmark-circle" size={20} color="#10B981" />
          <Text style={styles.featureText}>Add/Edit/Delete Grades</Text>
        </View>
        <View style={styles.featureItem}>
          <Ionicons name="checkmark-circle" size={20} color="#10B981" />
          <Text style={styles.featureText}>Manage Subjects by Grade</Text>
        </View>
        <View style={styles.featureItem}>
          <Ionicons name="checkmark-circle" size={20} color="#10B981" />
          <Text style={styles.featureText}>Configure Strands & Sub-strands</Text>
        </View>
        <View style={styles.featureItem}>
          <Ionicons name="checkmark-circle" size={20} color="#10B981" />
          <Text style={styles.featureText}>Define Learning Outcomes</Text>
        </View>
        <View style={styles.featureItem}>
          <Ionicons name="checkmark-circle" size={20} color="#10B981" />
          <Text style={styles.featureText}>Map Competencies & Values</Text>
        </View>
        <View style={styles.featureItem}>
          <Ionicons name="checkmark-circle" size={20} color="#10B981" />
          <Text style={styles.featureText}>Add Learning Activities</Text>
        </View>
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
  infoCard: {
    backgroundColor: '#FFFBEB',
    borderRadius: 12,
    padding: 24,
    alignItems: 'center',
    marginBottom: 24
  },
  infoTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#92400E',
    marginTop: 16,
    marginBottom: 12
  },
  infoText: {
    fontSize: 14,
    color: '#78350F',
    textAlign: 'center',
    marginBottom: 8,
    lineHeight: 20
  },
  featuresList: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16
  },
  featuresTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#111827',
    marginBottom: 16
  },
  featureItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12
  },
  featureText: {
    fontSize: 14,
    color: '#374151',
    marginLeft: 12
  }
});