import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
  TextInput,
  Modal,
  FlatList
} from 'react-native';
import { Picker } from '@react-native-picker/picker';
import { useAuth } from '../../contexts/AuthContext';
import { Ionicons } from '@expo/vector-icons';
import { SafeAreaView } from 'react-native-safe-area-context';
import axios from 'axios';
import * as Print from 'expo-print';
import * as Sharing from 'expo-sharing';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

interface Break {
  id: string;
  breakType: string;
  startWeek: number;
  startLesson?: number;
  durationType: string;
  durationValue: number;
  description?: string;
}

interface Grade { id: string; name: string; }
interface Subject { id: string; name: string; }

export default function SchemesOfWork() {
  const { user, firebaseUser } = useAuth();
  const [generating, setGenerating] = useState(false);
  
  // Form state
  const [grades, setGrades] = useState<Grade[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [selectedGrade, setSelectedGrade] = useState('');
  const [selectedSubject, setSelectedSubject] = useState('');
  const [term, setTerm] = useState(1);
  const [year, setYear] = useState(new Date().getFullYear());
  const [school, setSchool] = useState(user?.schoolName || '');
  const [teacherName, setTeacherName] = useState(`${user?.firstName || ''} ${user?.lastName || ''}`.trim());
  const [totalWeeks, setTotalWeeks] = useState(14);
  const [lessonsPerWeek, setLessonsPerWeek] = useState(5);
  
  // Breaks
  const [breaks, setBreaks] = useState<Break[]>([]);
  const [breakModalVisible, setBreakModalVisible] = useState(false);
  const [newBreak, setNewBreak] = useState<Partial<Break>>({
    breakType: 'Half-Term',
    startWeek: 1,
    durationType: 'weeks',
    durationValue: 1
  });
  
  // Generated scheme
  const [generatedScheme, setGeneratedScheme] = useState<any>(null);
  
  const getHeaders = async () => {
    if (firebaseUser) {
      const token = await firebaseUser.getIdToken();
      return { Authorization: `Bearer ${token}` };
    }
    return {};
  };

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

  const addBreak = () => {
    if (!newBreak.breakType || !newBreak.startWeek || !newBreak.durationValue) {
      Alert.alert('Error', 'Please fill in all break fields');
      return;
    }
    
    setBreaks([...breaks, {
      id: Date.now().toString(),
      breakType: newBreak.breakType!,
      startWeek: newBreak.startWeek!,
      startLesson: newBreak.startLesson,
      durationType: newBreak.durationType!,
      durationValue: newBreak.durationValue!,
      description: newBreak.description
    }]);
    
    setNewBreak({
      breakType: 'Half-Term',
      startWeek: 1,
      durationType: 'weeks',
      durationValue: 1
    });
    setBreakModalVisible(false);
  };

  const removeBreak = (id: string) => {
    setBreaks(breaks.filter(b => b.id !== id));
  };

  const handleGenerate = async () => {
    if (!selectedGrade || !selectedSubject) {
      Alert.alert('Error', 'Please select grade and subject');
      return;
    }

    setGenerating(true);
    try {
      const headers = await getHeaders();
      const response = await axios.post(
        `${BACKEND_URL}/api/schemes/generate`,
        {
          subjectId: selectedSubject,
          gradeId: selectedGrade,
          term,
          year,
          school,
          teacherName,
          curriculumStandard: 'KICD CBC',
          totalWeeks,
          lessonsPerWeek,
          breaks: breaks.map(b => ({
            breakType: b.breakType,
            startWeek: b.startWeek,
            startLesson: b.startLesson,
            durationType: b.durationType,
            durationValue: b.durationValue,
            description: b.description
          }))
        },
        { headers }
      );

      if (response.data.success) {
        setGeneratedScheme(response.data.scheme);
      }
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to generate scheme');
    } finally {
      setGenerating(false);
    }
  };

  const generatePDF = async () => {
    if (!generatedScheme) return;

    const lessonsHtml = generatedScheme.lessons.map((lesson: any) => {
      if (lesson.isBreak) {
        return `
          <tr class="break-row">
            <td colspan="10" class="break-cell">
              <strong>${lesson.breakType?.toUpperCase()} — WEEK ${lesson.week}</strong><br/>
              ${lesson.breakDescription || ''}
            </td>
          </tr>
        `;
      }
      return `
        <tr>
          <td>${lesson.week}</td>
          <td>${lesson.lessonNumber}</td>
          <td>${lesson.strand || ''}</td>
          <td>${lesson.substrand || ''}</td>
          <td>${lesson.slo || ''}</td>
          <td>${lesson.keyInquiryQuestions || ''}</td>
          <td>${lesson.learningExperiences || ''}</td>
          <td>${lesson.learningResources || ''}</td>
          <td>${lesson.assessmentMethods || ''}</td>
          <td>${lesson.reflection || ''}</td>
        </tr>
      `;
    }).join('');

    const htmlContent = `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="utf-8">
        <title>Scheme of Work</title>
        <style>
          @page { size: A4 landscape; margin: 8mm; }
          body { font-family: Arial, sans-serif; font-size: 9px; margin: 0; padding: 10px; }
          .title { text-align: center; margin-bottom: 10px; }
          .title h1 { font-size: 16px; margin: 0 0 5px 0; text-transform: uppercase; }
          .title h2 { font-size: 14px; margin: 0; font-weight: normal; }
          .header-info { margin-bottom: 10px; }
          .header-row { display: flex; margin-bottom: 5px; }
          .header-item { flex: 1; }
          .header-label { font-weight: bold; display: inline; }
          .header-dots { border-bottom: 1px dotted #000; display: inline-block; min-width: 200px; }
          table { width: 100%; border-collapse: collapse; font-size: 8px; margin-top: 10px; }
          th, td { border: 1px solid #000; padding: 4px; text-align: left; vertical-align: top; }
          th { background: #f0f0f0; font-weight: bold; text-align: center; }
          .break-row { background: #fff3cd !important; }
          .break-cell { text-align: center; padding: 8px; font-weight: bold; }
          .footer { margin-top: 10px; text-align: center; font-size: 8px; color: #666; }
          .col-week { width: 4%; }
          .col-lsn { width: 3%; }
          .col-strand { width: 10%; }
          .col-substrand { width: 10%; }
          .col-slo { width: 18%; }
          .col-inquiry { width: 15%; }
          .col-exp { width: 15%; }
          .col-res { width: 10%; }
          .col-assess { width: 8%; }
          .col-refl { width: 7%; }
        </style>
      </head>
      <body>
        <div class="title">
          <h1>SCHEMES OF WORK FOR TERM ${generatedScheme.term}</h1>
          <h2>${generatedScheme.gradeName.toUpperCase()} ${generatedScheme.subjectName.toUpperCase()}</h2>
        </div>
        
        <div class="header-info">
          <div class="header-row">
            <div class="header-item">
              <span class="header-label">SCHOOL:</span> 
              <span class="header-dots">${generatedScheme.school}</span>
            </div>
            <div class="header-item">
              <span class="header-label">YEAR:</span> 
              <span class="header-dots">${generatedScheme.year}</span>
            </div>
          </div>
          <div class="header-row">
            <div class="header-item">
              <span class="header-label">NAME OF THE TEACHER:</span> 
              <span class="header-dots">${generatedScheme.teacherName}</span>
            </div>
          </div>
        </div>
        
        <table>
          <thead>
            <tr>
              <th class="col-week">Week</th>
              <th class="col-lsn">LSN</th>
              <th class="col-strand">Strand</th>
              <th class="col-substrand">Sub-strand</th>
              <th class="col-slo">Specific Learning Outcomes</th>
              <th class="col-inquiry">Key Inquiry Question(s)</th>
              <th class="col-exp">Learning Experiences</th>
              <th class="col-res">Learning Resources</th>
              <th class="col-assess">Assessment Methods</th>
              <th class="col-refl">Refl</th>
            </tr>
          </thead>
          <tbody>
            ${lessonsHtml}
          </tbody>
        </table>
        
        <div class="footer">
          <p>Generated by CBE Planner | KICD-Aligned CBC Curriculum | ${new Date().toLocaleDateString()}</p>
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

  const breakTypes = ['Assessment', 'Half-Term', 'Examination', 'Holiday', 'Custom'];
  const durationTypes = [
    { label: 'Lessons', value: 'lessons' },
    { label: 'Fraction of Week', value: 'fraction' },
    { label: 'Weeks', value: 'weeks' }
  ];

  if (generatedScheme) {
    return (
      <SafeAreaView style={styles.container} edges={['bottom']}>
        <ScrollView contentContainerStyle={styles.scrollContent}>
          {/* Scheme Header */}
          <View style={styles.schemeHeader}>
            <Text style={styles.schemeTitle}>Scheme of Work</Text>
            <Text style={styles.schemeSubtitle}>
              {generatedScheme.subjectName} • {generatedScheme.gradeName} • Term {generatedScheme.term}
            </Text>
          </View>

          <View style={styles.schemeMeta}>
            <View style={styles.metaRow}>
              <View style={styles.metaItem}>
                <Text style={styles.metaLabel}>School</Text>
                <Text style={styles.metaValue}>{generatedScheme.school}</Text>
              </View>
              <View style={styles.metaItem}>
                <Text style={styles.metaLabel}>Teacher</Text>
                <Text style={styles.metaValue}>{generatedScheme.teacherName}</Text>
              </View>
            </View>
            <View style={styles.metaRow}>
              <View style={styles.metaItem}>
                <Text style={styles.metaLabel}>Total Weeks</Text>
                <Text style={styles.metaValue}>{generatedScheme.totalWeeks}</Text>
              </View>
              <View style={styles.metaItem}>
                <Text style={styles.metaLabel}>Lessons/Week</Text>
                <Text style={styles.metaValue}>{generatedScheme.lessonsPerWeek}</Text>
              </View>
            </View>
          </View>

          {/* Lessons List */}
          <View style={styles.lessonsContainer}>
            {generatedScheme.lessons.slice(0, 20).map((lesson: any, index: number) => (
              <View 
                key={index} 
                style={[styles.lessonCard, lesson.isBreak && styles.breakCard]}
              >
                {lesson.isBreak ? (
                  <View style={styles.breakContent}>
                    <Ionicons name="pause-circle" size={24} color="#F59E0B" />
                    <Text style={styles.breakTitle}>
                      Week {lesson.week} — {lesson.breakType}
                    </Text>
                    <Text style={styles.breakDescription}>{lesson.breakDescription}</Text>
                  </View>
                ) : (
                  <>
                    <View style={styles.lessonHeader}>
                      <Text style={styles.lessonWeek}>Week {lesson.week}</Text>
                      <Text style={styles.lessonNum}>Lesson {lesson.lessonNumber}</Text>
                    </View>
                    <Text style={styles.lessonStrand}>{lesson.strand}</Text>
                    <Text style={styles.lessonSubstrand}>{lesson.substrand}</Text>
                    <Text style={styles.lessonSlo}>{lesson.slo}</Text>
                  </>
                )}
              </View>
            ))}
            
            {generatedScheme.lessons.length > 20 && (
              <Text style={styles.moreText}>
                + {generatedScheme.lessons.length - 20} more lessons (download PDF for full view)
              </Text>
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
              onPress={() => setGeneratedScheme(null)}
            >
              <Ionicons name="add" size={20} color="#8B5CF6" />
              <Text style={styles.newButtonText}>Create New</Text>
            </TouchableOpacity>
          </View>
        </ScrollView>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container} edges={['bottom']}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Basic Info Card */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Scheme of Work Details</Text>

          <View style={styles.row}>
            <View style={styles.halfInput}>
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
            <View style={styles.halfInput}>
              <Text style={styles.label}>Subject</Text>
              <View style={styles.pickerContainer}>
                <Picker
                  selectedValue={selectedSubject}
                  onValueChange={setSelectedSubject}
                  style={styles.picker}
                  enabled={subjects.length > 0}
                >
                  <Picker.Item label="Select Subject" value="" />
                  {subjects.map((s) => (
                    <Picker.Item key={s.id} label={s.name} value={s.id} />
                  ))}
                </Picker>
              </View>
            </View>
          </View>

          <View style={styles.row}>
            <View style={styles.halfInput}>
              <Text style={styles.label}>Term</Text>
              <View style={styles.pickerContainer}>
                <Picker
                  selectedValue={term}
                  onValueChange={setTerm}
                  style={styles.picker}
                >
                  <Picker.Item label="Term 1" value={1} />
                  <Picker.Item label="Term 2" value={2} />
                  <Picker.Item label="Term 3" value={3} />
                </Picker>
              </View>
            </View>
            <View style={styles.halfInput}>
              <Text style={styles.label}>Year</Text>
              <TextInput
                style={styles.textInput}
                value={year.toString()}
                onChangeText={(text) => setYear(parseInt(text) || new Date().getFullYear())}
                keyboardType="numeric"
              />
            </View>
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.label}>School Name</Text>
            <TextInput
              style={styles.textInput}
              value={school}
              onChangeText={setSchool}
              placeholder="Enter school name"
            />
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.label}>Teacher Name</Text>
            <TextInput
              style={styles.textInput}
              value={teacherName}
              onChangeText={setTeacherName}
              placeholder="Enter teacher name"
            />
          </View>

          <View style={styles.row}>
            <View style={styles.halfInput}>
              <Text style={styles.label}>Total Weeks</Text>
              <TextInput
                style={styles.textInput}
                value={totalWeeks.toString()}
                onChangeText={(text) => setTotalWeeks(parseInt(text) || 14)}
                keyboardType="numeric"
              />
            </View>
            <View style={styles.halfInput}>
              <Text style={styles.label}>Lessons/Week</Text>
              <TextInput
                style={styles.textInput}
                value={lessonsPerWeek.toString()}
                onChangeText={(text) => setLessonsPerWeek(parseInt(text) || 5)}
                keyboardType="numeric"
              />
            </View>
          </View>
        </View>

        {/* Breaks Card */}
        <View style={styles.card}>
          <View style={styles.cardHeader}>
            <Text style={styles.cardTitle}>Breaks & Holidays</Text>
            <TouchableOpacity 
              style={styles.addBreakButton}
              onPress={() => setBreakModalVisible(true)}
            >
              <Ionicons name="add" size={20} color="#FFFFFF" />
            </TouchableOpacity>
          </View>

          {breaks.length === 0 ? (
            <Text style={styles.noBreaksText}>No breaks added. Tap + to add breaks.</Text>
          ) : (
            breaks.map((brk) => (
              <View key={brk.id} style={styles.breakItem}>
                <View style={styles.breakInfo}>
                  <Text style={styles.breakType}>{brk.breakType}</Text>
                  <Text style={styles.breakDetails}>
                    Week {brk.startWeek} • {brk.durationValue} {brk.durationType}
                  </Text>
                </View>
                <TouchableOpacity onPress={() => removeBreak(brk.id)}>
                  <Ionicons name="close-circle" size={24} color="#EF4444" />
                </TouchableOpacity>
              </View>
            ))
          )}
        </View>

        {/* Generate Button */}
        <TouchableOpacity
          style={[styles.generateButton, generating && styles.buttonDisabled]}
          onPress={handleGenerate}
          disabled={generating}
        >
          {generating ? (
            <ActivityIndicator color="#FFFFFF" />
          ) : (
            <>
              <Ionicons name="calendar" size={20} color="#FFFFFF" />
              <Text style={styles.generateButtonText}>Generate Scheme of Work</Text>
            </>
          )}
        </TouchableOpacity>

        {/* Break Modal */}
        <Modal
          visible={breakModalVisible}
          animationType="slide"
          transparent={true}
          onRequestClose={() => setBreakModalVisible(false)}
        >
          <View style={styles.modalOverlay}>
            <View style={styles.modalContent}>
              <View style={styles.modalHeader}>
                <Text style={styles.modalTitle}>Add Break</Text>
                <TouchableOpacity onPress={() => setBreakModalVisible(false)}>
                  <Ionicons name="close" size={24} color="#6B7280" />
                </TouchableOpacity>
              </View>

              <ScrollView style={styles.modalBody}>
                <View style={styles.inputGroup}>
                  <Text style={styles.label}>Break Type</Text>
                  <View style={styles.pickerContainer}>
                    <Picker
                      selectedValue={newBreak.breakType}
                      onValueChange={(val) => setNewBreak({...newBreak, breakType: val})}
                      style={styles.picker}
                    >
                      {breakTypes.map((type) => (
                        <Picker.Item key={type} label={type} value={type} />
                      ))}
                    </Picker>
                  </View>
                </View>

                <View style={styles.row}>
                  <View style={styles.halfInput}>
                    <Text style={styles.label}>Start Week</Text>
                    <TextInput
                      style={styles.textInput}
                      value={newBreak.startWeek?.toString()}
                      onChangeText={(text) => setNewBreak({...newBreak, startWeek: parseInt(text) || 1})}
                      keyboardType="numeric"
                    />
                  </View>
                  <View style={styles.halfInput}>
                    <Text style={styles.label}>Start Lesson (opt)</Text>
                    <TextInput
                      style={styles.textInput}
                      value={newBreak.startLesson?.toString() || ''}
                      onChangeText={(text) => setNewBreak({...newBreak, startLesson: parseInt(text) || undefined})}
                      keyboardType="numeric"
                      placeholder="Optional"
                    />
                  </View>
                </View>

                <View style={styles.inputGroup}>
                  <Text style={styles.label}>Duration Type</Text>
                  <View style={styles.pickerContainer}>
                    <Picker
                      selectedValue={newBreak.durationType}
                      onValueChange={(val) => setNewBreak({...newBreak, durationType: val})}
                      style={styles.picker}
                    >
                      {durationTypes.map((type) => (
                        <Picker.Item key={type.value} label={type.label} value={type.value} />
                      ))}
                    </Picker>
                  </View>
                </View>

                <View style={styles.inputGroup}>
                  <Text style={styles.label}>Duration Value</Text>
                  <TextInput
                    style={styles.textInput}
                    value={newBreak.durationValue?.toString()}
                    onChangeText={(text) => setNewBreak({...newBreak, durationValue: parseFloat(text) || 1})}
                    keyboardType="decimal-pad"
                  />
                </View>

                <View style={styles.inputGroup}>
                  <Text style={styles.label}>Description (optional)</Text>
                  <TextInput
                    style={[styles.textInput, styles.textArea]}
                    value={newBreak.description || ''}
                    onChangeText={(text) => setNewBreak({...newBreak, description: text})}
                    placeholder="e.g., Mid-term break for student assessment"
                    multiline
                  />
                </View>
              </ScrollView>

              <TouchableOpacity style={styles.addButton} onPress={addBreak}>
                <Text style={styles.addButtonText}>Add Break</Text>
              </TouchableOpacity>
            </View>
          </View>
        </Modal>
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
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#111827'
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
  textInput: {
    backgroundColor: '#F9FAFB',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    paddingHorizontal: 16,
    paddingVertical: 14,
    fontSize: 16,
    color: '#111827'
  },
  textArea: {
    minHeight: 80,
    textAlignVertical: 'top'
  },
  row: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 16
  },
  halfInput: {
    flex: 1
  },
  addBreakButton: {
    backgroundColor: '#8B5CF6',
    width: 36,
    height: 36,
    borderRadius: 18,
    justifyContent: 'center',
    alignItems: 'center'
  },
  noBreaksText: {
    fontSize: 14,
    color: '#9CA3AF',
    textAlign: 'center',
    paddingVertical: 20
  },
  breakItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FEF3C7',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8
  },
  breakInfo: {
    flex: 1
  },
  breakType: {
    fontSize: 14,
    fontWeight: '600',
    color: '#92400E'
  },
  breakDetails: {
    fontSize: 12,
    color: '#B45309',
    marginTop: 2
  },
  generateButton: {
    backgroundColor: '#8B5CF6',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 18,
    borderRadius: 12,
    marginBottom: 20
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
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'flex-end'
  },
  modalContent: {
    backgroundColor: '#FFFFFF',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    maxHeight: '80%'
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
    fontSize: 18,
    fontWeight: 'bold',
    color: '#111827'
  },
  modalBody: {
    padding: 16,
    maxHeight: 400
  },
  addButton: {
    backgroundColor: '#8B5CF6',
    margin: 16,
    padding: 16,
    borderRadius: 12,
    alignItems: 'center'
  },
  addButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600'
  },
  // Scheme display styles
  schemeHeader: {
    backgroundColor: '#8B5CF6',
    padding: 20,
    borderRadius: 16,
    marginBottom: 16
  },
  schemeTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FFFFFF'
  },
  schemeSubtitle: {
    fontSize: 14,
    color: '#E9D5FF',
    marginTop: 4
  },
  schemeMeta: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16
  },
  metaRow: {
    flexDirection: 'row',
    marginBottom: 12
  },
  metaItem: {
    flex: 1
  },
  metaLabel: {
    fontSize: 12,
    color: '#6B7280'
  },
  metaValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#111827',
    marginTop: 2
  },
  lessonsContainer: {
    marginBottom: 16
  },
  lessonCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#8B5CF6'
  },
  breakCard: {
    borderLeftColor: '#F59E0B',
    backgroundColor: '#FFFBEB'
  },
  breakContent: {
    alignItems: 'center',
    paddingVertical: 8
  },
  breakTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#92400E',
    marginTop: 8
  },
  breakDescription: {
    fontSize: 12,
    color: '#B45309',
    marginTop: 4
  },
  lessonHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8
  },
  lessonWeek: {
    fontSize: 12,
    fontWeight: '600',
    color: '#8B5CF6'
  },
  lessonNum: {
    fontSize: 12,
    color: '#6B7280'
  },
  lessonStrand: {
    fontSize: 14,
    fontWeight: '600',
    color: '#111827'
  },
  lessonSubstrand: {
    fontSize: 13,
    color: '#374151',
    marginTop: 2
  },
  lessonSlo: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 4,
    fontStyle: 'italic'
  },
  moreText: {
    fontSize: 12,
    color: '#9CA3AF',
    textAlign: 'center',
    paddingVertical: 12
  },
  actionButtons: {
    flexDirection: 'row',
    gap: 12
  },
  downloadButton: {
    flex: 1,
    backgroundColor: '#8B5CF6',
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
    backgroundColor: '#EDE9FE',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
    borderRadius: 12
  },
  newButtonText: {
    color: '#8B5CF6',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8
  }
});
