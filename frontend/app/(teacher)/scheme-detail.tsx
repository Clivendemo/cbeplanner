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
import { useDebouncedAction } from '../../hooks/useDebouncedAction';

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
  // Tracks a deferred download after user is sent to top up their wallet.
  // Lives only as long as the screen stays mounted (expo-router stack keeps
  // it alive while profile is pushed on top). If user abandons (navigates
  // elsewhere / closes browser), the flag is lost — no charge, safe.
  const [pendingDownload, setPendingDownload] = useState(false);

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
      if (err.response?.status === 410) {
        // Scheme auto-expired (24h). Surface a clean message so the UI
        // shows the expired state instead of a generic error.
        setError(
          err.response?.data?.detail ||
          'This scheme has expired. Schemes are automatically removed 24 hours after generation.'
        );
      } else if (err.response?.status === 404) setError('Scheme not found.');
      else setError('Failed to load scheme. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadScheme();
  }, [id]);

  // On focus: refresh balance, then auto-resume download if user topped up.
  useFocusEffect(
    useCallback(() => {
      let cancelled = false;
      (async () => {
        await refreshProfile();
        if (cancelled) return;
        // Small delay so `user.walletBalance` state is updated from context
        setTimeout(() => {
          if (cancelled) return;
          if (pendingDownload) {
            const latestBalance = user?.walletBalance || 0;
            if (latestBalance >= SCHEME_DOWNLOAD_COST) {
              setPendingDownload(false);
              // Resume download automatically — no extra click for the user
              handleDownload();
            }
            // If still insufficient, keep the pending flag; user will see the
            // friendly modal again when they click Download themselves.
          }
        }, 400);
      })();
      return () => { cancelled = true; };
    }, [pendingDownload, user?.walletBalance])
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

  const handleDownload = useDebouncedAction(async () => {
    if (!id || !firebaseUser) return;

    const balance = user?.walletBalance || 0;
    if (balance < SCHEME_DOWNLOAD_COST) {
      const shortfall = SCHEME_DOWNLOAD_COST - balance;
      Alert.alert(
        '🎯 Almost there!',
        `You're just KES ${shortfall} away from downloading your professional Scheme of Work.\n\nTop up your wallet now and we'll continue the download the moment you return — no extra clicks needed.\n\nBalance: KES ${balance} · Cost: KES ${SCHEME_DOWNLOAD_COST}`,
        [
          { text: 'Maybe Later', style: 'cancel' },
          {
            text: 'Top Up & Continue',
            onPress: () => {
              setPendingDownload(true);
              router.push('/(teacher)/profile' as any);
            },
          },
        ],
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
      }
      // Refresh to reflect isPaid/downloadCount
      loadScheme();
    } catch (err: any) {
      if (err.response?.status === 410) {
        Alert.alert(
          'Scheme Expired',
          err.response?.data?.detail ||
          'This scheme has expired. Schemes are automatically removed 24 hours after generation. Please generate a new one.',
          [{ text: 'Generate New', onPress: () => router.replace('/(teacher)/schemes' as any) }]
        );
      } else if (err.response?.status === 402) {
        // Edge case: balance race condition; backend did not charge
        Alert.alert(
          'Balance just changed',
          'Your wallet balance dropped below KES 15 right before the download. No charge was made — please top up and try again.',
          [
            { text: 'Maybe Later', style: 'cancel' },
            {
              text: 'Top Up',
              onPress: () => {
                setPendingDownload(true);
                router.push('/(teacher)/profile' as any);
              },
            },
          ],
        );
      } else {
        Alert.alert(
          'Download Failed',
          'Something went wrong. If your wallet was charged, it has been automatically refunded. Please try again.',
        );
      }
    } finally {
      setDownloading(false);
    }
  }, { leadingGap: 1500 });

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#5C6BC0" />
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

  return (
    <View style={styles.container}>
      {/* Sticky action bar */}
      <View style={styles.actionBar}>
        <TouchableOpacity
          style={[styles.downloadBtn, downloading && styles.downloadBtnDisabled]}
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
          <Ionicons name="create-outline" size={16} color="#5C6BC0" />
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

      {/* In-app scheme preview (no PDF exposed) */}
      <SchemeDisplay scheme={scheme} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#FFFFFF' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 24, backgroundColor: '#F9FAFB' },
  loadingText: { marginTop: 12, fontSize: 14, color: '#5A5A7A' },
  errorText: { fontSize: 16, color: '#374151', textAlign: 'center', marginTop: 16, marginBottom: 24 },
  goBack: { backgroundColor: '#5C6BC0', paddingHorizontal: 24, paddingVertical: 12, borderRadius: 8 },
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
    backgroundColor: '#F3F4FF',
    borderRadius: 8,
  },
  editBtnText: { fontSize: 13, color: '#5C6BC0', fontWeight: '600' },
  deleteBtn: {
    paddingHorizontal: 10,
    paddingVertical: 10,
  },
});
