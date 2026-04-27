import React, { useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
  Platform
} from 'react-native';
import { useAuth } from '../../contexts/AuthContext';
import { Ionicons } from '@expo/vector-icons';
import axios from 'axios';
import * as DocumentPicker from 'expo-document-picker';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

interface ProcessingResult {
  filename: string;
  grade: string;
  subject: string;
  pages_processed: number;
  strands_created: number;
  slos_created: number;
}

export default function CurriculumUpload() {
  const { firebaseUser } = useAuth();
  const [selectedFile, setSelectedFile] = useState<any>(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<ProcessingResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const getHeaders = async () => {
    const token = await firebaseUser?.getIdToken();
    return {
      Authorization: `Bearer ${token}`
    };
  };

  const selectFile = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: 'application/pdf',
        copyToCacheDirectory: true
      });
      
      if (result.canceled) {
        return;
      }
      
      const file = result.assets[0];
      
      // Check file size (10MB limit)
      if (file.size && file.size > 10 * 1024 * 1024) {
        Alert.alert('Error', 'File size exceeds 10MB limit');
        return;
      }
      
      setSelectedFile(file);
      setResult(null);
      setError(null);
    } catch (err) {
      Alert.alert('Error', 'Failed to select file');
    }
  };

  const uploadAndProcess = async () => {
    if (!selectedFile) {
      Alert.alert('Error', 'Please select a PDF file first');
      return;
    }

    setUploading(true);
    setError(null);
    setResult(null);

    try {
      const headers = await getHeaders();
      
      // Create form data
      const formData = new FormData();
      
      if (Platform.OS === 'web') {
        // For web, fetch the file and create a Blob
        const response = await fetch(selectedFile.uri);
        const blob = await response.blob();
        formData.append('file', blob, selectedFile.name);
      } else {
        // For native
        formData.append('file', {
          uri: selectedFile.uri,
          name: selectedFile.name,
          type: 'application/pdf'
        } as any);
      }

      const response = await axios.post(
        `${BACKEND_URL}/api/admin/upload-curriculum`,
        formData,
        {
          headers: {
            ...headers,
            'Content-Type': 'multipart/form-data'
          },
          timeout: 300000 // 5 minute timeout for large files
        }
      );

      if (response.data.status === 'success') {
        setResult(response.data.details);
        Alert.alert('Success', 'Curriculum processed successfully!');
      }
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Failed to process curriculum';
      setError(errorMsg);
      Alert.alert('Error', errorMsg);
    } finally {
      setUploading(false);
    }
  };

  const clearSelection = () => {
    setSelectedFile(null);
    setResult(null);
    setError(null);
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <View style={styles.header}>
        <Ionicons name="cloud-upload" size={48} color="#5C6BC0" />
        <Text style={styles.headerTitle}>Curriculum Import</Text>
        <Text style={styles.headerSubtitle}>
          Upload and process curriculum PDFs
        </Text>
      </View>

      <View style={styles.card}>
        <View style={styles.cardHeader}>
          <Ionicons name="document-text" size={24} color="#5C6BC0" />
          <Text style={styles.cardTitle}>Upload PDF</Text>
        </View>
        
        <Text style={styles.cardText}>
          Select a curriculum PDF file to process. The system will extract:
        </Text>
        
        <View style={styles.list}>
          <Text style={styles.listItem}>• Strands and Sub-strands</Text>
          <Text style={styles.listItem}>• Specific Learning Outcomes (SLOs)</Text>
          <Text style={styles.listItem}>• Learning Activities</Text>
          <Text style={styles.listItem}>• Competencies and Values</Text>
        </View>

        <View style={styles.requirements}>
          <Text style={styles.requirementsTitle}>Requirements:</Text>
          <Text style={styles.requirementItem}>• PDF format only</Text>
          <Text style={styles.requirementItem}>• Maximum size: 10MB</Text>
          <Text style={styles.requirementItem}>• KICD curriculum documents recommended</Text>
        </View>
      </View>

      {/* File Selection */}
      <View style={styles.uploadSection}>
        <TouchableOpacity
          style={styles.selectButton}
          onPress={selectFile}
          disabled={uploading}
          data-testid="select-pdf-btn"
        >
          <Ionicons name="folder-open-outline" size={24} color="#5C6BC0" />
          <Text style={styles.selectButtonText}>
            {selectedFile ? 'Change File' : 'Select PDF File'}
          </Text>
        </TouchableOpacity>

        {selectedFile && (
          <View style={styles.selectedFile}>
            <Ionicons name="document" size={20} color="#10B981" />
            <Text style={styles.fileName} numberOfLines={1}>
              {selectedFile.name}
            </Text>
            <TouchableOpacity onPress={clearSelection}>
              <Ionicons name="close-circle" size={20} color="#EF4444" />
            </TouchableOpacity>
          </View>
        )}

        <TouchableOpacity
          style={[
            styles.uploadButton,
            (!selectedFile || uploading) && styles.uploadButtonDisabled
          ]}
          onPress={uploadAndProcess}
          disabled={!selectedFile || uploading}
          data-testid="upload-process-btn"
        >
          {uploading ? (
            <>
              <ActivityIndicator size="small" color="#FFFFFF" />
              <Text style={styles.uploadButtonText}>Processing...</Text>
            </>
          ) : (
            <>
              <Ionicons name="cloud-upload-outline" size={24} color="#FFFFFF" />
              <Text style={styles.uploadButtonText}>Upload and Process</Text>
            </>
          )}
        </TouchableOpacity>
      </View>

      {/* Processing Status */}
      {uploading && (
        <View style={styles.statusCard}>
          <ActivityIndicator size="large" color="#5C6BC0" />
          <Text style={styles.statusTitle}>Processing Curriculum...</Text>
          <Text style={styles.statusText}>
            This may take a few minutes for large documents.
            The AI is extracting curriculum data from each page.
          </Text>
        </View>
      )}

      {/* Result */}
      {result && (
        <View style={styles.resultCard}>
          <View style={styles.resultHeader}>
            <Ionicons name="checkmark-circle" size={32} color="#10B981" />
            <Text style={styles.resultTitle}>Processing Complete!</Text>
          </View>
          
          <View style={styles.resultGrid}>
            <View style={styles.resultItem}>
              <Text style={styles.resultValue}>{result.grade}</Text>
              <Text style={styles.resultLabel}>Grade</Text>
            </View>
            <View style={styles.resultItem}>
              <Text style={styles.resultValue}>{result.subject}</Text>
              <Text style={styles.resultLabel}>Subject</Text>
            </View>
            <View style={styles.resultItem}>
              <Text style={styles.resultValue}>{result.pages_processed}</Text>
              <Text style={styles.resultLabel}>Pages</Text>
            </View>
            <View style={styles.resultItem}>
              <Text style={styles.resultValue}>{result.strands_created}</Text>
              <Text style={styles.resultLabel}>Strands</Text>
            </View>
            <View style={styles.resultItem}>
              <Text style={styles.resultValue}>{result.slos_created}</Text>
              <Text style={styles.resultLabel}>SLOs</Text>
            </View>
          </View>

          <TouchableOpacity
            style={styles.newUploadBtn}
            onPress={clearSelection}
          >
            <Ionicons name="add-circle-outline" size={20} color="#5C6BC0" />
            <Text style={styles.newUploadBtnText}>Upload Another File</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* Error */}
      {error && (
        <View style={styles.errorCard}>
          <Ionicons name="alert-circle" size={24} color="#EF4444" />
          <Text style={styles.errorText}>{error}</Text>
        </View>
      )}

      <View style={styles.developerCredit}>
        <Text style={styles.developerText}>Developed by LEGIT LAB</Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB'
  },
  content: {
    padding: 16,
    paddingBottom: 32
  },
  header: {
    alignItems: 'center',
    paddingVertical: 24,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    marginBottom: 16
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1A1A3A',
    marginTop: 12
  },
  headerSubtitle: {
    fontSize: 14,
    color: '#5A5A7A',
    marginTop: 4
  },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
    gap: 8
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1A1A3A'
  },
  cardText: {
    fontSize: 14,
    color: '#5A5A7A',
    lineHeight: 20,
    marginBottom: 12
  },
  list: {
    marginBottom: 16
  },
  listItem: {
    fontSize: 14,
    color: '#4B5563',
    marginBottom: 4,
    paddingLeft: 8
  },
  requirements: {
    backgroundColor: '#FEF3C7',
    padding: 12,
    borderRadius: 8
  },
  requirementsTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#92400E',
    marginBottom: 8
  },
  requirementItem: {
    fontSize: 13,
    color: '#92400E',
    marginBottom: 2
  },
  uploadSection: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    alignItems: 'center'
  },
  selectButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#F3F4FF',
    paddingVertical: 16,
    paddingHorizontal: 24,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#5C6BC0',
    borderStyle: 'dashed',
    width: '100%',
    gap: 8
  },
  selectButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#5C6BC0'
  },
  selectedFile: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#ECFDF5',
    padding: 12,
    borderRadius: 8,
    marginTop: 12,
    width: '100%',
    gap: 8
  },
  fileName: {
    flex: 1,
    fontSize: 14,
    color: '#065F46'
  },
  uploadButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#5C6BC0',
    paddingVertical: 16,
    paddingHorizontal: 24,
    borderRadius: 12,
    marginTop: 16,
    width: '100%',
    gap: 8
  },
  uploadButtonDisabled: {
    backgroundColor: '#9CA3AF'
  },
  uploadButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFFFFF'
  },
  statusCard: {
    backgroundColor: '#F3F4FF',
    borderRadius: 12,
    padding: 24,
    marginBottom: 16,
    alignItems: 'center'
  },
  statusTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#4338CA',
    marginTop: 12
  },
  statusText: {
    fontSize: 14,
    color: '#5C6BC0',
    textAlign: 'center',
    marginTop: 8,
    lineHeight: 20
  },
  resultCard: {
    backgroundColor: '#ECFDF5',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16
  },
  resultHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
    gap: 8
  },
  resultTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#065F46'
  },
  resultGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-around',
    marginBottom: 16
  },
  resultItem: {
    alignItems: 'center',
    minWidth: 80,
    marginVertical: 8
  },
  resultValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#065F46'
  },
  resultLabel: {
    fontSize: 12,
    color: '#047857',
    marginTop: 2
  },
  newUploadBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#FFFFFF',
    paddingVertical: 12,
    borderRadius: 8,
    gap: 8
  },
  newUploadBtnText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#5C6BC0'
  },
  errorCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FEF2F2',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    gap: 12
  },
  errorText: {
    flex: 1,
    fontSize: 14,
    color: '#991B1B'
  },
  developerCredit: {
    alignItems: 'center',
    marginTop: 16
  },
  developerText: {
    fontSize: 12,
    color: '#9CA3AF'
  }
});
