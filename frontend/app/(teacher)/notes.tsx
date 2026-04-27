import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
  Modal,
  Platform,
  Linking,
} from 'react-native';
import { Picker } from '@react-native-picker/picker';
import { useAuth } from '../../contexts/AuthContext';
import { Ionicons } from '@expo/vector-icons';
import { SafeAreaView } from 'react-native-safe-area-context';
import axios from 'axios';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

interface Grade { id: string; name: string; }
interface Subject { id: string; name: string; }
interface Strand { id: string; name: string; }
interface SubStrand { id: string; name: string; }
interface NotesSection {
  title: string;
  explanation: string;
  examples: string;
  applications: string;
}
interface GeneratedContent {
  title: string;
  introduction: string;
  sections: NotesSection[];
  key_terms: { term: string; meaning: string }[];
  practice_questions: string[];
  summary: string;
  activities: string[];
}
interface NotesData {
  id: string;
  teacherName: string;
  schoolName: string;
  gradeName: string;
  subjectName: string;
  strandName: string;
  substrandName: string;
  generatedContent: GeneratedContent;
  downloaded: boolean;
}

export default function Notes() {
  const { user, firebaseUser, refreshProfile } = useAuth();

  // Form state
  const [grades, setGrades] = useState<Grade[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [strands, setStrands] = useState<Strand[]>([]);
  const [substrands, setSubstrands] = useState<SubStrand[]>([]);

  const [selectedGrade, setSelectedGrade] = useState('');
  const [selectedSubject, setSelectedSubject] = useState('');
  const [selectedStrand, setSelectedStrand] = useState('');
  const [selectedSubstrand, setSelectedSubstrand] = useState('');

  const [generating, setGenerating] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [generatedNotes, setGeneratedNotes] = useState<NotesData | null>(null);

  // Insufficient funds modal
  const [showTopUpModal, setShowTopUpModal] = useState(false);
  const [pendingDownloadId, setPendingDownloadId] = useState<string | null>(null);

  const getHeaders = useCallback(async () => {
    if (firebaseUser) {
      const token = await firebaseUser.getIdToken();
      return { Authorization: `Bearer ${token}` };
    }
    return {};
  }, [firebaseUser]);

  // ── Load grades on mount ──
  useEffect(() => {
    (async () => {
      try {
        const headers = await getHeaders();
        const res = await axios.get(`${BACKEND_URL}/api/grades`, { headers });
        if (res.data.success) setGrades(res.data.grades);
      } catch (_) {}
    })();
  }, []);

  // ── Cascade: grade → subjects ──
  useEffect(() => {
    if (!selectedGrade) { setSubjects([]); setSelectedSubject(''); return; }
    (async () => {
      try {
        const headers = await getHeaders();
        const res = await axios.get(`${BACKEND_URL}/api/subjects?gradeId=${selectedGrade}`, { headers });
        if (res.data.success) setSubjects(res.data.subjects);
      } catch (_) {}
    })();
    setSelectedSubject('');
    setStrands([]);
    setSelectedStrand('');
    setSubstrands([]);
    setSelectedSubstrand('');
  }, [selectedGrade]);

  // ── Cascade: subject → strands ──
  useEffect(() => {
    if (!selectedSubject) { setStrands([]); setSelectedStrand(''); return; }
    (async () => {
      try {
        const headers = await getHeaders();
        const res = await axios.get(`${BACKEND_URL}/api/strands?subjectId=${selectedSubject}`, { headers });
        if (res.data.success) setStrands(res.data.strands);
      } catch (_) {}
    })();
    setSelectedStrand('');
    setSubstrands([]);
    setSelectedSubstrand('');
  }, [selectedSubject]);

  // ── Cascade: strand → substrands ──
  useEffect(() => {
    if (!selectedStrand) { setSubstrands([]); setSelectedSubstrand(''); return; }
    (async () => {
      try {
        const headers = await getHeaders();
        const res = await axios.get(`${BACKEND_URL}/api/substrands?strandId=${selectedStrand}`, { headers });
        if (res.data.success) setSubstrands(res.data.substrands);
      } catch (_) {}
    })();
    setSelectedSubstrand('');
  }, [selectedStrand]);

  // ── Generate notes ──
  const handleGenerate = async () => {
    if (!selectedGrade || !selectedSubject || !selectedStrand || !selectedSubstrand) {
      Alert.alert('Incomplete Selection', 'Please select Grade, Subject, Strand, and Sub-strand.');
      return;
    }
    setGenerating(true);
    try {
      const headers = await getHeaders();
      const res = await axios.post(`${BACKEND_URL}/api/notes/generate`, {
        gradeId: selectedGrade,
        subjectId: selectedSubject,
        strandId: selectedStrand,
        substrandId: selectedSubstrand,
        duration: 60,
      }, { headers });
      if (res.data.success) {
        setGeneratedNotes(res.data.notes);
      }
    } catch (err: any) {
      Alert.alert('Error', err.response?.data?.detail || 'Failed to generate notes.');
    } finally {
      setGenerating(false);
    }
  };

  // ── Download PDF ──
  const handleDownload = async (noteId?: string) => {
    const id = noteId || generatedNotes?.id;
    if (!id) return;
    setDownloading(true);
    try {
      const headers = await getHeaders();
      const res = await axios.post(
        `${BACKEND_URL}/api/notes/${id}/download`,
        {},
        { headers, responseType: Platform.OS === 'web' ? 'blob' : 'arraybuffer' },
      );
      // Trigger download on web
      if (Platform.OS === 'web') {
        const blob = new Blob([res.data], { type: 'application/pdf' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `notes_${id}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      } else {
        // On mobile, share the PDF
        Alert.alert('Success', 'Notes PDF downloaded successfully.');
      }
      setPendingDownloadId(null);
      refreshProfile();
    } catch (err: any) {
      if (err.response?.status === 402) {
        // Insufficient funds
        setPendingDownloadId(id);
        setShowTopUpModal(true);
      } else {
        Alert.alert('Error', 'Failed to download PDF. Please try again.');
      }
    } finally {
      setDownloading(false);
    }
  };

  // ── Auto-resume download after top-up ──
  const handleTopUpAndRetry = () => {
    setShowTopUpModal(false);
    // Navigate to profile/wallet for top-up — after returning, user clicks download again
    Alert.alert(
      'Top Up Required',
      'Please go to your Profile to top up via M-Pesa, then come back and try downloading again.',
    );
  };

  // ── Preview: rendered in-app (free) ──
  const renderPreview = () => {
    if (!generatedNotes) return null;
    const c = generatedNotes.generatedContent;
    return (
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
        keyboardShouldPersistTaps="always"
      >
        {/* Header */}
        <View style={styles.previewHeader} data-testid="notes-preview-header">
          <Text style={styles.previewSchool}>{(generatedNotes.schoolName || '').toUpperCase()}</Text>
          <Text style={styles.previewTitle}>NOTES</Text>
          <View style={styles.previewMeta}>
            <Text style={styles.previewMetaText}>Subject: {generatedNotes.subjectName}</Text>
            <Text style={styles.previewMetaText}>Strand: {generatedNotes.strandName}</Text>
            <Text style={styles.previewMetaText}>Sub-strand: {generatedNotes.substrandName}</Text>
            <Text style={styles.previewMetaText}>Grade: {generatedNotes.gradeName}</Text>
          </View>
        </View>

        {/* Introduction */}
        {c.introduction ? (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>INTRODUCTION</Text>
            <Text style={styles.bodyText}>{c.introduction}</Text>
          </View>
        ) : null}

        {/* Main Content */}
        {c.sections && c.sections.length > 0 ? (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>MAIN CONTENT</Text>
            {c.sections.map((sec: NotesSection, i: number) => (
              <View key={i} style={styles.conceptBlock}>
                <Text style={styles.conceptTitle}>{i + 1}. {sec.title}</Text>
                <Text style={styles.bodyText}>{sec.explanation}</Text>
                {sec.examples ? (
                  <>
                    <Text style={styles.subHeading}>Examples</Text>
                    <Text style={styles.bodyText}>{sec.examples}</Text>
                  </>
                ) : null}
                {sec.applications ? (
                  <>
                    <Text style={styles.subHeading}>Real-life Applications</Text>
                    <Text style={styles.bodyText}>{sec.applications}</Text>
                  </>
                ) : null}
              </View>
            ))}
          </View>
        ) : null}

        {/* Key Terms */}
        {c.key_terms && c.key_terms.length > 0 ? (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>KEY TERMS</Text>
            {c.key_terms.map((kt: { term: string; meaning: string }, i: number) => (
              <View key={i} style={styles.termRow}>
                <Text style={styles.termLabel}>{kt.term}: </Text>
                <Text style={styles.termMeaning}>{kt.meaning}</Text>
              </View>
            ))}
          </View>
        ) : null}

        {/* Practice Questions */}
        {c.practice_questions && c.practice_questions.length > 0 ? (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>PRACTICE QUESTIONS</Text>
            {c.practice_questions.map((q: string, i: number) => (
              <Text key={i} style={styles.questionText}>{i + 1}. {q}</Text>
            ))}
          </View>
        ) : null}

        {/* Summary */}
        {c.summary ? (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>SUMMARY</Text>
            <Text style={styles.bodyText}>{c.summary}</Text>
          </View>
        ) : null}

        {/* Action Buttons */}
        <View style={styles.actionRow} data-testid="notes-action-buttons">
          <TouchableOpacity
            style={styles.downloadBtn}
            onPress={() => handleDownload()}
            disabled={downloading}
            data-testid="notes-download-btn"
          >
            {downloading ? (
              <ActivityIndicator color="#FFFFFF" size="small" />
            ) : (
              <>
                <Ionicons name="download" size={20} color="#FFFFFF" />
                <Text style={styles.downloadBtnText}>Download PDF</Text>
              </>
            )}
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.newBtn}
            onPress={() => setGeneratedNotes(null)}
            data-testid="notes-generate-new-btn"
          >
            <Ionicons name="add-circle" size={20} color="#5C6BC0" />
            <Text style={styles.newBtnText}>New Notes</Text>
          </TouchableOpacity>
        </View>

        <View style={{ height: 40 }} />
      </ScrollView>
    );
  };

  // ── Form ──
  const renderForm = () => (
    <ScrollView
      contentContainerStyle={styles.scrollContent}
      showsVerticalScrollIndicator={false}
      keyboardShouldPersistTaps="always"
    >
      <View style={styles.card} data-testid="notes-form-card">
        <Text style={styles.cardTitle}>Generate Study Notes</Text>
        <Text style={styles.cardSubtitle}>Select topic details to generate KICD-aligned notes</Text>

        {/* Grade */}
        <View style={styles.inputGroup}>
          <Text style={styles.label}>Grade</Text>
          <View style={styles.pickerWrap}>
            <Picker
              selectedValue={selectedGrade}
              onValueChange={(v: string) => setSelectedGrade(v)}
              style={styles.picker}
              data-testid="notes-grade-picker"
            >
              <Picker.Item label="Select Grade" value="" />
              {grades.map(g => <Picker.Item key={g.id} label={g.name} value={g.id} />)}
            </Picker>
          </View>
        </View>

        {/* Subject */}
        <View style={styles.inputGroup}>
          <Text style={styles.label}>Subject</Text>
          <View style={styles.pickerWrap}>
            <Picker
              selectedValue={selectedSubject}
              onValueChange={(v: string) => setSelectedSubject(v)}
              style={styles.picker}
              enabled={subjects.length > 0}
              data-testid="notes-subject-picker"
            >
              <Picker.Item label={subjects.length ? "Select Subject" : "Select Grade first"} value="" />
              {subjects.map(s => <Picker.Item key={s.id} label={s.name} value={s.id} />)}
            </Picker>
          </View>
        </View>

        {/* Strand */}
        <View style={styles.inputGroup}>
          <Text style={styles.label}>Strand</Text>
          <View style={styles.pickerWrap}>
            <Picker
              selectedValue={selectedStrand}
              onValueChange={(v: string) => setSelectedStrand(v)}
              style={styles.picker}
              enabled={strands.length > 0}
              data-testid="notes-strand-picker"
            >
              <Picker.Item label={strands.length ? "Select Strand" : "Select Subject first"} value="" />
              {strands.map(s => <Picker.Item key={s.id} label={s.name} value={s.id} />)}
            </Picker>
          </View>
        </View>

        {/* Sub-strand */}
        <View style={styles.inputGroup}>
          <Text style={styles.label}>Sub-strand</Text>
          <View style={styles.pickerWrap}>
            <Picker
              selectedValue={selectedSubstrand}
              onValueChange={(v: string) => setSelectedSubstrand(v)}
              style={styles.picker}
              enabled={substrands.length > 0}
              data-testid="notes-substrand-picker"
            >
              <Picker.Item label={substrands.length ? "Select Sub-strand" : "Select Strand first"} value="" />
              {substrands.map(s => <Picker.Item key={s.id} label={s.name} value={s.id} />)}
            </Picker>
          </View>
        </View>

        {/* Generate Button */}
        <TouchableOpacity
          style={[styles.generateBtn, generating && styles.btnDisabled]}
          onPress={handleGenerate}
          disabled={generating}
          data-testid="notes-generate-btn"
        >
          {generating ? (
            <ActivityIndicator color="#FFFFFF" size="small" />
          ) : (
            <>
              <Ionicons name="create" size={20} color="#FFFFFF" />
              <Text style={styles.generateBtnText}>Generate Notes</Text>
            </>
          )}
        </TouchableOpacity>
      </View>

      {/* Info card */}
      <View style={styles.infoCard}>
        <Ionicons name="information-circle" size={22} color="#5C6BC0" />
        <View style={styles.infoContent}>
          <Text style={styles.infoTitle}>How it works</Text>
          <Text style={styles.infoText}>
            1. Select your topic details{'\n'}
            2. Click "Generate Notes"{'\n'}
            3. Preview notes for free{'\n'}
            4. Download PDF (KES 1 per download, first one free)
          </Text>
        </View>
      </View>
    </ScrollView>
  );

  return (
    <SafeAreaView style={styles.container} edges={['bottom']}>
      {generatedNotes ? renderPreview() : renderForm()}

      {/* Insufficient Funds Modal */}
      <Modal
        visible={showTopUpModal}
        transparent
        animationType="fade"
        onRequestClose={() => setShowTopUpModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalCard} data-testid="notes-topup-modal">
            <Ionicons name="wallet-outline" size={48} color="#F59E0B" style={{ alignSelf: 'center' }} />
            <Text style={styles.modalTitle}>You're almost there!</Text>
            <Text style={styles.modalBody}>
              To download these notes, you need KES 1.{'\n\n'}
              Your current balance: KES {user?.walletBalance || 0}{'\n\n'}
              Please top up your wallet to continue.
            </Text>
            <TouchableOpacity
              style={styles.modalTopUpBtn}
              onPress={handleTopUpAndRetry}
              data-testid="notes-topup-btn"
            >
              <Ionicons name="card" size={18} color="#FFFFFF" />
              <Text style={styles.modalTopUpText}>Top Up via M-Pesa</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={styles.modalCancelBtn}
              onPress={() => setShowTopUpModal(false)}
              data-testid="notes-topup-cancel-btn"
            >
              <Text style={styles.modalCancelText}>Cancel</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: 'transparent' },
  scrollContent: { padding: 16 },

  // ── Form Card ──
  card: { backgroundColor: '#FFFFFF', borderRadius: 16, padding: 20, marginBottom: 16 },
  cardTitle: { fontSize: 20, fontWeight: 'bold', color: '#1A1A3A', marginBottom: 4 },
  cardSubtitle: { fontSize: 13, color: '#5A5A7A', marginBottom: 20 },
  inputGroup: { marginBottom: 14 },
  label: { fontSize: 14, fontWeight: '600', color: '#374151', marginBottom: 6 },
  pickerWrap: {
    backgroundColor: '#F9FAFB',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#DDDDF5',
    overflow: 'hidden',
  },
  picker: { height: 50 },

  generateBtn: {
    backgroundColor: '#10B981',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 14,
    borderRadius: 12,
    marginTop: 8,
  },
  btnDisabled: { opacity: 0.6 },
  generateBtnText: { color: '#FFF', fontSize: 16, fontWeight: '600', marginLeft: 8 },

  // ── Info Card ──
  infoCard: {
    backgroundColor: '#F3F4FF',
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  infoContent: { marginLeft: 12, flex: 1 },
  infoTitle: { fontSize: 14, fontWeight: '600', color: '#4F46E5', marginBottom: 4 },
  infoText: { fontSize: 12, color: '#5C6BC0', lineHeight: 20 },

  // ── Preview ──
  previewHeader: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 20,
    marginBottom: 12,
    alignItems: 'center',
    borderBottomWidth: 3,
    borderBottomColor: '#10B981',
  },
  previewSchool: { fontSize: 15, fontWeight: 'bold', color: '#374151', marginBottom: 4, letterSpacing: 1 },
  previewTitle: { fontSize: 22, fontWeight: 'bold', color: '#1F2937', marginBottom: 12 },
  previewMeta: { width: '100%' },
  previewMetaText: { fontSize: 13, color: '#4B5563', marginBottom: 3 },

  section: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
  },
  sectionTitle: { fontSize: 15, fontWeight: 'bold', color: '#1E40AF', marginBottom: 10, letterSpacing: 0.5 },
  bodyText: { fontSize: 14, color: '#374151', lineHeight: 22, marginBottom: 8, textAlign: 'justify' as any },

  conceptBlock: { marginBottom: 14 },
  conceptTitle: { fontSize: 14, fontWeight: 'bold', color: '#1A1A3A', marginBottom: 6 },
  subHeading: { fontSize: 13, fontWeight: '600', color: '#4B5563', marginTop: 6, marginBottom: 4 },

  termRow: { flexDirection: 'row', flexWrap: 'wrap', marginBottom: 6 },
  termLabel: { fontSize: 13, fontWeight: 'bold', color: '#1A1A3A' },
  termMeaning: { fontSize: 13, color: '#374151', flex: 1 },

  questionText: { fontSize: 13, color: '#374151', lineHeight: 20, marginBottom: 6 },

  // ── Action Buttons ──
  actionRow: { flexDirection: 'row', gap: 12, marginTop: 4 },
  downloadBtn: {
    flex: 1,
    backgroundColor: '#5C6BC0',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 14,
    borderRadius: 12,
  },
  downloadBtnText: { color: '#FFF', fontSize: 15, fontWeight: '600', marginLeft: 8 },
  newBtn: {
    flex: 1,
    backgroundColor: '#F3F4FF',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 14,
    borderRadius: 12,
  },
  newBtnText: { color: '#5C6BC0', fontSize: 15, fontWeight: '600', marginLeft: 8 },

  // ── Modal ──
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 24,
  },
  modalCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    padding: 28,
    width: '100%',
    maxWidth: 400,
  },
  modalTitle: { fontSize: 20, fontWeight: 'bold', color: '#1A1A3A', textAlign: 'center', marginTop: 12, marginBottom: 8 },
  modalBody: { fontSize: 14, color: '#4B5563', textAlign: 'center', lineHeight: 22, marginBottom: 20 },
  modalTopUpBtn: {
    backgroundColor: '#F59E0B',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 14,
    borderRadius: 12,
    marginBottom: 10,
  },
  modalTopUpText: { color: '#FFF', fontSize: 15, fontWeight: '600', marginLeft: 8 },
  modalCancelBtn: {
    paddingVertical: 12,
    alignItems: 'center',
  },
  modalCancelText: { color: '#5A5A7A', fontSize: 14, fontWeight: '500' },
});
