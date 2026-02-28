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
import { LessonPlanDisplay } from '../../components/LessonPlanDisplay';
import { filterSubjectsByGrade, getGradeBand, getGradeBandDisplayName } from '../../utils/kicdSubjectMapping';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

const DURATIONS = [25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80];

export default function Home() {
  const { firebaseUser, user, refreshProfile } = useAuth();
  
  const [grades, setGrades] = useState<any[]>([]);
  const [allSubjects, setAllSubjects] = useState<any[]>([]); // All subjects from DB
  const [subjects, setSubjects] = useState<any[]>([]); // Filtered subjects for display
  const [strands, setStrands] = useState<any[]>([]);
  const [substrands, setSubstrands] = useState<any[]>([]);
  const [slos, setSlos] = useState<any[]>([]);
  
  const [selectedDuration, setSelectedDuration] = useState<number>(40);
  const [selectedGrade, setSelectedGrade] = useState<string>('');
  const [selectedGradeName, setSelectedGradeName] = useState<string>(''); // Track grade name for filtering
  const [selectedSubject, setSelectedSubject] = useState<string>('');
  const [selectedStrand, setSelectedStrand] = useState<string>('');
  const [selectedSubstrand, setSelectedSubstrand] = useState<string>('');
  const [selectedSLO, setSelectedSLO] = useState<string>('');
  
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [lessonPlan, setLessonPlan] = useState<any>(null);
  const [showPlan, setShowPlan] = useState(false);

  useEffect(() => {
    loadGrades();
  }, []);

  // Effect to load substrands when selectedStrand changes
  useEffect(() => {
    console.log('[DEBUG] selectedStrand changed to:', selectedStrand);
    if (selectedStrand) {
      console.log('[DEBUG] Triggering loadSubstrands from useEffect');
      loadSubstrands(selectedStrand);
    } else {
      setSubstrands([]);
      setSlos([]);
    }
  }, [selectedStrand]);

  // Effect to load SLOs when selectedSubstrand changes
  useEffect(() => {
    console.log('[DEBUG] selectedSubstrand changed to:', selectedSubstrand);
    if (selectedSubstrand) {
      console.log('[DEBUG] Triggering loadSLOs from useEffect');
      loadSLOs(selectedSubstrand);
    } else {
      setSlos([]);
    }
  }, [selectedSubstrand]);

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
    } catch (error: any) {
      console.error('Error loading grades:', error);
      Alert.alert('Error', 'Failed to load grades');
    }
  };

  const loadSubjects = async (gradeId: string, gradeName: string) => {
    try {
      setLoading(true);
      const headers = await getHeaders();
      const response = await axios.get(`${BACKEND_URL}/api/subjects?gradeId=${gradeId}`, { headers });
      if (response.data.success) {
        const allSubjectsFromDb = response.data.subjects;
        setAllSubjects(allSubjectsFromDb);
        
        // Filter subjects based on KICD grade band mapping
        const filteredSubjects = filterSubjectsByGrade(allSubjectsFromDb, gradeName);
        setSubjects(filteredSubjects);
        
        // Log for debugging
        const band = getGradeBand(gradeName);
        if (band) {
          console.log(`[KICD] ${gradeName} (${getGradeBandDisplayName(band)}): Showing ${filteredSubjects.length} of ${allSubjectsFromDb.length} subjects`);
        }
        
        setStrands([]);
        setSubstrands([]);
        setSlos([]);
      }
    } catch (error) {
      console.error('Error loading subjects:', error);
      Alert.alert('Error', 'Failed to load subjects');
    } finally {
      setLoading(false);
    }
  };

  const loadStrands = async (subjectId: string) => {
    try {
      setLoading(true);
      const headers = await getHeaders();
      console.log('Loading strands for subject:', subjectId);
      const response = await axios.get(`${BACKEND_URL}/api/strands?subjectId=${subjectId}`, { headers });
      console.log('Strands response:', response.data);
      if (response.data.success) {
        console.log('Strands loaded:', response.data.strands.length);
        setStrands(response.data.strands);
        setSubstrands([]);
        setSlos([]);
        if (response.data.strands.length === 0) {
          Alert.alert('No Data', 'No strands found for this subject. Please ask admin to seed sample data.');
        }
      }
    } catch (error: any) {
      console.error('Error loading strands:', error.response?.data || error.message);
      Alert.alert('Error', 'Failed to load strands. Please ensure sample data is loaded.');
    } finally {
      setLoading(false);
    }
  };

  const loadSubstrands = async (strandId: string) => {
    console.log('[DEBUG] loadSubstrands called with strandId:', strandId);
    try {
      setLoading(true);
      const headers = await getHeaders();
      console.log('[DEBUG] Making substrand request to:', `${BACKEND_URL}/api/substrands?strandId=${strandId}`);
      const response = await axios.get(`${BACKEND_URL}/api/substrands?strandId=${strandId}`, { headers });
      console.log('[DEBUG] Substrand response:', response.data);
      if (response.data.success) {
        console.log('[DEBUG] Setting substrands:', response.data.substrands.length, 'items');
        setSubstrands(response.data.substrands);
        setSlos([]);
      }
    } catch (error) {
      console.error('[DEBUG] Error loading substrands:', error);
      Alert.alert('Error', 'Failed to load sub-strands');
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
      Alert.alert('Error', 'Failed to load learning outcomes');
    } finally {
      setLoading(false);
    }
  };

  const handleGradeChange = (gradeId: string) => {
    // Find the grade name for filtering
    const grade = grades.find(g => g.id === gradeId);
    const gradeName = grade?.name || '';
    
    setSelectedGrade(gradeId);
    setSelectedGradeName(gradeName);
    
    // Clear all downstream selections
    setSelectedSubject('');
    setSelectedStrand('');
    setSelectedSubstrand('');
    setSelectedSLO('');
    
    // Clear all downstream data
    setAllSubjects([]);
    setSubjects([]);
    setStrands([]);
    setSubstrands([]);
    setSlos([]);
    
    // Load subjects with grade name for KICD filtering
    if (gradeId && gradeName) {
      loadSubjects(gradeId, gradeName);
    }
  };

  const handleSubjectChange = (subjectId: string) => {
    setSelectedSubject(subjectId);
    setSelectedStrand('');
    setSelectedSubstrand('');
    setSelectedSLO('');
    setStrands([]);
    setSubstrands([]);
    setSlos([]);
    if (subjectId) loadStrands(subjectId);
  };

  const handleStrandChange = (strandId: string) => {
    console.log('[DEBUG] handleStrandChange called with strandId:', strandId);
    setSelectedStrand(strandId);
    setSelectedSubstrand('');
    setSelectedSLO('');
    // Note: loadSubstrands will be triggered by useEffect watching selectedStrand
  };

  const handleSubstrandChange = (substrandId: string) => {
    setSelectedSubstrand(substrandId);
    setSelectedSLO('');
    setSlos([]);
    if (substrandId) loadSLOs(substrandId);
  };

  const generateLessonPlan = async () => {
    if (!selectedGrade || !selectedSubject || !selectedStrand || !selectedSubstrand || !selectedSLO) {
      Alert.alert('Error', 'Please select all required fields');
      return;
    }

    setGenerating(true);
    try {
      const headers = await getHeaders();
      const response = await axios.post(
        `${BACKEND_URL}/api/lesson-plans/generate`,
        {
          duration: selectedDuration,
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
          <View style={styles.infoCard}>
            <Text style={styles.infoLabel}>Teacher: {user?.firstName} {user?.lastName}</Text>
            <Text style={styles.infoLabel}>School: {user?.schoolName}</Text>
          </View>
          <View style={styles.balanceCard}>
            <Ionicons name="wallet-outline" size={20} color="#6366F1" />
            <Text style={styles.balanceText}>
              {user?.freeLessonUsed ? `Balance: ${user?.walletBalance} KES` : '1 Free Lesson Available'}
            </Text>
          </View>
        </View>

        <View style={styles.form}>
          <View style={styles.pickerContainer}>
            <Text style={styles.label}>Duration (minutes) *</Text>
            <View style={styles.pickerWrapper}>
              <Picker
                selectedValue={selectedDuration}
                onValueChange={setSelectedDuration}
                style={styles.picker}
              >
                {DURATIONS.map((duration) => (
                  <Picker.Item key={duration} label={`${duration} minutes`} value={duration} />
                ))}
              </Picker>
            </View>
          </View>

          <View style={styles.pickerContainer}>
            <Text style={styles.label}>Grade *</Text>
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
              <View style={styles.labelRow}>
                <Text style={styles.label}>Learning Area / Subject *</Text>
                {selectedGradeName && getGradeBand(selectedGradeName) && (
                  <Text style={styles.gradeBandLabel}>
                    {getGradeBandDisplayName(getGradeBand(selectedGradeName)!)}
                  </Text>
                )}
              </View>
              {subjects.length === 0 && !loading ? (
                <View style={styles.noSubjectsMessage}>
                  <Ionicons name="information-circle-outline" size={16} color="#F59E0B" />
                  <Text style={styles.noSubjectsText}>
                    No subjects available for this grade. Please contact admin to add curriculum data.
                  </Text>
                </View>
              ) : (
                <View style={styles.pickerWrapper}>
                  <Picker
                    selectedValue={selectedSubject}
                    onValueChange={handleSubjectChange}
                    style={styles.picker}
                  >
                    <Picker.Item label={`Select Subject (${subjects.length} available)`} value="" />
                    {subjects.map((subject) => (
                      <Picker.Item key={subject.id} label={subject.name} value={subject.id} />
                    ))}
                  </Picker>
                </View>
              )}
            </View>
          )}

          {selectedSubject && (
            <View style={styles.pickerContainer}>
              <Text style={styles.label}>Strand *</Text>
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
              <Text style={styles.label}>Sub-Strand *</Text>
              {loading ? (
                <View style={styles.loadingContainer}>
                  <ActivityIndicator size="small" color="#6366F1" />
                  <Text style={styles.loadingText}>Loading sub-strands...</Text>
                </View>
              ) : substrands.length === 0 ? (
                <View style={styles.emptyContainer}>
                  <Text style={styles.emptyText}>No sub-strands found for this strand</Text>
                </View>
              ) : (
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
              )}
            </View>
          )}

          {selectedSubstrand && (
            <View style={styles.pickerContainer}>
              <Text style={styles.label}>Specific Learning Outcome (SLO) *</Text>
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
                  <Text style={styles.sectionTitle}>Lesson Information</Text>
                  <Text style={styles.sectionText}>Teacher: {lessonPlan.teacherName}</Text>
                  <Text style={styles.sectionText}>School: {lessonPlan.schoolName}</Text>
                  <Text style={styles.sectionText}>Duration: {lessonPlan.duration} minutes</Text>
                  <Text style={styles.sectionText}>Grade: {lessonPlan.gradeName}</Text>
                  <Text style={styles.sectionText}>Subject: {lessonPlan.subjectName}</Text>
                </View>

                <View style={styles.section}>
                  <Text style={styles.sectionTitle}>Topic</Text>
                  <Text style={styles.sectionText}>{lessonPlan.strandName} / {lessonPlan.substrandName}</Text>
                </View>

                <View style={styles.section}>
                  <Text style={styles.sectionTitle}>Specific Learning Outcome</Text>
                  <Text style={styles.sectionText}>{lessonPlan.sloName}</Text>
                  <Text style={styles.sectionDescription}>{lessonPlan.sloDescription}</Text>
                </View>

                <View style={styles.section}>
                  <Text style={styles.sectionTitle}>SLOs by Domain</Text>
                  <Text style={styles.domainTitle}>Knowledge:</Text>
                  {lessonPlan.knowledge?.map((k: string, i: number) => (
                    <Text key={i} style={styles.listText}>• {k}</Text>
                  ))}
                  <Text style={styles.domainTitle}>Skills:</Text>
                  {lessonPlan.skills?.map((s: string, i: number) => (
                    <Text key={i} style={styles.listText}>• {s}</Text>
                  ))}
                  <Text style={styles.domainTitle}>Attitudes:</Text>
                  {lessonPlan.attitudes?.map((a: string, i: number) => (
                    <Text key={i} style={styles.listText}>• {a}</Text>
                  ))}
                </View>

                <View style={styles.section}>
                  <Text style={styles.sectionTitle}>Learning Resources</Text>
                  {lessonPlan.learningResources?.map((resource: string, i: number) => (
                    <Text key={i} style={styles.listText}>• {resource}</Text>
                  ))}
                </View>

                <View style={styles.section}>
                  <Text style={styles.sectionTitle}>Core Competencies</Text>
                  {lessonPlan.competencies?.map((comp: any, i: number) => (
                    <View key={i} style={styles.itemCard}>
                      <Text style={styles.itemName}>{comp.name}</Text>
                      <Text style={styles.itemDescription}>{comp.description}</Text>
                    </View>
                  ))}
                </View>

                <View style={styles.section}>
                  <Text style={styles.sectionTitle}>Core Values</Text>
                  {lessonPlan.values?.map((value: any, i: number) => (
                    <View key={i} style={styles.itemCard}>
                      <Text style={styles.itemName}>{value.name}</Text>
                      <Text style={styles.itemDescription}>{value.description}</Text>
                    </View>
                  ))}
                </View>

                <View style={styles.section}>
                  <Text style={styles.sectionTitle}>Pertinent and Contemporary Issues (PCIs)</Text>
                  {lessonPlan.pcis?.map((pci: any, i: number) => (
                    <View key={i} style={styles.itemCard}>
                      <Text style={styles.itemName}>{pci.name}</Text>
                      <Text style={styles.itemDescription}>{pci.description}</Text>
                    </View>
                  ))}
                </View>

                <View style={styles.section}>
                  <Text style={styles.sectionTitle}>Lesson Body</Text>
                  <View style={styles.lessonStep}>
                    <Text style={styles.stepTitle}>1. Introduction</Text>
                    <Text style={styles.stepText}>{lessonPlan.introduction}</Text>
                  </View>
                  <View style={styles.lessonStep}>
                    <Text style={styles.stepTitle}>2. Lesson Development</Text>
                    <Text style={styles.stepText}>{lessonPlan.lessonDevelopment}</Text>
                  </View>
                  {lessonPlan.extendedActivity && (
                    <View style={styles.lessonStep}>
                      <Text style={styles.stepTitle}>3. Extended Activity</Text>
                      <Text style={styles.stepText}>{lessonPlan.extendedActivity}</Text>
                    </View>
                  )}
                  <View style={styles.lessonStep}>
                    <Text style={styles.stepTitle}>{lessonPlan.extendedActivity ? '4' : '3'}. Conclusion</Text>
                    <Text style={styles.stepText}>{lessonPlan.conclusion}</Text>
                  </View>
                </View>

                <View style={styles.section}>
                  <Text style={styles.sectionTitle}>Assessment</Text>
                  <Text style={styles.sectionText}>{lessonPlan.assessment}</Text>
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
  infoCard: {
    backgroundColor: '#F3F4F6',
    padding: 12,
    borderRadius: 8,
    marginBottom: 12
  },
  infoLabel: {
    fontSize: 14,
    color: '#374151',
    marginBottom: 4
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
    marginBottom: 4
  },
  sectionDescription: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 4,
    fontStyle: 'italic'
  },
  domainTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#111827',
    marginTop: 8,
    marginBottom: 4
  },
  listText: {
    fontSize: 14,
    color: '#374151',
    marginBottom: 4,
    marginLeft: 8
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
  },
  lessonStep: {
    backgroundColor: '#FFFBEB',
    padding: 12,
    borderRadius: 8,
    marginBottom: 12,
    borderLeftWidth: 4,
    borderLeftColor: '#F59E0B'
  },
  stepTitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#92400E',
    marginBottom: 8
  },
  stepText: {
    fontSize: 14,
    color: '#78350F',
    lineHeight: 20
  },
  loadingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#F3F4F6',
    borderRadius: 8
  },
  loadingText: {
    marginLeft: 12,
    fontSize: 14,
    color: '#6B7280'
  },
  emptyContainer: {
    padding: 16,
    backgroundColor: '#FEF3C7',
    borderRadius: 8,
    alignItems: 'center'
  },
  emptyText: {
    fontSize: 14,
    color: '#92400E'
  }
});
