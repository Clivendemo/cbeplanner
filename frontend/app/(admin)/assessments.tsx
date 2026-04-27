/**
 * Admin → Past Papers (Assessments) management.
 *
 * Upload PDF / .doc / .docx files directly to Cloudflare R2 under
 *   assessments/{grade-slug}/term-{term}/{subject-slug}-{year}.{ext}
 * and manage (list + delete) what's already there.
 *
 * No MongoDB involvement — the bucket itself is the source of truth.
 */
import React, { useEffect, useRef, useState } from 'react';
import {
  View,
  Text,
  TextInput,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
  Alert,
  Platform,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { SafeAreaView } from 'react-native-safe-area-context';
import axios from 'axios';
import { useAuth } from '../../contexts/AuthContext';
import { useDebouncedAction } from '../../hooks/useDebouncedAction';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

interface Grade { id: string; name: string }
interface AdminPaper {
  key: string;
  grade: string;
  term: string;
  subjectName: string;
  year: number | null;
  sizeBytes: number;
  uploadedAt: string | null;
}

function bytes(n: number): string {
  if (!n) return '—';
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
  return `${(n / (1024 * 1024)).toFixed(1)} MB`;
}

export default function AdminAssessments() {
  const { firebaseUser } = useAuth();
  const getIdToken = async () => {
    if (!firebaseUser) throw new Error('Not authenticated');
    return firebaseUser.getIdToken();
  };

  const [grades, setGrades] = useState<Grade[]>([]);
  const [gradeId, setGradeId] = useState('');
  const [term, setTerm] = useState<number>(1);
  const [subject, setSubject] = useState('');
  const [year, setYear] = useState<string>(String(new Date().getFullYear()));
  const [uploading, setUploading] = useState(false);

  const [papers, setPapers] = useState<AdminPaper[]>([]);
  const [loadingList, setLoadingList] = useState(false);
  const [filterGradeId, setFilterGradeId] = useState('');
  const [filterTerm, setFilterTerm] = useState<string>('all');

  // Native file picker (web only — admin is web-only anyway)
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [pickedFile, setPickedFile] = useState<File | null>(null);

  // Load grades once
  useEffect(() => {
    (async () => {
      try {
        const token = await getIdToken();
        const res = await axios.get(`${BACKEND_URL}/api/grades`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        const list: Grade[] = res.data.map((g: any) => ({ id: g._id || g.id, name: g.name }));
        setGrades(list);
        if (list.length && !gradeId) setGradeId(list[0].id);
      } catch { /* noop */ }
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const refreshList = async () => {
    setLoadingList(true);
    try {
      const token = await getIdToken();
      const params: any = {};
      if (filterGradeId) params.gradeId = filterGradeId;
      if (filterTerm !== 'all') params.term = Number(filterTerm);
      const res = await axios.get(`${BACKEND_URL}/api/admin/assessments`, {
        params,
        headers: { Authorization: `Bearer ${token}` },
      });
      setPapers(res.data.items || []);
    } catch (e: any) {
      const detail = e?.response?.data?.detail || e?.message;
      Alert.alert('Unable to load papers', typeof detail === 'string' ? detail : 'Please try again.');
    } finally {
      setLoadingList(false);
    }
  };

  useEffect(() => { refreshList(); /* eslint-disable-line react-hooks/exhaustive-deps */ }, [filterGradeId, filterTerm]);

  const handlePickFile = () => {
    if (Platform.OS !== 'web' || !fileInputRef.current) return;
    fileInputRef.current.click();
  };

  const handleUpload = useDebouncedAction(async () => {
    if (!pickedFile) { Alert.alert('Pick a file', 'Please choose a PDF or Word document first.'); return; }
    if (!gradeId) { Alert.alert('Missing grade', 'Please pick a grade.'); return; }
    if (!subject.trim()) { Alert.alert('Missing subject', 'Please type a subject name.'); return; }
    const y = parseInt(year, 10);
    if (!y || y < 2000 || y > 2100) { Alert.alert('Invalid year', 'Enter a 4-digit year.'); return; }

    setUploading(true);
    try {
      const token = await getIdToken();
      const fd = new FormData();
      fd.append('file', pickedFile);
      fd.append('gradeId', gradeId);
      fd.append('term', String(term));
      fd.append('subject', subject.trim());
      fd.append('year', String(y));
      const res = await axios.post(`${BACKEND_URL}/api/admin/assessments/upload`, fd, {
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'multipart/form-data' },
      });
      Alert.alert('Uploaded', `Stored as ${res.data.key}`);
      setPickedFile(null);
      setSubject('');
      if (fileInputRef.current) fileInputRef.current.value = '';
      refreshList();
    } catch (e: any) {
      const detail = e?.response?.data?.detail || e?.message;
      Alert.alert('Upload failed', typeof detail === 'string' ? detail : 'Please try again.');
    } finally {
      setUploading(false);
    }
  });

  const handleDelete = useDebouncedAction(async (key: string) => {
    if (!confirm(`Delete this paper?\n\n${key}`)) return;
    try {
      const token = await getIdToken();
      await axios.delete(`${BACKEND_URL}/api/admin/assessments`, {
        data: { key },
        headers: { Authorization: `Bearer ${token}` },
      });
      setPapers((prev) => prev.filter((p) => p.key !== key));
    } catch (e: any) {
      const detail = e?.response?.data?.detail || e?.message;
      Alert.alert('Delete failed', typeof detail === 'string' ? detail : 'Please try again.');
    }
  });

  return (
    <SafeAreaView style={styles.container} edges={['bottom']}>
      <ScrollView style={styles.scroll} contentContainerStyle={styles.content}>
        <Text style={styles.pageTitle}>Past Papers (Assessments)</Text>
        <Text style={styles.pageSub}>
          Upload .pdf / .doc / .docx to Cloudflare R2. Teachers pay KES 10 per download.
        </Text>

        {/* ---- Upload card ---- */}
        <View style={styles.card} data-testid="admin-assessments-upload-card">
          <Text style={styles.cardTitle}>Upload a new paper</Text>

          <Text style={styles.label}>Grade</Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.chipRow}>
            {grades.map((g) => {
              const active = g.id === gradeId;
              return (
                <TouchableOpacity
                  key={g.id}
                  style={[styles.chip, active && styles.chipActive]}
                  onPress={() => setGradeId(g.id)}
                  testID={`admin-upload-grade-${g.id}`}
                  data-testid={`admin-upload-grade-${g.id}`}
                >
                  <Text style={[styles.chipText, active && styles.chipTextActive]}>{g.name}</Text>
                </TouchableOpacity>
              );
            })}
          </ScrollView>

          <Text style={[styles.label, { marginTop: 14 }]}>Term</Text>
          <View style={styles.chipRow}>
            {[1, 2, 3].map((t) => {
              const active = t === term;
              return (
                <TouchableOpacity
                  key={t}
                  style={[styles.chip, active && styles.chipActive]}
                  onPress={() => setTerm(t)}
                  testID={`admin-upload-term-${t}`}
                  data-testid={`admin-upload-term-${t}`}
                >
                  <Text style={[styles.chipText, active && styles.chipTextActive]}>Term {t}</Text>
                </TouchableOpacity>
              );
            })}
          </View>

          <View style={{ flexDirection: 'row', gap: 12, marginTop: 14 }}>
            <View style={{ flex: 2 }}>
              <Text style={styles.label}>Subject</Text>
              <TextInput
                value={subject}
                onChangeText={setSubject}
                placeholder="e.g. Mathematics"
                style={styles.input}
                placeholderTextColor="#9CA3AF"
                testID="admin-upload-subject"
                data-testid="admin-upload-subject"
              />
            </View>
            <View style={{ flex: 1 }}>
              <Text style={styles.label}>Year</Text>
              <TextInput
                value={year}
                onChangeText={setYear}
                keyboardType="numeric"
                maxLength={4}
                style={styles.input}
                placeholder="2024"
                placeholderTextColor="#9CA3AF"
                testID="admin-upload-year"
                data-testid="admin-upload-year"
              />
            </View>
          </View>

          <Text style={[styles.label, { marginTop: 14 }]}>File (.pdf, .doc, .docx)</Text>
          {Platform.OS === 'web' && (
            // @ts-ignore — plain DOM input, web-only admin route
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.doc,.docx,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
              onChange={(e: any) => setPickedFile(e.target.files?.[0] || null)}
              style={{ display: 'none' }}
              data-testid="admin-upload-file-input"
            />
          )}
          <TouchableOpacity
            onPress={handlePickFile}
            style={styles.filePickBtn}
            testID="admin-upload-pick-file"
            data-testid="admin-upload-pick-file"
          >
            <Ionicons name="document-attach" size={18} color="#5C6BC0" />
            <Text style={styles.filePickText}>
              {pickedFile ? `${pickedFile.name} · ${bytes(pickedFile.size)}` : 'Choose file…'}
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            onPress={handleUpload}
            disabled={uploading}
            style={[styles.primaryBtn, uploading && { opacity: 0.6 }]}
            testID="admin-upload-submit"
            data-testid="admin-upload-submit"
          >
            {uploading ? (
              <ActivityIndicator color="#FFFFFF" />
            ) : (
              <>
                <Ionicons name="cloud-upload" size={16} color="#FFFFFF" />
                <Text style={styles.primaryBtnText}>Upload to R2</Text>
              </>
            )}
          </TouchableOpacity>
        </View>

        {/* ---- Existing papers ---- */}
        <View style={styles.card} data-testid="admin-assessments-list-card">
          <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
            <Text style={styles.cardTitle}>Existing papers</Text>
            <TouchableOpacity onPress={refreshList} style={styles.refreshBtn} testID="admin-assessments-refresh">
              <Ionicons name="refresh" size={14} color="#5C6BC0" />
              <Text style={styles.refreshText}>Refresh</Text>
            </TouchableOpacity>
          </View>

          <Text style={[styles.label, { marginTop: 12 }]}>Filter by grade</Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.chipRow}>
            <TouchableOpacity
              style={[styles.chip, filterGradeId === '' && styles.chipActive]}
              onPress={() => setFilterGradeId('')}
            >
              <Text style={[styles.chipText, filterGradeId === '' && styles.chipTextActive]}>All</Text>
            </TouchableOpacity>
            {grades.map((g) => {
              const active = g.id === filterGradeId;
              return (
                <TouchableOpacity
                  key={g.id}
                  style={[styles.chip, active && styles.chipActive]}
                  onPress={() => setFilterGradeId(g.id)}
                >
                  <Text style={[styles.chipText, active && styles.chipTextActive]}>{g.name}</Text>
                </TouchableOpacity>
              );
            })}
          </ScrollView>

          <Text style={[styles.label, { marginTop: 12 }]}>Filter by term</Text>
          <View style={styles.chipRow}>
            {['all', '1', '2', '3'].map((t) => {
              const active = filterTerm === t;
              return (
                <TouchableOpacity
                  key={t}
                  style={[styles.chip, active && styles.chipActive]}
                  onPress={() => setFilterTerm(t)}
                >
                  <Text style={[styles.chipText, active && styles.chipTextActive]}>
                    {t === 'all' ? 'All' : `Term ${t}`}
                  </Text>
                </TouchableOpacity>
              );
            })}
          </View>

          <View style={{ marginTop: 12 }}>
            {loadingList ? (
              <ActivityIndicator color="#5C6BC0" />
            ) : papers.length === 0 ? (
              <Text style={styles.emptyText}>No papers match these filters yet.</Text>
            ) : (
              papers.map((p) => (
                <View key={p.key} style={styles.paperRow}>
                  <View style={{ flex: 1 }}>
                    <Text style={styles.paperTitle}>
                      {p.subjectName}{p.year ? ` — ${p.year}` : ''}
                    </Text>
                    <Text style={styles.paperMeta}>
                      {p.grade} · {p.term} · {bytes(p.sizeBytes)}
                    </Text>
                    <Text style={styles.paperKey} numberOfLines={1}>{p.key}</Text>
                  </View>
                  <TouchableOpacity
                    onPress={() => handleDelete(p.key)}
                    style={styles.deleteBtn}
                    testID={`admin-delete-${p.key}`}
                    data-testid={`admin-delete-${p.key}`}
                  >
                    <Ionicons name="trash-outline" size={16} color="#DC2626" />
                  </TouchableOpacity>
                </View>
              ))
            )}
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: 'transparent' },
  scroll: { flex: 1 },
  content: { padding: 16, paddingBottom: 48 },

  pageTitle: { fontSize: 20, fontWeight: '700', color: '#1A1A3A' },
  pageSub: { fontSize: 13, color: '#5A5A7A', marginTop: 4, marginBottom: 16 },

  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 14, padding: 16,
    borderWidth: 1, borderColor: '#DDDDF5',
    marginBottom: 16,
  },
  cardTitle: { fontSize: 15, fontWeight: '700', color: '#1A1A3A' },

  label: { fontSize: 11, fontWeight: '700', color: '#5A5A7A', textTransform: 'uppercase', letterSpacing: 0.5, marginTop: 10, marginBottom: 6 },

  chipRow: { flexDirection: 'row', gap: 8, paddingVertical: 2, flexWrap: 'wrap' },
  chip: {
    paddingHorizontal: 12, paddingVertical: 7, borderRadius: 999,
    backgroundColor: '#FFFFFF',
    borderWidth: 1, borderColor: '#DDDDF5',
  },
  chipActive: { backgroundColor: '#5C6BC0', borderColor: '#5C6BC0' },
  chipText: { fontSize: 12, color: '#374151', fontWeight: '500' },
  chipTextActive: { color: '#FFFFFF', fontWeight: '700' },

  input: {
    backgroundColor: '#F9FAFB',
    borderWidth: 1, borderColor: '#DDDDF5', borderRadius: 10,
    paddingHorizontal: 12, paddingVertical: 10,
    fontSize: 13, color: '#1A1A3A',
  },

  filePickBtn: {
    flexDirection: 'row', alignItems: 'center', gap: 8,
    backgroundColor: '#F3F4FF',
    borderWidth: 1, borderColor: '#F3F4FF', borderStyle: 'dashed' as any,
    borderRadius: 10, paddingHorizontal: 14, paddingVertical: 12,
    marginTop: 4,
  },
  filePickText: { fontSize: 13, color: '#283593', fontWeight: '600', flex: 1 },

  primaryBtn: {
    marginTop: 14, paddingVertical: 12,
    backgroundColor: '#5C6BC0',
    borderRadius: 10,
    flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 8,
  },
  primaryBtnText: { color: '#FFFFFF', fontWeight: '700', fontSize: 13 },

  refreshBtn: { flexDirection: 'row', alignItems: 'center', gap: 4 },
  refreshText: { color: '#5C6BC0', fontSize: 12, fontWeight: '600' },

  paperRow: {
    flexDirection: 'row', alignItems: 'center',
    paddingVertical: 10, gap: 10,
    borderBottomWidth: 1, borderBottomColor: '#F3F4F6',
  },
  paperTitle: { fontSize: 13, fontWeight: '700', color: '#1A1A3A' },
  paperMeta: { fontSize: 11, color: '#5A5A7A', marginTop: 2 },
  paperKey: { fontSize: 10, color: '#9CA3AF', marginTop: 2 },
  deleteBtn: { padding: 8, borderRadius: 8, backgroundColor: '#FEE2E2' },

  emptyText: { fontSize: 13, color: '#9CA3AF', paddingVertical: 12, textAlign: 'center' },
});
