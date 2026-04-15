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
  FlatList,
  Platform,
  TextInput,
  Dimensions
} from 'react-native';
import { Picker } from '@react-native-picker/picker';
import { useAuth } from '../../contexts/AuthContext';
import { Ionicons } from '@expo/vector-icons';
import axios from 'axios';
import * as FileSystem from 'expo-file-system';
import * as Sharing from 'expo-sharing';
import { useRouter } from 'expo-router';
import { useFocusEffect } from '@react-navigation/native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { WebView } from 'react-native-webview';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;
const SCHEME_DOWNLOAD_COST = 15;
const { width: SCREEN_WIDTH, height: SCREEN_HEIGHT } = Dimensions.get('window');

interface Grade { id: string; name: string; }
interface Subject { id: string; name: string; }
interface Substrand { id: string; name: string; sloCount: number; }
interface Topic { id: string; name: string; substrands: Substrand[]; totalSlos: number; }
interface Break {
  breakType: string;
  startWeek: number;
  startLesson: number;
  endWeek: number;
  endLesson: number;
  startDate?: string; // Optional calendar date in ISO format
}

interface DoubleLesson {
  enabled: boolean;
  position: string; // e.g., "2-3", "3-4", "4-5"
}

type Step = 'select' | 'topics' | 'breaks' | 'preview';

export default function SchemesOfWork() {
  const { user, firebaseUser, refreshProfile } = useAuth();
  const router = useRouter();
  
  // Step management
  const [currentStep, setCurrentStep] = useState<Step>('select');
  
  // Step 1: Basic selection
  const [grades, setGrades] = useState<Grade[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [selectedGrade, setSelectedGrade] = useState('');
  const [selectedSubject, setSelectedSubject] = useState('');
  const [term, setTerm] = useState(1);
  const [year, setYear] = useState(new Date().getFullYear());
  const [totalWeeks, setTotalWeeks] = useState(12);
  const [lessonsPerWeek, setLessonsPerWeek] = useState<number | null>(null);
  const [showLessonsOverride, setShowLessonsOverride] = useState(false);
  
  // Double lesson support
  const [doubleLesson, setDoubleLesson] = useState<DoubleLesson>({ enabled: false, position: '2-3' });
  
  // Carry-over/compression mode
  const [includeCarryOver, setIncludeCarryOver] = useState(false);
  
  // PDF preview modal
  const [showPdfModal, setShowPdfModal] = useState(false);
  const [pdfPreviewUrl, setPdfPreviewUrl] = useState<string | null>(null);
  
  // Step 2: Topic selection
  const [topics, setTopics] = useState<Topic[]>([]);
  const [selectedTopics, setSelectedTopics] = useState<Set<string>>(new Set());
  const [expandedStrands, setExpandedStrands] = useState<Set<string>>(new Set());
  const [loadingTopics, setLoadingTopics] = useState(false);
  
  // Step 3: Breaks
  const [breaks, setBreaks] = useState<Break[]>([
    { breakType: 'Mid-Term Break', startWeek: 5, startLesson: 1, endWeek: 5, endLesson: 5 },
    { breakType: 'End Term Exams', startWeek: 13, startLesson: 1, endWeek: 14, endLesson: 5 }
  ]);
  const [breakModalVisible, setBreakModalVisible] = useState(false);
  const [editingBreak, setEditingBreak] = useState<Break | null>(null);
  
  // Step 4: Preview & Download
  const [generatedScheme, setGeneratedScheme] = useState<any>(null);
  const [generating, setGenerating] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [previewing, setPreviewing] = useState(false);
  
  // Insufficient funds modal
  const [showFundsModal, setShowFundsModal] = useState(false);
  
  // Track if user was redirected to top-up
  const [pendingDownload, setPendingDownload] = useState(false);
  
  // Refresh profile when screen comes into focus (after top-up)
  useFocusEffect(
    useCallback(() => {
      refreshProfile();
      // Check if we have a pending download and now have sufficient balance
      if (pendingDownload && user && (user.walletBalance || 0) >= SCHEME_DOWNLOAD_COST) {
        setPendingDownload(false);
        // Show a message that they can now download
        Alert.alert(
          'Balance Updated! 🎉',
          'Your wallet has been topped up. You can now download your scheme.',
          [{ text: 'Great!' }]
        );
      }
    }, [pendingDownload, user?.walletBalance])
  );
  
  const getHeaders = async () => {
    if (firebaseUser) {
      const token = await firebaseUser.getIdToken();
      return { Authorization: `Bearer ${token}` };
    }
    return {};
  };

  // Load grades on mount
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
      
    }
  };

  // Load subjects when grade changes
  useEffect(() => {
    if (selectedGrade) {
      loadSubjects();
    } else {
      setSubjects([]);
      setSelectedSubject('');
      setLessonsPerWeek(null);
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
      
    }
  };

  // Auto-fetch lessons per week when subject changes
  useEffect(() => {
    if (selectedGrade && selectedSubject) {
      fetchLessonsPerWeek();
    }
  }, [selectedGrade, selectedSubject]);

  const fetchLessonsPerWeek = async () => {
    try {
      const headers = await getHeaders();
      const response = await axios.get(
        `${BACKEND_URL}/api/schemes/config/lessons-per-week?gradeId=${selectedGrade}&subjectId=${selectedSubject}`,
        { headers }
      );
      if (response.data.success) {
        setLessonsPerWeek(response.data.lessonsPerWeek);
      }
    } catch (error) {
      
      setLessonsPerWeek(5); // Default fallback
    }
  };

  // Load topics for step 2
  const loadTopics = async () => {
    setLoadingTopics(true);
    try {
      const headers = await getHeaders();
      const response = await axios.get(
        `${BACKEND_URL}/api/schemes/topics/${selectedSubject}`,
        { headers }
      );
      if (response.data.success) {
        setTopics(response.data.topics);
        // Expand first strand by default
        if (response.data.topics.length > 0) {
          setExpandedStrands(new Set([response.data.topics[0].id]));
        }
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to load topics');
    } finally {
      setLoadingTopics(false);
    }
  };

  // Navigation handlers
  const handleNext = () => {
    if (currentStep === 'select') {
      if (!selectedGrade || !selectedSubject) {
        Alert.alert('Required', 'Please select a grade and subject');
        return;
      }
      loadTopics();
      setCurrentStep('topics');
    } else if (currentStep === 'topics') {
      if (selectedTopics.size === 0) {
        Alert.alert('Required', 'Please select at least one topic');
        return;
      }
      setCurrentStep('breaks');
    } else if (currentStep === 'breaks') {
      generateScheme();
    }
  };

  const handleBack = () => {
    if (currentStep === 'topics') setCurrentStep('select');
    else if (currentStep === 'breaks') setCurrentStep('topics');
    else if (currentStep === 'preview') setCurrentStep('breaks');
  };

  // Calculate break duration display text
  const calculateBreakDuration = (brk: Break | null) => {
    if (!brk) return 'Select start and end points';
    
    const startWeek = brk.startWeek || 1;
    const startLesson = brk.startLesson || 1;
    const endWeek = brk.endWeek || startWeek;
    const endLesson = brk.endLesson || (lessonsPerWeek || 5);
    const lpw = lessonsPerWeek || 5;
    
    // Calculate total lessons
    const startPosition = (startWeek - 1) * lpw + startLesson;
    const endPosition = (endWeek - 1) * lpw + endLesson;
    const totalLessons = endPosition - startPosition + 1;
    
    if (totalLessons <= 0) return 'Invalid range';
    
    const weeks = Math.floor(totalLessons / lpw);
    const extraLessons = totalLessons % lpw;
    
    let duration = '';
    if (weeks > 0) {
      duration += `${weeks} week${weeks > 1 ? 's' : ''}`;
    }
    if (extraLessons > 0) {
      duration += (weeks > 0 ? ' and ' : '') + `${extraLessons} lesson${extraLessons > 1 ? 's' : ''}`;
    }
    
    return `Duration: ${duration} (${totalLessons} total lesson${totalLessons > 1 ? 's' : ''})`;
  };

  // Topic selection handlers
  const toggleStrandExpand = (strandId: string) => {
    setExpandedStrands(prev => {
      const next = new Set(prev);
      if (next.has(strandId)) {
        next.delete(strandId);
      } else {
        next.add(strandId);
      }
      return next;
    });
  };

  const toggleTopicSelection = (substrandId: string) => {
    setSelectedTopics(prev => {
      const next = new Set(prev);
      if (next.has(substrandId)) {
        next.delete(substrandId);
      } else {
        next.add(substrandId);
      }
      return next;
    });
  };

  const selectAllTopics = () => {
    const allIds = new Set<string>();
    topics.forEach(strand => {
      strand.substrands.forEach(ss => allIds.add(ss.id));
    });
    setSelectedTopics(allIds);
  };

  const deselectAllTopics = () => {
    setSelectedTopics(new Set());
  };

  const isStrandFullySelected = (strand: Topic) => {
    return strand.substrands.every(ss => selectedTopics.has(ss.id));
  };

  const toggleStrandSelection = (strand: Topic) => {
    const allSelected = isStrandFullySelected(strand);
    setSelectedTopics(prev => {
      const next = new Set(prev);
      strand.substrands.forEach(ss => {
        if (allSelected) {
          next.delete(ss.id);
        } else {
          next.add(ss.id);
        }
      });
      return next;
    });
  };

  // Generate scheme
  const generateScheme = async () => {
    setGenerating(true);
    try {
      const headers = await getHeaders();
      const response = await axios.post(
        `${BACKEND_URL}/api/schemes/generate-v2`,
        {
          gradeId: selectedGrade,
          subjectId: selectedSubject,
          term,
          year,
          totalWeeks,
          lessonsPerWeek: lessonsPerWeek || 5,
          selectedTopics: Array.from(selectedTopics),
          breaks: breaks.map(b => ({
            breakType: b.breakType,
            startWeek: b.startWeek,
            startLesson: b.startLesson,
            endWeek: b.endWeek,
            endLesson: b.endLesson
          })),
          doubleLesson: doubleLesson.enabled ? doubleLesson : null,
          includeCarryOver
        },
        { headers }
      );
      
      if (response.data.success) {
        setGeneratedScheme(response.data.scheme);
        setCurrentStep('preview');
      } else {
        Alert.alert('Error', response.data.detail || 'Failed to generate scheme');
      }
    } catch (error: any) {
      
      Alert.alert('Error', error.response?.data?.detail || 'Failed to generate scheme');
    } finally {
      setGenerating(false);
    }
  };

  // Preview PDF (in-app modal)
  const handlePreview = async () => {
    if (!generatedScheme) return;
    
    setPreviewing(true);
    try {
      const headers = await getHeaders();
      
      if (Platform.OS === 'web') {
        // For web, show in modal with iframe
        const response = await axios.post(
          `${BACKEND_URL}/api/schemes/preview`,
          generatedScheme,
          { 
            headers,
            responseType: 'blob'
          }
        );
        
        const blob = new Blob([response.data], { type: 'application/pdf' });
        const url = URL.createObjectURL(blob);
        setPdfPreviewUrl(url);
        setShowPdfModal(true);
      } else {
        // For native (mobile), use axios to POST and save manually
        const token = await firebaseUser?.getIdToken();
        
        const response = await axios.post(
          `${BACKEND_URL}/api/schemes/preview`,
          generatedScheme,
          { 
            headers: {
              Authorization: `Bearer ${token}`,
              'Content-Type': 'application/json'
            },
            responseType: 'arraybuffer'
          }
        );
        
        // Convert arraybuffer to base64
        const base64 = btoa(
          new Uint8Array(response.data).reduce(
            (data, byte) => data + String.fromCharCode(byte),
            ''
          )
        );
        
        // Save to file
        const fileUri = `${FileSystem.documentDirectory}scheme_preview_${Date.now()}.pdf`;
        await FileSystem.writeAsStringAsync(fileUri, base64, {
          encoding: FileSystem.EncodingType.Base64
        });
        
        // Share the file (most reliable way to view PDF on mobile)
        const canShare = await Sharing.isAvailableAsync();
        if (canShare) {
          await Sharing.shareAsync(fileUri, {
            mimeType: 'application/pdf',
            dialogTitle: 'Preview Scheme of Work',
            UTI: 'com.adobe.pdf'
          });
        } else {
          Alert.alert('Preview Ready', 'PDF has been saved to your device.');
        }
      }
    } catch (error: any) {
      Alert.alert('Error', 'Failed to generate preview. Please try again.');
    } finally {
      setPreviewing(false);
    }
  };

  // Download PDF (with wallet check)
  const handleDownload = async () => {
    if (!generatedScheme) return;
    
    // Check wallet balance first
    const currentBalance = user?.walletBalance || 0;
    if (currentBalance < SCHEME_DOWNLOAD_COST) {
      setShowFundsModal(true);
      return;
    }
    
    setDownloading(true);
    try {
      const headers = await getHeaders();
      
      // For web
      if (Platform.OS === 'web') {
        const response = await axios.post(
          `${BACKEND_URL}/api/schemes/download`,
          generatedScheme,
          { 
            headers,
            responseType: 'blob'
          }
        );
        
        const blob = new Blob([response.data], { type: 'application/pdf' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Scheme_${generatedScheme.subjectName}_Term${generatedScheme.term}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        // Refresh wallet balance
        await refreshWalletBalance();
        
        Alert.alert('Success', `Scheme downloaded! KES ${SCHEME_DOWNLOAD_COST} deducted from wallet.`);
      } else {
        // Native download
        const token = await firebaseUser?.getIdToken();
        const fileUri = `${FileSystem.documentDirectory}Scheme_${generatedScheme.subjectName}_Term${generatedScheme.term}.pdf`;
        
        const downloadResult = await FileSystem.downloadAsync(
          `${BACKEND_URL}/api/schemes/download`,
          fileUri,
          {
            headers: { 
              Authorization: `Bearer ${token}`,
              'Content-Type': 'application/json'
            },
            httpMethod: 'POST',
            body: JSON.stringify(generatedScheme)
          }
        );
        
        if (downloadResult.status === 200) {
          await Sharing.shareAsync(downloadResult.uri, { mimeType: 'application/pdf' });
          
          // Refresh wallet balance
          await refreshWalletBalance();
          
          Alert.alert('Success', `Scheme downloaded! KES ${SCHEME_DOWNLOAD_COST} deducted from wallet.`);
        } else {
          throw new Error('Download failed');
        }
      }
    } catch (error: any) {
      
      if (error.response?.status === 402) {
        setShowFundsModal(true);
      } else {
        Alert.alert('Error', error.response?.data?.detail || 'Failed to download');
      }
    } finally {
      setDownloading(false);
    }
  };
  
  // Refresh wallet balance after download
  const refreshWalletBalance = async () => {
    try {
      const headers = await getHeaders();
      const response = await axios.get(`${BACKEND_URL}/api/wallet/balance`, { headers });
      if (response.data && typeof response.data.balance === 'number') {
        // Update user context with new balance
        if (user) {
          user.walletBalance = response.data.balance;
        }
      }
    } catch (error) {
      
    }
  };

  // Get selected grade/subject names
  const selectedGradeName = grades.find(g => g.id === selectedGrade)?.name || '';
  const selectedSubjectName = subjects.find(s => s.id === selectedSubject)?.name || '';

  // Render Step 1: Basic Selection
  const renderSelectionStep = () => (
    <ScrollView style={styles.stepContent}>
      <View style={styles.formSection}>
        <Text style={styles.sectionTitle}>Basic Information</Text>
        
        {/* Grade Picker */}
        <View style={styles.inputGroup}>
          <Text style={styles.label}>Grade *</Text>
          <View style={styles.pickerContainer}>
            <Picker
              selectedValue={selectedGrade}
              onValueChange={setSelectedGrade}
              style={styles.picker}
            >
              <Picker.Item label="Select Grade..." value="" />
              {grades.map(g => (
                <Picker.Item key={g.id} label={g.name} value={g.id} />
              ))}
            </Picker>
          </View>
        </View>
        
        {/* Subject Picker */}
        <View style={styles.inputGroup}>
          <Text style={styles.label}>Subject *</Text>
          <View style={styles.pickerContainer}>
            <Picker
              selectedValue={selectedSubject}
              onValueChange={setSelectedSubject}
              style={styles.picker}
              enabled={subjects.length > 0}
            >
              <Picker.Item label="Select Subject..." value="" />
              {subjects.map(s => (
                <Picker.Item key={s.id} label={s.name} value={s.id} />
              ))}
            </Picker>
          </View>
        </View>
        
        {/* Term Picker */}
        <View style={styles.inputGroup}>
          <Text style={styles.label}>Term</Text>
          <View style={styles.termRow}>
            {[1, 2, 3].map(t => (
              <TouchableOpacity
                key={t}
                style={[styles.termButton, term === t && styles.termButtonActive]}
                onPress={() => setTerm(t)}
              >
                <Text style={[styles.termButtonText, term === t && styles.termButtonTextActive]}>
                  Term {t}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>
        
        {/* Lessons per Week (User Selectable with auto-default) */}
        <View style={styles.inputGroup}>
          <Text style={styles.label}>Lessons per Week</Text>
          <View style={styles.lessonsRow}>
            {[4, 5, 6, 7, 8].map(l => (
              <TouchableOpacity
                key={l}
                style={[styles.lessonButton, lessonsPerWeek === l && styles.lessonButtonActive]}
                onPress={() => setLessonsPerWeek(l)}
              >
                <Text style={[styles.lessonButtonText, lessonsPerWeek === l && styles.lessonButtonTextActive]}>
                  {l}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
          {lessonsPerWeek && selectedSubjectName && (
            <Text style={styles.autoHint}>
              Default for {selectedSubjectName}: {lessonsPerWeek} lessons/week
            </Text>
          )}
        </View>
        
        {/* Number of Weeks (8-14) */}
        <View style={styles.inputGroup}>
          <Text style={styles.label}>Number of Weeks</Text>
          <View style={styles.weeksRow}>
            {[8, 9, 10, 11, 12, 13, 14].map(w => (
              <TouchableOpacity
                key={w}
                style={[styles.weekButton, totalWeeks === w && styles.weekButtonActive]}
                onPress={() => setTotalWeeks(w)}
              >
                <Text style={[styles.weekButtonText, totalWeeks === w && styles.weekButtonTextActive]}>
                  {w}
                </Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>
        
        {/* Double Lesson Support */}
        <View style={styles.inputGroup}>
          <Text style={styles.label}>Double Lesson</Text>
          <View style={styles.doubleLessonRow}>
            <TouchableOpacity
              style={[styles.toggleBtn, !doubleLesson.enabled && styles.toggleBtnActive]}
              onPress={() => setDoubleLesson(prev => ({ ...prev, enabled: false }))}
            >
              <Text style={[styles.toggleBtnText, !doubleLesson.enabled && styles.toggleBtnTextActive]}>No</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.toggleBtn, doubleLesson.enabled && styles.toggleBtnActive]}
              onPress={() => setDoubleLesson(prev => ({ ...prev, enabled: true }))}
            >
              <Text style={[styles.toggleBtnText, doubleLesson.enabled && styles.toggleBtnTextActive]}>Yes</Text>
            </TouchableOpacity>
          </View>
          
          {doubleLesson.enabled && (
            <View style={styles.doubleLessonPosition}>
              <Text style={styles.subLabel}>Double lesson position:</Text>
              <View style={styles.positionRow}>
                {['2-3', '3-4', '4-5'].map(pos => (
                  <TouchableOpacity
                    key={pos}
                    style={[styles.positionBtn, doubleLesson.position === pos && styles.positionBtnActive]}
                    onPress={() => setDoubleLesson(prev => ({ ...prev, position: pos }))}
                  >
                    <Text style={[styles.positionBtnText, doubleLesson.position === pos && styles.positionBtnTextActive]}>
                      Lesson {pos}
                    </Text>
                  </TouchableOpacity>
                ))}
              </View>
            </View>
          )}
        </View>
        
        {/* Carry-over Content Option */}
        <View style={styles.inputGroup}>
          <Text style={styles.label}>Include Previous Term Uncovered Content?</Text>
          <Text style={styles.subHint}>Compresses scheduling to fit more topics</Text>
          <View style={styles.doubleLessonRow}>
            <TouchableOpacity
              style={[styles.toggleBtn, !includeCarryOver && styles.toggleBtnActive]}
              onPress={() => setIncludeCarryOver(false)}
            >
              <Text style={[styles.toggleBtnText, !includeCarryOver && styles.toggleBtnTextActive]}>No</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.toggleBtn, includeCarryOver && styles.toggleBtnActive]}
              onPress={() => setIncludeCarryOver(true)}
            >
              <Text style={[styles.toggleBtnText, includeCarryOver && styles.toggleBtnTextActive]}>Yes</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </ScrollView>
  );

  // Render Step 2: Topic Selection
  const renderTopicsStep = () => (
    <View style={styles.stepContent}>
      {loadingTopics ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#6366F1" />
          <Text style={styles.loadingText}>Loading topics...</Text>
        </View>
      ) : (
        <>
          {/* Selection header */}
          <View style={styles.topicsHeader}>
            <Text style={styles.topicsTitle}>
              Select Topics ({selectedTopics.size} selected)
            </Text>
            <View style={styles.selectActions}>
              <TouchableOpacity onPress={selectAllTopics} style={styles.selectAllBtn}>
                <Text style={styles.selectAllText}>Select All</Text>
              </TouchableOpacity>
              <TouchableOpacity onPress={deselectAllTopics} style={styles.deselectAllBtn}>
                <Text style={styles.deselectAllText}>Clear</Text>
              </TouchableOpacity>
            </View>
          </View>
          
          {/* Topics list */}
          <FlatList
            data={topics}
            keyExtractor={(item) => item.id}
            renderItem={({ item: strand }) => (
              <View style={styles.strandContainer}>
                {/* Strand header */}
                <TouchableOpacity
                  style={styles.strandHeader}
                  onPress={() => toggleStrandExpand(strand.id)}
                >
                  <TouchableOpacity
                    style={styles.strandCheckbox}
                    onPress={() => toggleStrandSelection(strand)}
                  >
                    <Ionicons
                      name={isStrandFullySelected(strand) ? "checkbox" : 
                            strand.substrands.some(ss => selectedTopics.has(ss.id)) ? "remove-circle" : "square-outline"}
                      size={22}
                      color={isStrandFullySelected(strand) ? "#6366F1" : "#9CA3AF"}
                    />
                  </TouchableOpacity>
                  <View style={styles.strandInfo}>
                    <Text style={styles.strandName}>{strand.name}</Text>
                    <Text style={styles.strandMeta}>
                      {strand.substrands.length} sub-topics • {strand.totalSlos} SLOs
                    </Text>
                  </View>
                  <Ionicons
                    name={expandedStrands.has(strand.id) ? "chevron-up" : "chevron-down"}
                    size={20}
                    color="#6B7280"
                  />
                </TouchableOpacity>
                
                {/* Substrands */}
                {expandedStrands.has(strand.id) && (
                  <View style={styles.substrandsContainer}>
                    {strand.substrands.map(ss => (
                      <TouchableOpacity
                        key={ss.id}
                        style={styles.substrandItem}
                        onPress={() => toggleTopicSelection(ss.id)}
                      >
                        <Ionicons
                          name={selectedTopics.has(ss.id) ? "checkbox" : "square-outline"}
                          size={20}
                          color={selectedTopics.has(ss.id) ? "#6366F1" : "#D1D5DB"}
                        />
                        <Text style={[
                          styles.substrandName,
                          selectedTopics.has(ss.id) && styles.substrandNameSelected
                        ]}>
                          {ss.name}
                        </Text>
                        <Text style={styles.sloCount}>{ss.sloCount} SLOs</Text>
                      </TouchableOpacity>
                    ))}
                  </View>
                )}
              </View>
            )}
            contentContainerStyle={styles.topicsList}
          />
        </>
      )}
    </View>
  );

  // Render Step 3: Breaks
  const renderBreaksStep = () => (
    <ScrollView style={styles.stepContent}>
      <View style={styles.formSection}>
        <Text style={styles.sectionTitle}>Term Breaks</Text>
        <Text style={styles.sectionSubtitle}>
          Add breaks like mid-term, exams, or holidays
        </Text>
        
        {breaks.map((brk, index) => (
          <View key={index} style={styles.breakCard}>
            <View style={styles.breakInfo}>
              <Text style={styles.breakType}>{brk.breakType}</Text>
              <Text style={styles.breakDetails}>
                Week {brk.startWeek}, Lesson {brk.startLesson} → Week {brk.endWeek}, Lesson {brk.endLesson}
              </Text>
            </View>
            <TouchableOpacity
              onPress={() => {
                const newBreaks = [...breaks];
                newBreaks.splice(index, 1);
                setBreaks(newBreaks);
              }}
            >
              <Ionicons name="trash-outline" size={20} color="#EF4444" />
            </TouchableOpacity>
          </View>
        ))}
        
        <TouchableOpacity
          style={styles.addBreakBtn}
          onPress={() => setBreakModalVisible(true)}
        >
          <Ionicons name="add" size={20} color="#6366F1" />
          <Text style={styles.addBreakText}>Add Break</Text>
        </TouchableOpacity>
      </View>
      
      {/* Summary */}
      <View style={styles.summaryCard}>
        <Text style={styles.summaryTitle}>Summary</Text>
        <View style={styles.summaryRow}>
          <Text style={styles.summaryLabel}>Grade & Subject</Text>
          <Text style={styles.summaryValue}>{selectedGradeName} - {selectedSubjectName}</Text>
        </View>
        <View style={styles.summaryRow}>
          <Text style={styles.summaryLabel}>Term</Text>
          <Text style={styles.summaryValue}>Term {term}, {year}</Text>
        </View>
        <View style={styles.summaryRow}>
          <Text style={styles.summaryLabel}>Duration</Text>
          <Text style={styles.summaryValue}>{totalWeeks} weeks × {lessonsPerWeek} lessons/week</Text>
        </View>
        <View style={styles.summaryRow}>
          <Text style={styles.summaryLabel}>Topics Selected</Text>
          <Text style={styles.summaryValue}>{selectedTopics.size} sub-topics</Text>
        </View>
      </View>
    </ScrollView>
  );

  // Render Step 4: Preview
  // ── Duplicate-click guard for download ──
  const downloadLockRef = React.useRef(false);

  const renderPreviewStep = () => {
    if (!generatedScheme) return null;
    const lessons = generatedScheme.lessons || [];
    const teachingLessons = lessons.filter((l: any) => !l.isBreak);

    return (
      <View style={{ flex: 1 }}>
        {/* ── Sticky top action bar (like lesson-detail) ── */}
        <View style={styles.previewActionBar}>
          <TouchableOpacity
            style={styles.previewEditBtn}
            onPress={() => setCurrentStep('breaks')}
            data-testid="scheme-edit-btn"
          >
            <Ionicons name="create-outline" size={16} color="#6366F1" />
            <Text style={styles.previewEditBtnText}>Edit</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.previewDownloadBtn, downloading && { opacity: 0.6 }]}
            onPress={handleDownload}
            disabled={downloading}
            data-testid="scheme-download-btn"
          >
            {downloading ? (
              <ActivityIndicator size={14} color="#fff" />
            ) : (
              <Ionicons name="download-outline" size={16} color="#fff" />
            )}
            <Text style={styles.previewDownloadBtnText}>
              {downloading ? 'Downloading...' : `Download PDF (KES ${SCHEME_DOWNLOAD_COST})`}
            </Text>
          </TouchableOpacity>
        </View>

        {/* ── Scrollable scheme content ── */}
        <ScrollView style={styles.stepContent} contentContainerStyle={{ paddingBottom: 40 }}>
          {/* Header card */}
          <View style={styles.schemeHeaderCard}>
            <Text style={styles.schemeHeaderTitle}>{generatedScheme.subjectName || 'Scheme of Work'}</Text>
            <Text style={styles.schemeHeaderSub}>
              {generatedScheme.gradeName} | Term {generatedScheme.term}, {generatedScheme.year}
            </Text>
            <View style={styles.schemeStatRow}>
              <View style={styles.schemeStatItem}>
                <Text style={styles.schemeStatVal}>{teachingLessons.length}</Text>
                <Text style={styles.schemeStatLbl}>Lessons</Text>
              </View>
              <View style={styles.schemeStatItem}>
                <Text style={styles.schemeStatVal}>{totalWeeks}</Text>
                <Text style={styles.schemeStatLbl}>Weeks</Text>
              </View>
              <View style={styles.schemeStatItem}>
                <Text style={styles.schemeStatVal}>KES {user?.walletBalance || 0}</Text>
                <Text style={styles.schemeStatLbl}>Balance</Text>
              </View>
            </View>
          </View>

          {/* Lesson rows */}
          {lessons.map((lesson: any, idx: number) => {
            if (lesson.isBreak) {
              return (
                <View key={`brk-${idx}`} style={styles.schemeBreakRow}>
                  <Ionicons name="pause-circle-outline" size={16} color="#F59E0B" />
                  <Text style={styles.schemeBreakText}>
                    Week {lesson.week}: {lesson.breakType || lesson.breakDescription || 'Break'}
                  </Text>
                </View>
              );
            }
            return (
              <View key={`l-${idx}`} style={styles.schemeLessonCard}>
                <View style={styles.schemeLessonHeader}>
                  <Text style={styles.schemeLessonWk}>W{lesson.week} L{lesson.lesson || lesson.lessonNumber}</Text>
                  {lesson.isDouble && (
                    <View style={styles.schemeDoubleBadge}>
                      <Text style={styles.schemeDoubleBadgeText}>Double</Text>
                    </View>
                  )}
                </View>
                <Text style={styles.schemeLessonStrand}>{lesson.strand} / {lesson.substrand}</Text>
                <Text style={styles.schemeLessonSlo} numberOfLines={3}>{lesson.slo}</Text>
                {lesson.keyInquiryQuestions ? (
                  <View style={styles.schemeLessonIqRow}>
                    <Ionicons name="help-circle-outline" size={14} color="#6366F1" />
                    <Text style={styles.schemeLessonIq} numberOfLines={2}>{lesson.keyInquiryQuestions}</Text>
                  </View>
                ) : null}
                {lesson.learningResources ? (
                  <View style={styles.schemeLessonResRow}>
                    <Ionicons name="book-outline" size={13} color="#6B7280" />
                    <Text style={styles.schemeLessonRes} numberOfLines={2}>
                      {Array.isArray(lesson.learningResources) ? lesson.learningResources.join(', ') : lesson.learningResources}
                    </Text>
                  </View>
                ) : null}
              </View>
            );
          })}
        </ScrollView>
      </View>
    );
  };

  // Insufficient Funds Modal
  const renderFundsModal = () => (
    <Modal visible={showFundsModal} transparent animationType="fade">
      <View style={styles.modalOverlay}>
        <View style={styles.fundsModal}>
          <View style={styles.fundsModalHeader}>
            <Ionicons name="wallet-outline" size={48} color="#F59E0B" />
            <Text style={styles.fundsModalTitle}>You're almost there! 😊</Text>
          </View>
          
          <Text style={styles.fundsModalText}>
            To download this Scheme of Work, you need KES {SCHEME_DOWNLOAD_COST}.
          </Text>
          
          <Text style={styles.fundsModalBalance}>
            Your current balance: KES {user?.walletBalance || 0}
          </Text>
          
          <Text style={styles.fundsModalHint}>
            Top up your wallet and come back - your scheme will be waiting!
          </Text>
          
          <View style={styles.fundsModalButtons}>
            <TouchableOpacity
              style={styles.topUpBtn}
              onPress={() => {
                setShowFundsModal(false);
                setPendingDownload(true); // Mark that we have a pending download
                router.push('/(teacher)/profile');
              }}
              data-testid="top-up-mpesa-btn"
            >
              <Ionicons name="phone-portrait-outline" size={18} color="#FFFFFF" />
              <Text style={styles.topUpBtnText}>Top Up via M-PESA</Text>
            </TouchableOpacity>
            
            <TouchableOpacity
              style={styles.cancelBtn}
              onPress={() => setShowFundsModal(false)}
              data-testid="cancel-funds-btn"
            >
              <Text style={styles.cancelBtnText}>Maybe Later</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );

  // Break Modal
  const renderBreakModal = () => (
    <Modal visible={breakModalVisible} transparent animationType="slide">
      <View style={styles.modalOverlay}>
        <View style={styles.breakModal}>
          <Text style={styles.breakModalTitle}>
            {editingBreak && breaks.some(b => b === editingBreak) ? 'Edit Break' : 'Add Break'}
          </Text>
          
          <ScrollView style={styles.breakModalContent}>
            <View style={styles.inputGroup}>
              <Text style={styles.label}>Break Type</Text>
              <View style={styles.pickerContainer}>
                <Picker
                  selectedValue={editingBreak?.breakType || 'Half-Term Break'}
                  onValueChange={(v) => setEditingBreak(prev => ({...prev, breakType: v} as Break))}
                  style={styles.picker}
                >
                  <Picker.Item label="Opener CAT" value="Opener CAT" />
                  <Picker.Item label="Half-Term Break" value="Half-Term Break" />
                  <Picker.Item label="Mid-Term Break" value="Mid-Term Break" />
                  <Picker.Item label="End Term Exams" value="End Term Exams" />
                  <Picker.Item label="Holiday" value="Holiday" />
                  <Picker.Item label="Public Holiday" value="Public Holiday" />
                  <Picker.Item label="School Event" value="School Event" />
                  <Picker.Item label="Sports Day" value="Sports Day" />
                  <Picker.Item label="Staff Meeting" value="Staff Meeting" />
                </Picker>
              </View>
            </View>
            
            <Text style={styles.breakSectionLabel}>Break Starts At:</Text>
            
            <View style={styles.breakRowPickers}>
              <View style={styles.breakPickerHalf}>
                <Text style={styles.label}>Week</Text>
                <View style={styles.pickerContainer}>
                  <Picker
                    selectedValue={editingBreak?.startWeek || 1}
                    onValueChange={(v) => setEditingBreak(prev => ({
                      ...prev, 
                      startWeek: v,
                      endWeek: Math.max(prev?.endWeek || v, v)
                    } as Break))}
                    style={styles.picker}
                  >
                    {Array.from({length: totalWeeks}, (_, i) => i + 1).map(w => (
                      <Picker.Item key={w} label={`Week ${w}`} value={w} />
                    ))}
                  </Picker>
                </View>
              </View>
              
              <View style={styles.breakPickerHalf}>
                <Text style={styles.label}>Lesson</Text>
                <View style={styles.pickerContainer}>
                  <Picker
                    selectedValue={editingBreak?.startLesson || 1}
                    onValueChange={(v) => setEditingBreak(prev => ({...prev, startLesson: v} as Break))}
                    style={styles.picker}
                  >
                    {Array.from({length: lessonsPerWeek || 5}, (_, i) => i + 1).map(l => (
                      <Picker.Item key={l} label={`Lesson ${l}`} value={l} />
                    ))}
                  </Picker>
                </View>
              </View>
            </View>
            
            <Text style={styles.breakSectionLabel}>Break Ends At:</Text>
            
            <View style={styles.breakRowPickers}>
              <View style={styles.breakPickerHalf}>
                <Text style={styles.label}>Week</Text>
                <View style={styles.pickerContainer}>
                  <Picker
                    selectedValue={editingBreak?.endWeek || editingBreak?.startWeek || 1}
                    onValueChange={(v) => setEditingBreak(prev => ({...prev, endWeek: v} as Break))}
                    style={styles.picker}
                  >
                    {Array.from({length: totalWeeks}, (_, i) => i + 1)
                      .filter(w => w >= (editingBreak?.startWeek || 1))
                      .map(w => (
                        <Picker.Item key={w} label={`Week ${w}`} value={w} />
                      ))}
                  </Picker>
                </View>
              </View>
              
              <View style={styles.breakPickerHalf}>
                <Text style={styles.label}>Lesson</Text>
                <View style={styles.pickerContainer}>
                  <Picker
                    selectedValue={editingBreak?.endLesson || lessonsPerWeek || 5}
                    onValueChange={(v) => setEditingBreak(prev => ({...prev, endLesson: v} as Break))}
                    style={styles.picker}
                  >
                    {Array.from({length: lessonsPerWeek || 5}, (_, i) => i + 1).map(l => (
                      <Picker.Item key={l} label={`Lesson ${l}`} value={l} />
                    ))}
                  </Picker>
                </View>
              </View>
            </View>
            
            <View style={styles.breakDurationInfo}>
              <Ionicons name="information-circle-outline" size={16} color="#6B7280" />
              <Text style={styles.breakDurationText}>
                {calculateBreakDuration(editingBreak)}
              </Text>
            </View>
            
            {/* Optional Calendar Date */}
            <View style={styles.inputGroup}>
              <Text style={styles.label}>Calendar Date (Optional)</Text>
              <TextInput
                style={styles.dateInput}
                placeholder="e.g., 2025-04-15"
                placeholderTextColor="#9CA3AF"
                value={editingBreak?.startDate || ''}
                onChangeText={(text) => setEditingBreak(prev => ({...prev, startDate: text} as Break))}
              />
              <Text style={styles.dateHint}>Format: YYYY-MM-DD (for reference only)</Text>
            </View>
          </ScrollView>
          
          <View style={styles.breakModalButtons}>
            <TouchableOpacity
              style={styles.breakModalCancel}
              onPress={() => {
                setBreakModalVisible(false);
                setEditingBreak(null);
              }}
            >
              <Text style={styles.breakModalCancelText}>Cancel</Text>
            </TouchableOpacity>
            
            <TouchableOpacity
              style={styles.breakModalAdd}
              onPress={() => {
                if (editingBreak && editingBreak.breakType) {
                  const newBreak: Break = {
                    breakType: editingBreak.breakType,
                    startWeek: editingBreak.startWeek || 1,
                    startLesson: editingBreak.startLesson || 1,
                    endWeek: editingBreak.endWeek || editingBreak.startWeek || 1,
                    endLesson: editingBreak.endLesson || (lessonsPerWeek || 5),
                    startDate: editingBreak.startDate
                  };
                  setBreaks(prev => [...prev, newBreak]);
                }
                setBreakModalVisible(false);
                setEditingBreak(null);
              }}
            >
              <Text style={styles.breakModalAddText}>Add Break</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );

  // PDF Preview Modal (in-app viewer)
  const renderPdfPreviewModal = () => (
    <Modal visible={showPdfModal} transparent animationType="slide">
      <SafeAreaView style={styles.pdfModalSafeArea}>
        <View style={styles.pdfModalContainer}>
          <View style={styles.pdfModalHeader}>
            <Text style={styles.pdfModalTitle}>Scheme Preview</Text>
            <View style={styles.pdfModalActions}>
              {pdfPreviewUrl && Platform.OS !== 'web' && (
                <TouchableOpacity 
                  style={styles.pdfShareBtn}
                  onPress={async () => {
                    try {
                      const canShare = await Sharing.isAvailableAsync();
                      if (canShare && pdfPreviewUrl) {
                        await Sharing.shareAsync(pdfPreviewUrl, { 
                          mimeType: 'application/pdf',
                          dialogTitle: 'Share Scheme of Work'
                        });
                      }
                    } catch (err) {
                      Alert.alert('Error', 'Unable to share PDF');
                    }
                  }}
                >
                  <Ionicons name="share-outline" size={22} color="#6366F1" />
                </TouchableOpacity>
              )}
              <TouchableOpacity 
                onPress={() => {
                  setShowPdfModal(false);
                  if (pdfPreviewUrl && Platform.OS === 'web') {
                    URL.revokeObjectURL(pdfPreviewUrl);
                  }
                  setPdfPreviewUrl(null);
                }} 
                style={styles.pdfModalCloseBtn}
              >
                <Ionicons name="close" size={24} color="#374151" />
              </TouchableOpacity>
            </View>
          </View>
          <View style={styles.pdfModalContent}>
            {Platform.OS === 'web' && pdfPreviewUrl ? (
              <iframe
                src={pdfPreviewUrl}
                style={{ width: '100%', height: '100%', border: 'none' } as any}
                title="PDF Preview"
              />
            ) : Platform.OS !== 'web' && pdfPreviewUrl ? (
              <WebView
                source={{ uri: pdfPreviewUrl }}
                style={styles.pdfWebView}
                startInLoadingState={true}
                renderLoading={() => (
                  <View style={styles.pdfLoading}>
                    <ActivityIndicator size="large" color="#6366F1" />
                    <Text style={styles.pdfLoadingText}>Loading PDF...</Text>
                  </View>
                )}
                onError={() => {
                  Alert.alert('Error', 'Unable to display PDF. Tap Share to open in another app.');
                }}
              />
            ) : (
              <View style={styles.pdfModalPlaceholder}>
                <ActivityIndicator size="large" color="#6366F1" />
                <Text style={styles.pdfModalPlaceholderText}>Loading Preview...</Text>
              </View>
            )}
          </View>
        </View>
      </SafeAreaView>
    </Modal>
  );

  return (
    <View style={styles.container}>
      {/* Step indicator */}
      <View style={styles.stepIndicator}>
        {(['select', 'topics', 'breaks', 'preview'] as Step[]).map((step, index) => (
          <View key={step} style={styles.stepItem}>
            <View style={[
              styles.stepDot,
              currentStep === step && styles.stepDotActive,
              (['select', 'topics', 'breaks', 'preview'] as Step[]).indexOf(currentStep) > index && styles.stepDotComplete
            ]}>
              {(['select', 'topics', 'breaks', 'preview'] as Step[]).indexOf(currentStep) > index ? (
                <Ionicons name="checkmark" size={14} color="#FFFFFF" />
              ) : (
                <Text style={[
                  styles.stepDotText,
                  currentStep === step && styles.stepDotTextActive
                ]}>{index + 1}</Text>
              )}
            </View>
            <Text style={[
              styles.stepLabel,
              currentStep === step && styles.stepLabelActive
            ]}>
              {step === 'select' ? 'Select' : step === 'topics' ? 'Topics' : step === 'breaks' ? 'Breaks' : 'Preview'}
            </Text>
          </View>
        ))}
      </View>
      
      {/* Content */}
      {currentStep === 'select' && renderSelectionStep()}
      {currentStep === 'topics' && renderTopicsStep()}
      {currentStep === 'breaks' && renderBreaksStep()}
      {currentStep === 'preview' && renderPreviewStep()}
      
      {/* Footer buttons */}
      {currentStep !== 'preview' && (
        <View style={styles.footer}>
          {currentStep !== 'select' && (
            <TouchableOpacity style={styles.backBtn} onPress={handleBack}>
              <Ionicons name="arrow-back" size={20} color="#6B7280" />
              <Text style={styles.backBtnText}>Back</Text>
            </TouchableOpacity>
          )}
          
          <TouchableOpacity
            style={[styles.nextBtn, generating && styles.nextBtnDisabled]}
            onPress={handleNext}
            disabled={generating}
          >
            {generating ? (
              <ActivityIndicator size={18} color="#FFFFFF" />
            ) : (
              <>
                <Text style={styles.nextBtnText}>
                  {currentStep === 'breaks' ? 'Generate Scheme' : 'Next'}
                </Text>
                <Ionicons name="arrow-forward" size={20} color="#FFFFFF" />
              </>
            )}
          </TouchableOpacity>
        </View>
      )}
      
      {/* New Scheme button on preview */}
      {currentStep === 'preview' && (
        <View style={styles.footer}>
          <TouchableOpacity
            style={styles.newSchemeBtn}
            onPress={() => {
              setCurrentStep('select');
              setGeneratedScheme(null);
              setSelectedTopics(new Set());
            }}
          >
            <Ionicons name="add" size={20} color="#6366F1" />
            <Text style={styles.newSchemeBtnText}>Create New Scheme</Text>
          </TouchableOpacity>
        </View>
      )}
      
      {renderFundsModal()}
      {renderBreakModal()}
      {renderPdfPreviewModal()}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB'
  },
  stepIndicator: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingHorizontal: 24,
    paddingVertical: 16,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB'
  },
  stepItem: {
    alignItems: 'center'
  },
  stepDot: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: '#E5E7EB',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 4
  },
  stepDotActive: {
    backgroundColor: '#6366F1'
  },
  stepDotComplete: {
    backgroundColor: '#10B981'
  },
  stepDotText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#6B7280'
  },
  stepDotTextActive: {
    color: '#FFFFFF'
  },
  stepLabel: {
    fontSize: 11,
    color: '#9CA3AF'
  },
  stepLabelActive: {
    color: '#6366F1',
    fontWeight: '600'
  },
  stepContent: {
    flex: 1
  },
  formSection: {
    backgroundColor: '#FFFFFF',
    margin: 16,
    padding: 16,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 4
  },
  sectionSubtitle: {
    fontSize: 13,
    color: '#6B7280',
    marginBottom: 16
  },
  inputGroup: {
    marginBottom: 16
  },
  label: {
    fontSize: 13,
    fontWeight: '500',
    color: '#374151',
    marginBottom: 6
  },
  labelRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 6
  },
  overrideLink: {
    fontSize: 12,
    color: '#6366F1'
  },
  pickerContainer: {
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRadius: 8,
    backgroundColor: '#FFFFFF'
  },
  picker: {
    height: 48
  },
  termRow: {
    flexDirection: 'row',
    gap: 8
  },
  termButton: {
    flex: 1,
    paddingVertical: 10,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#D1D5DB',
    alignItems: 'center'
  },
  termButtonActive: {
    backgroundColor: '#6366F1',
    borderColor: '#6366F1'
  },
  termButtonText: {
    fontSize: 14,
    color: '#374151'
  },
  termButtonTextActive: {
    color: '#FFFFFF',
    fontWeight: '600'
  },
  lessonsRow: {
    flexDirection: 'row',
    gap: 8
  },
  lessonButton: {
    width: 48,
    height: 48,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#D1D5DB',
    justifyContent: 'center',
    alignItems: 'center'
  },
  lessonButtonActive: {
    backgroundColor: '#6366F1',
    borderColor: '#6366F1'
  },
  lessonButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151'
  },
  lessonButtonTextActive: {
    color: '#FFFFFF'
  },
  autoValueContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    padding: 12,
    backgroundColor: '#F0FDF4',
    borderRadius: 8
  },
  autoValueText: {
    fontSize: 13,
    color: '#166534'
  },
  weeksRow: {
    flexDirection: 'row',
    gap: 8
  },
  weekButton: {
    flex: 1,
    paddingVertical: 10,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#D1D5DB',
    alignItems: 'center'
  },
  weekButtonActive: {
    backgroundColor: '#6366F1',
    borderColor: '#6366F1'
  },
  weekButtonText: {
    fontSize: 14,
    color: '#374151'
  },
  weekButtonTextActive: {
    color: '#FFFFFF',
    fontWeight: '600'
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center'
  },
  loadingText: {
    marginTop: 12,
    fontSize: 14,
    color: '#6B7280'
  },
  topicsHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB'
  },
  topicsTitle: {
    fontSize: 15,
    fontWeight: '600',
    color: '#1F2937'
  },
  selectActions: {
    flexDirection: 'row',
    gap: 12
  },
  selectAllBtn: {
    paddingVertical: 6,
    paddingHorizontal: 12,
    backgroundColor: '#EEF2FF',
    borderRadius: 6
  },
  selectAllText: {
    fontSize: 12,
    color: '#6366F1',
    fontWeight: '500'
  },
  deselectAllBtn: {
    paddingVertical: 6,
    paddingHorizontal: 12
  },
  deselectAllText: {
    fontSize: 12,
    color: '#6B7280'
  },
  topicsList: {
    padding: 16
  },
  strandContainer: {
    backgroundColor: '#FFFFFF',
    borderRadius: 10,
    marginBottom: 12,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: '#E5E7EB'
  },
  strandHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 14,
    backgroundColor: '#F9FAFB'
  },
  strandCheckbox: {
    marginRight: 12
  },
  strandInfo: {
    flex: 1
  },
  strandName: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 2
  },
  strandMeta: {
    fontSize: 12,
    color: '#6B7280'
  },
  substrandsContainer: {
    paddingLeft: 48,
    paddingRight: 14,
    paddingBottom: 8
  },
  substrandItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6'
  },
  substrandName: {
    flex: 1,
    fontSize: 13,
    color: '#374151',
    marginLeft: 10
  },
  substrandNameSelected: {
    color: '#6366F1',
    fontWeight: '500'
  },
  sloCount: {
    fontSize: 11,
    color: '#9CA3AF',
    backgroundColor: '#F3F4F6',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 10
  },
  breakCard: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 14,
    backgroundColor: '#F9FAFB',
    borderRadius: 8,
    marginBottom: 10
  },
  breakInfo: {
    flex: 1
  },
  breakType: {
    fontSize: 14,
    fontWeight: '500',
    color: '#1F2937'
  },
  breakDetails: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 2
  },
  addBreakBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    borderWidth: 1,
    borderColor: '#6366F1',
    borderStyle: 'dashed',
    borderRadius: 8,
    gap: 8
  },
  addBreakText: {
    fontSize: 14,
    color: '#6366F1',
    fontWeight: '500'
  },
  summaryCard: {
    backgroundColor: '#FFFFFF',
    margin: 16,
    marginTop: 0,
    padding: 16,
    borderRadius: 12
  },
  summaryTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 12
  },
  summaryRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6'
  },
  summaryLabel: {
    fontSize: 13,
    color: '#6B7280'
  },
  summaryValue: {
    fontSize: 13,
    fontWeight: '500',
    color: '#1F2937'
  },
  // ── Preview action bar (sticky top, like lesson-detail) ──
  previewActionBar: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 10,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  previewEditBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 5,
    paddingVertical: 8,
    paddingHorizontal: 14,
    borderRadius: 8,
    backgroundColor: '#EEF2FF',
  },
  previewEditBtnText: {
    fontSize: 13,
    fontWeight: '600',
    color: '#6366F1',
  },
  previewDownloadBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 8,
    backgroundColor: '#6366F1',
  },
  previewDownloadBtnText: {
    fontSize: 13,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  // ── Scheme header card ──
  schemeHeaderCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 20,
    marginBottom: 12,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  schemeHeaderTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#111827',
  },
  schemeHeaderSub: {
    fontSize: 13,
    color: '#6B7280',
    marginTop: 4,
  },
  schemeStatRow: {
    flexDirection: 'row',
    marginTop: 14,
    gap: 20,
  },
  schemeStatItem: {
    alignItems: 'center',
  },
  schemeStatVal: {
    fontSize: 18,
    fontWeight: '700',
    color: '#6366F1',
  },
  schemeStatLbl: {
    fontSize: 11,
    color: '#6B7280',
    marginTop: 2,
  },
  // ── Break row ──
  schemeBreakRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    backgroundColor: '#FFFBEB',
    borderRadius: 8,
    padding: 10,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#FDE68A',
  },
  schemeBreakText: {
    fontSize: 13,
    color: '#92400E',
    fontWeight: '500',
  },
  // ── Lesson card ──
  schemeLessonCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 10,
    padding: 12,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  schemeLessonHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 4,
  },
  schemeLessonWk: {
    fontSize: 12,
    fontWeight: '700',
    color: '#6366F1',
    backgroundColor: '#EEF2FF',
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 6,
    overflow: 'hidden',
  },
  schemeDoubleBadge: {
    backgroundColor: '#FEF3C7',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 6,
  },
  schemeDoubleBadgeText: {
    fontSize: 10,
    fontWeight: '600',
    color: '#92400E',
  },
  schemeLessonStrand: {
    fontSize: 11,
    color: '#6B7280',
    marginBottom: 4,
  },
  schemeLessonSlo: {
    fontSize: 13,
    color: '#111827',
    lineHeight: 18,
    marginBottom: 4,
  },
  schemeLessonIqRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 5,
    marginTop: 2,
  },
  schemeLessonIq: {
    fontSize: 12,
    color: '#4B5563',
    flex: 1,
    fontStyle: 'italic',
  },
  schemeLessonResRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 5,
    marginTop: 4,
  },
  schemeLessonRes: {
    fontSize: 11,
    color: '#6B7280',
    flex: 1,
  },
  // ── Keep old styles for other parts ──
  previewHeader: {
    alignItems: 'center',
    paddingVertical: 32
  },
  previewTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: '#1F2937',
    marginTop: 12
  },
  previewSubtitle: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 4
  },
  previewStats: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 16,
    paddingHorizontal: 16
  },
  statCard: {
    backgroundColor: '#FFFFFF',
    paddingVertical: 16,
    paddingHorizontal: 24,
    borderRadius: 12,
    alignItems: 'center',
    minWidth: 90
  },
  statValue: {
    fontSize: 24,
    fontWeight: '700',
    color: '#6366F1'
  },
  statLabel: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 2
  },
  actionButtons: {
    padding: 16,
    gap: 12
  },
  previewBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 14,
    backgroundColor: '#EEF2FF',
    borderRadius: 10,
    gap: 8
  },
  previewBtnText: {
    fontSize: 15,
    fontWeight: '600',
    color: '#6366F1'
  },
  downloadBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 14,
    backgroundColor: '#6366F1',
    borderRadius: 10,
    gap: 8
  },
  downloadBtnText: {
    fontSize: 15,
    fontWeight: '600',
    color: '#FFFFFF'
  },
  walletInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 6,
    paddingVertical: 8
  },
  walletText: {
    fontSize: 13,
    color: '#6B7280'
  },
  footer: {
    flexDirection: 'row',
    padding: 16,
    backgroundColor: '#FFFFFF',
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
    gap: 12
  },
  backBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 16,
    gap: 6
  },
  backBtnText: {
    fontSize: 14,
    color: '#6B7280'
  },
  nextBtn: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 14,
    backgroundColor: '#6366F1',
    borderRadius: 10,
    gap: 8
  },
  nextBtnDisabled: {
    opacity: 0.7
  },
  nextBtnText: {
    fontSize: 15,
    fontWeight: '600',
    color: '#FFFFFF'
  },
  newSchemeBtn: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 14,
    backgroundColor: '#EEF2FF',
    borderRadius: 10,
    gap: 8
  },
  newSchemeBtnText: {
    fontSize: 15,
    fontWeight: '600',
    color: '#6366F1'
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center'
  },
  fundsModal: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 24,
    margin: 20,
    width: '90%',
    maxWidth: 400
  },
  fundsModalHeader: {
    alignItems: 'center',
    marginBottom: 16
  },
  fundsModalTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#1F2937',
    marginTop: 12
  },
  fundsModalText: {
    fontSize: 14,
    color: '#4B5563',
    textAlign: 'center',
    marginBottom: 8
  },
  fundsModalBalance: {
    fontSize: 15,
    fontWeight: '600',
    color: '#EF4444',
    textAlign: 'center',
    marginBottom: 8
  },
  fundsModalHint: {
    fontSize: 13,
    color: '#6B7280',
    textAlign: 'center',
    marginBottom: 20
  },
  fundsModalButtons: {
    gap: 10
  },
  topUpBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 14,
    backgroundColor: '#10B981',
    borderRadius: 10,
    gap: 8
  },
  topUpBtnText: {
    fontSize: 15,
    fontWeight: '600',
    color: '#FFFFFF'
  },
  cancelBtn: {
    paddingVertical: 12,
    alignItems: 'center'
  },
  cancelBtnText: {
    fontSize: 14,
    color: '#6B7280'
  },
  breakModal: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 20,
    margin: 20,
    width: '90%',
    maxWidth: 400
  },
  breakModalTitle: {
    fontSize: 17,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 16
  },
  breakModalContent: {
    marginBottom: 16
  },
  breakModalButtons: {
    flexDirection: 'row',
    gap: 12
  },
  breakModalCancel: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#D1D5DB',
    alignItems: 'center'
  },
  breakModalCancelText: {
    fontSize: 14,
    color: '#6B7280'
  },
  breakModalAdd: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 8,
    backgroundColor: '#6366F1',
    alignItems: 'center'
  },
  breakModalAddText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#FFFFFF'
  },
  breakSectionLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#374151',
    marginTop: 12,
    marginBottom: 8
  },
  breakRowPickers: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 8
  },
  breakPickerHalf: {
    flex: 1
  },
  breakDurationInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F3F4F6',
    padding: 12,
    borderRadius: 8,
    marginTop: 12,
    gap: 8
  },
  breakDurationText: {
    fontSize: 13,
    color: '#4B5563',
    flex: 1
  },
  editSchemeBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 14,
    backgroundColor: '#EEF2FF',
    borderRadius: 10,
    marginHorizontal: 16,
    marginBottom: 16,
    gap: 8
  },
  editSchemeBtnText: {
    fontSize: 15,
    fontWeight: '600',
    color: '#6366F1'
  },
  // Double lesson styles
  doubleLessonRow: {
    flexDirection: 'row',
    gap: 12,
    marginTop: 8
  },
  toggleBtn: {
    flex: 1,
    paddingVertical: 10,
    paddingHorizontal: 16,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#D1D5DB',
    alignItems: 'center',
    backgroundColor: '#FFFFFF'
  },
  toggleBtnActive: {
    borderColor: '#6366F1',
    backgroundColor: '#EEF2FF'
  },
  toggleBtnText: {
    fontSize: 14,
    color: '#6B7280'
  },
  toggleBtnTextActive: {
    color: '#6366F1',
    fontWeight: '600'
  },
  doubleLessonPosition: {
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB'
  },
  subLabel: {
    fontSize: 13,
    color: '#6B7280',
    marginBottom: 8
  },
  subHint: {
    fontSize: 12,
    color: '#9CA3AF',
    marginTop: 4,
    marginBottom: 8
  },
  positionRow: {
    flexDirection: 'row',
    gap: 10
  },
  positionBtn: {
    paddingVertical: 8,
    paddingHorizontal: 14,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#D1D5DB',
    backgroundColor: '#FFFFFF'
  },
  positionBtnActive: {
    borderColor: '#6366F1',
    backgroundColor: '#EEF2FF'
  },
  positionBtnText: {
    fontSize: 13,
    color: '#6B7280'
  },
  positionBtnTextActive: {
    color: '#6366F1',
    fontWeight: '600'
  },
  autoHint: {
    fontSize: 12,
    color: '#10B981',
    marginTop: 6
  },
  // PDF Modal styles
  pdfModalSafeArea: {
    flex: 1,
    backgroundColor: '#FFFFFF'
  },
  pdfModalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.7)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20
  },
  pdfModalContainer: {
    flex: 1,
    width: '100%',
    backgroundColor: '#FFFFFF'
  },
  pdfModalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
    backgroundColor: '#F9FAFB'
  },
  pdfModalTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1F2937'
  },
  pdfModalActions: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12
  },
  pdfShareBtn: {
    padding: 8,
    borderRadius: 8,
    backgroundColor: '#EEF2FF'
  },
  pdfModalCloseBtn: {
    padding: 4
  },
  pdfModalContent: {
    flex: 1,
    backgroundColor: '#F3F4F6'
  },
  pdfWebView: {
    flex: 1,
    backgroundColor: '#F3F4F6'
  },
  pdfLoading: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F3F4F6'
  },
  pdfLoadingText: {
    marginTop: 12,
    fontSize: 14,
    color: '#6B7280'
  },
  pdfModalPlaceholder: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center'
  },
  pdfModalPlaceholderText: {
    fontSize: 16,
    color: '#9CA3AF',
    marginTop: 12
  },
  dateInput: {
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 14,
    color: '#374151',
    backgroundColor: '#FFFFFF'
  },
  dateHint: {
    fontSize: 11,
    color: '#9CA3AF',
    marginTop: 4
  }
});
