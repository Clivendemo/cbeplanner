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
  Modal,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { SafeAreaView } from 'react-native-safe-area-context';
import axios from 'axios';
import { useAuth } from '../../contexts/AuthContext';
import { useDebouncedAction } from '../../hooks/useDebouncedAction';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

interface Grade { id: string; name: string }
interface CurriculumSubject { id: string; name: string }
interface CurriculumStrand { id: string; name: string }
interface AdminPaper {
  key: string;
  grade: string;
  term: string;
  subjectName: string;
  year: number | null;
  sizeBytes: number;
  uploadedAt: string | null;
  subjectId: string | null;
  strandIds: string[];
  strandNames: string[];
}

// Mirrors backend `_grade_slug`: grade.name lowercased, spaces → hyphens.
const gradeSlug = (name: string) => name.trim().toLowerCase().replace(/\s+/g, '-');

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

  // ── Strand tagging modal ───────────────────────────────────────────────
  const [tagModalOpen, setTagModalOpen] = useState(false);
  const [tagTargetPaper, setTagTargetPaper] = useState<AdminPaper | null>(null);
  const [tagSubjects, setTagSubjects] = useState<CurriculumSubject[]>([]);
  const [tagSubjectId, setTagSubjectId] = useState<string>('');
  const [tagStrands, setTagStrands] = useState<CurriculumStrand[]>([]);
  const [tagSelectedStrandIds, setTagSelectedStrandIds] = useState<string[]>([]);
  const [tagLoadingSubjects, setTagLoadingSubjects] = useState(false);
  const [tagLoadingStrands, setTagLoadingStrands] = useState(false);
  const [tagSaving, setTagSaving] = useState(false);

  // Native file picker (web only — admin is web-only anyway)
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [pickedFiles, setPickedFiles] = useState<File[]>([]);

  // React Native's Alert is a silent no-op on web. Use the real window.alert
  // so admins actually see validation feedback when clicking "Upload to R2".
  const notify = (title: string, body?: string) => {
    const msg = body ? `${title}\n\n${body}` : title;
    if (Platform.OS === 'web' && typeof window !== 'undefined') {
      window.alert(msg);
    } else {
      Alert.alert(title, body);
    }
  };

  // Load grades once
  useEffect(() => {
    (async () => {
      try {
        const token = await getIdToken();
        const res = await axios.get(`${BACKEND_URL}/api/grades`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        // Backend returns { success: true, grades: [...] }; handle both shapes
        // defensively so this never silently breaks the upload form again.
        const raw: any[] = Array.isArray(res.data)
          ? res.data
          : Array.isArray(res.data?.grades)
          ? res.data.grades
          : [];
        const list: Grade[] = raw.map((g: any) => ({ id: g._id || g.id, name: g.name }));
        setGrades(list);
        if (list.length && !gradeId) setGradeId(list[0].id);
      } catch (e) {
        // surface the failure so admins know why grades didn't load
        // eslint-disable-next-line no-console
        console.warn('[admin/assessments] failed to load grades', e);
      }
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
      const res = await axios.get(`${BACKEND_URL}/api/admin/papers`, {
        params,
        headers: { Authorization: `Bearer ${token}` },
      });
      setPapers(res.data.items || []);
    } catch (e: any) {
      const detail = e?.response?.data?.detail || e?.message;
      notify('Unable to load papers', typeof detail === 'string' ? detail : 'Please try again.');
    } finally {
      setLoadingList(false);
    }
  };

  useEffect(() => { refreshList(); /* eslint-disable-line react-hooks/exhaustive-deps */ }, [filterGradeId, filterTerm]);

  const handleUpload = useDebouncedAction(async () => {
    if (pickedFiles.length === 0) { notify('Pick a file', 'Please choose at least one PDF or Word document.'); return; }
    if (pickedFiles.length > 5) { notify('Too many files', 'Maximum 5 files per upload session.'); return; }
    if (!gradeId) { notify('Missing grade', 'Please pick a grade.'); return; }
    if (!subject.trim()) { notify('Missing subject', 'Please type a subject name.'); return; }
    const y = parseInt(year, 10);
    if (!y || y < 2000 || y > 2100) { notify('Invalid year', 'Enter a 4-digit year.'); return; }

    setUploading(true);
    try {
      const token = await getIdToken();
      const fd = new FormData();
      pickedFiles.forEach((f) => fd.append('files', f));
      fd.append('gradeId', gradeId);
      fd.append('term', String(term));
      fd.append('subject', subject.trim());
      fd.append('year', String(y));
      const res = await axios.post(`${BACKEND_URL}/api/admin/papers/upload`, fd, {
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'multipart/form-data' },
      });
      const uploaded = (res.data.results || []).filter((r: any) => r.success);
      const failed = (res.data.results || []).filter((r: any) => !r.success);
      let msg = `${uploaded.length} of ${res.data.totalSubmitted} file(s) uploaded successfully.`;
      if (failed.length) {
        msg += '\n\nFailed:\n' + failed.map((r: any) => `• ${r.filename}: ${r.error}`).join('\n');
      }
      notify('Upload complete', msg);
      setPickedFiles([]);
      setSubject('');
      if (fileInputRef.current) fileInputRef.current.value = '';
      refreshList();
    } catch (e: any) {
      const detail = e?.response?.data?.detail || e?.message;
      notify('Upload failed', typeof detail === 'string' ? detail : 'Please try again.');
    } finally {
      setUploading(false);
    }
  });

  const handleDelete = useDebouncedAction(async (key: string) => {
    if (typeof window !== 'undefined' && !window.confirm(`Delete this paper?\n\n${key}`)) return;
    try {
      const token = await getIdToken();
      await axios.delete(`${BACKEND_URL}/api/admin/papers`, {
        data: { key },
        headers: { Authorization: `Bearer ${token}` },
      });
      setPapers((prev) => prev.filter((p) => p.key !== key));
    } catch (e: any) {
      const detail = e?.response?.data?.detail || e?.message;
      notify('Delete failed', typeof detail === 'string' ? detail : 'Please try again.');
    }
  });

  // Paper only carries a grade *slug* (e.g. "grade-10"); resolve it back to
  // the curriculum gradeId so we can look up real subjects/strands for it.
  const resolveGradeId = (slug: string): string | undefined =>
    grades.find((g) => gradeSlug(g.name) === slug)?.id;

  const openTagModal = async (paper: AdminPaper) => {
    setTagTargetPaper(paper);
    setTagModalOpen(true);
    setTagSubjects([]);
    setTagStrands([]);
    setTagSubjectId(paper.subjectId || '');
    setTagSelectedStrandIds(paper.strandIds || []);

    const gId = resolveGradeId(paper.grade);
    if (!gId) {
      notify('Unable to resolve grade', 'Could not match this paper to a curriculum grade.');
      return;
    }
    setTagLoadingSubjects(true);
    try {
      const token = await getIdToken();
      const res = await axios.get(`${BACKEND_URL}/api/admin/subjects`, {
        params: { gradeId: gId },
        headers: { Authorization: `Bearer ${token}` },
      });
      const list: CurriculumSubject[] = (res.data?.subjects || []).map((s: any) => ({
        id: s._id || s.id,
        name: s.name,
      }));
      setTagSubjects(list);
      // If the paper already has a subjectId tagged, load its strands right away.
      if (paper.subjectId) {
        loadTagStrands(paper.subjectId);
      }
    } catch (e) {
      notify('Unable to load subjects', 'Please try again.');
    } finally {
      setTagLoadingSubjects(false);
    }
  };

  const loadTagStrands = async (subjectId: string) => {
    setTagLoadingStrands(true);
    setTagStrands([]);
    try {
      const token = await getIdToken();
      const res = await axios.get(`${BACKEND_URL}/api/admin/strands`, {
        params: { subjectId },
        headers: { Authorization: `Bearer ${token}` },
      });
      const list: CurriculumStrand[] = (res.data?.strands || []).map((s: any) => ({
        id: s._id || s.id,
        name: s.name,
      }));
      setTagStrands(list);
    } catch (e) {
      notify('Unable to load strands', 'Please try again.');
    } finally {
      setTagLoadingStrands(false);
    }
  };

  const handleTagSubjectSelect = (subjectId: string) => {
    setTagSubjectId(subjectId);
    // Changing subject invalidates any previously selected strands from a
    // different subject — start the strand selection fresh.
    setTagSelectedStrandIds([]);
    if (subjectId) loadTagStrands(subjectId);
    else setTagStrands([]);
  };

  const toggleTagStrand = (strandId: string) => {
    setTagSelectedStrandIds((prev) =>
      prev.includes(strandId) ? prev.filter((id) => id !== strandId) : [...prev, strandId]
    );
  };

  const closeTagModal = () => {
    setTagModalOpen(false);
    setTagTargetPaper(null);
  };

  const saveTagStrands = useDebouncedAction(async () => {
    if (!tagTargetPaper) return;
    if (!tagSubjectId) { notify('Pick a subject', 'Choose which curriculum subject this paper belongs to.'); return; }
    setTagSaving(true);
    try {
      const token = await getIdToken();
      const res = await axios.put(
        `${BACKEND_URL}/api/admin/papers/strands`,
        { key: tagTargetPaper.key, subjectId: tagSubjectId, strandIds: tagSelectedStrandIds },
        { headers: { Authorization: `Bearer ${token}` } },
      );
      const { subjectId, strandIds, strandNames } = res.data || {};
      setPapers((prev) =>
        prev.map((p) => (p.key === tagTargetPaper.key ? { ...p, subjectId, strandIds, strandNames } : p))
      );
      closeTagModal();
    } catch (e: any) {
      const detail = e?.response?.data?.detail || e?.message;
      notify('Save failed', typeof detail === 'string' ? detail : 'Please try again.');
    } finally {
      setTagSaving(false);
    }
  });

  return (
    <SafeAreaView style={styles.container} edges={['bottom']}>
      <ScrollView style={styles.scroll} contentContainerStyle={styles.content}>
        <Text style={styles.pageTitle}>Past Papers (Assessments)</Text>
        <Text style={styles.pageSub}>
          Upload up to 5 .pdf / .doc / .docx files at once to Cloudflare R2. Teachers pay KES 10 per download.
        </Text>

        {/* ---- Upload card ---- */}
        <View style={styles.card} data-testid="admin-assessments-upload-card">
          <Text style={styles.cardTitle}>Upload papers (up to 5 at once)</Text>

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

          <Text style={[styles.label, { marginTop: 14 }]}>Files (.pdf, .doc, .docx — up to 5)</Text>
          {Platform.OS === 'web' ? (
            // Plain DOM label → input: RN Web passes these through to real
            // HTML. TouchableOpacity + hidden input is flaky on RN Web because
            // refs don't always attach cleanly; a native <label htmlFor> is
            // bulletproof and still matches the design.
            // @ts-ignore — web-only escape hatch
            <label
              htmlFor="admin-upload-file-input"
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                backgroundColor: '#F3F4FF',
                border: '1px dashed #DDDDF5',
                borderRadius: 10,
                padding: '12px 14px',
                cursor: 'pointer',
                color: '#283593',
                fontWeight: 600,
                fontSize: 13,
              }}
              data-testid="admin-upload-pick-file"
            >
              <Ionicons name="document-attach" size={18} color="#5C6BC0" />
              <span>
                {pickedFiles.length === 0
                  ? 'Choose up to 5 files…'
                  : pickedFiles.length === 1
                  ? `${pickedFiles[0].name} · ${bytes(pickedFiles[0].size)}`
                  : `${pickedFiles.length} files selected · ${bytes(pickedFiles.reduce((s, f) => s + f.size, 0))} total`}
              </span>
              {/* @ts-ignore */}
              <input
                id="admin-upload-file-input"
                ref={fileInputRef}
                type="file"
                accept=".pdf,.doc,.docx,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                multiple
                onChange={(e: any) => setPickedFiles(Array.from(e.target.files || []))}
                style={{ display: 'none' }}
                data-testid="admin-upload-file-input"
              />
            </label>
          ) : (
            <TouchableOpacity
              onPress={() => notify('File picker unavailable', 'Open the admin page in a web browser to upload files.')}
              style={styles.filePickBtn}
            >
              <Ionicons name="document-attach" size={18} color="#5C6BC0" />
              <Text style={styles.filePickText}>Choose file…</Text>
            </TouchableOpacity>
          )}

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
                    {p.strandNames && p.strandNames.length > 0 ? (
                      <View style={styles.strandChipRow}>
                        {p.strandNames.map((s) => (
                          <View key={s} style={styles.strandChip}>
                            <Text style={styles.strandChipText}>{s}</Text>
                          </View>
                        ))}
                      </View>
                    ) : (
                      <Text style={styles.strandsPending}>No strands tagged yet</Text>
                    )}
                  </View>
                  <TouchableOpacity
                    onPress={() => openTagModal(p)}
                    style={styles.tagBtn}
                    testID={`admin-tag-strands-${p.key}`}
                    data-testid={`admin-tag-strands-${p.key}`}
                  >
                    <Ionicons name="pricetag-outline" size={16} color="#283593" />
                  </TouchableOpacity>
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

      {/* ---- Strand tagging modal ---- */}
      <Modal
        visible={tagModalOpen}
        transparent
        animationType="fade"
        onRequestClose={closeTagModal}
      >
        <View style={styles.tagModalBackdrop}>
          <View style={styles.tagModalCard} data-testid="admin-tag-strands-modal">
            <Text style={styles.modalTitle}>Tag strands covered</Text>
            {tagTargetPaper && (
              <Text style={styles.modalSub} numberOfLines={2}>
                {tagTargetPaper.subjectName}{tagTargetPaper.year ? ` — ${tagTargetPaper.year}` : ''} · {tagTargetPaper.grade} · {tagTargetPaper.term}
              </Text>
            )}

            <Text style={[styles.label, { marginTop: 14 }]}>Curriculum subject</Text>
            {tagLoadingSubjects ? (
              <ActivityIndicator color="#5C6BC0" style={{ marginTop: 8 }} />
            ) : tagSubjects.length === 0 ? (
              <Text style={styles.emptyText}>No curriculum subjects found for this grade.</Text>
            ) : (
              <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.chipRow}>
                {tagSubjects.map((s) => {
                  const active = s.id === tagSubjectId;
                  return (
                    <TouchableOpacity
                      key={s.id}
                      style={[styles.chip, active && styles.chipActive]}
                      onPress={() => handleTagSubjectSelect(s.id)}
                      testID={`admin-tag-subject-${s.id}`}
                      data-testid={`admin-tag-subject-${s.id}`}
                    >
                      <Text style={[styles.chipText, active && styles.chipTextActive]}>{s.name}</Text>
                    </TouchableOpacity>
                  );
                })}
              </ScrollView>
            )}

            <Text style={[styles.label, { marginTop: 14 }]}>Strands covered by this paper</Text>
            {tagLoadingStrands ? (
              <ActivityIndicator color="#5C6BC0" style={{ marginTop: 8 }} />
            ) : !tagSubjectId ? (
              <Text style={styles.emptyText}>Pick a subject first.</Text>
            ) : tagStrands.length === 0 ? (
              <Text style={styles.emptyText}>No strands found for this subject.</Text>
            ) : (
              <ScrollView style={styles.strandListScroll} nestedScrollEnabled>
                {tagStrands.map((s) => {
                  const checked = tagSelectedStrandIds.includes(s.id);
                  return (
                    <TouchableOpacity
                      key={s.id}
                      style={styles.strandOption}
                      onPress={() => toggleTagStrand(s.id)}
                      testID={`admin-tag-strand-${s.id}`}
                      data-testid={`admin-tag-strand-${s.id}`}
                    >
                      <Ionicons
                        name={checked ? 'checkbox' : 'square-outline'}
                        size={18}
                        color={checked ? '#5C6BC0' : '#9CA3AF'}
                      />
                      <Text style={styles.strandOptionText}>{s.name}</Text>
                    </TouchableOpacity>
                  );
                })}
              </ScrollView>
            )}

            <View style={styles.modalActions}>
              <TouchableOpacity onPress={closeTagModal} style={styles.modalSecondary} data-testid="admin-tag-cancel">
                <Text style={styles.modalSecondaryText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity
                onPress={saveTagStrands}
                disabled={tagSaving}
                style={[styles.modalPrimary, tagSaving && { opacity: 0.6 }]}
                data-testid="admin-tag-save"
              >
                {tagSaving ? (
                  <ActivityIndicator color="#FFFFFF" size="small" />
                ) : (
                  <Text style={styles.modalPrimaryText}>Save</Text>
                )}
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
    flexDirection: 'row', alignItems: 'flex-start',
    paddingVertical: 10, gap: 10,
    borderBottomWidth: 1, borderBottomColor: '#F3F4F6',
  },
  paperTitle: { fontSize: 13, fontWeight: '700', color: '#1A1A3A' },
  paperMeta: { fontSize: 11, color: '#5A5A7A', marginTop: 2 },
  paperKey: { fontSize: 10, color: '#9CA3AF', marginTop: 2 },
  deleteBtn: { padding: 8, borderRadius: 8, backgroundColor: '#FEE2E2' },
  tagBtn: { padding: 8, borderRadius: 8, backgroundColor: '#F3F4FF' },

  strandChipRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 6, marginTop: 6 },
  strandChip: {
    backgroundColor: '#F3F4FF',
    borderWidth: 1, borderColor: '#DDDDF5',
    borderRadius: 999,
    paddingHorizontal: 9, paddingVertical: 4,
  },
  strandChipText: { fontSize: 10.5, color: '#283593', fontWeight: '600' },
  strandsPending: { fontSize: 11, color: '#9CA3AF', fontStyle: 'italic', marginTop: 4 },

  tagModalBackdrop: {
    flex: 1, backgroundColor: 'rgba(17, 24, 39, 0.55)',
    alignItems: 'center', justifyContent: 'center', padding: 20,
  },
  tagModalCard: {
    width: '100%', maxWidth: 480,
    backgroundColor: '#FFFFFF', borderRadius: 16,
    padding: 20,
  },
  modalTitle: { fontSize: 17, fontWeight: '700', color: '#1A1A3A' },
  modalSub: { fontSize: 12, color: '#5A5A7A', marginTop: 4 },
  strandListScroll: {
    maxHeight: 220, marginTop: 8,
    borderWidth: 1, borderColor: '#F3F4F6', borderRadius: 10,
  },
  strandOption: {
    flexDirection: 'row', alignItems: 'center', gap: 10,
    paddingHorizontal: 12, paddingVertical: 10,
    borderBottomWidth: 0.5, borderBottomColor: '#F3F4F6',
  },
  strandOptionText: { fontSize: 13, color: '#374151', flex: 1 },
  modalActions: { flexDirection: 'row', gap: 10, marginTop: 18 },
  modalSecondary: {
    flex: 1, paddingVertical: 12, borderRadius: 10,
    borderWidth: 1, borderColor: '#DDDDF5', alignItems: 'center',
  },
  modalSecondaryText: { color: '#374151', fontWeight: '600', fontSize: 13 },
  modalPrimary: {
    flex: 1, paddingVertical: 12, borderRadius: 10,
    backgroundColor: '#5C6BC0', alignItems: 'center', justifyContent: 'center',
  },
  modalPrimaryText: { color: '#FFFFFF', fontWeight: '700', fontSize: 13 },

  emptyText: { fontSize: 13, color: '#9CA3AF', paddingVertical: 12, textAlign: 'center' },
});
