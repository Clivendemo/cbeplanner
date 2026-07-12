/**
 * Revision Papers — teacher-facing screen.
 *
 * Three inline dropdowns: Grade → Term → Subject (subject controlled by grade+term).
 * Papers list filters client-side by subject. Download charges wallet via backend.
 */
import React, { useEffect, useRef, useState, useCallback } from 'react';
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

// ─── Reusable inline dropdown ─────────────────────────────────────────────────

interface DropdownProps {
  label: string;
  value: string;
  options: { label: string; value: string }[];
  onSelect: (value: string) => void;
  disabled?: boolean;
  placeholder?: string;
  testID?: string;
}

const Dropdown: React.FC<DropdownProps> = ({
  label, value, options, onSelect, disabled, placeholder = 'Select…', testID,
}) => {
  const [open, setOpen] = useState(false);
  const [menuPos, setMenuPos] = useState({ top: 0, left: 0, width: 0 });
  const triggerRef = useRef<View>(null);
  const selected = options.find((o) => o.value === value);

  // Measure the trigger button position so we can anchor the portal menu to it
  const measureAndOpen = useCallback(() => {
    if (disabled) return;
    if (!open && triggerRef.current) {
      triggerRef.current.measureInWindow((x, y, width, height) => {
        setMenuPos({ top: y + height + 4, left: x, width });
        setOpen(true);
      });
    } else {
      setOpen(false);
    }
  }, [disabled, open]);

  return (
    <View style={dd.wrap}>
      <Text style={dd.label}>{label}</Text>
      <TouchableOpacity
        ref={triggerRef}
        style={[dd.trigger, open && dd.triggerOpen, disabled && dd.triggerDisabled]}
        onPress={measureAndOpen}
        activeOpacity={0.8}
        testID={testID}
        data-testid={testID}
      >
        <Text
          style={[dd.triggerText, !selected && dd.placeholder]}
          numberOfLines={1}
        >
          {selected ? selected.label : placeholder}
        </Text>
        <Ionicons
          name={open ? 'chevron-up' : 'chevron-down'}
          size={14}
          color={disabled ? '#D1D5DB' : '#5C6BC0'}
        />
      </TouchableOpacity>

      {/* Portal modal — renders at root level so it floats above all siblings */}
      <Modal
        visible={open}
        transparent
        animationType="none"
        onRequestClose={() => setOpen(false)}
        statusBarTranslucent
      >
        {/* Invisible full-screen backdrop captures outside taps to close */}
        <TouchableOpacity
          style={dd.backdrop}
          activeOpacity={1}
          onPress={() => setOpen(false)}
        >
          {/* Menu anchored to measured trigger position */}
          <TouchableOpacity
            activeOpacity={1}
            onPress={() => {}}
            style={[
              dd.menu,
              {
                position: 'absolute',
                top: menuPos.top,
                left: menuPos.left,
                width: menuPos.width,
              },
            ]}
          >
            <ScrollView
              style={{ maxHeight: 240 }}
              nestedScrollEnabled
              showsVerticalScrollIndicator={false}
              keyboardShouldPersistTaps="handled"
            >
              {options.map((opt) => (
                <TouchableOpacity
                  key={opt.value}
                  style={[dd.option, opt.value === value && dd.optionActive]}
                  onPress={() => { onSelect(opt.value); setOpen(false); }}
                  testID={`${testID}-opt-${opt.value}`}
                  data-testid={`${testID}-opt-${opt.value}`}
                >
                  <Text style={[dd.optionText, opt.value === value && dd.optionTextActive]}>
                    {opt.label}
                  </Text>
                  {opt.value === value && (
                    <Ionicons name="checkmark" size={14} color="#5C6BC0" />
                  )}
                </TouchableOpacity>
              ))}
            </ScrollView>
          </TouchableOpacity>
        </TouchableOpacity>
      </Modal>
    </View>
  );
};

const dd = StyleSheet.create({
  wrap: { flex: 1 },
  label: {
    fontSize: 10, fontWeight: '700', color: '#5A5A7A',
    textTransform: 'uppercase', letterSpacing: 0.5, marginBottom: 5,
  },
  trigger: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    backgroundColor: '#FFFFFF', borderWidth: 1, borderColor: '#DDDDF5',
    borderRadius: 10, paddingHorizontal: 12, paddingVertical: 10, gap: 6,
  },
  triggerOpen: { borderColor: '#5C6BC0' },
  triggerDisabled: { backgroundColor: '#F9FAFB', borderColor: '#E5E7EB' },
  triggerText: { flex: 1, fontSize: 13, color: '#1A1A3A', fontWeight: '500' },
  placeholder: { color: '#9CA3AF', fontWeight: '400' },
  backdrop: {
    flex: 1,
    // Fully transparent — just captures outside taps
    backgroundColor: 'transparent',
  },
  menu: {
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#DDDDF5',
    borderRadius: 10,
    // @ts-ignore web shadow
    boxShadow: '0 4px 20px rgba(55,48,163,0.15)',
    overflow: 'hidden',
  },
  option: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    paddingHorizontal: 14, paddingVertical: 10,
    borderBottomWidth: 0.5, borderBottomColor: '#F3F4F6',
  },
  optionActive: { backgroundColor: '#F3F4FF' },
  optionText: { fontSize: 13, color: '#374151' },
  optionTextActive: { color: '#5C6BC0', fontWeight: '600' },
});

// ─── Main page ────────────────────────────────────────────────────────────────

export default function RevisionPapers() {
  const router = useRouter();
  const { firebaseUser, user } = useAuth();
  const getIdToken = async () => {
    if (!firebaseUser) throw new Error('Not authenticated');
    return firebaseUser.getIdToken();
  };

  const [grades, setGrades] = useState<Grade[]>([]);
  const [gradeId, setGradeId] = useState<string>('');
  const [term, setTerm] = useState<string>('');
  const [selectedSubject, setSelectedSubject] = useState<string>('all');
  const [loadingGrades, setLoadingGrades] = useState(true);
  const [loadingList, setLoadingList] = useState(false);
  const [items, setItems] = useState<Assessment[]>([]);
  const [costPerDownload, setCostPerDownload] = useState<number>(10);
  const [downloadingKey, setDownloadingKey] = useState<string | null>(null);
  const [topupOpen, setTopupOpen] = useState(false);
  const [topupMessage, setTopupMessage] = useState<string>('');
  const abortRef = useRef<AbortController | null>(null);

  // ── Grade options ─────────────────────────────────────────────────────────

  const gradeOptions = grades.map((g) => ({ label: g.name, value: g.id }));

  // ── Term options — always fixed ───────────────────────────────────────────

  const termOptions = [
    { label: 'Term 1', value: '1' },
    { label: 'Term 2', value: '2' },
    { label: 'Term 3', value: '3' },
  ];

  // ── Subject options — derived from fetched items ──────────────────────────

  const subjectOptions = [
    ...Array.from(new Set(items.map((i) => i.subjectName)))
      .sort()
      .map((s) => ({
        label: `${s} (${items.filter((i) => i.subjectName === s).length})`,
        value: s,
      })),
  ];

  // ── Visible papers — filtered by subject ─────────────────────────────────

  // Papers are only displayed once teacher has chosen grade + term + a specific subject
  const allSelected = Boolean(gradeId && term && selectedSubject && selectedSubject !== 'all');

  const visibleItems = selectedSubject === 'all'
    ? items
    : items.filter((i) => i.subjectName === selectedSubject);

  // ── Load grades once auth is ready ───────────────────────────────────────

  useEffect(() => {
    if (!firebaseUser) return;
    let alive = true;
    setLoadingGrades(true);
    (async () => {
      try {
        const token = await getIdToken();
        const res = await axios.get(`${BACKEND_URL}/api/grades`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!alive) return;
        const raw: any[] = Array.isArray(res.data)
          ? res.data
          : Array.isArray(res.data?.grades)
          ? res.data.grades
          : [];
        const list: Grade[] = raw.map((g: any) => ({ id: g._id || g.id, name: g.name }));
        setGrades(list);
        // Don't auto-select — teacher must choose explicitly
      } catch (e) {
        console.warn('[revision] failed to load grades', e);
      } finally {
        if (alive) setLoadingGrades(false);
      }
    })();
    return () => { alive = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [firebaseUser]);

  // ── Fetch papers when grade + term are both selected ─────────────────────
  // Subject filtering is client-side. We fetch as soon as grade+term are set
  // to populate the subject dropdown, but papers are only SHOWN once the
  // teacher also picks a subject.

  useEffect(() => {
    if (!gradeId || !term) return;
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    setLoadingList(true);
    setSelectedSubject(''); // reset subject on grade/term change
    (async () => {
      try {
        const token = await getIdToken();
        const res = await axios.get(`${BACKEND_URL}/api/assessments`, {
          params: { gradeId, term: Number(term) },
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

  // ── Download ──────────────────────────────────────────────────────────────

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
      notify(
        'Download started',
        `KES ${costPerDownload} charged. New balance: KES ${Number(newBalance ?? 0).toFixed(2)}`,
      );
    } catch (err: any) {
      const status = err?.response?.status;
      const detail = err?.response?.data?.detail;
      if (status === 402) {
        const msg =
          (typeof detail === 'object' && detail?.message) ||
          'Your wallet is running low. Top up to keep downloading assessments.';
        setTopupMessage(msg);
        setTopupOpen(true);
      } else {
        notify(
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
    // Pass returnTo=revision so profile redirects back here after a successful top-up.
    // If the teacher abandons the top-up they stay on profile — they must navigate
    // back to revision manually and start the download selection afresh.
    router.push('/(teacher)/profile?returnTo=revision');
  };

  const notify = (title: string, body?: string) => {
    const msg = body ? `${title}\n\n${body}` : title;
    if (Platform.OS === 'web' && typeof window !== 'undefined') {
      window.alert(msg);
    } else {
      Alert.alert(title, body);
    }
  };

  // ── Selected grade name (for section heading) ─────────────────────────────

  const selectedGradeName = grades.find((g) => g.id === gradeId)?.name || '';
  const selectedTermLabel = termOptions.find((t) => t.value === term)?.label || '';

  // ─────────────────────────────────────────────────────────────────────────

  return (
    <SafeAreaView style={styles.container} edges={['bottom']}>
      <ScrollView
        style={styles.scroll}
        contentContainerStyle={styles.scrollContent}
        keyboardShouldPersistTaps="handled"
      >
        {/* Header */}
        <View style={styles.header}>
          <View style={styles.headerIconWrap}>
            <Ionicons name="school" size={28} color="#5C6BC0" />
          </View>
          <View style={{ flex: 1 }}>
            <Text style={styles.title}>Revision Papers</Text>
            <Text style={styles.subtitle}>
              Download past assessments · KES {costPerDownload} per paper
            </Text>
          </View>
          <View style={styles.walletPill}>
            <Ionicons name="wallet-outline" size={14} color="#283593" />
            <Text style={styles.walletPillText}>KES {user?.walletBalance ?? 0}</Text>
          </View>
        </View>

        {/* Three dropdowns in a single row */}
        <View style={styles.filtersCard}>
          {loadingGrades ? (
            <View style={styles.loadingRow}>
              <ActivityIndicator color="#5C6BC0" size="small" />
              <Text style={styles.loadingText}>Loading grades…</Text>
            </View>
          ) : (
            <View style={styles.dropdownRow}>
              {/* Grade */}
              <Dropdown
                label="Grade"
                value={gradeId}
                options={gradeOptions}
                onSelect={(v) => setGradeId(v)}
                placeholder="Select grade"
                testID="revision-grade-dropdown"
              />

              {/* Term */}
              <Dropdown
                label="Term"
                value={term}
                options={termOptions}
                onSelect={(v) => setTerm(v)}
                testID="revision-term-dropdown"
              />

              {/* Subject — disabled until papers loaded */}
              <Dropdown
                label="Subject"
                value={selectedSubject}
                options={subjectOptions}
                onSelect={(v) => setSelectedSubject(v)}
                disabled={loadingList || items.length === 0}
                placeholder={loadingList ? 'Loading…' : 'All Subjects'}
                testID="revision-subject-dropdown"
              />
            </View>
          )}
        </View>

        {/* Papers — only shown once grade + term + subject all selected */}
        {!allSelected ? (
          <View style={styles.promptWrap}>
            <Ionicons name="filter-outline" size={36} color="#C7D2FE" />
            <Text style={styles.promptText}>
              {!gradeId
                ? 'Select a grade to get started'
                : !term
                ? 'Now select a term'
                : 'Now select a subject to see papers'}
            </Text>
          </View>
        ) : (
          <>
            <Text style={styles.sectionLabel}>
              {`${selectedSubject} — ${selectedGradeName} ${selectedTermLabel}`}
            </Text>

            {loadingList ? (
              <View style={styles.emptyWrap}>
                <ActivityIndicator color="#5C6BC0" />
                <Text style={styles.loadingText}>Loading papers…</Text>
              </View>
            ) : visibleItems.length === 0 ? (
              <View style={styles.emptyWrap}>
                <Ionicons name="file-tray-outline" size={36} color="#9CA3AF" />
                <Text style={styles.emptyText}>No {selectedSubject} papers for this selection.</Text>
                <Text style={styles.emptyHint}>Check back soon — we add fresh assessments every term.</Text>
              </View>
            ) : (
              visibleItems.map((item) => (
            <View
              key={item.key}
              style={styles.paperRow}
              data-testid={`assessment-row-${item.key}`}
            >
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
                  {item.subjectName} · {item.ext.replace('.', '').toUpperCase()} · {formatBytes(item.sizeBytes)}
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
          </>
        )}
      </ScrollView>

      {/* Insufficient-balance modal — untouched */}
      <Modal
        visible={topupOpen}
        transparent
        animationType="fade"
        onRequestClose={() => setTopupOpen(false)}
      >
        <View style={styles.modalBackdrop}>
          <View style={styles.modalCard} data-testid="assessments-topup-modal">
            <View style={styles.modalIconWrap}>
              <Ionicons name="wallet" size={32} color="#5C6BC0" />
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

// ─── Styles ───────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: 'transparent' },
  scroll: { flex: 1 },
  scrollContent: { padding: 16, paddingBottom: 48 },

  header: {
    flexDirection: 'row', alignItems: 'center',
    backgroundColor: '#FFFFFF', borderRadius: 14,
    padding: 14, marginBottom: 14, gap: 12,
    borderWidth: 1, borderColor: '#F3F4FF',
  },
  headerIconWrap: {
    width: 44, height: 44, borderRadius: 22,
    backgroundColor: '#F3F4FF',
    alignItems: 'center', justifyContent: 'center',
  },
  title: { fontSize: 18, fontWeight: '700', color: '#1A1A3A' },
  subtitle: { fontSize: 12, color: '#5A5A7A', marginTop: 2 },
  walletPill: {
    flexDirection: 'row', alignItems: 'center', gap: 4,
    backgroundColor: '#F3E8FF',
    paddingHorizontal: 8, paddingVertical: 4, borderRadius: 12,
  },
  walletPillText: { fontSize: 11, fontWeight: '700', color: '#283593' },

  filtersCard: {
    backgroundColor: '#FFFFFF', borderRadius: 14,
    borderWidth: 1, borderColor: '#DDDDF5',
    padding: 14, marginBottom: 16,
  },
  dropdownRow: {
    flexDirection: 'row',
    gap: 10,
    // No zIndex needed — dropdown menus render via Modal portal at root level
  },
  loadingRow: {
    flexDirection: 'row', alignItems: 'center', gap: 8, paddingVertical: 8,
  },
  loadingText: { fontSize: 13, color: '#9CA3AF' },

  sectionLabel: {
    fontSize: 12, fontWeight: '700', color: '#374151',
    textTransform: 'uppercase', letterSpacing: 0.5,
    marginBottom: 10,
  },

  promptWrap: {
    alignItems: 'center', justifyContent: 'center',
    paddingVertical: 48, gap: 12,
  },
  promptText: {
    fontSize: 14, color: '#9CA3AF', textAlign: 'center',
    fontWeight: '500', maxWidth: 260,
  },
  emptyWrap: {
    alignItems: 'center', justifyContent: 'center',
    paddingVertical: 40, backgroundColor: '#FFFFFF',
    borderRadius: 14, borderWidth: 1, borderColor: '#F3F4F6',
    gap: 8,
  },
  emptyText: { fontSize: 14, color: '#374151', fontWeight: '600' },
  emptyHint: { fontSize: 12, color: '#9CA3AF' },

  paperRow: {
    flexDirection: 'row', alignItems: 'center', gap: 12,
    backgroundColor: '#FFFFFF', padding: 12,
    borderRadius: 12, marginBottom: 10,
    borderWidth: 1, borderColor: '#F3F4F6',
  },
  paperIcon: {
    width: 40, height: 40, borderRadius: 10,
    backgroundColor: '#F9FAFB',
    alignItems: 'center', justifyContent: 'center',
  },
  paperTitle: { fontSize: 14, fontWeight: '600', color: '#1A1A3A' },
  paperMeta: { fontSize: 11, color: '#5A5A7A', marginTop: 2 },
  downloadBtn: {
    flexDirection: 'row', alignItems: 'center', gap: 4,
    backgroundColor: '#5C6BC0',
    paddingHorizontal: 12, paddingVertical: 8, borderRadius: 8,
    minWidth: 90, justifyContent: 'center',
  },
  downloadBtnBusy: { opacity: 0.7 },
  downloadBtnText: { color: '#FFFFFF', fontSize: 12, fontWeight: '700' },

  modalBackdrop: {
    flex: 1, backgroundColor: 'rgba(17, 24, 39, 0.55)',
    alignItems: 'center', justifyContent: 'center', padding: 20,
  },
  modalCard: {
    width: '100%', maxWidth: 400,
    backgroundColor: '#FFFFFF', borderRadius: 16,
    padding: 24, alignItems: 'center',
  },
  modalIconWrap: {
    width: 64, height: 64, borderRadius: 32,
    backgroundColor: '#F3F4FF',
    alignItems: 'center', justifyContent: 'center', marginBottom: 12,
  },
  modalTitle: { fontSize: 18, fontWeight: '700', color: '#1A1A3A', marginBottom: 6 },
  modalBody: { fontSize: 13, color: '#4B5563', textAlign: 'center', lineHeight: 20, marginBottom: 18 },
  modalActions: { flexDirection: 'row', gap: 10, width: '100%' },
  modalSecondary: {
    flex: 1, paddingVertical: 12, borderRadius: 10,
    borderWidth: 1, borderColor: '#DDDDF5', alignItems: 'center',
  },
  modalSecondaryText: { color: '#374151', fontWeight: '600', fontSize: 13 },
  modalPrimary: {
    flex: 1, paddingVertical: 12, borderRadius: 10,
    backgroundColor: '#5C6BC0',
    flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 6,
  },
  modalPrimaryText: { color: '#FFFFFF', fontWeight: '700', fontSize: 13 },
});
