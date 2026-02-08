import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
  Share,
  Platform
} from 'react-native';
import { Picker } from '@react-native-picker/picker';
import { useAuth } from '../../contexts/AuthContext';
import { Ionicons } from '@expo/vector-icons';
import { SafeAreaView } from 'react-native-safe-area-context';
import axios from 'axios';
import * as Print from 'expo-print';
import * as Sharing from 'expo-sharing';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

interface Grade { id: string; name: string; }
interface Subject { id: string; name: string; }
interface Strand { id: string; name: string; }
interface SubStrand { id: string; name: string; }

export default function Notes() {
  const { user, firebaseUser } = useAuth();
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  
  // Form state
  const [duration, setDuration] = useState(40);
  const [grades, setGrades] = useState<Grade[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [strands, setStrands] = useState<Strand[]>([]);
  const [substrands, setSubstrands] = useState<SubStrand[]>([]);
  
  const [selectedGrade, setSelectedGrade] = useState('');
  const [selectedSubject, setSelectedSubject] = useState('');
  const [selectedStrand, setSelectedStrand] = useState('');
  const [selectedSubstrand, setSelectedSubstrand] = useState('');
  
  // Generated notes
  const [generatedNotes, setGeneratedNotes] = useState<any>(null);
  
  const getHeaders = async () => {
    if (firebaseUser) {
      const token = await firebaseUser.getIdToken();
      return { Authorization: `Bearer ${token}` };
    }
    return {};
  };

  // Load grades
  useEffect(() => {
    loadGrades();
  }, []);

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

  // Load subjects when grade changes
  useEffect(() => {
    if (selectedGrade) {
      loadSubjects();
    } else {
      setSubjects([]);
      setSelectedSubject('');
    }
  }, [selectedGrade]);

  const loadSubjects = async () => {
    try {
      const headers = await getHeaders();
      const response = await axios.get(`${BACKEND_URL}/api/subjects?gradeId=${selectedGrade}`, { headers });
      if (response.data.success) {
        setSubjects(response.data.subjects);
      }
    } catch (error) {
      console.error('Error loading subjects:', error);
    }
  };

  // Load strands when subject changes
  useEffect(() => {
    if (selectedSubject) {
      loadStrands();
    } else {
      setStrands([]);
      setSelectedStrand('');
    }
  }, [selectedSubject]);

  const loadStrands = async () => {
    try {
      const headers = await getHeaders();
      const response = await axios.get(`${BACKEND_URL}/api/strands?subjectId=${selectedSubject}`, { headers });
      if (response.data.success) {
        setStrands(response.data.strands);
      }
    } catch (error) {
      console.error('Error loading strands:', error);
    }
  };

  // Load substrands when strand changes
  useEffect(() => {
    if (selectedStrand) {
      loadSubstrands();
    } else {
      setSubstrands([]);
      setSelectedSubstrand('');
    }
  }, [selectedStrand]);

  const loadSubstrands = async () => {
    try {
      const headers = await getHeaders();
      const response = await axios.get(`${BACKEND_URL}/api/substrands?strandId=${selectedStrand}`, { headers });
      if (response.data.success) {
        setSubstrands(response.data.substrands);
      }
    } catch (error) {
      console.error('Error loading substrands:', error);
    }
  };

  const handleGenerate = async () => {
    if (!selectedGrade || !selectedSubject || !selectedStrand || !selectedSubstrand) {
      Alert.alert('Error', 'Please select all fields');
      return;
    }

    setGenerating(true);
    try {
      const headers = await getHeaders();
      const response = await axios.post(
        `${BACKEND_URL}/api/notes/generate`,
        {
          duration,
          gradeId: selectedGrade,
          subjectId: selectedSubject,
          strandId: selectedStrand,
          substrandId: selectedSubstrand
        },
        { headers }
      );

      if (response.data.success) {
        setGeneratedNotes(response.data.notes);
      }
    } catch (error: any) {
      if (error.response?.status === 402) {
        Alert.alert('Insufficient Balance', 'Please top up your wallet to generate notes');
      } else {
        Alert.alert('Error', error.response?.data?.detail || 'Failed to generate notes');
      }
    } finally {
      setGenerating(false);
    }
  };

  const generatePDF = async () => {
    if (!generatedNotes) return;

    const htmlContent = `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="utf-8">
        <title>Study Notes</title>
        <style>
          body { font-family: Arial, sans-serif; padding: 20px; line-height: 1.6; }
          .header { text-align: center; border-bottom: 2px solid #6366F1; padding-bottom: 20px; margin-bottom: 20px; }
          .header h1 { color: #6366F1; margin: 0; }
          .meta { display: flex; justify-content: space-between; margin-bottom: 20px; background: #F3F4F6; padding: 10px; border-radius: 8px; }
          .meta-item { text-align: center; }
          .meta-label { font-size: 12px; color: #6B7280; }
          .meta-value { font-weight: bold; color: #111827; }
          .content { margin-top: 20px; }
          .content h2 { color: #4F46E5; border-bottom: 1px solid #E5E7EB; padding-bottom: 8px; }
          .content ul { padding-left: 20px; }
          .content li { margin-bottom: 8px; }
          .footer { margin-top: 30px; text-align: center; font-size: 12px; color: #9CA3AF; border-top: 1px solid #E5E7EB; padding-top: 20px; }
        </style>
      </head>
      <body>
        <div class="header">
          <h1>STUDY NOTES</h1>
          <p>${generatedNotes.subjectName} - ${generatedNotes.gradeName}</p>
        </div>
        
        <div class="meta">
          <div class="meta-item">
            <div class="meta-label">School</div>
            <div class="meta-value">${generatedNotes.schoolName || 'N/A'}</div>
          </div>
          <div class="meta-item">
            <div class="meta-label">Teacher</div>
            <div class="meta-value">${generatedNotes.teacherName}</div>
          </div>
          <div class="meta-item">
            <div class="meta-label">Duration</div>
            <div class="meta-value">${generatedNotes.duration} min</div>
          </div>
        </div>
        
        <div class="content">
          <h2>Topic: ${generatedNotes.strandName}</h2>
          <h3>Sub-topic: ${generatedNotes.substrandName}</h3>
          
          ${generatedNotes.content.replace(/\n/g, '<br>').replace(/# /g, '<h2>').replace(/## /g, '<h3>').replace(/- /g, '• ')}
        </div>
        
        ${generatedNotes.activities && generatedNotes.activities.length > 0 ? `
        <div class="content">
          <h2>Learning Activities</h2>
          <ul>
            ${generatedNotes.activities.map((a: string) => `<li>${a}</li>`).join('')}
          </ul>
        </div>
        ` : ''}
        
        <div class="footer">
          <p>Generated by CBE Planner | KICD-Aligned Curriculum</p>
          <p>Date: ${new Date().toLocaleDateString()}</p>
        </div>
      </body>
      </html>
    `;

    try {
      const { uri } = await Print.printToFileAsync({ html: htmlContent });
      
      if (await Sharing.isAvailableAsync()) {
        await Sharing.shareAsync(uri);
      } else {
        Alert.alert('Success', `PDF saved to ${uri}`);
      }
    } catch (error) {
      console.error('Error generating PDF:', error);
      Alert.alert('Error', 'Failed to generate PDF');
    }
  };

  const durations = [25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80];

  return (
    <SafeAreaView style={styles.container} edges={['bottom']}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        {!generatedNotes ? (
          <>
            {/* Form */}
            <View style={styles.card}>
              <Text style={styles.cardTitle}>Generate Study Notes</Text>
              
              <View style={styles.inputGroup}>
                <Text style={styles.label}>Duration (minutes)</Text>
                <View style={styles.pickerContainer}>
                  <Picker
                    selectedValue={duration}
                    onValueChange={setDuration}
                    style={styles.picker}
                  >
                    {durations.map((d) => (
                      <Picker.Item key={d} label={`${d} minutes`} value={d} />
                    ))}
                  </Picker>
                </View>
              </View>

              <View style={styles.inputGroup}>
                <Text style={styles.label}>Grade</Text>
                <View style={styles.pickerContainer}>
                  <Picker
                    selectedValue={selectedGrade}
                    onValueChange={setSelectedGrade}
                    style={styles.picker}
                  >
                    <Picker.Item label="Select Grade" value="" />
                    {grades.map((g) => (
                      <Picker.Item key={g.id} label={g.name} value={g.id} />
                    ))}
                  </Picker>
                </View>
              </View>

              <View style={styles.inputGroup}>
                <Text style={styles.label}>Subject</Text>
                <View style={styles.pickerContainer}>
                  <Picker
                    selectedValue={selectedSubject}
                    onValueChange={setSelectedSubject}
                    style={styles.picker}
                    enabled={subjects.length > 0}
                  >
                    <Picker.Item label={subjects.length > 0 ? "Select Subject" : "Select Grade first"} value="" />
                    {subjects.map((s) => (
                      <Picker.Item key={s.id} label={s.name} value={s.id} />
                    ))}
                  </Picker>
                </View>
              </View>

              <View style={styles.inputGroup}>
                <Text style={styles.label}>Strand</Text>
                <View style={styles.pickerContainer}>
                  <Picker
                    selectedValue={selectedStrand}
                    onValueChange={setSelectedStrand}
                    style={styles.picker}
                    enabled={strands.length > 0}
                  >
                    <Picker.Item label={strands.length > 0 ? "Select Strand" : "Select Subject first"} value="" />
                    {strands.map((s) => (
                      <Picker.Item key={s.id} label={s.name} value={s.id} />
                    ))}
                  </Picker>
                </View>
              </View>

              <View style={styles.inputGroup}>
                <Text style={styles.label}>Sub-strand</Text>
                <View style={styles.pickerContainer}>
                  <Picker
                    selectedValue={selectedSubstrand}
                    onValueChange={setSelectedSubstrand}
                    style={styles.picker}
                    enabled={substrands.length > 0}
                  >
                    <Picker.Item label={substrands.length > 0 ? "Select Sub-strand" : "Select Strand first"} value="" />
                    {substrands.map((s) => (
                      <Picker.Item key={s.id} label={s.name} value={s.id} />
                    ))}
                  </Picker>
                </View>
              </View>

              <TouchableOpacity
                style={[styles.generateButton, generating && styles.buttonDisabled]}
                onPress={handleGenerate}
                disabled={generating}
              >
                {generating ? (
                  <ActivityIndicator color="#FFFFFF" />
                ) : (
                  <>
                    <Ionicons name="create" size={20} color="#FFFFFF" />
                    <Text style={styles.generateButtonText}>Generate Notes</Text>
                  </>
                )}
              </TouchableOpacity>
            </View>

            {/* Info Card */}
            <View style={styles.infoCard}>
              <Ionicons name="information-circle" size={24} color="#6366F1" />
              <View style={styles.infoContent}>
                <Text style={styles.infoTitle}>About Notes Generation</Text>
                <Text style={styles.infoText}>
                  Notes are generated based on duration:{'\n'}
                  • Short (25-40 min): Brief bullet points{'\n'}
                  • Medium (45-60 min): Moderate detail{'\n'}
                  • Long (65-80 min): Comprehensive coverage
                </Text>
              </View>
            </View>
          </>
        ) : (
          <>
            {/* Generated Notes Display */}
            <View style={styles.notesCard}>
              <View style={styles.notesHeader}>
                <Text style={styles.notesTitle}>{generatedNotes.substrandName}</Text>
                <Text style={styles.notesSubtitle}>{generatedNotes.strandName} • {generatedNotes.subjectName}</Text>
              </View>

              <View style={styles.notesMeta}>
                <View style={styles.metaItem}>
                  <Text style={styles.metaLabel}>Grade</Text>
                  <Text style={styles.metaValue}>{generatedNotes.gradeName}</Text>
                </View>
                <View style={styles.metaItem}>
                  <Text style={styles.metaLabel}>Duration</Text>
                  <Text style={styles.metaValue}>{generatedNotes.duration} min</Text>
                </View>
                <View style={styles.metaItem}>
                  <Text style={styles.metaLabel}>Teacher</Text>
                  <Text style={styles.metaValue}>{generatedNotes.teacherName}</Text>
                </View>
              </View>

              <View style={styles.notesContent}>
                <Text style={styles.notesText}>{generatedNotes.content}</Text>
              </View>

              {generatedNotes.activities && generatedNotes.activities.length > 0 && (
                <View style={styles.activitiesSection}>
                  <Text style={styles.sectionTitle}>Learning Activities</Text>
                  {generatedNotes.activities.map((activity: string, index: number) => (
                    <View key={index} style={styles.activityItem}>
                      <Ionicons name="checkmark-circle" size={16} color="#10B981" />
                      <Text style={styles.activityText}>{activity}</Text>
                    </View>
                  ))}
                </View>
              )}
            </View>

            {/* Action Buttons */}
            <View style={styles.actionButtons}>
              <TouchableOpacity style={styles.downloadButton} onPress={generatePDF}>
                <Ionicons name="download" size={20} color="#FFFFFF" />
                <Text style={styles.downloadButtonText}>Download PDF</Text>
              </TouchableOpacity>

              <TouchableOpacity 
                style={styles.newButton} 
                onPress={() => setGeneratedNotes(null)}
              >
                <Ionicons name="add" size={20} color="#6366F1" />
                <Text style={styles.newButtonText}>Generate New</Text>
              </TouchableOpacity>
            </View>
          </>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F3F4F6'
  },
  scrollContent: {
    padding: 16
  },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 20,
    marginBottom: 16
  },
  cardTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#111827',
    marginBottom: 20
  },
  inputGroup: {
    marginBottom: 16
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 8
  },
  pickerContainer: {
    backgroundColor: '#F9FAFB',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    overflow: 'hidden'
  },
  picker: {
    height: 50
  },
  generateButton: {
    backgroundColor: '#10B981',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
    borderRadius: 12,
    marginTop: 8
  },
  buttonDisabled: {
    opacity: 0.7
  },
  generateButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8
  },
  infoCard: {
    backgroundColor: '#EEF2FF',
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row'
  },
  infoContent: {
    marginLeft: 12,
    flex: 1
  },
  infoTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#4F46E5',
    marginBottom: 4
  },
  infoText: {
    fontSize: 12,
    color: '#6366F1',
    lineHeight: 18
  },
  notesCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    overflow: 'hidden',
    marginBottom: 16
  },
  notesHeader: {
    backgroundColor: '#10B981',
    padding: 20
  },
  notesTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#FFFFFF'
  },
  notesSubtitle: {
    fontSize: 14,
    color: '#D1FAE5',
    marginTop: 4
  },
  notesMeta: {
    flexDirection: 'row',
    backgroundColor: '#F0FDF4',
    padding: 12
  },
  metaItem: {
    flex: 1,
    alignItems: 'center'
  },
  metaLabel: {
    fontSize: 11,
    color: '#6B7280'
  },
  metaValue: {
    fontSize: 13,
    fontWeight: '600',
    color: '#111827',
    marginTop: 2
  },
  notesContent: {
    padding: 20
  },
  notesText: {
    fontSize: 15,
    color: '#374151',
    lineHeight: 24
  },
  activitiesSection: {
    padding: 20,
    paddingTop: 0
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 12
  },
  activityItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 8
  },
  activityText: {
    fontSize: 14,
    color: '#374151',
    marginLeft: 8,
    flex: 1
  },
  actionButtons: {
    flexDirection: 'row',
    gap: 12
  },
  downloadButton: {
    flex: 1,
    backgroundColor: '#6366F1',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
    borderRadius: 12
  },
  downloadButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8
  },
  newButton: {
    flex: 1,
    backgroundColor: '#EEF2FF',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
    borderRadius: 12
  },
  newButtonText: {
    color: '#6366F1',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8
  }
});
