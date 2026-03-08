import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  TextInput,
  Modal
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../../contexts/AuthContext';
import axios from 'axios';
import * as DocumentPicker from 'expo-document-picker';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

interface PreviewRow {
  row_number: number;
  strand_name: string;
  substrand_name: string;
  slo_name: string;
  slo_description: string;
  introduction_activities: string[];
  development_activities: string[];
  conclusion_activities: string[];
  extended_activities: string[];
  competencies: string[];
  values: string[];
  pcis: string[];
  assessment_methods: string[];
  learning_resources: string[];
}

interface PreviewData {
  rows: PreviewRow[];
  summary: {
    total_rows: number;
    strands: number;
    substrands: number;
    slos: number;
    errors: number;
    warnings: number;
  };
  errors: string[];
  warnings: string[];
}

interface Grade {
  id: string;
  name: string;
}

interface Subject {
  id: string;
  name: string;
  gradeIds: string[];
}

interface ImportHistoryItem {
  id: string;
  filename: string;
  import_type: string;
  grade_name: string;
  subject_name: string;
  stats: {
    strands_created: number;
    substrands_created: number;
    slos_created: number;
    mappings_created: number;
    activities_created: number;
  };
  imported_by: string;
  created_at: string;
}

export default function DataImport() {
  const { firebaseUser } = useAuth();
  
  // State
  const [activeTab, setActiveTab] = useState<'csv' | 'pdf'>('csv');
  const [loading, setLoading] = useState(false);
  const [previewData, setPreviewData] = useState<PreviewData | null>(null);
  const [csvContent, setCsvContent] = useState<string>('');
  const [selectedFile, setSelectedFile] = useState<string>('');
  
  // Grade/Subject selection
  const [grades, setGrades] = useState<Grade[]>([]);
  const [subjects, setSubjects] = useState<Subject[]>([]);
  const [selectedGrade, setSelectedGrade] = useState<string>('');
  const [selectedSubject, setSelectedSubject] = useState<string>('');
  
  // Modal states
  const [showPreviewModal, setShowPreviewModal] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saveResult, setSaveResult] = useState<any>(null);
  
  // Import history
  const [importHistory, setImportHistory] = useState<ImportHistoryItem[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(false);

  const getHeaders = async () => {
    if (firebaseUser) {
      const token = await firebaseUser.getIdToken();
      return { Authorization: `Bearer ${token}` };
    }
    return {};
  };

  // Load grades and subjects
  useEffect(() => {
    loadGradesAndSubjects();
    loadImportHistory();
  }, []);

  const loadGradesAndSubjects = async () => {
    try {
      const headers = await getHeaders();
      const [gradesRes, subjectsRes] = await Promise.all([
        axios.get(`${BACKEND_URL}/api/admin/grades`, { headers }),
        axios.get(`${BACKEND_URL}/api/admin/subjects`, { headers })
      ]);
      setGrades(gradesRes.data.grades || []);
      setSubjects(subjectsRes.data.subjects || []);
    } catch (error) {
      console.error('Error loading grades/subjects:', error);
    }
  };

  const loadImportHistory = async () => {
    setLoadingHistory(true);
    try {
      const headers = await getHeaders();
      const response = await axios.get(`${BACKEND_URL}/api/admin/import/history`, { headers });
      if (response.data.success) {
        setImportHistory(response.data.history || []);
      }
    } catch (error) {
      console.error('Error loading import history:', error);
    } finally {
      setLoadingHistory(false);
    }
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Download CSV template
  const handleDownloadTemplate = async () => {
    try {
      const headers = await getHeaders();
      const response = await axios.get(`${BACKEND_URL}/api/admin/import/template`, {
        headers,
        responseType: 'blob'
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'curriculum_template.csv');
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      alert('Failed to download template');
    }
  };

  // Handle CSV file upload
  const handleCsvUpload = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: ['text/csv', 'text/comma-separated-values', 'application/vnd.ms-excel'],
        copyToCacheDirectory: true
      });
      
      if (result.canceled) return;
      
      const file = result.assets[0];
      setSelectedFile(file.name);
      setLoading(true);
      
      // Read file content
      const response = await fetch(file.uri);
      const text = await response.text();
      
      // Send to backend for parsing
      const headers = await getHeaders();
      const formData = new FormData();
      formData.append('file', {
        uri: file.uri,
        type: 'text/csv',
        name: file.name
      } as any);
      
      const previewResponse = await axios.post(
        `${BACKEND_URL}/api/admin/import/preview-csv`,
        formData,
        { 
          headers: {
            ...headers,
            'Content-Type': 'multipart/form-data'
          }
        }
      );
      
      if (previewResponse.data.success) {
        setPreviewData(previewResponse.data.preview);
        setShowPreviewModal(true);
      }
    } catch (error: any) {
      console.error('Error uploading CSV:', error);
      alert(error.response?.data?.detail || 'Failed to process CSV file');
    } finally {
      setLoading(false);
    }
  };

  // Handle PDF file upload
  const handlePdfUpload = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: ['application/pdf'],
        copyToCacheDirectory: true
      });
      
      if (result.canceled) return;
      
      const file = result.assets[0];
      setSelectedFile(file.name);
      setLoading(true);
      
      const headers = await getHeaders();
      const formData = new FormData();
      formData.append('file', {
        uri: file.uri,
        type: 'application/pdf',
        name: file.name
      } as any);
      
      const extractResponse = await axios.post(
        `${BACKEND_URL}/api/admin/import/extract-pdf`,
        formData,
        { 
          headers: {
            ...headers,
            'Content-Type': 'multipart/form-data'
          }
        }
      );
      
      if (extractResponse.data.success) {
        setPreviewData(extractResponse.data.preview);
        setCsvContent(extractResponse.data.csv_content);
        setShowPreviewModal(true);
      }
    } catch (error: any) {
      console.error('Error extracting PDF:', error);
      alert(error.response?.data?.detail || 'Failed to extract PDF');
    } finally {
      setLoading(false);
    }
  };

  // Download extracted CSV
  const handleDownloadExtractedCsv = () => {
    if (!csvContent) return;
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `extracted_${selectedFile.replace('.pdf', '.csv')}`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  };

  // Save imported data
  const handleSaveImport = async () => {
    if (!selectedGrade || !selectedSubject) {
      alert('Please select a grade and subject first');
      return;
    }
    
    if (!previewData || previewData.rows.length === 0) {
      alert('No data to import');
      return;
    }
    
    setSaving(true);
    try {
      const headers = await getHeaders();
      const response = await axios.post(
        `${BACKEND_URL}/api/admin/import/save`,
        {
          gradeId: selectedGrade,
          subjectId: selectedSubject,
          rows: previewData.rows,
          filename: selectedFile || 'manual_import'
        },
        { headers }
      );
      
      if (response.data.success) {
        setSaveResult(response.data);
        alert(`Import successful!\n\nStrands: ${response.data.stats.strands_created}\nSub-strands: ${response.data.stats.substrands_created}\nSLOs: ${response.data.stats.slos_created}`);
        setShowPreviewModal(false);
        setPreviewData(null);
        setSelectedFile('');
        // Refresh history
        loadImportHistory();
      }
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to save import');
    } finally {
      setSaving(false);
    }
  };

  const filteredSubjects = selectedGrade 
    ? subjects.filter(s => s.gradeIds?.includes(selectedGrade))
    : subjects;

  return (
    <ScrollView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <View style={styles.headerIcon}>
          <Ionicons name="cloud-upload" size={32} color="#6366F1" />
        </View>
        <Text style={styles.headerTitle}>Data Import</Text>
        <Text style={styles.headerSubtitle}>
          Upload curriculum data from CSV files or extract from PDF documents
        </Text>
      </View>

      {/* Tab Selector */}
      <View style={styles.tabContainer}>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'csv' && styles.tabActive]}
          onPress={() => setActiveTab('csv')}
        >
          <Ionicons 
            name="document-text" 
            size={24} 
            color={activeTab === 'csv' ? '#6366F1' : '#6B7280'} 
          />
          <Text style={[styles.tabText, activeTab === 'csv' && styles.tabTextActive]}>
            CSV Upload
          </Text>
          <Text style={styles.tabDesc}>Recommended</Text>
        </TouchableOpacity>
        
        <TouchableOpacity
          style={[styles.tab, activeTab === 'pdf' && styles.tabActive]}
          onPress={() => setActiveTab('pdf')}
        >
          <Ionicons 
            name="document" 
            size={24} 
            color={activeTab === 'pdf' ? '#6366F1' : '#6B7280'} 
          />
          <Text style={[styles.tabText, activeTab === 'pdf' && styles.tabTextActive]}>
            PDF Extract
          </Text>
          <Text style={styles.tabDesc}>Helper Tool</Text>
        </TouchableOpacity>
      </View>

      {/* Content Area */}
      <View style={styles.content}>
        {activeTab === 'csv' ? (
          <View>
            {/* CSV Instructions */}
            <View style={styles.instructionCard}>
              <View style={styles.instructionHeader}>
                <Ionicons name="information-circle" size={24} color="#3B82F6" />
                <Text style={styles.instructionTitle}>How to Use CSV Upload</Text>
              </View>
              <View style={styles.instructionSteps}>
                <Text style={styles.stepText}>
                  <Text style={styles.stepNumber}>1.</Text> Download the CSV template below
                </Text>
                <Text style={styles.stepText}>
                  <Text style={styles.stepNumber}>2.</Text> Fill in your curriculum data (strands, sub-strands, SLOs, activities)
                </Text>
                <Text style={styles.stepText}>
                  <Text style={styles.stepNumber}>3.</Text> Save the file and upload it here
                </Text>
                <Text style={styles.stepText}>
                  <Text style={styles.stepNumber}>4.</Text> Review the preview and save to database
                </Text>
              </View>
              
              <TouchableOpacity style={styles.templateBtn} onPress={handleDownloadTemplate}>
                <Ionicons name="download" size={20} color="#FFFFFF" />
                <Text style={styles.templateBtnText}>Download CSV Template</Text>
              </TouchableOpacity>
            </View>

            {/* CSV Upload Area */}
            <View style={styles.uploadCard}>
              <Text style={styles.uploadTitle}>Upload Your CSV File</Text>
              <Text style={styles.uploadDesc}>
                Select a CSV file containing your curriculum data
              </Text>
              
              <TouchableOpacity 
                style={styles.uploadBtn}
                onPress={handleCsvUpload}
                disabled={loading}
              >
                {loading ? (
                  <ActivityIndicator color="#6366F1" />
                ) : (
                  <>
                    <Ionicons name="cloud-upload" size={32} color="#6366F1" />
                    <Text style={styles.uploadBtnText}>Select CSV File</Text>
                    <Text style={styles.uploadBtnHint}>Click to browse files</Text>
                  </>
                )}
              </TouchableOpacity>
              
              {selectedFile && activeTab === 'csv' && (
                <View style={styles.selectedFile}>
                  <Ionicons name="document-text" size={20} color="#10B981" />
                  <Text style={styles.selectedFileName}>{selectedFile}</Text>
                </View>
              )}
            </View>
          </View>
        ) : (
          <View>
            {/* PDF Instructions */}
            <View style={[styles.instructionCard, { backgroundColor: '#FEF3C7', borderColor: '#F59E0B' }]}>
              <View style={styles.instructionHeader}>
                <Ionicons name="bulb" size={24} color="#F59E0B" />
                <Text style={[styles.instructionTitle, { color: '#92400E' }]}>PDF Extraction Helper</Text>
              </View>
              <Text style={styles.warningText}>
                This tool attempts to extract curriculum data from KICD PDF documents. 
                The extraction may not be 100% accurate - always review and edit the generated CSV before importing.
              </Text>
              <View style={styles.instructionSteps}>
                <Text style={styles.stepText}>
                  <Text style={styles.stepNumber}>1.</Text> Upload a KICD curriculum PDF
                </Text>
                <Text style={styles.stepText}>
                  <Text style={styles.stepNumber}>2.</Text> System extracts strands, sub-strands, SLOs, etc.
                </Text>
                <Text style={styles.stepText}>
                  <Text style={styles.stepNumber}>3.</Text> Download the generated CSV to review/edit
                </Text>
                <Text style={styles.stepText}>
                  <Text style={styles.stepNumber}>4.</Text> Upload the edited CSV using the CSV Upload tab
                </Text>
              </View>
            </View>

            {/* PDF Upload Area */}
            <View style={styles.uploadCard}>
              <Text style={styles.uploadTitle}>Upload KICD Curriculum PDF</Text>
              <Text style={styles.uploadDesc}>
                Select a PDF file to extract curriculum structure
              </Text>
              
              <TouchableOpacity 
                style={styles.uploadBtn}
                onPress={handlePdfUpload}
                disabled={loading}
              >
                {loading ? (
                  <>
                    <ActivityIndicator color="#6366F1" />
                    <Text style={styles.uploadBtnText}>Extracting...</Text>
                    <Text style={styles.uploadBtnHint}>This may take a moment</Text>
                  </>
                ) : (
                  <>
                    <Ionicons name="document" size={32} color="#F59E0B" />
                    <Text style={styles.uploadBtnText}>Select PDF File</Text>
                    <Text style={styles.uploadBtnHint}>KICD curriculum documents</Text>
                  </>
                )}
              </TouchableOpacity>
            </View>
          </View>
        )}

        {/* CSV Column Guide */}
        <View style={styles.guideCard}>
          <Text style={styles.guideTitle}>CSV Column Guide</Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false}>
            <View style={styles.guideTable}>
              <View style={styles.guideRow}>
                <Text style={[styles.guideCell, styles.guideCellHeader]}>Column</Text>
                <Text style={[styles.guideCell, styles.guideCellHeader, { width: 200 }]}>Description</Text>
                <Text style={[styles.guideCell, styles.guideCellHeader]}>Required</Text>
              </View>
              {[
                { col: 'strand_name', desc: 'Main topic/theme (e.g., "Listening and Speaking")', req: 'Yes' },
                { col: 'substrand_name', desc: 'Specific area within strand (e.g., "Comprehension")', req: 'Yes' },
                { col: 'slo_name', desc: 'What learner should achieve', req: 'Yes' },
                { col: 'slo_description', desc: 'Detailed SLO description', req: 'No' },
                { col: 'introduction_activities', desc: 'Opening activities (separate with ;)', req: 'No' },
                { col: 'development_activities', desc: 'Main learning activities', req: 'No' },
                { col: 'conclusion_activities', desc: 'Closing/summary activities', req: 'No' },
                { col: 'competencies', desc: 'Core competencies (e.g., "Critical Thinking; Communication")', req: 'No' },
                { col: 'values', desc: 'Core values (e.g., "Respect; Responsibility")', req: 'No' },
                { col: 'pcis', desc: 'Pertinent issues (e.g., "Life Skills; Citizenship")', req: 'No' },
                { col: 'assessment_methods', desc: 'How to assess (e.g., "Observation; Oral questions")', req: 'No' },
                { col: 'learning_resources', desc: 'Materials needed (e.g., "Textbooks; Charts")', req: 'No' },
              ].map((item, index) => (
                <View key={index} style={styles.guideRow}>
                  <Text style={[styles.guideCell, styles.guideCellCode]}>{item.col}</Text>
                  <Text style={[styles.guideCell, { width: 200 }]}>{item.desc}</Text>
                  <Text style={[styles.guideCell, item.req === 'Yes' ? styles.guideCellReq : styles.guideCellOpt]}>
                    {item.req}
                  </Text>
                </View>
              ))}
            </View>
          </ScrollView>
        </View>
      </View>

      {/* Import History Section */}
      <View style={styles.historySection}>
        <View style={styles.historyHeader}>
          <Ionicons name="time" size={24} color="#6366F1" />
          <Text style={styles.historyTitle}>Import History</Text>
          <TouchableOpacity onPress={loadImportHistory} style={styles.refreshBtn}>
            <Ionicons name="refresh" size={20} color="#6366F1" />
          </TouchableOpacity>
        </View>
        
        {loadingHistory ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="small" color="#6366F1" />
            <Text style={styles.loadingText}>Loading history...</Text>
          </View>
        ) : importHistory.length === 0 ? (
          <View style={styles.emptyHistory}>
            <Ionicons name="folder-open-outline" size={48} color="#D1D5DB" />
            <Text style={styles.emptyHistoryText}>No imports yet</Text>
            <Text style={styles.emptyHistorySubtext}>Your import history will appear here</Text>
          </View>
        ) : (
          <View style={styles.historyList}>
            {importHistory.map((item) => (
              <View key={item.id} style={styles.historyItem}>
                <View style={styles.historyItemLeft}>
                  <View style={styles.historyIconContainer}>
                    <Ionicons 
                      name={item.import_type === 'pdf' ? 'document' : 'document-text'} 
                      size={20} 
                      color="#6366F1" 
                    />
                  </View>
                  <View style={styles.historyItemInfo}>
                    <Text style={styles.historyFilename} numberOfLines={1}>{item.filename}</Text>
                    <Text style={styles.historyMeta}>
                      {item.grade_name} • {item.subject_name}
                    </Text>
                    <Text style={styles.historyDate}>{formatDate(item.created_at)}</Text>
                  </View>
                </View>
                <View style={styles.historyStats}>
                  <View style={styles.historyStatItem}>
                    <Text style={styles.historyStatValue}>{item.stats?.strands_created || 0}</Text>
                    <Text style={styles.historyStatLabel}>Strands</Text>
                  </View>
                  <View style={styles.historyStatItem}>
                    <Text style={styles.historyStatValue}>{item.stats?.substrands_created || 0}</Text>
                    <Text style={styles.historyStatLabel}>Sub-strands</Text>
                  </View>
                  <View style={styles.historyStatItem}>
                    <Text style={styles.historyStatValue}>{item.stats?.slos_created || 0}</Text>
                    <Text style={styles.historyStatLabel}>SLOs</Text>
                  </View>
                </View>
              </View>
            ))}
          </View>
        )}
      </View>

      {/* Preview Modal */}
      <Modal visible={showPreviewModal} animationType="slide" transparent>
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Import Preview</Text>
              <TouchableOpacity onPress={() => setShowPreviewModal(false)}>
                <Ionicons name="close" size={24} color="#6B7280" />
              </TouchableOpacity>
            </View>

            {previewData && (
              <ScrollView style={styles.modalBody}>
                {/* Summary Stats */}
                <View style={styles.summaryCard}>
                  <Text style={styles.summaryTitle}>Data Summary</Text>
                  <View style={styles.summaryGrid}>
                    <View style={styles.summaryItem}>
                      <Text style={styles.summaryValue}>{previewData.summary.strands}</Text>
                      <Text style={styles.summaryLabel}>Strands</Text>
                    </View>
                    <View style={styles.summaryItem}>
                      <Text style={styles.summaryValue}>{previewData.summary.substrands}</Text>
                      <Text style={styles.summaryLabel}>Sub-strands</Text>
                    </View>
                    <View style={styles.summaryItem}>
                      <Text style={styles.summaryValue}>{previewData.summary.slos}</Text>
                      <Text style={styles.summaryLabel}>SLOs</Text>
                    </View>
                  </View>
                </View>

                {/* Errors */}
                {previewData.errors.length > 0 && (
                  <View style={styles.errorCard}>
                    <Text style={styles.errorTitle}>
                      <Ionicons name="alert-circle" size={16} color="#EF4444" /> Errors ({previewData.errors.length})
                    </Text>
                    {previewData.errors.slice(0, 5).map((err, i) => (
                      <Text key={i} style={styles.errorText}>{err}</Text>
                    ))}
                  </View>
                )}

                {/* Warnings */}
                {previewData.warnings.length > 0 && (
                  <View style={styles.warningCard}>
                    <Text style={styles.warningTitle}>
                      <Ionicons name="warning" size={16} color="#F59E0B" /> Warnings ({previewData.warnings.length})
                    </Text>
                    {previewData.warnings.slice(0, 5).map((warn, i) => (
                      <Text key={i} style={styles.warningTextSmall}>{warn}</Text>
                    ))}
                  </View>
                )}

                {/* Grade/Subject Selection */}
                <View style={styles.selectionCard}>
                  <Text style={styles.selectionTitle}>Select Destination</Text>
                  
                  <Text style={styles.selectLabel}>Grade *</Text>
                  <ScrollView horizontal style={styles.selectScroll}>
                    {grades.map((grade) => (
                      <TouchableOpacity
                        key={grade.id}
                        style={[styles.selectChip, selectedGrade === grade.id && styles.selectChipActive]}
                        onPress={() => {
                          setSelectedGrade(grade.id);
                          setSelectedSubject('');
                        }}
                      >
                        <Text style={[styles.selectChipText, selectedGrade === grade.id && styles.selectChipTextActive]}>
                          {grade.name}
                        </Text>
                      </TouchableOpacity>
                    ))}
                  </ScrollView>
                  
                  <Text style={styles.selectLabel}>Subject *</Text>
                  <ScrollView horizontal style={styles.selectScroll}>
                    {filteredSubjects.map((subject) => (
                      <TouchableOpacity
                        key={subject.id}
                        style={[styles.selectChip, selectedSubject === subject.id && styles.selectChipActive]}
                        onPress={() => setSelectedSubject(subject.id)}
                      >
                        <Text style={[styles.selectChipText, selectedSubject === subject.id && styles.selectChipTextActive]}>
                          {subject.name}
                        </Text>
                      </TouchableOpacity>
                    ))}
                  </ScrollView>
                </View>

                {/* Data Preview Table */}
                <View style={styles.previewTableCard}>
                  <Text style={styles.previewTableTitle}>
                    Data Preview (First 10 rows)
                  </Text>
                  <ScrollView horizontal>
                    <View>
                      <View style={styles.previewTableHeader}>
                        <Text style={[styles.previewTableCell, { width: 40 }]}>#</Text>
                        <Text style={[styles.previewTableCell, { width: 150 }]}>Strand</Text>
                        <Text style={[styles.previewTableCell, { width: 150 }]}>Sub-strand</Text>
                        <Text style={[styles.previewTableCell, { width: 250 }]}>SLO</Text>
                        <Text style={[styles.previewTableCell, { width: 120 }]}>Competencies</Text>
                        <Text style={[styles.previewTableCell, { width: 100 }]}>Values</Text>
                        <Text style={[styles.previewTableCell, { width: 100 }]}>PCIs</Text>
                      </View>
                      {previewData.rows.slice(0, 10).map((row, index) => (
                        <View key={index} style={styles.previewTableRow}>
                          <Text style={[styles.previewTableCell, { width: 40 }]}>{row.row_number}</Text>
                          <Text style={[styles.previewTableCell, { width: 150 }]} numberOfLines={2}>{row.strand_name}</Text>
                          <Text style={[styles.previewTableCell, { width: 150 }]} numberOfLines={2}>{row.substrand_name}</Text>
                          <Text style={[styles.previewTableCell, { width: 250 }]} numberOfLines={3}>{row.slo_name}</Text>
                          <Text style={[styles.previewTableCell, { width: 120 }]} numberOfLines={2}>{row.competencies?.join(', ')}</Text>
                          <Text style={[styles.previewTableCell, { width: 100 }]} numberOfLines={2}>{row.values?.join(', ')}</Text>
                          <Text style={[styles.previewTableCell, { width: 100 }]} numberOfLines={2}>{row.pcis?.join(', ')}</Text>
                        </View>
                      ))}
                    </View>
                  </ScrollView>
                </View>

                {/* Download CSV button for PDF extraction */}
                {activeTab === 'pdf' && csvContent && (
                  <TouchableOpacity style={styles.downloadCsvBtn} onPress={handleDownloadExtractedCsv}>
                    <Ionicons name="download" size={20} color="#FFFFFF" />
                    <Text style={styles.downloadCsvBtnText}>Download Extracted CSV for Review</Text>
                  </TouchableOpacity>
                )}
              </ScrollView>
            )}

            {/* Modal Footer */}
            <View style={styles.modalFooter}>
              <TouchableOpacity 
                style={styles.cancelBtn}
                onPress={() => setShowPreviewModal(false)}
              >
                <Text style={styles.cancelBtnText}>Cancel</Text>
              </TouchableOpacity>
              
              <TouchableOpacity 
                style={[
                  styles.saveBtn, 
                  (!selectedGrade || !selectedSubject || saving) && styles.saveBtnDisabled
                ]}
                onPress={handleSaveImport}
                disabled={!selectedGrade || !selectedSubject || saving}
              >
                {saving ? (
                  <ActivityIndicator color="#FFFFFF" size="small" />
                ) : (
                  <>
                    <Ionicons name="save" size={20} color="#FFFFFF" />
                    <Text style={styles.saveBtnText}>Save to Database</Text>
                  </>
                )}
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F3F4F6'
  },
  header: {
    backgroundColor: '#FFFFFF',
    padding: 24,
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB'
  },
  headerIcon: {
    width: 64,
    height: 64,
    borderRadius: 16,
    backgroundColor: '#EEF2FF',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: '#111827'
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#6B7280',
    textAlign: 'center',
    marginTop: 4
  },
  tabContainer: {
    flexDirection: 'row',
    padding: 16,
    gap: 12
  },
  tab: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#E5E7EB'
  },
  tabActive: {
    borderColor: '#6366F1',
    backgroundColor: '#EEF2FF'
  },
  tabText: {
    fontSize: 15,
    fontWeight: '600',
    color: '#6B7280',
    marginTop: 8
  },
  tabTextActive: {
    color: '#6366F1'
  },
  tabDesc: {
    fontSize: 11,
    color: '#9CA3AF',
    marginTop: 2
  },
  content: {
    padding: 16
  },
  instructionCard: {
    backgroundColor: '#EFF6FF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#BFDBFE'
  },
  instructionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    marginBottom: 12
  },
  instructionTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#1E40AF'
  },
  instructionSteps: {
    marginBottom: 16
  },
  stepText: {
    fontSize: 14,
    color: '#374151',
    marginBottom: 8,
    lineHeight: 20
  },
  stepNumber: {
    fontWeight: '700',
    color: '#6366F1'
  },
  warningText: {
    fontSize: 13,
    color: '#92400E',
    lineHeight: 18,
    marginBottom: 12
  },
  templateBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    backgroundColor: '#6366F1',
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 10
  },
  templateBtnText: {
    fontSize: 15,
    fontWeight: '600',
    color: '#FFFFFF'
  },
  uploadCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 20,
    marginBottom: 16,
    alignItems: 'center'
  },
  uploadTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#111827',
    marginBottom: 4
  },
  uploadDesc: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 16
  },
  uploadBtn: {
    width: '100%',
    paddingVertical: 32,
    borderWidth: 2,
    borderColor: '#E5E7EB',
    borderStyle: 'dashed',
    borderRadius: 12,
    alignItems: 'center',
    backgroundColor: '#F9FAFB'
  },
  uploadBtnText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
    marginTop: 8
  },
  uploadBtnHint: {
    fontSize: 13,
    color: '#9CA3AF',
    marginTop: 4
  },
  selectedFile: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginTop: 16,
    padding: 10,
    backgroundColor: '#ECFDF5',
    borderRadius: 8
  },
  selectedFileName: {
    fontSize: 14,
    color: '#059669',
    fontWeight: '500'
  },
  guideCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginTop: 8
  },
  guideTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#111827',
    marginBottom: 12
  },
  guideTable: {
    borderWidth: 1,
    borderColor: '#E5E7EB',
    borderRadius: 8,
    overflow: 'hidden'
  },
  guideRow: {
    flexDirection: 'row',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB'
  },
  guideCell: {
    width: 140,
    padding: 10,
    fontSize: 12,
    color: '#374151'
  },
  guideCellHeader: {
    backgroundColor: '#F3F4F6',
    fontWeight: '700',
    color: '#111827'
  },
  guideCellCode: {
    fontFamily: 'monospace',
    backgroundColor: '#FEF3C7',
    color: '#92400E'
  },
  guideCellReq: {
    color: '#DC2626',
    fontWeight: '600'
  },
  guideCellOpt: {
    color: '#6B7280'
  },
  // Modal styles
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 16
  },
  modalContent: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    width: '100%',
    maxWidth: 800,
    maxHeight: '90%'
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB'
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: '#111827'
  },
  modalBody: {
    padding: 16,
    maxHeight: 500
  },
  summaryCard: {
    backgroundColor: '#EEF2FF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16
  },
  summaryTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#4338CA',
    marginBottom: 12
  },
  summaryGrid: {
    flexDirection: 'row',
    justifyContent: 'space-around'
  },
  summaryItem: {
    alignItems: 'center'
  },
  summaryValue: {
    fontSize: 28,
    fontWeight: '700',
    color: '#4338CA'
  },
  summaryLabel: {
    fontSize: 13,
    color: '#6366F1'
  },
  errorCard: {
    backgroundColor: '#FEF2F2',
    borderRadius: 12,
    padding: 12,
    marginBottom: 12
  },
  errorTitle: {
    fontSize: 14,
    fontWeight: '700',
    color: '#DC2626',
    marginBottom: 8
  },
  errorText: {
    fontSize: 12,
    color: '#B91C1C',
    marginBottom: 4
  },
  warningCard: {
    backgroundColor: '#FFFBEB',
    borderRadius: 12,
    padding: 12,
    marginBottom: 12
  },
  warningTitle: {
    fontSize: 14,
    fontWeight: '700',
    color: '#D97706',
    marginBottom: 8
  },
  warningTextSmall: {
    fontSize: 12,
    color: '#B45309',
    marginBottom: 4
  },
  selectionCard: {
    backgroundColor: '#F9FAFB',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16
  },
  selectionTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#111827',
    marginBottom: 12
  },
  selectLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 8,
    marginTop: 8
  },
  selectScroll: {
    marginBottom: 8
  },
  selectChip: {
    paddingVertical: 8,
    paddingHorizontal: 16,
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    marginRight: 8
  },
  selectChipActive: {
    backgroundColor: '#6366F1',
    borderColor: '#6366F1'
  },
  selectChipText: {
    fontSize: 14,
    color: '#374151'
  },
  selectChipTextActive: {
    color: '#FFFFFF',
    fontWeight: '600'
  },
  previewTableCard: {
    marginBottom: 16
  },
  previewTableTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 8
  },
  previewTableHeader: {
    flexDirection: 'row',
    backgroundColor: '#F3F4F6'
  },
  previewTableRow: {
    flexDirection: 'row',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB'
  },
  previewTableCell: {
    padding: 8,
    fontSize: 12,
    color: '#374151',
    borderRightWidth: 1,
    borderRightColor: '#E5E7EB'
  },
  downloadCsvBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    backgroundColor: '#F59E0B',
    paddingVertical: 12,
    borderRadius: 10,
    marginBottom: 16
  },
  downloadCsvBtnText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#FFFFFF'
  },
  modalFooter: {
    flexDirection: 'row',
    gap: 12,
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB'
  },
  cancelBtn: {
    flex: 1,
    paddingVertical: 14,
    borderRadius: 10,
    backgroundColor: '#F3F4F6',
    alignItems: 'center'
  },
  cancelBtnText: {
    fontSize: 15,
    fontWeight: '600',
    color: '#6B7280'
  },
  saveBtn: {
    flex: 2,
    flexDirection: 'row',
    gap: 8,
    paddingVertical: 14,
    borderRadius: 10,
    backgroundColor: '#10B981',
    alignItems: 'center',
    justifyContent: 'center'
  },
  saveBtnDisabled: {
    backgroundColor: '#A7F3D0'
  },
  saveBtnText: {
    fontSize: 15,
    fontWeight: '600',
    color: '#FFFFFF'
  },
  // Import History Styles
  historySection: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 24,
    borderWidth: 1,
    borderColor: '#E5E7EB'
  },
  historyHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16
  },
  historyTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#111827',
    marginLeft: 8,
    flex: 1
  },
  refreshBtn: {
    padding: 8,
    borderRadius: 8,
    backgroundColor: '#EEF2FF'
  },
  loadingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24
  },
  loadingText: {
    marginLeft: 8,
    fontSize: 14,
    color: '#6B7280'
  },
  emptyHistory: {
    alignItems: 'center',
    padding: 32
  },
  emptyHistoryText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#6B7280',
    marginTop: 12
  },
  emptyHistorySubtext: {
    fontSize: 13,
    color: '#9CA3AF',
    marginTop: 4
  },
  historyList: {
    gap: 12
  },
  historyItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#F9FAFB',
    padding: 12,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#E5E7EB'
  },
  historyItemLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1
  },
  historyIconContainer: {
    width: 40,
    height: 40,
    borderRadius: 8,
    backgroundColor: '#EEF2FF',
    alignItems: 'center',
    justifyContent: 'center'
  },
  historyItemInfo: {
    marginLeft: 12,
    flex: 1
  },
  historyFilename: {
    fontSize: 14,
    fontWeight: '600',
    color: '#111827'
  },
  historyMeta: {
    fontSize: 12,
    color: '#6366F1',
    marginTop: 2
  },
  historyDate: {
    fontSize: 11,
    color: '#9CA3AF',
    marginTop: 2
  },
  historyStats: {
    flexDirection: 'row',
    gap: 12
  },
  historyStatItem: {
    alignItems: 'center',
    paddingHorizontal: 8
  },
  historyStatValue: {
    fontSize: 16,
    fontWeight: '700',
    color: '#10B981'
  },
  historyStatLabel: {
    fontSize: 10,
    color: '#6B7280',
    marginTop: 2
  }
});
