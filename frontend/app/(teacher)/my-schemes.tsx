import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import { useAuth } from '../../contexts/AuthContext';
import { useRouter } from 'expo-router';
import { useFocusEffect } from '@react-navigation/native';
import axios from 'axios';
import { Ionicons } from '@expo/vector-icons';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

interface SchemeListItem {
  id: string;
  gradeName: string;
  subjectName: string;
  term: number;
  year: number;
  totalWeeks?: number;
  lessonsPerWeek?: number;
  schoolName?: string;
  createdAt?: string;
  isPaid?: boolean;
  downloadCount?: number;
}

export default function MySchemes() {
  const { firebaseUser } = useAuth();
  const router = useRouter();
  const [schemes, setSchemes] = useState<SchemeListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadSchemes = async () => {
    try {
      if (!firebaseUser) return;
      const token = await firebaseUser.getIdToken();
      const res = await axios.get(`${BACKEND_URL}/api/schemes`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.data?.success) {
        setSchemes(res.data.schemes || []);
      }
    } catch {
      // Ignore — shown as empty state
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useFocusEffect(
    useCallback(() => {
      setLoading(true);
      loadSchemes();
    }, [firebaseUser])
  );

  const onRefresh = () => {
    setRefreshing(true);
    loadSchemes();
  };

  const formatDate = (iso?: string) => {
    if (!iso) return '';
    const d = new Date(iso);
    return d.toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' });
  };

  const openScheme = (id: string) => {
    router.push(`/(teacher)/scheme-detail?id=${id}` as any);
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#6366F1" />
      </View>
    );
  }

  return (
    <ScrollView
      style={styles.container}
      contentContainerStyle={styles.content}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={['#6366F1']} />}
    >
      <View style={styles.header}>
        <Text style={styles.headerTitle}>My Schemes</Text>
        <Text style={styles.headerSubtitle}>{schemes.length} scheme(s) generated</Text>
      </View>

      <View style={styles.noticeBox}>
        <Ionicons name="information-circle" size={20} color="#6366F1" />
        <Text style={styles.noticeText}>
          Preview any scheme for free. Downloading the final PDF costs KES 15.
        </Text>
      </View>

      <TouchableOpacity
        style={styles.newBtn}
        onPress={() => router.push('/(teacher)/schemes' as any)}
        data-testid="my-schemes-new-btn"
      >
        <Ionicons name="add-circle-outline" size={18} color="#FFFFFF" />
        <Text style={styles.newBtnText}>Create New Scheme</Text>
      </TouchableOpacity>

      {schemes.length === 0 ? (
        <View style={styles.empty}>
          <Ionicons name="calendar-outline" size={64} color="#D1D5DB" />
          <Text style={styles.emptyTitle}>No schemes yet</Text>
          <Text style={styles.emptySub}>Generate your first Scheme of Work from the Scheme Generator.</Text>
        </View>
      ) : (
        schemes.map((s) => (
          <TouchableOpacity
            key={s.id}
            style={styles.card}
            onPress={() => openScheme(s.id)}
            activeOpacity={0.75}
            data-testid={`scheme-card-${s.id}`}
          >
            <View style={styles.cardHeader}>
              <View style={styles.iconCircle}>
                <Ionicons name="calendar" size={22} color="#8B5CF6" />
              </View>
              <View style={styles.cardHeaderText}>
                <Text style={styles.cardTitle}>{s.subjectName}</Text>
                <Text style={styles.cardSub}>{s.gradeName}</Text>
              </View>
              <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />
            </View>

            <View style={styles.cardBody}>
              <View style={styles.row}>
                <Ionicons name="time-outline" size={14} color="#6B7280" />
                <Text style={styles.rowText}>Term {s.term} · {s.year}</Text>
              </View>
              {s.totalWeeks ? (
                <View style={styles.row}>
                  <Ionicons name="layers-outline" size={14} color="#6B7280" />
                  <Text style={styles.rowText}>
                    {s.totalWeeks} weeks · {s.lessonsPerWeek || '—'} lessons/wk
                  </Text>
                </View>
              ) : null}
              {s.schoolName ? (
                <View style={styles.row}>
                  <Ionicons name="business-outline" size={14} color="#6B7280" />
                  <Text style={styles.rowText} numberOfLines={1}>{s.schoolName}</Text>
                </View>
              ) : null}
            </View>

            <View style={styles.cardFooter}>
              <View style={styles.dateRow}>
                <Ionicons name="calendar-outline" size={12} color="#9CA3AF" />
                <Text style={styles.dateText}>{formatDate(s.createdAt)}</Text>
              </View>
              <View style={[styles.badge, s.isPaid ? styles.badgePaid : styles.badgeDraft]}>
                <Ionicons
                  name={s.isPaid ? 'checkmark-circle' : 'document-outline'}
                  size={11}
                  color={s.isPaid ? '#065F46' : '#1E40AF'}
                />
                <Text style={[styles.badgeText, { color: s.isPaid ? '#065F46' : '#1E40AF' }]}>
                  {s.isPaid ? 'Downloaded' : 'Preview Only'}
                </Text>
              </View>
            </View>
          </TouchableOpacity>
        ))
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F9FAFB' },
  content: { padding: 16 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  header: { marginBottom: 16 },
  headerTitle: { fontSize: 24, fontWeight: 'bold', color: '#111827', marginBottom: 4 },
  headerSubtitle: { fontSize: 14, color: '#6B7280' },
  noticeBox: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    backgroundColor: '#EEF2FF',
    paddingHorizontal: 12,
    paddingVertical: 10,
    borderRadius: 10,
    marginBottom: 12,
  },
  noticeText: { flex: 1, color: '#4338CA', fontSize: 12, lineHeight: 16 },
  newBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    backgroundColor: '#8B5CF6',
    paddingVertical: 12,
    borderRadius: 10,
    marginBottom: 16,
  },
  newBtnText: { color: '#FFFFFF', fontSize: 14, fontWeight: '600' },
  empty: { alignItems: 'center', justifyContent: 'center', paddingVertical: 64 },
  emptyTitle: { fontSize: 18, fontWeight: '600', color: '#6B7280', marginTop: 16 },
  emptySub: { fontSize: 13, color: '#9CA3AF', marginTop: 6, textAlign: 'center', maxWidth: 280 },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 14,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  cardHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 12 },
  iconCircle: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#F5F3FF',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  cardHeaderText: { flex: 1 },
  cardTitle: { fontSize: 16, fontWeight: '700', color: '#111827' },
  cardSub: { fontSize: 13, color: '#8B5CF6', marginTop: 2, fontWeight: '600' },
  cardBody: { gap: 6, marginBottom: 10 },
  row: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  rowText: { flex: 1, fontSize: 13, color: '#374151' },
  cardFooter: {
    borderTopWidth: 1,
    borderTopColor: '#F3F4F6',
    paddingTop: 10,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  dateRow: { flexDirection: 'row', alignItems: 'center', gap: 4 },
  dateText: { fontSize: 11, color: '#9CA3AF' },
  badge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 10,
  },
  badgePaid: { backgroundColor: '#D1FAE5' },
  badgeDraft: { backgroundColor: '#DBEAFE' },
  badgeText: { fontSize: 10, fontWeight: '700' },
});
