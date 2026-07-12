import React, { useCallback, useEffect, useState } from 'react';
import {
  View, Text, ScrollView, TouchableOpacity, StyleSheet,
  ActivityIndicator, TextInput, Modal, Platform, Switch, Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import axios from 'axios';
import { useAuth } from '../../contexts/AuthContext';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

interface NewsDoc {
  id: string;
  tag: string;
  text: string;
  active: boolean;
  order: number;
}

function confirmDelete(message: string): Promise<boolean> {
  if (Platform.OS === 'web') {
    return Promise.resolve(typeof window !== 'undefined' ? window.confirm(message) : false);
  }
  return new Promise((resolve) => {
    Alert.alert('Delete', message, [
      { text: 'Cancel', style: 'cancel', onPress: () => resolve(false) },
      { text: 'Delete', style: 'destructive', onPress: () => resolve(true) },
    ]);
  });
}

export default function NewsAdminScreen() {
  const { firebaseUser } = useAuth();
  const [items, setItems] = useState<NewsDoc[]>([]);
  const [loading, setLoading] = useState(true);
  const [modal, setModal] = useState<NewsDoc | null>(null);

  const authHeaders = useCallback(async () => {
    if (!firebaseUser) return {};
    const token = await firebaseUser.getIdToken();
    return { Authorization: `Bearer ${token}` };
  }, [firebaseUser]);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const headers = await authHeaders();
      const res = await axios.get(`${BACKEND_URL}/api/admin/news`, { headers });
      setItems(res.data.news || []);
    } catch (e) {
      console.error('Failed to load news', e);
    } finally {
      setLoading(false);
    }
  }, [authHeaders]);

  useEffect(() => { load(); }, [load]);

  const save = async (draft: NewsDoc) => {
    const headers = await authHeaders();
    const body = {
      tag: draft.tag.trim(),
      text: draft.text.trim(),
      active: draft.active,
      order: draft.order,
    };
    try {
      if (draft.id) {
        await axios.put(`${BACKEND_URL}/api/admin/news/${draft.id}`, body, { headers });
      } else {
        await axios.post(`${BACKEND_URL}/api/admin/news`, body, { headers });
      }
      setModal(null);
      await load();
    } catch (e: any) {
      Alert.alert('Save failed', e?.response?.data?.detail || e?.message || 'Unknown error');
    }
  };

  const toggleActive = async (item: NewsDoc) => {
    try {
      const headers = await authHeaders();
      await axios.put(`${BACKEND_URL}/api/admin/news/${item.id}`, {
        tag: item.tag, text: item.text, active: !item.active, order: item.order,
      }, { headers });
      await load();
    } catch (e: any) {
      Alert.alert('Update failed', e?.response?.data?.detail || e?.message || 'Unknown error');
    }
  };

  const remove = async (item: NewsDoc) => {
    const ok = await confirmDelete(`Delete news item "${item.tag}"?`);
    if (!ok) return;
    try {
      const headers = await authHeaders();
      await axios.delete(`${BACKEND_URL}/api/admin/news/${item.id}`, { headers });
      await load();
    } catch (e: any) {
      Alert.alert('Delete failed', e?.response?.data?.detail || e?.message || 'Unknown error');
    }
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#F59E0B" />
        <Text style={styles.muted}>Loading announcements…</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollBody}>
        <View style={styles.sectionHeader}>
          <View>
            <Text style={styles.sectionTitle}>News Strip Announcements</Text>
            <Text style={styles.muted}>Drives the marquee at the top of every page.</Text>
          </View>
          <TouchableOpacity
            onPress={() => setModal({ id: '', tag: '', text: '', active: true, order: items.length + 1 })}
            style={styles.addBtn}
            data-testid="news-add"
          >
            <Ionicons name="add" size={16} color="#FFFFFF" />
            <Text style={styles.addBtnText}>Add News</Text>
          </TouchableOpacity>
        </View>

        {items.length === 0 ? (
          <Text style={styles.muted}>No announcements yet. Defaults + calendar events still scroll.</Text>
        ) : items.map((n) => (
          <View key={n.id} style={[styles.listCard, !n.active && { opacity: 0.55 }]}>
            <View style={styles.tagPill}>
              <Text style={styles.tagPillText}>{n.tag}</Text>
            </View>
            <View style={{ flex: 1 }}>
              <Text style={styles.cardTitle} numberOfLines={2}>{n.text}</Text>
              <Text style={styles.cardSubtle}>Order {n.order} · {n.active ? 'Live' : 'Hidden'}</Text>
            </View>
            <Switch
              value={n.active}
              onValueChange={() => toggleActive(n)}
              data-testid={`news-toggle-${n.id}`}
            />
            <TouchableOpacity onPress={() => setModal(n)} style={styles.iconBtn} data-testid={`news-edit-${n.id}`}>
              <Ionicons name="pencil" size={16} color="#5C6BC0" />
            </TouchableOpacity>
            <TouchableOpacity onPress={() => remove(n)} style={styles.iconBtn} data-testid={`news-delete-${n.id}`}>
              <Ionicons name="trash" size={16} color="#EF4444" />
            </TouchableOpacity>
          </View>
        ))}
      </ScrollView>

      {modal && (
        <NewsEditorModal
          draft={modal}
          onCancel={() => setModal(null)}
          onSave={save}
        />
      )}
    </View>
  );
}

const NewsEditorModal: React.FC<{
  draft: NewsDoc;
  onCancel: () => void;
  onSave: (d: NewsDoc) => void;
}> = ({ draft, onCancel, onSave }) => {
  const [state, setState] = useState<NewsDoc>(draft);
  const canSave = state.tag.trim().length > 0 && state.text.trim().length > 0;

  return (
    <Modal transparent animationType="fade" visible>
      <View style={styles.backdrop}>
        <View style={styles.modalCard}>
          <Text style={styles.modalTitle}>{draft.id ? 'Edit Announcement' : 'Add Announcement'}</Text>

          <Text style={styles.fieldLabel}>Tag (short label) *</Text>
          <TextInput
            style={styles.input}
            value={state.tag}
            placeholder="MoE / KNEC / KICD / Update / Tip"
            maxLength={16}
            onChangeText={(v) => setState({ ...state, tag: v })}
            data-testid="news-tag"
          />

          <Text style={styles.fieldLabel}>Message *</Text>
          <TextInput
            style={[styles.input, { minHeight: 70 }]}
            value={state.text}
            multiline
            placeholder="CBC reforms update released by Ministry of Education"
            onChangeText={(v) => setState({ ...state, text: v })}
            data-testid="news-text"
          />

          <View style={{ flexDirection: 'row', alignItems: 'center', gap: 10, marginTop: 10 }}>
            <Text style={styles.fieldLabel}>Active</Text>
            <Switch
              value={state.active}
              onValueChange={(v) => setState({ ...state, active: v })}
              data-testid="news-active"
            />
          </View>

          <Text style={styles.fieldLabel}>Order</Text>
          <TextInput
            style={styles.input}
            value={String(state.order)}
            keyboardType="number-pad"
            onChangeText={(v) => setState({ ...state, order: parseInt(v || '0', 10) || 0 })}
            data-testid="news-order"
          />

          <View style={styles.modalFooter}>
            <TouchableOpacity onPress={onCancel} style={[styles.modalBtn, { backgroundColor: '#DDDDF5' }]} data-testid="news-cancel">
              <Text style={[styles.modalBtnText, { color: '#374151' }]}>Cancel</Text>
            </TouchableOpacity>
            <TouchableOpacity
              onPress={() => canSave && onSave(state)}
              style={[styles.modalBtn, !canSave && { opacity: 0.5 }]}
              disabled={!canSave}
              data-testid="news-save"
            >
              <Text style={styles.modalBtnText}>Save</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: 'transparent' },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  muted: { color: '#5A5A7A', fontSize: 13, marginTop: 4 },

  scrollBody: { padding: 16, paddingBottom: 80 },
  sectionHeader: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    marginBottom: 14,
  },
  sectionTitle: { fontSize: 16, fontWeight: '700', color: '#1A1A3A' },
  addBtn: {
    flexDirection: 'row', alignItems: 'center', gap: 6,
    backgroundColor: '#5C6BC0', paddingHorizontal: 12, paddingVertical: 8,
    borderRadius: 8,
  },
  addBtnText: { color: '#FFFFFF', fontSize: 13, fontWeight: '600' },

  listCard: {
    flexDirection: 'row', alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 10, borderWidth: 1, borderColor: '#DDDDF5',
    padding: 12, marginBottom: 10, gap: 10,
  },
  tagPill: {
    backgroundColor: '#F3F4FF',
    paddingHorizontal: 8, paddingVertical: 4,
    borderRadius: 12,
  },
  tagPillText: { color: '#5C6BC0', fontSize: 11, fontWeight: '700' },
  cardTitle: { fontSize: 13, color: '#1A1A3A' },
  cardSubtle: { fontSize: 11, color: '#5A5A7A', marginTop: 3 },
  iconBtn: { padding: 6 },

  backdrop: { flex: 1, backgroundColor: 'rgba(0,0,0,0.4)', alignItems: 'center', justifyContent: 'center', padding: 16 },
  modalCard: {
    width: '100%', maxWidth: 500, backgroundColor: '#FFFFFF', borderRadius: 12,
    padding: 20,
  },
  modalTitle: { fontSize: 16, fontWeight: '700', color: '#1A1A3A', marginBottom: 12 },
  fieldLabel: { fontSize: 12, fontWeight: '600', color: '#374151', marginTop: 8, marginBottom: 4 },
  input: {
    borderWidth: 1, borderColor: '#D1D5DB', borderRadius: 8,
    paddingHorizontal: 10, paddingVertical: 8, fontSize: 13,
    backgroundColor: '#FFFFFF', color: '#1A1A3A',
  },
  modalFooter: {
    flexDirection: 'row', justifyContent: 'flex-end', gap: 8, marginTop: 18,
  },
  modalBtn: {
    backgroundColor: '#5C6BC0', paddingHorizontal: 16, paddingVertical: 10,
    borderRadius: 8, alignItems: 'center', justifyContent: 'center',
  },
  modalBtnText: { color: '#FFFFFF', fontSize: 13, fontWeight: '600' },
});
