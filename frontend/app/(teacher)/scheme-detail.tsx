import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ActivityIndicator,
  TouchableOpacity,
  Alert,
  Platform,
} from 'react-native';
import { useAuth } from '../../contexts/AuthContext';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { useFocusEffect } from '@react-navigation/native';
import axios from 'axios';
import { Ionicons } from '@expo/vector-icons';
import * as FileSystem from 'expo-file-system';
import * as Sharing from 'expo-sharing';
import { SchemeDisplay } from '../../components/SchemeDisplay';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;
const SCHEME_DOWNLOAD_COST = 15;

export default function SchemeDetail() {
  const { firebaseUser, user, refreshProfile } = useAuth();
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();

  const [scheme, setScheme] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [downloading, setDownloading] = useState(false);

  const loadScheme = async () => {
    if (!id || !firebaseUser) return;
    try {
      setLoading(true);
      setError(null);
      const token = await firebaseUser.getIdToken();
      const res = await axios.get(`${BACKEND_URL}/api/schemes/${id}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.data?.success) {
        setScheme(res.data.scheme);
      } else {
        setError('Scheme not found.');
      }
    } catch (err: any) {
      if (err.response?.status === 404) setError('Scheme not found.');
      else setError('Failed to load scheme. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadScheme();
  }, [id]);

  // Refresh wallet on focus (after top-up)
  useFocusEffect(
    useCallback(() => {
      refreshProfile();
    }, [])
  );

  const handleEdit = () => {
    if (!scheme?.id && !id) return;
    router.push(`/(teacher)/schemes?editId=${id}` as any);
  };

  const handleDelete = () => {
    Alert.alert(
      'Delete Scheme',
      'Are you sure you want to delete this scheme? This cannot be undone.',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              if (!firebaseUser) return;
              const token = await firebaseUser.getIdToken();
              await axios.delete(`${BACKEND_URL}/api/schemes/${id}`, {
                headers: { Authorization: `Bearer ${token}` },
              });
              router.back();
            } catch {
              Alert.alert('Error', 'Failed to delete scheme.');
            }
          },
        },
      ]
    );
  };

  const handleDownload = async () => {
    if (!id || !firebaseUser) return;

    const balance = user?.walletBalance || 0;
    if (balance < SCHEME_DOWNLOAD_COST) {
      Alert.alert(
        'Top Up Required',
        `You need KES ${SCHEME_DOWNLOAD_COST - balance} more to download this scheme.\n\nBalance: KES ${balance}\nCost: KES ${SCHEME_DOWNLOAD_COST}`,
        [
          { text: 'Maybe Later', style: 'cancel' },
          {
            text: 'Top Up Wallet',
            onPress: () => router.push('/(teacher)/profile' as any),
          },
        ]
      );
      return;
    }

    setDownloading(true);
    try {
      const token = await firebaseUser.getIdToken();
      const url = `${BACKEND_URL}/api/schemes/${id}/download`;

      if (Platform.OS === 'web') {
        const response = await axios.post(url, {}, {
          headers: { Authorization: `Bearer ${token}` },
          responseType: 'blob',
        });
        const blob = new Blob([response.data], { type: 'application/pdf' });
        const blobUrl = URL.createObjectURL(blob);
        const subject = (scheme?.subjectName || 'Subject').replace(/\s+/g, '_');
        const grade = (scheme?.gradeName || 'Grade').replace(/\s+/g, '_');
        const filename = `Scheme_${subject}_${grade}_Term${scheme?.term || 1}.pdf`;
        const a = document.createElement('a');
        a.href = blobUrl;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(blobUrl);
        await refreshProfile();
        Alert.alert('Success', `Scheme downloaded. KES ${SCHEME_DOWNLOAD_COST} deducted from wallet.`);
      } else {
        const subject = (scheme?.subjectName || 'Subject').replace(/\s+/g, '_');
        const grade = (scheme?.gradeName || 'Grade').replace(/\s+/g, '_');
        const filename = `Scheme_${subject}_${grade}_Term${scheme?.term || 1}.pdf`;
        const fileUri = `${FileSystem.cacheDirectory}${filename}`;
        const dl = await FileSystem.downloadAsync(url, fileUri, {
          httpMethod: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({}),
        });
        if (dl.status !== 200) throw new Error('Download failed');
        const canShare = await Sharing.isAvailableAsync();
        if (canShare) {
          await Sharing.shareAsync(dl.uri, {
            mimeType: 'application/pdf',
            dialogTitle: 'Save / Share Scheme PDF',
            UTI: 'com.adobe.pdf',
          });
        }
        await refreshProfile();
        Alert.alert('Success', `Scheme downloaded. KES ${SCHEME_DOWNLOAD_COST} deducted from wallet.`);
      }
      // Refresh to reflect isPaid/downloadCount
      loadScheme();
    } catch (err: any) {
      if (err.response?.status === 402) {
        Alert.alert(
          'Insufficient Balance',
          'Please top up your wallet to download this scheme.',
          [
            { text: 'Maybe Later', style: 'cancel' },
            { text: 'Top Up', onPress: () => router.push('/(teacher)/profile' as any) },
          ]
        );
      } else {
        Alert.alert('Download Failed', 'Please try again. If the problem persists, no charge was applied.');
      }
    } finally {
      setDownloading(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#6366F1" />
        <Text style={styles.loadingText}>Loading scheme...</Text>
      </View>
    );
  }

  if (error || !scheme) {
    return (
      <View style={styles.center}>
        <Ionicons name="alert-circle-outline" size={64} color="#EF4444" />
        <Text style={styles.errorText}>{error || 'No scheme data.'}</Text>
        <TouchableOpacity style={styles.goBack} onPress={() => router.back()}>
          <Text style={styles.goBackText}>Go Back</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const balance = user?.walletBalance || 0;
  const canAfford = balance >= SCHEME_DOWNLOAD_COST;

  return (
    <View style={styles.container}>
      {/* Sticky action bar */}
      <View style={styles.actionBar}>
        <TouchableOpacity
          style={[styles.downloadBtn, (downloading || !canAfford) && styles.downloadBtnDisabled]}
          onPress={handleDownload}
          disabled={downloading}
          data-testid="scheme-detail-download-btn"
        >
          {downloading ? (
            <ActivityIndicator size={14} color="#FFFFFF" />
          ) : (
            <Ionicons name="download-outline" size={16} color="#FFFFFF" />
          )}
          <Text style={styles.downloadBtnText}>
            {downloading ? 'Downloading…' : `Download PDF (KES ${SCHEME_DOWNLOAD_COST})`}
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.editBtn}
          onPress={handleEdit}
          data-testid="scheme-detail-edit-btn"
        >
          <Ionicons name="create-outline" size={16} color="#6366F1" />
          <Text style={styles.editBtnText}>Edit</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.deleteBtn}
          onPress={handleDelete}
          data-testid="scheme-detail-delete-btn"
        >
          <Ionicons name="trash-outline" size={16} color="#EF4444" />
        </TouchableOpacity>
      </View>

      {!canAfford && (
        <View style={styles.insufficientBar} data-testid="scheme-detail-insufficient-bar">
          <Ionicons name="alert-circle" size={16} color="#B45309" />
          <Text style={styles.insufficientText}>
            KES {SCHEME_DOWNLOAD_COST - balance} more needed · Balance KES {balance}
          </Text>
          <TouchableOpacity
            onPress={() => router.push('/(teacher)/profile' as any)}
            data-testid="scheme-detail-topup-btn"
          >
            <Text style={styles.topupLink}>Top Up</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* In-app scheme preview (no PDF exposed) */}
      <SchemeDisplay scheme={scheme} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#FFFFFF' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 24, backgroundColor: '#F9FAFB' },
  loadingText: { marginTop: 12, fontSize: 14, color: '#6B7280' },
  errorText: { fontSize: 16, color: '#374151', textAlign: 'center', marginTop: 16, marginBottom: 24 },
  goBack: { backgroundColor: '#6366F1', paddingHorizontal: 24, paddingVertical: 12, borderRadius: 8 },
  goBackText: { color: '#FFFFFF', fontSize: 14, fontWeight: '600' },
  actionBar: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
    gap: 10,
    backgroundColor: '#FFFFFF',
  },
  downloadBtn: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 6,
    backgroundColor: '#10B981',
    paddingVertical: 10,
    paddingHorizontal: 12,
    borderRadius: 8,
  },
  downloadBtnDisabled: { opacity: 0.6 },
  downloadBtnText: { color: '#FFFFFF', fontSize: 13, fontWeight: '700' },
  editBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    paddingHorizontal: 12,
    paddingVertical: 10,
    backgroundColor: '#EEF2FF',
    borderRadius: 8,
  },
  editBtnText: { fontSize: 13, color: '#6366F1', fontWeight: '600' },
  deleteBtn: {
    paddingHorizontal: 10,
    paddingVertical: 10,
  },
  insufficientBar: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    paddingHorizontal: 14,
    paddingVertical: 8,
    backgroundColor: '#FFFBEB',
    borderBottomWidth: 1,
    borderBottomColor: '#FDE68A',
  },
  insufficientText: { flex: 1, fontSize: 12, color: '#92400E', fontWeight: '500' },
  topupLink: { fontSize: 12, color: '#D97706', fontWeight: '700', textDecorationLine: 'underline' },
});
