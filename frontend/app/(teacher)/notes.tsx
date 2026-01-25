import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
  Modal
} from 'react-native';
import { Picker } from '@react-native-picker/picker';
import { useAuth } from '../../contexts/AuthContext';
import axios from 'axios';
import { Ionicons } from '@expo/vector-icons';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

interface Grade {
  id: string;
  name: string;
}

interface Subject {
  id: string;
  name: string;
}

interface Strand {
  id: string;
  name: string;
}

interface SubStrand {
  id: string;
  name: string;
}

interface Notes {
  gradeName: string;
  subjectName: string;
  strandName: string;
  substrandName: string;
  content: string;
  activities: string[];
  createdAt: string;
}

export default function NotesGeneration() {
  const { firebaseUser, user, refreshProfile } = useAuth();
  
  const [grades, setGrades] = useState<Grade[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [strands, setStrands] = useState<Strand[]>([]);
  const [substrands, setSubstrands] = useState<SubStrand[]>([]);
  const [myNotes, setMyNotes] = useState<Notes[]>([]);
  
  const [selectedGrade, setSelectedGrade] = useState<string>('');
  const [selectedSubject, setSelectedSubject] = useState<string>('');
  const [selectedStrand, setSelectedStrand] = useState<string>('');
  const [selectedSubstrand, setSelectedSubstrand] = useState<string>('');
  
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [generatedNotes, setGeneratedNotes] = useState<Notes | null>(null);
  const [showNotes, setShowNotes] = useState(false);

  useEffect(() => {
    loadGrades();
    loadMyNotes();
  }, []);

  const getHeaders = async () => {
    if (firebaseUser) {
      const token = await firebaseUser.getIdToken();
      return { Authorization: `Bearer ${token}` };
    }
    return {};
  };

  const loadGrades = async () => {
    try {
      const headers = await getHeaders();
      const response = await axios.get(`${BACKEND_URL}/api/grades`, { headers });
      if (response.data.success) {
        setGrades(response.data.grades);
      }
    } catch (error) {
      console.error('Error loading grades:', error);
    }
  };

  const loadSubjects = async (gradeId: string) => {
    try {
      setLoading(true);
      const headers = await getHeaders();
      const response = await axios.get(`${BACKEND_URL}/api/subjects?gradeId=${gradeId}`, { headers });
      if (response.data.success) {
        setSubjects(response.data.subjects);
        setStrands([]);
        setSubstrands([]);
      }
    } catch (error) {
      console.error('Error loading subjects:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadStrands = async (subjectId: string) => {
    try {
      setLoading(true);
      const headers = await getHeaders();
      const response = await axios.get(`${BACKEND_URL}/api/strands?subjectId=${subjectId}`, { headers });
      if (response.data.success) {
        setStrands(response.data.strands);
        setSubstrands([]);
      }
    } catch (error) {
      console.error('Error loading strands:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadSubstrands = async (strandId: string) => {
    try {
      setLoading(true);
      const headers = await getHeaders();
      const response = await axios.get(`${BACKEND_URL}/api/substrands?strandId=${strandId}`, { headers });
      if (response.data.success) {
        setSubstrands(response.data.substrands);
      }
    } catch (error) {
      console.error('Error loading substrands:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadMyNotes = async () => {
    try {
      const headers = await getHeaders();
      const response = await axios.get(`${BACKEND_URL}/api/notes`, { headers });
      if (response.data.success) {
        setMyNotes(response.data.notes);
      }
    } catch (error) {
      console.error('Error loading notes:', error);
    }
  };

  const handleGradeChange = (gradeId: string) => {
    setSelectedGrade(gradeId);
    setSelectedSubject('');
    setSelectedStrand('');
    setSelectedSubstrand('');
    if (gradeId) loadSubjects(gradeId);
  };

  const handleSubjectChange = (subjectId: string) => {
    setSelectedSubject(subjectId);
    setSelectedStrand('');
    setSelectedSubstrand('');
    if (subjectId) loadStrands(subjectId);
  };

  const handleStrandChange = (strandId: string) => {
    setSelectedStrand(strandId);
    setSelectedSubstrand('');
    if (strandId) loadSubstrands(strandId);
  };

  const generateNotes = async () => {
    if (!selectedGrade || !selectedSubject || !selectedStrand || !selectedSubstrand) {
      Alert.alert('Error', 'Please select all options');
      return;
    }

    setGenerating(true);
    try {
      const headers = await getHeaders();
      const response = await axios.post(
        `${BACKEND_URL}/api/notes/generate`,
        {
          gradeId: selectedGrade,
          subjectId: selectedSubject,
          strandId: selectedStrand,
          substrandId: selectedSubstrand
        },
        { headers }
      );

      if (response.data.success) {
        setGeneratedNotes(response.data.notes);
        setShowNotes(true);
        await refreshProfile();
        await loadMyNotes();
        Alert.alert('Success', 'Notes generated successfully!');
      }
    } catch (error: any) {
      if (error.response?.status === 402) {
        Alert.alert('Insufficient Balance', 'Please top up your wallet to generate more notes');
      } else {
        Alert.alert('Error', error.response?.data?.detail || 'Failed to generate notes');
      }
    } finally {
      setGenerating(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  };

  return (
    <View style={styles.container}>
      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scrollContent}>
        <View style={styles.header}>
          <Text style={styles.headerTitle}>Generate Short Notes</Text>
          <View style={styles.balanceCard}>
            <Ionicons name="wallet-outline" size={20} color="#3B82F6" />
            <Text style={styles.balanceText}>
              {user?.freeNotesUsed ? `Balance: ${user?.walletBalance} KES (5 KES per notes)` : '1 Free Notes Available'}
            </Text>
          </View>
        </View>

        <View style={styles.form}>
          <View style={styles.pickerContainer}>
            <Text style={styles.label}>Grade</Text>
            <View style={styles.pickerWrapper}>
              <Picker
                selectedValue={selectedGrade}
                onValueChange={handleGradeChange}
                style={styles.picker}
              >
                <Picker.Item label="Select Grade" value="" />
                {grades.map((grade) => (
                  <Picker.Item key={grade.id} label={grade.name} value={grade.id} />
                ))}
              </Picker>
            </View>
          </View>

          {selectedGrade && (
            <View style={styles.pickerContainer}>
              <Text style={styles.label}>Subject / Learning Area</Text>
              <View style={styles.pickerWrapper}>
                <Picker
                  selectedValue={selectedSubject}
                  onValueChange={handleSubjectChange}
                  style={styles.picker}
                >
                  <Picker.Item label="Select Subject" value="" />
                  {subjects.map((subject) => (
                    <Picker.Item key={subject.id} label={subject.name} value={subject.id} />
                  ))}
                </Picker>
              </View>
            </View>
          )}

          {selectedSubject && (
            <View style={styles.pickerContainer}>
              <Text style={styles.label}>Strand</Text>
              <View style={styles.pickerWrapper}>
                <Picker
                  selectedValue={selectedStrand}
                  onValueChange={handleStrandChange}
                  style={styles.picker}
                >
                  <Picker.Item label="Select Strand" value="" />
                  {strands.map((strand) => (
                    <Picker.Item key={strand.id} label={strand.name} value={strand.id} />
                  ))}
                </Picker>
              </View>
            </View>
          )}

          {selectedStrand && (
            <View style={styles.pickerContainer}>
              <Text style={styles.label}>Sub-Strand</Text>
              <View style={styles.pickerWrapper}>
                <Picker
                  selectedValue={selectedSubstrand}
                  onValueChange={setSelectedSubstrand}
                  style={styles.picker}
                >
                  <Picker.Item label="Select Sub-Strand" value="" />
                  {substrands.map((substrand) => (
                    <Picker.Item key={substrand.id} label={substrand.name} value={substrand.id} />
                  ))}
                </Picker>
              </View>
            </View>
          )}

          {selectedSubstrand && (
            <TouchableOpacity
              style={[styles.generateButton, generating && styles.buttonDisabled]}
              onPress={generateNotes}
              disabled={generating}
            >
              {generating ? (
                <ActivityIndicator color="#FFFFFF" />
              ) : (
                <>
                  <Ionicons name="create-outline" size={20} color="#FFFFFF" />
                  <Text style={styles.generateButtonText}>Generate Notes</Text>
                </>
              )}
            </TouchableOpacity>
          )}
        </View>

        {myNotes.length > 0 && (
          <View style={styles.notesSection}>
            <Text style={styles.notesSectionTitle}>My Generated Notes ({myNotes.length})</Text>
            {myNotes.map((note, index) => (
              <View key={index} style={styles.noteCard}>
                <Text style={styles.noteTitle}>{note.gradeName} - {note.subjectName}</Text>
                <Text style={styles.noteSubtitle}>{note.strandName} / {note.substrandName}</Text>
                <Text style={styles.noteDate}>{formatDate(note.createdAt)}</Text>
              </View>
            ))}
          </View>
        )}
      </ScrollView>

      <Modal
        visible={showNotes}
        animationType="slide"
        onRequestClose={() => setShowNotes(false)}
      >
        <View style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>Generated Notes</Text>
            <TouchableOpacity onPress={() => setShowNotes(false)}>
              <Ionicons name="close" size={24} color="#6B7280" />
            </TouchableOpacity>
          </View>
          
          <ScrollView style={styles.modalContent}>
            {generatedNotes && (
              <>
                <View style={styles.section}>
                  <Text style={styles.sectionTitle}>Subject & Topic</Text>
                  <Text style={styles.sectionText}>
                    {generatedNotes.gradeName} - {generatedNotes.subjectName}
                  </Text>
                  <Text style={styles.sectionText}>
                    {generatedNotes.strandName} / {generatedNotes.substrandName}
                  </Text>
                </View>

                <View style={styles.section}>
                  <Text style={styles.sectionTitle}>Notes Content</Text>
                  <Text style={styles.notesContent}>{generatedNotes.content}</Text>
                </View>

                {generatedNotes.activities.length > 0 && (
                  <View style={styles.section}>
                    <Text style={styles.sectionTitle}>Learning Activities</Text>
                    {generatedNotes.activities.map((activity, index) => (
                      <View key={index} style={styles.listItem}>
                        <Text style={styles.bullet}>•</Text>
                        <Text style={styles.listText}>{activity}</Text>
                      </View>
                    ))}
                  </View>
                )}
              </>
            )}
          </ScrollView>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB'
  },
  scrollView: {
    flex: 1
  },
  scrollContent: {
    padding: 16
  },
  header: {
    marginBottom: 24
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#111827',
    marginBottom: 12
  },
  balanceCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#DBEAFE',
    padding: 12,
    borderRadius: 8
  },
  balanceText: {
    marginLeft: 8,
    fontSize: 14,
    color: '#1E40AF',
    fontWeight: '500'
  },
  form: {
    gap: 16,
    marginBottom: 24
  },
  pickerContainer: {
    marginBottom: 8
  },
  label: {
    fontSize: 14,
    fontWeight: '500',
    color: '#374151',
    marginBottom: 8
  },
  pickerWrapper: {
    backgroundColor: '#FFFFFF',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    overflow: 'hidden'
  },
  picker: {
    height: 50
  },
  generateButton: {
    flexDirection: 'row',
    backgroundColor: '#3B82F6',
    borderRadius: 8,
    paddingVertical: 16,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    marginTop: 16
  },
  buttonDisabled: {
    opacity: 0.6
  },
  generateButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600'
  },
  notesSection: {
    marginTop: 24
  },
  notesSectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#111827',
    marginBottom: 12
  },
  noteCard: {
    backgroundColor: '#FFFFFF',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#E5E7EB'
  },
  noteTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 4
  },
  noteSubtitle: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 8
  },
  noteDate: {
    fontSize: 12,
    color: '#9CA3AF'
  },
  modalContainer: {
    flex: 1,
    backgroundColor: '#FFFFFF'
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB'
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#111827'
  },
  modalContent: {
    flex: 1,
    padding: 16
  },
  section: {
    marginBottom: 24
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#3B82F6',
    marginBottom: 8
  },
  sectionText: {
    fontSize: 14,
    color: '#374151',
    fontWeight: '500',
    marginBottom: 4
  },
  notesContent: {
    fontSize: 14,
    color: '#374151',
    lineHeight: 22
  },
  listItem: {
    flexDirection: 'row',
    marginBottom: 8
  },
  bullet: {
    fontSize: 14,
    color: '#6B7280',
    marginRight: 8
  },
  listText: {
    flex: 1,
    fontSize: 14,
    color: '#374151'
  }
});
