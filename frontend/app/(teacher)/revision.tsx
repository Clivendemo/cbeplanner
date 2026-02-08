import React from 'react';
import {
  View,
  Text,
  StyleSheet
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { SafeAreaView } from 'react-native-safe-area-context';

export default function RevisionPapers() {
  return (
    <SafeAreaView style={styles.container} edges={['bottom']}>
      <View style={styles.content}>
        <View style={styles.iconContainer}>
          <Ionicons name="school" size={80} color="#EF4444" />
        </View>
        <Text style={styles.title}>Revision Papers</Text>
        <Text style={styles.subtitle}>Coming Soon!</Text>
        <Text style={styles.description}>
          Generate custom revision papers and assessment materials for your students.
        </Text>
        <View style={styles.featureList}>
          <View style={styles.featureItem}>
            <Ionicons name="checkmark-circle" size={20} color="#EF4444" />
            <Text style={styles.featureText}>End-term exams</Text>
          </View>
          <View style={styles.featureItem}>
            <Ionicons name="checkmark-circle" size={20} color="#EF4444" />
            <Text style={styles.featureText}>CAT papers</Text>
          </View>
          <View style={styles.featureItem}>
            <Ionicons name="checkmark-circle" size={20} color="#EF4444" />
            <Text style={styles.featureText}>Topic-based quizzes</Text>
          </View>
          <View style={styles.featureItem}>
            <Ionicons name="checkmark-circle" size={20} color="#EF4444" />
            <Text style={styles.featureText}>Answer keys included</Text>
          </View>
        </View>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB'
  },
  content: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24
  },
  iconContainer: {
    width: 140,
    height: 140,
    borderRadius: 70,
    backgroundColor: '#FEE2E2',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 24
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#111827',
    marginBottom: 8
  },
  subtitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#EF4444',
    marginBottom: 16
  },
  description: {
    fontSize: 14,
    color: '#6B7280',
    textAlign: 'center',
    lineHeight: 22,
    marginBottom: 32,
    maxWidth: 300
  },
  featureList: {
    alignSelf: 'stretch',
    maxWidth: 280
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
