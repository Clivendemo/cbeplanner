import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
  useWindowDimensions,
} from 'react-native';
import { useAuth } from '../../contexts/AuthContext';
import { useRouter, useFocusEffect } from 'expo-router';
import axios from 'axios';
import { Ionicons } from '@expo/vector-icons';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;
const MOBILE_BREAKPOINT = 768;

interface LessonPlan {
  id: string;
  gradeName: string;
  subjectName: string;
  strandName: string;
  substrandName: string;
  sloName: string;
  createdAt: string;
  daysRemaining: number | null;
}

export default function Lessons() {
  const { firebaseUser } = useAuth();
  const router = useRouter();
  const { width } = useWindowDimensions();
  const isMobile = width < MOBILE_BREAKPOINT;
  const [lessons, setLessons] = useState<LessonPlan[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadLessons();
  }, []);

  useFocusEffect(
    useCallback(() => {
      loadLessons();
    }, [])
  );

  const loadLessons = async () => {
    try {
      if (firebaseUser) {
        const token = await firebaseUser.getIdToken();
        const response = await axios.get(`${BACKEND_URL}/api/lesson-plans`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        if (response.data.success) {
          setLessons(response.data.lessonPlans);
        }
      }
    } catch (error) {
      
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadLessons();
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  };

  const handleLessonPress = (lessonId: string) => {
    router.push(`/(teacher)/lesson-detail?id=${lessonId}`);
  };

  const getExpirationBadge = (daysRemaining: number | null) => {
    if (daysRemaining === null) return null;
    
    let bgColor = '#10B981'; // Green
    let textColor = '#FFFFFF';
    
    if (daysRemaining <= 0) {
      bgColor = '#EF4444'; // Red
    } else if (daysRemaining <= 1) {
      bgColor = '#F59E0B'; // Orange
    }
    
    return (
      <View style={[styles.expirationBadge, { backgroundColor: bgColor }]}>
        <Ionicons name="time-outline" size={12} color={textColor} />
        <Text style={[styles.expirationText, { color: textColor }]}>
          {daysRemaining === 0 ? 'Expires today' : `${daysRemaining} days left`}
        </Text>
      </View>
    );
  };

  if (loading) {
    return (
      <View style={styles.centerContainer}>
        <ActivityIndicator size="large" color="#5C6BC0" />
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={[styles.content, isMobile && styles.contentMobile]}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={['#5C6BC0']} />
      }
    >
      <View style={styles.header}>
        <Text style={styles.headerTitle}>My Lesson Plans</Text>
        <Text style={styles.headerSubtitle}>{lessons.length} lesson(s) created</Text>
      </View>

      {/* Expiration Notice */}
      <View style={styles.noticeBox}>
        <Ionicons name="information-circle" size={20} color="#5C6BC0" />
        <Text style={styles.noticeText}>
          Lesson plans are available for 2 days after creation, then automatically deleted.
        </Text>
      </View>

      {lessons.length === 0 ? (
        <View style={styles.emptyState}>
          <Ionicons name="document-text-outline" size={64} color="#D1D5DB" />
          <Text style={styles.emptyText}>No lesson plans yet</Text>
          <Text style={styles.emptySubtext}>Create your first lesson plan to get started</Text>
        </View>
      ) : (
        lessons.map((lesson) => (
          <TouchableOpacity 
            key={lesson.id} 
            style={styles.card}
            onPress={() => handleLessonPress(lesson.id)}
            activeOpacity={0.7}
          >
            <View style={styles.cardHeader}>
              <View style={styles.iconContainer}>
                <Ionicons name="book" size={24} color="#5C6BC0" />
              </View>
              <View style={styles.cardHeaderText}>
                <Text style={styles.cardTitle}>{lesson.gradeName}</Text>
                <Text style={styles.cardSubject}>{lesson.subjectName}</Text>
              </View>
              <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />
            </View>

            <View style={styles.cardContent}>
              <View style={styles.infoRow}>
                <Ionicons name="layers-outline" size={16} color="#5A5A7A" />
                <Text style={styles.infoText}>{lesson.strandName}</Text>
              </View>
              <View style={styles.infoRow}>
                <Ionicons name="git-branch-outline" size={16} color="#5A5A7A" />
                <Text style={styles.infoText}>{lesson.substrandName}</Text>
              </View>
              <View style={styles.infoRow}>
                <Ionicons name="checkmark-circle-outline" size={16} color="#5A5A7A" />
                <Text style={styles.infoText} numberOfLines={2}>{lesson.sloName}</Text>
              </View>
            </View>

            <View style={styles.cardFooter}>
              <View style={styles.dateContainer}>
                <Ionicons name="calendar-outline" size={14} color="#9CA3AF" />
                <Text style={styles.dateText}>{formatDate(lesson.createdAt)}</Text>
              </View>
              {getExpirationBadge(lesson.daysRemaining)}
            </View>
          </TouchableOpacity>
        ))
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: 'transparent'
  },
  content: {
    paddingHorizontal: 32,
    paddingVertical: 24,
    maxWidth: 1280,
    width: '100%',
    alignSelf: 'center',
  },
  contentMobile: {
    paddingHorizontal: 16,
    paddingVertical: 16,
  },
  centerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center'
  },
  header: {
    marginBottom: 24
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1A1A3A',
    marginBottom: 4
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#5A5A7A'
  },
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 64
  },
  emptyText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#5A5A7A',
    marginTop: 16
  },
  emptySubtext: {
    fontSize: 14,
    color: '#9CA3AF',
    marginTop: 8
  },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#DDDDF5'
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12
  },
  iconContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#F3F4FF',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12
  },
  cardHeaderText: {
    flex: 1
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1A1A3A'
  },
  cardSubject: {
    fontSize: 14,
    color: '#5C6BC0',
    marginTop: 2
  },
  cardContent: {
    gap: 8,
    marginBottom: 12
  },
  infoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8
  },
  infoText: {
    flex: 1,
    fontSize: 14,
    color: '#374151'
  },
  cardFooter: {
    borderTopWidth: 1,
    borderTopColor: '#F3F4F6',
    paddingTop: 12,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  dateContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6
  },
  dateText: {
    fontSize: 12,
    color: '#9CA3AF'
  },
  expirationBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    gap: 4
  },
  expirationText: {
    fontSize: 11,
    fontWeight: '600'
  }
});
