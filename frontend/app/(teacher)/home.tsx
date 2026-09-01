import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator
} from 'react-native';
import { Picker } from '@react-native-picker/picker';
import { useAuth } from '../../contexts/AuthContext';
import { useRouter } from 'expo-router';
import axios from 'axios';
import { Ionicons } from '@expo/vector-icons';
import { getErrorMessage, isPaymentError, isRateLimitError } from '../../utils/errorHandler';
import { WalletCreditsPopup } from '../../components/WalletCreditsPopup';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

const DURATIONS = [25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80];

export default function Home() {
  const { firebaseUser, user, refreshProfile, isNewUser, clearNewUserFlag } = useAuth();
  const router = useRouter();
  
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
  
  // Wallet popup state
  const [showWalletPopup, setShowWalletPopup] = useState(false);

  useEffect(() => {
    loadGrades();
  }, []);

  // Effect to load substrands when selectedStrand changes
  useEffect(() => {
    if (selectedStrand) {
      loadSubstrands(selectedStrand);
    } else {
      setSubstrands([]);
      setSlos([]);
    }
  }, [selectedStrand]);

  // Effect to load SLOs when selectedSubstrand changes
  useEffect(() => {
    if (selectedSubstrand) {
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
      const response = await axios.get(`${BACKEND_URL}/api/grades?context=creation`, { headers });
      if (response.data.success) {
        setGrades(response.data.grades);
      }
    } catch (error: any) {
      
      Alert.alert('Error', 'Failed to load grades');
    }
  };

  const loadSubjects = async (gradeId: string, gradeName: string) => {
    try {
      setLoading(true);
      const headers = await getHeaders();
      const response = await axios.get(`${BACKEND_URL}/api/subjects?gradeId=${gradeId}&context=creation`, { headers });
      if (response.data.success) {
        const subjectsFromDb = response.data.subjects;
        // Show all subjects from database - admin panel is the source of truth
        setAllSubjects(subjectsFromDb);
        setSubjects(subjectsFromDb);
        
        setStrands([]);
        setSubstrands([]);
        setSlos([]);
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to load subjects');
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
        if (response.data.strands.length === 0) {
          Alert.alert('No Data', 'No strands found for this subject. Please ask admin to seed sample data.');
        }
      }
    } catch (error: any) {
      Alert.alert('Error', 'Failed to load strands. Please ensure sample data is loaded.');
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

  // Check if user has sufficient credits
  const hasCredits = () => {
    const freeRemaining = user?.freeLessonsRemaining ?? 0;
    const walletBalance = user?.walletBalance ?? 0;
    const lessonCost = 2; // KES 2 per lesson
    
    return freeRemaining > 0 || walletBalance >= lessonCost;
  };

  // Handle navigation to wallet/profile page
  const navigateToWallet = () => {
    setShowWalletPopup(false);
    router.push('/(teacher)/profile');
  };

  const generateLessonPlan = async () => {
    if (!selectedGrade || !selectedSubject || !selectedStrand || !selectedSubstrand || !selectedSLO) {
      Alert.alert('Missing Fields', 'Please select all required fields before generating');
      return;
    }

    // FRONTEND CHECK: Show friendly popup if no credits
    if (!hasCredits()) {
      setShowWalletPopup(true);
      return; // Don't attempt generation
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
        { headers, timeout: 30000 } // 30 second timeout
      );

      if (response.data.success) {
        await refreshProfile();
        router.push('/(teacher)/lessons');
      }
    } catch (error: any) {
      const errorMessage = getErrorMessage(error);
      
      if (isPaymentError(error)) {
        // Show friendly popup instead of alert for payment errors
        await refreshProfile(); // Refresh to get latest balance
        setShowWalletPopup(true);
      } else if (isRateLimitError(error)) {
        Alert.alert('Please Wait', errorMessage);
      } else {
        Alert.alert('Generation Failed', errorMessage);
      }
    } finally {
      setGenerating(false);
    }
  };

  return (
    <View style={styles.container}>
      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scrollContent}>
        <View style={styles.header}>
          <Text style={styles.welcomeText}>
            {isNewUser ? 'Welcome' : 'Welcome back'}, {user?.firstName}!
          </Text>
          <Text style={styles.headerTitle}>Create Lesson Plan</Text>
          <View style={styles.infoCard}>
            <Text style={styles.infoLabel}>Teacher: {user?.firstName} {user?.lastName}</Text>
            <Text style={styles.infoLabel}>School: {user?.schoolName}</Text>
          </View>
          <View style={styles.balanceCard}>
            <Ionicons name="wallet-outline" size={20} color="#5C6BC0" />
            <Text style={styles.balanceText}>
              {(user?.freeLessonsRemaining ?? 0) > 0 
                ? `${user?.freeLessonsRemaining} Free Lesson${(user?.freeLessonsRemaining ?? 0) !== 1 ? 's' : ''} Available`
                : `Balance: KES ${user?.walletBalance ?? 0}`
              }
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
                  <ActivityIndicator size="small" color="#5C6BC0" />
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
              {slos.length === 0 ? (
                <Text style={styles.noDataText}>No SLOs available for this sub-strand</Text>
              ) : (
                <View style={styles.pickerWrapper}>
                  <Picker
                    selectedValue={selectedSLO}
                    onValueChange={(value: string) => setSelectedSLO(value)}
                    style={styles.picker}
                  >
                    <Picker.Item label={`Select SLO (${slos.length} available)`} value="" />
                    {slos.map((slo) => (
                      <Picker.Item key={slo.id} label={slo.name} value={slo.id} />
                    ))}
                  </Picker>
                </View>
              )}
              {selectedSLO && slos.find((s: any) => s.id === selectedSLO)?.description && (
                <View style={styles.sloPreview}>
                  <Text style={styles.sloPreviewLabel}>Description:</Text>
                  <Text style={styles.sloPreviewText}>
                    {slos.find((s: any) => s.id === selectedSLO)?.description}
                  </Text>
                </View>
              )}
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

      {/* Wallet Credits Popup */}
      <WalletCreditsPopup
        visible={showWalletPopup}
        currentBalance={user?.walletBalance ?? 0}
        freeLessonsRemaining={user?.freeLessonsRemaining ?? 0}
        onAddCredits={navigateToWallet}
        onClose={() => setShowWalletPopup(false)}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: 'transparent'
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
  welcomeText: {
    fontSize: 16,
    color: '#5C6BC0',
    fontWeight: '600',
    marginBottom: 4
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1A1A3A',
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
    backgroundColor: '#F3F4FF',
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
    color: '#374151'
  },
  pickerWrapper: {
    backgroundColor: '#FFFFFF',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#DDDDF5',
    overflow: 'hidden'
  },
  picker: {
    height: 50
  },
  generateButton: {
    flexDirection: 'row',
    backgroundColor: '#5C6BC0',
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
    borderBottomColor: '#DDDDF5'
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1A1A3A'
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
    color: '#5C6BC0',
    marginBottom: 8
  },
  sectionText: {
    fontSize: 14,
    color: '#374151',
    marginBottom: 4
  },
  sectionDescription: {
    fontSize: 14,
    color: '#5A5A7A',
    marginTop: 4,
    fontStyle: 'italic'
  },
  domainTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1A1A3A',
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
    color: '#1A1A3A',
    marginBottom: 4
  },
  itemDescription: {
    fontSize: 13,
    color: '#5A5A7A'
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
    color: '#5A5A7A'
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
  },
  labelRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8
  },
  gradeBandLabel: {
    fontSize: 11,
    color: '#5C6BC0',
    backgroundColor: '#F3F4FF',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 10,
    fontWeight: '500'
  },
  noSubjectsMessage: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FEF3C7',
    padding: 12,
    borderRadius: 8,
    gap: 8
  },
  noSubjectsText: {
    flex: 1,
    fontSize: 13,
    color: '#92400E'
  },
  // SLO Preview Styles
  sloPreview: {
    marginTop: 8,
    backgroundColor: '#F0F4FF',
    borderRadius: 8,
    padding: 12,
    borderLeftWidth: 3,
    borderLeftColor: '#5C6BC0'
  },
  sloPreviewLabel: {
    fontSize: 12,
    fontWeight: '600',
    color: '#5C6BC0',
    marginBottom: 4
  },
  sloPreviewText: {
    fontSize: 13,
    color: '#374151',
    lineHeight: 20
  },
  noDataText: {
    fontSize: 14,
    color: '#9CA3AF',
    textAlign: 'center',
    padding: 16
  }
});
