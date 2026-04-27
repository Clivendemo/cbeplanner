/**
 * Revision Papers — teacher-facing screen.
 *
 * Pick Grade + Term → list of assessments stored in Cloudflare R2 → tap
 * "Download". Backend atomically charges the wallet (KES 10 per paper). If the
 * user lacks balance we show a polite top-up prompt that routes to the Profile
 * page where the M-Pesa top-up modal already exists.
 */
import React, { useEffect, useRef, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
  Alert,
  Platform,
  Modal,
  Linking,
} from 'react-native';
import axios from 'axios';
import { Ionicons } from '@expo/vector-icons';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { useAuth } from '../../contexts/AuthContext';
import { useDebouncedAction } from '../../hooks/useDebouncedAction';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

interface Grade { id: string; name: string }
interface Assessment {
  id: string;
  key: string;
  subjectName: string;
  year: number | null;
  title: string;
  ext: string;
  sizeBytes: number;
  uploadedAt: string | null;
}

function formatBytes(n: number): string {
  if (!n) return '—';
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
  return `${(n / (1024 * 1024)).toFixed(1)} MB`;
}

export default function RevisionPapers() {
  const router = useRouter();
  const { firebaseUser, user } = useAuth();
  const getIdToken = async () => {
    if (!firebaseUser) throw new Error('Not authenticated');
    return firebaseUser.getIdToken();
  };
  const [grades, setGrades] = useState<Grade[]>([]);
  const [gradeId, setGradeId] = useState<string>('');
  const [term, setTerm] = useState<number>(1);
  const [loadingGrades, setLoadingGrades] = useState(true);
  const [loadingList, setLoadingList] = useState(false);
  const [items, setItems] = useState<Assessment[]>([]);
  const [costPerDownload, setCostPerDownload] = useState<number>(10);
  const [downloadingKey, setDownloadingKey] = useState<string | null>(null);
  const [topupOpen, setTopupOpen] = useState(false);
  const [topupMessage, setTopupMessage] = useState<string>('');
  const abortRef = useRef<AbortController | null>(null);

  // Fetch grades once
  useEffect(() => {
    let alive = true;
    (async () => {
      try {
        const token = await getIdToken();
        const res = await axios.get(`${BACKEND_URL}/api/grades`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!alive) return;
        const list: Grade[] = res.data.map((g: any) => ({ id: g._id || g.id, name: g.name }));
        setGrades(list);
        if (list.length && !gradeId) setGradeId(list[0].id);
      } catch (e) {
        // keep UI usable even if grades fail to load
        setGrades([]);
      } finally {
        if (alive) setLoadingGrades(false);
      }
    })();
    return () => { alive = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Fetch list whenever grade or term changes
  useEffect(() => {
    if (!gradeId) return;
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    setLoadingList(true);
    (async () => {
      try {
        const token = await getIdToken();
        const res = await axios.get(`${BACKEND_URL}/api/assessments`, {
          params: { gradeId, term },
          headers: { Authorization: `Bearer ${token}` },
          signal: controller.signal as any,
        });
        setItems(res.data.items || []);
        setCostPerDownload(res.data.costPerDownload || 10);
      } catch (e: any) {
        if (axios.isCancel(e) || e?.name === 'CanceledError') return;
        setItems([]);
      } finally {
        setLoadingList(false);
      }
    })();
    return () => controller.abort();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [gradeId, term]);

  const handleDownload = useDebouncedAction(async (item: Assessment) => {
    if (downloadingKey) return;
    setDownloadingKey(item.key);
    try {
      const token = await getIdToken();
      const res = await axios.post(
        `${BACKEND_URL}/api/assessments/download`,
        { key: item.key },
        { headers: { Authorization: `Bearer ${token}` } },
      );
      const { signedUrl, newBalance } = res.data || {};
      if (!signedUrl) throw new Error('No download URL returned');

      // Trigger download in the browser
      if (Platform.OS === 'web') {
        const a = document.createElement('a');
        a.href = signedUrl;
        a.download = item.key.split('/').pop() || 'assessment';
        a.rel = 'noopener noreferrer';
        document.body.appendChild(a);
        a.click();
        setTimeout(() => document.body.removeChild(a), 0);
      } else {
        await Linking.openURL(signedUrl);
      }
      Alert.alert(
        'Download started',
        `KES ${costPerDownload} charged. New wallet balance: KES ${Number(newBalance ?? 0).toFixed(2)}`,
      );
    } catch (err: any) {
      const status = err?.response?.status;
      const detail = err?.response?.data?.detail;
      if (status === 402) {
        const msg =
          (typeof detail === 'object' && detail?.message) ||
          'Your wallet is running low. Top up to keep enjoying high-quality assessments.';
        setTopupMessage(msg);
        setTopupOpen(true);
      } else {
        Alert.alert(
          'Download failed',
          (typeof detail === 'string' ? detail : detail?.message) || 'Please try again in a moment.',
        );
      }
    } finally {
      setDownloadingKey(null);
    }
  });

  const goTopUp = () => {
    setTopupOpen(false);
    router.push('/(teacher)/profile');
  };

  return (
    <SafeAreaView style={styles.container} edges={['bottom']}>
      <ScrollView style={styles.scroll} contentContainerStyle={styles.scrollContent}>
        <View style={styles.header}>
          <View style={styles.headerIconWrap}>
            <Ionicons name="school" size={28} color="#5B5BD6" />
          </View>
          <View style={{ flex: 1 }}>
            <Text style={styles.title}>Revision Papers</Text>
            <Text style={styles.subtitle}>
              Download past assessments per grade and term — KES {costPerDownload} per paper.
            </Text>
          </View>
          <View style={styles.walletPill}>
            <Ionicons name="wallet-outline" size={14} color="#4C1D95" />
            <Text style={styles.walletPillText}>KES {user?.walletBalance ?? 0}</Text>
          </View>
        </View>

        {/* Grade picker */}
        <Text style={styles.sectionLabel}>Grade</Text>
        {loadingGrades ? (
          <ActivityIndicator color="#5B5BD6" />
        ) : (
          <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.chipRow}>
            {grades.map((g) => {
              const active = g.id === gradeId;
              return (
                <TouchableOpacity
                  key={g.id}
                  onPress={() => setGradeId(g.id)}
                  style={[styles.chip, active && styles.chipActive]}
                  testID={`assessments-grade-${g.id}`}
                  data-testid={`assessments-grade-${g.id}`}
                >
                  <Text style={[styles.chipText, active && styles.chipTextActive]}>{g.name}</Text>
                </TouchableOpacity>
              );
            })}
          </ScrollView>
        )}

        {/* Term picker */}
        <Text style={[styles.sectionLabel, { marginTop: 14 }]}>Term</Text>
        <View style={styles.chipRow}>
          {[1, 2, 3].map((t) => {
            const active = t === term;
            return (
              <TouchableOpacity
                key={t}
                onPress={() => setTerm(t)}
                style={[styles.chip, active && styles.chipActive]}
                testID={`assessments-term-${t}`}
                data-testid={`assessments-term-${t}`}
              >
                <Text style={[styles.chipText, active && styles.chipTextActive]}>Term {t}</Text>
              </TouchableOpacity>
            );
          })}
        </View>

        {/* List */}
        <Text style={[styles.sectionLabel, { marginTop: 22 }]}>Available Papers</Text>

        {loadingList ? (
          <View style={styles.emptyWrap}>
            <ActivityIndicator color="#5B5BD6" />
          </View>
        ) : items.length === 0 ? (
          <View style={styles.emptyWrap}>
            <Ionicons name="file-tray-outline" size={36} color="#9CA3AF" />
            <Text style={styles.emptyText}>No papers uploaded yet for this grade & term.</Text>
            <Text style={styles.emptyHint}>Check back soon — we add fresh assessments every term.</Text>
          </View>
        ) : (
          items.map((item) => (
            <View key={item.key} style={styles.paperRow} data-testid={`assessment-row-${item.key}`}>
              <View style={styles.paperIcon}>
                <Ionicons
                  name={item.ext === '.pdf' ? 'document-text' : 'document'}
                  size={22}
                  color={item.ext === '.pdf' ? '#EF4444' : '#2563EB'}
                />
              </View>
              <View style={{ flex: 1 }}>
                <Text style={styles.paperTitle} numberOfLines={1}>{item.title}</Text>
                <Text style={styles.paperMeta}>
                  {item.ext.replace('.', '').toUpperCase()} · {formatBytes(item.sizeBytes)}
                </Text>
              </View>
              <TouchableOpacity
                onPress={() => handleDownload(item)}
                disabled={downloadingKey === item.key}
                style={[styles.downloadBtn, downloadingKey === item.key && styles.downloadBtnBusy]}
                testID={`assessment-download-${item.key}`}
                data-testid={`assessment-download-${item.key}`}
              >
                {downloadingKey === item.key ? (
                  <ActivityIndicator color="#FFFFFF" size="small" />
                ) : (
                  <>
                    <Ionicons name="download-outline" size={14} color="#FFFFFF" />
                    <Text style={styles.downloadBtnText}>KES {costPerDownload}</Text>
                  </>
                )}
              </TouchableOpacity>
            </View>
          ))
        )}
      </ScrollView>

      {/* Insufficient-balance polite modal */}
      <Modal visible={topupOpen} transparent animationType="fade" onRequestClose={() => setTopupOpen(false)}>
        <View style={styles.modalBackdrop}>
          <View style={styles.modalCard} data-testid="assessments-topup-modal">
            <View style={styles.modalIconWrap}>
              <Ionicons name="wallet" size={32} color="#5B5BD6" />
            </View>
            <Text style={styles.modalTitle}>A little more in the tank</Text>
            <Text style={styles.modalBody}>{topupMessage}</Text>
            <View style={styles.modalActions}>
              <TouchableOpacity
                onPress={() => setTopupOpen(false)}
                style={styles.modalSecondary}
                testID="assessments-topup-cancel"
                data-testid="assessments-topup-cancel"
              >
                <Text style={styles.modalSecondaryText}>Not now</Text>
              </TouchableOpacity>
              <TouchableOpacity
                onPress={goTopUp}
                style={styles.modalPrimary}
                testID="assessments-topup-confirm"
                data-testid="assessments-topup-confirm"
              >
                <Ionicons name="arrow-forward" size={14} color="#FFFFFF" />
                <Text style={styles.modalPrimaryText}>Top up now</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: 'transparent' },
  scroll: { flex: 1 },
  scrollContent: { padding: 16, paddingBottom: 48 },

  header: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 14,
    padding: 14,
    marginBottom: 18,
    gap: 12,
    borderWidth: 1,
    borderColor: '#EDE9FE',
  },
  headerIconWrap: {
    width: 44, height: 44, borderRadius: 22,
    backgroundColor: '#EEF2FF',
    alignItems: 'center', justifyContent: 'center',
  },
  title: { fontSize: 18, fontWeight: '700', color: '#111827' },
  subtitle: { fontSize: 12, color: '#6B7280', marginTop: 2 },
  walletPill: {
    flexDirection: 'row', alignItems: 'center', gap: 4,
    backgroundColor: '#F3E8FF',
    paddingHorizontal: 8, paddingVertical: 4, borderRadius: 12,
  },
  walletPillText: { fontSize: 11, fontWeight: '700', color: '#4C1D95' },

  sectionLabel: { fontSize: 12, fontWeight: '700', color: '#374151', textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 8 },

  chipRow: { flexDirection: 'row', gap: 8, paddingVertical: 2, flexWrap: 'wrap' },
  chip: {
    paddingHorizontal: 14, paddingVertical: 8, borderRadius: 999,
    backgroundColor: '#FFFFFF',
    borderWidth: 1, borderColor: '#E5E7EB',
  },
  chipActive: { backgroundColor: '#5B5BD6', borderColor: '#5B5BD6' },
  chipText: { fontSize: 13, color: '#374151', fontWeight: '500' },
  chipTextActive: { color: '#FFFFFF', fontWeight: '600' },

  emptyWrap: {
    alignItems: 'center', justifyContent: 'center',
    paddingVertical: 40,
    backgroundColor: '#FFFFFF',
    borderRadius: 14,
    borderWidth: 1, borderColor: '#F3F4F6',
  },
  emptyText: { fontSize: 14, color: '#374151', fontWeight: '600', marginTop: 12 },
  emptyHint: { fontSize: 12, color: '#9CA3AF', marginTop: 4 },

  paperRow: {
    flexDirection: 'row', alignItems: 'center', gap: 12,
    backgroundColor: '#FFFFFF',
    padding: 12,
    borderRadius: 12,
    marginBottom: 10,
    borderWidth: 1, borderColor: '#F3F4F6',
  },
  paperIcon: {
    width: 40, height: 40, borderRadius: 10,
    backgroundColor: '#F9FAFB',
    alignItems: 'center', justifyContent: 'center',
  },
  paperTitle: { fontSize: 14, fontWeight: '600', color: '#111827' },
  paperMeta: { fontSize: 11, color: '#6B7280', marginTop: 2 },
  downloadBtn: {
    flexDirection: 'row', alignItems: 'center', gap: 4,
    backgroundColor: '#5B5BD6',
    paddingHorizontal: 12, paddingVertical: 8, borderRadius: 8,
    minWidth: 90, justifyContent: 'center',
  },
  downloadBtnBusy: { opacity: 0.7 },
  downloadBtnText: { color: '#FFFFFF', fontSize: 12, fontWeight: '700' },

  modalBackdrop: {
    flex: 1,
    backgroundColor: 'rgba(17, 24, 39, 0.55)',
    alignItems: 'center', justifyContent: 'center',
    padding: 20,
  },
  modalCard: {
    width: '100%', maxWidth: 400,
    backgroundColor: '#FFFFFF',
    borderRadius: 16, padding: 24,
    alignItems: 'center',
  },
  modalIconWrap: {
    width: 64, height: 64, borderRadius: 32,
    backgroundColor: '#EDE9FE',
    alignItems: 'center', justifyContent: 'center',
    marginBottom: 12,
  },
  modalTitle: { fontSize: 18, fontWeight: '700', color: '#111827', marginBottom: 6 },
  modalBody: { fontSize: 13, color: '#4B5563', textAlign: 'center', lineHeight: 20, marginBottom: 18 },
  modalActions: { flexDirection: 'row', gap: 10, width: '100%' },
  modalSecondary: { flex: 1, paddingVertical: 12, borderRadius: 10, borderWidth: 1, borderColor: '#E5E7EB', alignItems: 'center' },
  modalSecondaryText: { color: '#374151', fontWeight: '600', fontSize: 13 },
  modalPrimary: {
    flex: 1, paddingVertical: 12, borderRadius: 10,
    backgroundColor: '#5B5BD6',
    flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 6,
  },
  modalPrimaryText: { color: '#FFFFFF', fontWeight: '700', fontSize: 13 },
});
