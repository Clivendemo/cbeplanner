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

interface SLO {
  id: string;
  name: string;
  description: string;
}

interface LessonPlan {
  gradeName: string;
  subjectName: string;
  strandName: string;
  substrandName: string;
  sloName: string;
  sloDescription: string;
  activities: string[];
  competencies: Array<{ name: string; description: string }>;
  values: Array<{ name: string; description: string }>;
  pcis: Array<{ name: string; description: string }>;
  assessments: Array<{ name: string; description: string }>;
}

export default function Home() {
  const { firebaseUser, user, refreshProfile } = useAuth();
  
  const [grades, setGrades] = useState<Grade[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [strands, setStrands] = useState<Strand[]>([]);
  const [substrands, setSubstrands] = useState<SubStrand[]>([]);
  const [slos, setSlos] = useState<SLO[]>([]);
  
  const [selectedGrade, setSelectedGrade] = useState<string>('');
  const [selectedSubject, setSelectedSubject] = useState<string>('');
  const [selectedStrand, setSelectedStrand] = useState<string>('');
  const [selectedSubstrand, setSelectedSubstrand] = useState<string>('');
  const [selectedSLO, setSelectedSLO] = useState<string>('');
  
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [lessonPlan, setLessonPlan] = useState<LessonPlan | null>(null);
  const [showPlan, setShowPlan] = useState(false);

  useEffect(() => {
    loadGrades();
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
        setSlos([]);
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
        setSlos([]);
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
        setSlos([]);
      }
    } catch (error) {
      console.error('Error loading substrands:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadSLOs = async (substrandId: string) => {
    try {
      setLoading(true);
      const headers = await getHeaders();
      const response = await axios.get(`${BACKEND_URL}/api/slos?substrandId=${substrandId}`, { headers });
      if (response.data.success) {
        setSlos(response.data.slos);
      }
    } catch (error) {
      console.error('Error loading SLOs:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGradeChange = (gradeId: string) => {
    setSelectedGrade(gradeId);
    setSelectedSubject('');
    setSelectedStrand('');
    setSelectedSubstrand('');
    setSelectedSLO('');
    if (gradeId) loadSubjects(gradeId);
  };

  const handleSubjectChange = (subjectId: string) => {
    setSelectedSubject(subjectId);
    setSelectedStrand('');
    setSelectedSubstrand('');
    setSelectedSLO('');
    if (subjectId) loadStrands(subjectId);
  };

  const handleStrandChange = (strandId: string) => {
    setSelectedStrand(strandId);
    setSelectedSubstrand('');
    setSelectedSLO('');
    if (strandId) loadSubstrands(strandId);
  };

  const handleSubstrandChange = (substrandId: string) => {
    setSelectedSubstrand(substrandId);
    setSelectedSLO('');
    if (substrandId) loadSLOs(substrandId);
  };

  const generateLessonPlan = async () => {
    if (!selectedGrade || !selectedSubject || !selectedStrand || !selectedSubstrand || !selectedSLO) {
      Alert.alert('Error', 'Please select all options');
      return;
    }

    setGenerating(true);
    try {
      const headers = await getHeaders();
      const response = await axios.post(
        `${BACKEND_URL}/api/lesson-plans/generate`,
        {
          gradeId: selectedGrade,
          subjectId: selectedSubject,
          strandId: selectedStrand,
          substrandId: selectedSubstrand,
          sloId: selectedSLO
        },
        { headers }
      );

      if (response.data.success) {
        setLessonPlan(response.data.lessonPlan);
        setShowPlan(true);
        await refreshProfile();
        Alert.alert('Success', 'Lesson plan generated successfully!');
      }
    } catch (error: any) {
      if (error.response?.status === 402) {
        Alert.alert('Insufficient Balance', 'Please top up your wallet to generate more lesson plans');
      } else {
        Alert.alert('Error', error.response?.data?.detail || 'Failed to generate lesson plan');
      }
    } finally {
      setGenerating(false);
    }
  };

  return (
    <View style={styles.container}>
      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scrollContent}>
        <View style={styles.header}>
          <Text style={styles.headerTitle}>Create Lesson Plan</Text>
          <View style={styles.balanceCard}>
            <Ionicons name="wallet-outline" size={20} color="#6366F1" />
            <Text style={styles.balanceText}>
              {user?.freeLessonUsed ? `Balance: ${user?.walletBalance} KES` : '1 Free Lesson Available'}
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
                  onValueChange={handleSubstrandChange}
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
            <View style={styles.pickerContainer}>
              <Text style={styles.label}>Specific Learning Outcome (SLO)</Text>
              <View style={styles.pickerWrapper}>
                <Picker
                  selectedValue={selectedSLO}
                  onValueChange={setSelectedSLO}
                  style={styles.picker}
                >
                  <Picker.Item label="Select SLO" value="" />
                  {slos.map((slo) => (
                    <Picker.Item key={slo.id} label={slo.name} value={slo.id} />
                  ))}
                </Picker>
              </View>
            </View>
          )}

          {selectedSLO && (
            <TouchableOpacity
              style={[styles.generateButton, generating && styles.buttonDisabled]}
              onPress={generateLessonPlan}
              disabled={generating}
            >
              {generating ? (
                <ActivityIndicator color="#FFFFFF" />
              ) : (
                <>
                  <Ionicons name="create-outline" size={20} color="#FFFFFF" />
                  <Text style={styles.generateButtonText}>Generate Lesson Plan</Text>
                </>
              )}
            </TouchableOpacity>
          )}
        </View>
      </ScrollView>

      {/* Lesson Plan Modal */}
      <Modal
        visible={showPlan}
        animationType="slide"
        onRequestClose={() => setShowPlan(false)}
      >
        <View style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>Lesson Plan</Text>
            <TouchableOpacity onPress={() => setShowPlan(false)}>
              <Ionicons name="close" size={24} color="#6B7280" />
            </TouchableOpacity>
          </View>
          
          <ScrollView style={styles.modalContent}>
            {lessonPlan && (
              <>
                <View style={styles.section}>
                  <Text style={styles.sectionTitle}>Grade & Subject</Text>
                  <Text style={styles.sectionText}>{lessonPlan.gradeName} - {lessonPlan.subjectName}</Text>
                </View>

                <View style={styles.section}>
                  <Text style={styles.sectionTitle}>Strand</Text>
                  <Text style={styles.sectionText}>{lessonPlan.strandName}</Text>
                </View>

                <View style={styles.section}>
                  <Text style={styles.sectionTitle}>Sub-Strand</Text>
                  <Text style={styles.sectionText}>{lessonPlan.substrandName}</Text>
                </View>

                <View style={styles.section}>
                  <Text style={styles.sectionTitle}>Specific Learning Outcome</Text>
                  <Text style={styles.sectionText}>{lessonPlan.sloName}</Text>
                  <Text style={styles.sectionDescription}>{lessonPlan.sloDescription}</Text>
                </View>

                <View style={styles.section}>
                  <Text style={styles.sectionTitle}>Learning Activities</Text>
                  {lessonPlan.activities.map((activity, index) => (
                    <View key={index} style={styles.listItem}>
                      <Text style={styles.bullet}>•</Text>
                      <Text style={styles.listText}>{activity}</Text>
                    </View>
                  ))}
                </View>

                <View style={styles.section}>
                  <Text style={styles.sectionTitle}>Core Competencies</Text>
                  {lessonPlan.competencies.map((comp, index) => (
                    <View key={index} style={styles.itemCard}>
                      <Text style={styles.itemName}>{comp.name}</Text>
                      <Text style={styles.itemDescription}>{comp.description}</Text>
                    </View>
                  ))}
                </View>

                <View style={styles.section}>
                  <Text style={styles.sectionTitle}>Core Values</Text>
                  {lessonPlan.values.map((value, index) => (
                    <View key={index} style={styles.itemCard}>
                      <Text style={styles.itemName}>{value.name}</Text>
                      <Text style={styles.itemDescription}>{value.description}</Text>
                    </View>
                  ))}
                </View>

                <View style={styles.section}>
                  <Text style={styles.sectionTitle}>Pertinent & Contemporary Issues</Text>
                  {lessonPlan.pcis.map((pci, index) => (
                    <View key={index} style={styles.itemCard}>
                      <Text style={styles.itemName}>{pci.name}</Text>
                      <Text style={styles.itemDescription}>{pci.description}</Text>
                    </View>
                  ))}
                </View>

                <View style={styles.section}>
                  <Text style={styles.sectionTitle}>Assessment Methods</Text>
                  {lessonPlan.assessments.map((assessment, index) => (
                    <View key={index} style={styles.itemCard}>
                      <Text style={styles.itemName}>{assessment.name}</Text>
                      <Text style={styles.itemDescription}>{assessment.description}</Text>
                    </View>
                  ))}
                </View>
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
    backgroundColor: '#EEF2FF',
    padding: 12,
    borderRadius: 8
  },
  balanceText: {
    marginLeft: 8,
    fontSize: 14,
    color: '#4338CA',
    fontWeight: '500'
  },
  form: {
    gap: 16
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
    backgroundColor: '#6366F1',
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
    color: '#6366F1',
    marginBottom: 8
  },
  sectionText: {
    fontSize: 14,
    color: '#374151',
    fontWeight: '500'
  },
  sectionDescription: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 4
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
  },
  itemCard: {
    backgroundColor: '#F3F4F6',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8
  },
  itemName: {
    fontSize: 14,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 4
  },
  itemDescription: {
    fontSize: 13,
    color: '#6B7280'
  }
});