import React, { useCallback, useEffect, useMemo, useState } from 'react';
import {
  View, Text, ScrollView, TouchableOpacity, StyleSheet,
  ActivityIndicator, TextInput, Modal, Platform, Pressable, Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import axios from 'axios';
import { useAuth } from '../../contexts/AuthContext';
import { invalidateCalendarCache } from '../../components/useCalendarData';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

// ===== Types =====
interface EventDoc {
  id: string;
  date: string;      // YYYY-MM-DD
  title: string;
  category: 'academic' | 'cocurricular' | 'exam';
  order: number;
  palette?: { bg: string; tc: string; dot: string };
}

interface TermActivityDoc { label: string; date: string; }
interface TermDoc {
  id: string;
  name: string;
  period: string;
  status: 'past' | 'current' | 'upcoming';
  year: number;
  academic: TermActivityDoc[];
  cocurricular: TermActivityDoc[];
  order: number;
}

const CATEGORIES: { value: EventDoc['category']; label: string; color: string }[] = [
  { value: 'academic', label: 'Academic', color: '#5C6BC0' },
  { value: 'cocurricular', label: 'Co-curricular', color: '#16A34A' },
  { value: 'exam', label: 'Exam', color: '#EA580C' },
];

const STATUSES: { value: TermDoc['status']; label: string; color: string }[] = [
  { value: 'past', label: 'Past', color: '#9CA3AF' },
  { value: 'current', label: 'Current', color: '#3730A3' },
  { value: 'upcoming', label: 'Upcoming', color: '#166534' },
];

// Tiny inline alert helper for web
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

export default function CalendarAdminScreen() {
  const { firebaseUser } = useAuth();
  const [tab, setTab] = useState<'events' | 'terms'>('events');

  const [events, setEvents] = useState<EventDoc[]>([]);
  const [terms, setTerms] = useState<TermDoc[]>([]);
  const [loading, setLoading] = useState(true);

  const [eventModal, setEventModal] = useState<EventDoc | null>(null);
  const [termModal, setTermModal] = useState<TermDoc | null>(null);

  const authHeaders = useCallback(async () => {
    if (!firebaseUser) return {};
    const token = await firebaseUser.getIdToken();
    return { Authorization: `Bearer ${token}` };
  }, [firebaseUser]);

  const loadAll = useCallback(async () => {
    setLoading(true);
    try {
      const [ev, tm] = await Promise.all([
        axios.get(`${BACKEND_URL}/api/calendar/events`),
        axios.get(`${BACKEND_URL}/api/calendar/terms`),
      ]);
      setEvents(ev.data.events || []);
      setTerms(tm.data.terms || []);
    } catch (e) {
      console.error('Failed to load calendar data', e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadAll();
  }, [loadAll]);

  // ===== Event CRUD =====
  const saveEvent = async (draft: EventDoc) => {
    const headers = await authHeaders();
    const body = {
      date: draft.date,
      title: draft.title.trim(),
      category: draft.category,
      order: draft.order,
    };
    try {
      if (draft.id) {
        await axios.put(`${BACKEND_URL}/api/admin/calendar/events/${draft.id}`, body, { headers });
      } else {
        await axios.post(`${BACKEND_URL}/api/admin/calendar/events`, body, { headers });
      }
      invalidateCalendarCache();
      setEventModal(null);
      await loadAll();
    } catch (e: any) {
      Alert.alert('Save failed', e?.response?.data?.detail || e?.message || 'Unknown error');
    }
  };

  const deleteEvent = async (ev: EventDoc) => {
    const ok = await confirmDelete(`Delete event "${ev.title}"?`);
    if (!ok) return;
    try {
      const headers = await authHeaders();
      await axios.delete(`${BACKEND_URL}/api/admin/calendar/events/${ev.id}`, { headers });
      invalidateCalendarCache();
      await loadAll();
    } catch (e: any) {
      Alert.alert('Delete failed', e?.response?.data?.detail || e?.message || 'Unknown error');
    }
  };

  // ===== Term CRUD =====
  const saveTerm = async (draft: TermDoc) => {
    const headers = await authHeaders();
    const body = {
      name: draft.name.trim(),
      period: draft.period.trim(),
      status: draft.status,
      year: draft.year,
      academic: draft.academic,
      cocurricular: draft.cocurricular,
      order: draft.order,
    };
    try {
      if (draft.id) {
        await axios.put(`${BACKEND_URL}/api/admin/calendar/terms/${draft.id}`, body, { headers });
      } else {
        await axios.post(`${BACKEND_URL}/api/admin/calendar/terms`, body, { headers });
      }
      invalidateCalendarCache();
      setTermModal(null);
      await loadAll();
    } catch (e: any) {
      Alert.alert('Save failed', e?.response?.data?.detail || e?.message || 'Unknown error');
    }
  };

  const deleteTerm = async (tm: TermDoc) => {
    const ok = await confirmDelete(`Delete term "${tm.name}"?`);
    if (!ok) return;
    try {
      const headers = await authHeaders();
      await axios.delete(`${BACKEND_URL}/api/admin/calendar/terms/${tm.id}`, { headers });
      invalidateCalendarCache();
      await loadAll();
    } catch (e: any) {
      Alert.alert('Delete failed', e?.response?.data?.detail || e?.message || 'Unknown error');
    }
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#F59E0B" />
        <Text style={styles.muted}>Loading calendar…</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Tab switcher */}
      <View style={styles.tabsRow}>
        <TouchableOpacity
          data-testid="cal-tab-events"
          style={[styles.tabBtn, tab === 'events' && styles.tabBtnActive]}
          onPress={() => setTab('events')}
        >
          <Ionicons name="calendar-outline" size={16} color={tab === 'events' ? '#FFFFFF' : '#5A5A7A'} />
          <Text style={[styles.tabBtnText, tab === 'events' && styles.tabBtnTextActive]}>
            Upcoming Events ({events.length})
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          data-testid="cal-tab-terms"
          style={[styles.tabBtn, tab === 'terms' && styles.tabBtnActive]}
          onPress={() => setTab('terms')}
        >
          <Ionicons name="school-outline" size={16} color={tab === 'terms' ? '#FFFFFF' : '#5A5A7A'} />
          <Text style={[styles.tabBtnText, tab === 'terms' && styles.tabBtnTextActive]}>
            Term Calendar ({terms.length})
          </Text>
        </TouchableOpacity>
      </View>

      {tab === 'events' ? (
        <EventsPanel
          events={events}
          onAdd={() => setEventModal({ id: '', date: toIsoToday(), title: '', category: 'academic', order: events.length + 1 })}
          onEdit={setEventModal}
          onDelete={deleteEvent}
        />
      ) : (
        <TermsPanel
          terms={terms}
          onAdd={() => setTermModal(blankTerm(terms.length + 1))}
          onEdit={setTermModal}
          onDelete={deleteTerm}
        />
      )}

      {eventModal && (
        <EventEditorModal
          draft={eventModal}
          onCancel={() => setEventModal(null)}
          onSave={saveEvent}
        />
      )}
      {termModal && (
        <TermEditorModal
          draft={termModal}
          onCancel={() => setTermModal(null)}
          onSave={saveTerm}
        />
      )}
    </View>
  );
}

// ===== Events panel =====

const EventsPanel: React.FC<{
  events: EventDoc[];
  onAdd: () => void;
  onEdit: (e: EventDoc) => void;
  onDelete: (e: EventDoc) => void;
}> = ({ events, onAdd, onEdit, onDelete }) => (
  <ScrollView contentContainerStyle={styles.scrollBody}>
    <View style={styles.sectionHeader}>
      <Text style={styles.sectionTitle}>Upcoming Events</Text>
      <TouchableOpacity onPress={onAdd} style={styles.addBtn} data-testid="cal-add-event">
        <Ionicons name="add" size={16} color="#FFFFFF" />
        <Text style={styles.addBtnText}>Add Event</Text>
      </TouchableOpacity>
    </View>

    {events.length === 0 ? (
      <Text style={styles.muted}>No events yet. Tap "Add Event" to create one.</Text>
    ) : (
      events.map((ev) => {
        const cat = CATEGORIES.find((c) => c.value === ev.category);
        return (
          <View key={ev.id} style={styles.listCard}>
            <View style={[styles.colourStrip, { backgroundColor: cat?.color || '#5A5A7A' }]} />
            <View style={{ flex: 1 }}>
              <Text style={styles.cardTitle}>{ev.title}</Text>
              <Text style={styles.cardSubtle}>{formatIsoForDisplay(ev.date)} · {cat?.label}</Text>
            </View>
            <TouchableOpacity onPress={() => onEdit(ev)} style={styles.iconBtn} data-testid={`cal-edit-event-${ev.id}`}>
              <Ionicons name="pencil" size={16} color="#5C6BC0" />
            </TouchableOpacity>
            <TouchableOpacity onPress={() => onDelete(ev)} style={styles.iconBtn} data-testid={`cal-delete-event-${ev.id}`}>
              <Ionicons name="trash" size={16} color="#EF4444" />
            </TouchableOpacity>
          </View>
        );
      })
    )}
  </ScrollView>
);

// ===== Terms panel =====

const TermsPanel: React.FC<{
  terms: TermDoc[];
  onAdd: () => void;
  onEdit: (t: TermDoc) => void;
  onDelete: (t: TermDoc) => void;
}> = ({ terms, onAdd, onEdit, onDelete }) => (
  <ScrollView contentContainerStyle={styles.scrollBody}>
    <View style={styles.sectionHeader}>
      <Text style={styles.sectionTitle}>Term Calendar</Text>
      <TouchableOpacity onPress={onAdd} style={styles.addBtn} data-testid="cal-add-term">
        <Ionicons name="add" size={16} color="#FFFFFF" />
        <Text style={styles.addBtnText}>Add Term</Text>
      </TouchableOpacity>
    </View>

    {terms.length === 0 ? (
      <Text style={styles.muted}>No terms yet. Tap "Add Term" to create one.</Text>
    ) : (
      terms.map((tm) => {
        const st = STATUSES.find((s) => s.value === tm.status);
        return (
          <View key={tm.id} style={styles.listCard}>
            <View style={[styles.colourStrip, { backgroundColor: st?.color || '#5A5A7A' }]} />
            <View style={{ flex: 1 }}>
              <Text style={styles.cardTitle}>{tm.name} · {tm.year}</Text>
              <Text style={styles.cardSubtle}>
                {tm.period} · {st?.label} · {tm.academic.length} academic, {tm.cocurricular.length} co-curr
              </Text>
            </View>
            <TouchableOpacity onPress={() => onEdit(tm)} style={styles.iconBtn} data-testid={`cal-edit-term-${tm.id}`}>
              <Ionicons name="pencil" size={16} color="#5C6BC0" />
            </TouchableOpacity>
            <TouchableOpacity onPress={() => onDelete(tm)} style={styles.iconBtn} data-testid={`cal-delete-term-${tm.id}`}>
              <Ionicons name="trash" size={16} color="#EF4444" />
            </TouchableOpacity>
          </View>
        );
      })
    )}
  </ScrollView>
);

// ===== Event editor modal =====

const EventEditorModal: React.FC<{
  draft: EventDoc;
  onCancel: () => void;
  onSave: (e: EventDoc) => void;
}> = ({ draft, onCancel, onSave }) => {
  const [state, setState] = useState<EventDoc>(draft);

  const canSave = state.title.trim().length > 0 && /^\d{4}-\d{2}-\d{2}$/.test(state.date);

  return (
    <Modal transparent animationType="fade" visible>
      <View style={styles.backdrop}>
        <View style={styles.modalCard}>
          <Text style={styles.modalTitle}>{draft.id ? 'Edit Event' : 'Add Event'}</Text>

          <Text style={styles.fieldLabel}>Date *</Text>
          <TextInput
            style={styles.input}
            value={state.date}
            placeholder="YYYY-MM-DD"
            onChangeText={(v) => setState({ ...state, date: v })}
            data-testid="cal-event-date"
            {...(Platform.OS === 'web' ? ({ type: 'date' } as any) : {})}
          />

          <Text style={styles.fieldLabel}>Title *</Text>
          <TextInput
            style={styles.input}
            value={state.title}
            placeholder="e.g. Term 2 Opens"
            onChangeText={(v) => setState({ ...state, title: v })}
            data-testid="cal-event-title"
          />

          <Text style={styles.fieldLabel}>Category *</Text>
          <View style={styles.chipRow}>
            {CATEGORIES.map((c) => (
              <Pressable
                key={c.value}
                onPress={() => setState({ ...state, category: c.value })}
                style={[
                  styles.chip,
                  state.category === c.value && { backgroundColor: c.color, borderColor: c.color },
                ]}
                data-testid={`cal-event-cat-${c.value}`}
              >
                <Text style={[styles.chipText, state.category === c.value && { color: '#FFFFFF' }]}>{c.label}</Text>
              </Pressable>
            ))}
          </View>

          <Text style={styles.fieldLabel}>Order</Text>
          <TextInput
            style={styles.input}
            value={String(state.order)}
            keyboardType="number-pad"
            onChangeText={(v) => setState({ ...state, order: parseInt(v || '0', 10) || 0 })}
            data-testid="cal-event-order"
          />

          <View style={styles.modalFooter}>
            <TouchableOpacity onPress={onCancel} style={[styles.modalBtn, { backgroundColor: '#DDDDF5' }]} data-testid="cal-event-cancel">
              <Text style={[styles.modalBtnText, { color: '#374151' }]}>Cancel</Text>
            </TouchableOpacity>
            <TouchableOpacity
              onPress={() => canSave && onSave(state)}
              style={[styles.modalBtn, !canSave && { opacity: 0.5 }]}
              disabled={!canSave}
              data-testid="cal-event-save"
            >
              <Text style={styles.modalBtnText}>Save</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );
};

// ===== Term editor modal =====

const TermEditorModal: React.FC<{
  draft: TermDoc;
  onCancel: () => void;
  onSave: (t: TermDoc) => void;
}> = ({ draft, onCancel, onSave }) => {
  const [state, setState] = useState<TermDoc>(draft);
  const canSave = state.name.trim().length > 0 && state.period.trim().length > 0;

  const addActivity = (kind: 'academic' | 'cocurricular') => {
    const list = state[kind];
    setState({ ...state, [kind]: [...list, { label: '', date: '' }] });
  };
  const updateActivity = (kind: 'academic' | 'cocurricular', idx: number, patch: Partial<TermActivityDoc>) => {
    const list = [...state[kind]];
    list[idx] = { ...list[idx], ...patch };
    setState({ ...state, [kind]: list });
  };
  const removeActivity = (kind: 'academic' | 'cocurricular', idx: number) => {
    const list = [...state[kind]];
    list.splice(idx, 1);
    setState({ ...state, [kind]: list });
  };

  return (
    <Modal transparent animationType="fade" visible>
      <View style={styles.backdrop}>
        <View style={[styles.modalCard, { maxHeight: '90%' }]}>
          <Text style={styles.modalTitle}>{draft.id ? 'Edit Term' : 'Add Term'}</Text>
          <ScrollView style={{ maxHeight: 480 }}>
            <Text style={styles.fieldLabel}>Name *</Text>
            <TextInput
              style={styles.input}
              value={state.name}
              placeholder="e.g. Term 2"
              onChangeText={(v) => setState({ ...state, name: v })}
              data-testid="cal-term-name"
            />

            <Text style={styles.fieldLabel}>Period *</Text>
            <TextInput
              style={styles.input}
              value={state.period}
              placeholder="e.g. Apr 29 – Aug 1"
              onChangeText={(v) => setState({ ...state, period: v })}
              data-testid="cal-term-period"
            />

            <Text style={styles.fieldLabel}>Year</Text>
            <TextInput
              style={styles.input}
              value={String(state.year)}
              keyboardType="number-pad"
              onChangeText={(v) => setState({ ...state, year: parseInt(v || '0', 10) || new Date().getFullYear() })}
              data-testid="cal-term-year"
            />

            <Text style={styles.fieldLabel}>Status *</Text>
            <View style={styles.chipRow}>
              {STATUSES.map((s) => (
                <Pressable
                  key={s.value}
                  onPress={() => setState({ ...state, status: s.value })}
                  style={[
                    styles.chip,
                    state.status === s.value && { backgroundColor: s.color, borderColor: s.color },
                  ]}
                  data-testid={`cal-term-status-${s.value}`}
                >
                  <Text style={[styles.chipText, state.status === s.value && { color: '#FFFFFF' }]}>{s.label}</Text>
                </Pressable>
              ))}
            </View>

            <Text style={styles.fieldLabel}>Order</Text>
            <TextInput
              style={styles.input}
              value={String(state.order)}
              keyboardType="number-pad"
              onChangeText={(v) => setState({ ...state, order: parseInt(v || '0', 10) || 0 })}
              data-testid="cal-term-order"
            />

            <ActivitiesEditor
              title="📚 Academic Milestones"
              list={state.academic}
              onAdd={() => addActivity('academic')}
              onUpdate={(i, p) => updateActivity('academic', i, p)}
              onRemove={(i) => removeActivity('academic', i)}
              idPrefix="academic"
            />
            <ActivitiesEditor
              title="🏆 Co-curricular Milestones"
              list={state.cocurricular}
              onAdd={() => addActivity('cocurricular')}
              onUpdate={(i, p) => updateActivity('cocurricular', i, p)}
              onRemove={(i) => removeActivity('cocurricular', i)}
              idPrefix="cocurr"
            />
          </ScrollView>

          <View style={styles.modalFooter}>
            <TouchableOpacity onPress={onCancel} style={[styles.modalBtn, { backgroundColor: '#DDDDF5' }]} data-testid="cal-term-cancel">
              <Text style={[styles.modalBtnText, { color: '#374151' }]}>Cancel</Text>
            </TouchableOpacity>
            <TouchableOpacity
              onPress={() => canSave && onSave(state)}
              style={[styles.modalBtn, !canSave && { opacity: 0.5 }]}
              disabled={!canSave}
              data-testid="cal-term-save"
            >
              <Text style={styles.modalBtnText}>Save</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );
};

const ActivitiesEditor: React.FC<{
  title: string;
  list: TermActivityDoc[];
  onAdd: () => void;
  onUpdate: (i: number, patch: Partial<TermActivityDoc>) => void;
  onRemove: (i: number) => void;
  idPrefix: string;
}> = ({ title, list, onAdd, onUpdate, onRemove, idPrefix }) => (
  <View style={{ marginTop: 14 }}>
    <View style={styles.sectionHeader}>
      <Text style={styles.subSectionTitle}>{title}</Text>
      <TouchableOpacity onPress={onAdd} style={styles.smallAddBtn} data-testid={`cal-term-add-${idPrefix}`}>
        <Ionicons name="add" size={12} color="#FFFFFF" />
        <Text style={styles.smallAddBtnText}>Add</Text>
      </TouchableOpacity>
    </View>
    {list.length === 0 ? (
      <Text style={[styles.muted, { fontSize: 11 }]}>No entries yet.</Text>
    ) : (
      list.map((a, i) => (
        <View key={i} style={styles.activityRow}>
          <TextInput
            style={[styles.input, { flex: 2, marginBottom: 0, marginRight: 6 }]}
            value={a.label}
            placeholder="Label (e.g. Schools open)"
            onChangeText={(v) => onUpdate(i, { label: v })}
          />
          <TextInput
            style={[styles.input, { flex: 1, marginBottom: 0, marginRight: 6 }]}
            value={a.date}
            placeholder="Date (e.g. Jan 6)"
            onChangeText={(v) => onUpdate(i, { date: v })}
          />
          <TouchableOpacity onPress={() => onRemove(i)} style={styles.iconBtn}>
            <Ionicons name="close-circle" size={18} color="#EF4444" />
          </TouchableOpacity>
        </View>
      ))
    )}
  </View>
);

// ===== Helpers =====

function toIsoToday(): string {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

function formatIsoForDisplay(iso: string): string {
  try {
    const [y, m, d] = iso.split('-').map((v) => parseInt(v, 10));
    const MONTH = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    return `${MONTH[m - 1]} ${d}, ${y}`;
  } catch {
    return iso;
  }
}

function blankTerm(order: number): TermDoc {
  return {
    id: '',
    name: '',
    period: '',
    status: 'upcoming',
    year: new Date().getFullYear(),
    academic: [],
    cocurricular: [],
    order,
  };
}

// ===== Styles =====

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: 'transparent' },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  muted: { color: '#5A5A7A', fontSize: 13, marginTop: 8 },

  tabsRow: {
    flexDirection: 'row',
    gap: 8,
    padding: 12,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#DDDDF5',
  },
  tabBtn: {
    flex: 1,
    flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 6,
    paddingVertical: 10, paddingHorizontal: 12,
    borderRadius: 8, borderWidth: 1, borderColor: '#DDDDF5',
    backgroundColor: '#FFFFFF',
  },
  tabBtnActive: { backgroundColor: '#F59E0B', borderColor: '#F59E0B' },
  tabBtnText: { color: '#5A5A7A', fontSize: 13, fontWeight: '600' },
  tabBtnTextActive: { color: '#FFFFFF' },

  scrollBody: { padding: 16, paddingBottom: 80 },
  sectionHeader: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    marginBottom: 12,
  },
  sectionTitle: { fontSize: 16, fontWeight: '700', color: '#1A1A3A' },
  subSectionTitle: { fontSize: 13, fontWeight: '700', color: '#374151' },

  addBtn: {
    flexDirection: 'row', alignItems: 'center', gap: 6,
    backgroundColor: '#F59E0B', paddingHorizontal: 12, paddingVertical: 8,
    borderRadius: 8,
  },
  addBtnText: { color: '#FFFFFF', fontSize: 13, fontWeight: '600' },
  smallAddBtn: {
    flexDirection: 'row', alignItems: 'center', gap: 4,
    backgroundColor: '#5C6BC0', paddingHorizontal: 8, paddingVertical: 4,
    borderRadius: 6,
  },
  smallAddBtnText: { color: '#FFFFFF', fontSize: 11, fontWeight: '600' },

  listCard: {
    flexDirection: 'row', alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 10, borderWidth: 1, borderColor: '#DDDDF5',
    padding: 12, marginBottom: 10, gap: 10,
  },
  colourStrip: { width: 4, height: 40, borderRadius: 2 },
  cardTitle: { fontSize: 14, fontWeight: '600', color: '#1A1A3A' },
  cardSubtle: { fontSize: 12, color: '#5A5A7A', marginTop: 2 },
  iconBtn: { padding: 6 },

  backdrop: { flex: 1, backgroundColor: 'rgba(0,0,0,0.4)', alignItems: 'center', justifyContent: 'center', padding: 16 },
  modalCard: {
    width: '100%', maxWidth: 500, backgroundColor: '#FFFFFF', borderRadius: 12,
    padding: 20, gap: 4,
  },
  modalTitle: { fontSize: 16, fontWeight: '700', color: '#1A1A3A', marginBottom: 10 },
  fieldLabel: { fontSize: 12, fontWeight: '600', color: '#374151', marginTop: 8, marginBottom: 4 },
  input: {
    borderWidth: 1, borderColor: '#D1D5DB', borderRadius: 8,
    paddingHorizontal: 10, paddingVertical: 8, fontSize: 13,
    backgroundColor: '#FFFFFF', color: '#1A1A3A',
    marginBottom: 4,
  },
  chipRow: { flexDirection: 'row', gap: 6, flexWrap: 'wrap', marginBottom: 4 },
  chip: {
    paddingHorizontal: 12, paddingVertical: 6,
    borderRadius: 20, borderWidth: 1, borderColor: '#D1D5DB',
    backgroundColor: '#FFFFFF',
  },
  chipText: { fontSize: 12, color: '#374151', fontWeight: '600' },

  modalFooter: {
    flexDirection: 'row', justifyContent: 'flex-end', gap: 8, marginTop: 14,
  },
  modalBtn: {
    backgroundColor: '#F59E0B', paddingHorizontal: 16, paddingVertical: 10,
    borderRadius: 8, alignItems: 'center', justifyContent: 'center',
  },
  modalBtnText: { color: '#FFFFFF', fontSize: 13, fontWeight: '600' },

  activityRow: { flexDirection: 'row', alignItems: 'center', marginVertical: 4 },
});
