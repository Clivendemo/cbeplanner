import React, { useState, useCallback } from 'react';
import {
  View, Text, ScrollView, TouchableOpacity, StyleSheet,
  ActivityIndicator, TextInput, Modal, Platform, Pressable, Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../../contexts/AuthContext';
import axios from 'axios';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

// ── Types ──

interface Resource {
  type: string;
  title?: string;
  pages?: string;
  display_text: string;
}

interface Slot {
  id: string;
  slot_index: number;
  outcome: string;
  description: string;
  key_inquiry_question: string;
  learning_activities: string[];
  resources: Resource[];
  assessment_methods: string[];
  competencies: string[];
  values: string[];
  pcis: string[];
  is_customized: boolean;
}

interface PickItem { id: string; name: string; number_of_lessons?: number; }

// ── Component ──

export default function LessonSlotsScreen() {
  const { firebaseUser } = useAuth();

  // Cascade selection
  const [grades, setGrades] = useState<PickItem[]>([]);
  const [subjects, setSubjects] = useState<PickItem[]>([]);
  const [strands, setStrands] = useState<PickItem[]>([]);
  const [substrands, setSubstrands] = useState<PickItem[]>([]);

  const [selGrade, setSelGrade] = useState('');
  const [selSubject, setSelSubject] = useState('');
  const [selStrand, setSelStrand] = useState('');
  const [selSubstrand, setSelSubstrand] = useState('');
  const [numLessons, setNumLessons] = useState(0);

  // Slots
  const [slots, setSlots] = useState<Slot[]>([]);
  const [loading, setLoading] = useState(false);
  const [slotsLoading, setSlotsLoading] = useState(false);

  // Edit modal
  const [editSlot, setEditSlot] = useState<Slot | null>(null);
  const [editModalVisible, setEditModalVisible] = useState(false);

  // Resource modal
  const [resModalVisible, setResModalVisible] = useState(false);
  const [resSlotIdx, setResSlotIdx] = useState(-1);
  const [resType, setResType] = useState<'textbook' | 'material'>('textbook');
  const [resTitle, setResTitle] = useState('');
  const [resPages, setResPages] = useState('');
  const [resDisplay, setResDisplay] = useState('');

  const getHeaders = async () => {
    if (firebaseUser) {
      const token = await firebaseUser.getIdToken();
      return { Authorization: `Bearer ${token}` };
    }
    return {};
  };

  // ── Cascade loaders ──

  const loadGrades = useCallback(async () => {
    try {
      setLoading(true);
      const h = await getHeaders();
      const res = await axios.get(`${BACKEND_URL}/api/admin/grades`, { headers: h });
      setGrades(res.data.grades || []);
    } catch { } finally { setLoading(false); }
  }, [firebaseUser]);

  React.useEffect(() => { loadGrades(); }, [loadGrades]);

  const onGrade = async (id: string) => {
    setSelGrade(id); setSelSubject(''); setSelStrand(''); setSelSubstrand('');
    setSubjects([]); setStrands([]); setSubstrands([]); setSlots([]);
    try {
      const h = await getHeaders();
      const res = await axios.get(`${BACKEND_URL}/api/admin/subjects?gradeId=${id}`, { headers: h });
      setSubjects(res.data.subjects || []);
    } catch { }
  };

  const onSubject = async (id: string) => {
    setSelSubject(id); setSelStrand(''); setSelSubstrand('');
    setStrands([]); setSubstrands([]); setSlots([]);
    try {
      const h = await getHeaders();
      const res = await axios.get(`${BACKEND_URL}/api/admin/strands?subjectId=${id}`, { headers: h });
      setStrands(res.data.strands || []);
    } catch { }
  };

  const onStrand = async (id: string) => {
    setSelStrand(id); setSelSubstrand('');
    setSubstrands([]); setSlots([]);
    try {
      const h = await getHeaders();
      const res = await axios.get(`${BACKEND_URL}/api/admin/substrands?strandId=${id}`, { headers: h });
      setSubstrands(res.data.substrands || []);
    } catch { }
  };

  const onSubstrand = async (id: string) => {
    setSelSubstrand(id);
    const ss = substrands.find(s => s.id === id);
    setNumLessons(ss?.number_of_lessons || 0);
    await loadSlots(id);
  };

  // ── Slot loaders ──

  const loadSlots = async (ssId: string) => {
    setSlotsLoading(true);
    try {
      const h = await getHeaders();
      const res = await axios.get(`${BACKEND_URL}/api/admin/lesson-slots/${ssId}`, { headers: h });
      setSlots(res.data.slots || []);
      setNumLessons(res.data.number_of_lessons || 0);
    } catch { } finally { setSlotsLoading(false); }
  };

  // ── Slot actions ──

  const openEditModal = (slot: Slot) => {
    setEditSlot({ ...slot });
    setEditModalVisible(true);
  };

  const saveSlot = async () => {
    if (!editSlot) return;
    try {
      const h = await getHeaders();
      await axios.put(
        `${BACKEND_URL}/api/admin/lesson-slots/${selSubstrand}/${editSlot.slot_index}`,
        {
          outcome: editSlot.outcome,
          description: editSlot.description,
          key_inquiry_question: editSlot.key_inquiry_question,
          learning_activities: editSlot.learning_activities,
          assessment_methods: editSlot.assessment_methods,
          competencies: editSlot.competencies,
          values: editSlot.values,
          pcis: editSlot.pcis,
          resources: editSlot.resources,
        },
        { headers: h }
      );
      setEditModalVisible(false);
      await loadSlots(selSubstrand);
    } catch (e: any) {
      Alert.alert('Error', e?.response?.data?.detail || 'Failed to save');
    }
  };

  const clearSlot = async (idx: number) => {
    try {
      const h = await getHeaders();
      await axios.post(`${BACKEND_URL}/api/admin/lesson-slots/${selSubstrand}/${idx}/clear`, {}, { headers: h });
      await loadSlots(selSubstrand);
    } catch { }
  };

  // ── Resource helpers ──

  const openResourceModal = (slotIdx: number) => {
    setResSlotIdx(slotIdx);
    setResType('textbook');
    setResTitle(''); setResPages(''); setResDisplay('');
    setResModalVisible(true);
  };

  const addResource = async () => {
    const slot = slots.find(s => s.slot_index === resSlotIdx);
    if (!slot) return;

    const newRes: Resource = resType === 'textbook'
      ? {
          type: 'textbook',
          title: resTitle,
          pages: resPages,
          display_text: resPages ? `${resTitle}, pp. ${resPages}` : resTitle,
        }
      : { type: 'material', display_text: resDisplay };

    const updated = [...(slot.resources || []), newRes];
    try {
      const h = await getHeaders();
      await axios.put(
        `${BACKEND_URL}/api/admin/lesson-slots/${selSubstrand}/${resSlotIdx}`,
        { resources: updated },
        { headers: h }
      );
      setResModalVisible(false);
      await loadSlots(selSubstrand);
    } catch (e: any) {
      Alert.alert('Error', e?.response?.data?.detail || 'Failed to add resource');
    }
  };

  const removeResource = async (slotIdx: number, resIdx: number) => {
    const slot = slots.find(s => s.slot_index === slotIdx);
    if (!slot) return;
    const updated = slot.resources.filter((_, i) => i !== resIdx);
    try {
      const h = await getHeaders();
      await axios.put(
        `${BACKEND_URL}/api/admin/lesson-slots/${selSubstrand}/${slotIdx}`,
        { resources: updated },
        { headers: h }
      );
      await loadSlots(selSubstrand);
    } catch { }
  };

  // ── Helpers for edit modal list fields ──

  const updateEditList = (field: 'learning_activities' | 'assessment_methods' | 'competencies' | 'values' | 'pcis', text: string) => {
    if (!editSlot) return;
    setEditSlot({ ...editSlot, [field]: text.split('\n').map(s => s.trim()).filter(Boolean) });
  };

  const getEditListText = (field: 'learning_activities' | 'assessment_methods' | 'competencies' | 'values' | 'pcis') => {
    if (!editSlot) return '';
    return (editSlot[field] || []).join('\n');
  };

  // ── Pickers ──

  const Picker = ({ label, items, selected, onSelect, placeholder }: {
    label: string; items: PickItem[]; selected: string;
    onSelect: (id: string) => void; placeholder: string;
  }) => (
    <View style={S.pickerWrap}>
      <Text style={S.pickerLabel}>{label}</Text>
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={S.pickerScroll}>
        {items.map(item => (
          <TouchableOpacity
            key={item.id}
            style={[S.chip, selected === item.id && S.chipActive]}
            onPress={() => onSelect(item.id)}
            data-testid={`pick-${label.toLowerCase()}-${item.id}`}
          >
            <Text style={[S.chipText, selected === item.id && S.chipTextActive]}>
              {item.name}
            </Text>
          </TouchableOpacity>
        ))}
        {items.length === 0 && <Text style={S.pickerEmpty}>{placeholder}</Text>}
      </ScrollView>
    </View>
  );

  // ── Render ──

  return (
    <ScrollView style={S.container} contentContainerStyle={S.content}>
      <Text style={S.title}>Lesson SLO Slots</Text>
      <Text style={S.subtitle}>Select a substrand to manage lesson-level outcomes and resources</Text>

      {/* Cascade selectors */}
      <Picker label="Grade" items={grades} selected={selGrade} onSelect={onGrade} placeholder="Loading grades..." />
      {selGrade !== '' && <Picker label="Subject" items={subjects} selected={selSubject} onSelect={onSubject} placeholder="Select a grade first" />}
      {selSubject !== '' && <Picker label="Strand" items={strands} selected={selStrand} onSelect={onStrand} placeholder="Select a subject first" />}
      {selStrand !== '' && <Picker label="Substrand" items={substrands} selected={selSubstrand} onSelect={onSubstrand} placeholder="Select a strand first" />}

      {/* Slots */}
      {slotsLoading && <ActivityIndicator size="large" color="#5C6BC0" style={{ marginTop: 24 }} />}

      {selSubstrand !== '' && !slotsLoading && numLessons === 0 && (
        <View style={S.emptyCard}>
          <Ionicons name="warning-outline" size={24} color="#F59E0B" />
          <Text style={S.emptyText}>This substrand has no number_of_lessons set. Set it in Curriculum Management first.</Text>
        </View>
      )}

      {selSubstrand !== '' && !slotsLoading && numLessons > 0 && (
        <View style={S.slotsHeader}>
          <Text style={S.slotsTitle}>{numLessons} Lesson Slots</Text>
          <Text style={S.slotsSubtitle}>Each slot = one lesson. Edit outcomes, inquiry questions, and resources.</Text>
        </View>
      )}

      {slots.map(slot => (
        <View key={slot.slot_index} style={[S.slotCard, slot.is_customized && S.slotCardCustom]} data-testid={`slot-card-${slot.slot_index}`}>
          {/* Header */}
          <View style={S.slotHeader}>
            <View style={S.slotBadgeRow}>
              <View style={[S.slotBadge, slot.is_customized ? S.badgeCustom : S.badgeFallback]}>
                <Text style={S.badgeText}>{slot.is_customized ? 'Customized' : 'Fallback'}</Text>
              </View>
              <Text style={S.slotNum}>Lesson {slot.slot_index + 1}</Text>
            </View>
            <View style={{ flexDirection: 'row', gap: 8 }}>
              <TouchableOpacity onPress={() => openEditModal(slot)} style={S.iconBtn} data-testid={`edit-slot-${slot.slot_index}`}>
                <Ionicons name="create-outline" size={20} color="#5C6BC0" />
              </TouchableOpacity>
              {slot.is_customized && (
                <TouchableOpacity onPress={() => clearSlot(slot.slot_index)} style={S.iconBtn} data-testid={`clear-slot-${slot.slot_index}`}>
                  <Ionicons name="refresh-outline" size={20} color="#EF4444" />
                </TouchableOpacity>
              )}
            </View>
          </View>

          {/* Outcome */}
          <Text style={S.slotOutcome} numberOfLines={2}>{slot.outcome || '(no outcome)'}</Text>

          {/* Inquiry */}
          {slot.key_inquiry_question ? (
            <View style={S.infoRow}>
              <Ionicons name="help-circle-outline" size={16} color="#5C6BC0" />
              <Text style={S.infoText}>{slot.key_inquiry_question}</Text>
            </View>
          ) : null}

          {/* Resources */}
          <View style={S.resSection}>
            <View style={S.resSectionHeader}>
              <Text style={S.resSectionTitle}>Teaching/Learning Resources</Text>
              <TouchableOpacity onPress={() => openResourceModal(slot.slot_index)} style={S.addResBtn} data-testid={`add-res-${slot.slot_index}`}>
                <Ionicons name="add-circle-outline" size={18} color="#10B981" />
                <Text style={S.addResBtnText}>Add</Text>
              </TouchableOpacity>
            </View>
            {(slot.resources || []).length === 0 && (
              <Text style={S.resEmpty}>No resources yet</Text>
            )}
            {(slot.resources || []).map((r, ri) => (
              <View key={ri} style={S.resItem}>
                <Ionicons name={r.type === 'textbook' ? 'book-outline' : 'cube-outline'} size={14} color="#5A5A7A" />
                <Text style={S.resText} numberOfLines={2}>{r.display_text || r.title || ''}</Text>
                <TouchableOpacity onPress={() => removeResource(slot.slot_index, ri)} hitSlop={{ top: 8, bottom: 8, left: 8, right: 8 }}>
                  <Ionicons name="close-circle" size={18} color="#EF4444" />
                </TouchableOpacity>
              </View>
            ))}
          </View>
        </View>
      ))}

      {/* ── Edit Modal ── */}
      <Modal visible={editModalVisible} animationType="fade" transparent onRequestClose={() => setEditModalVisible(false)}>
        <Pressable style={S.overlay} onPress={() => setEditModalVisible(false)}>
          <Pressable style={S.modal} onPress={e => e.stopPropagation()}>
            <View style={S.modalHeader}>
              <Text style={S.modalTitle}>Edit Lesson {editSlot ? editSlot.slot_index + 1 : ''}</Text>
              <TouchableOpacity onPress={() => setEditModalVisible(false)}>
                <Ionicons name="close" size={24} color="#5A5A7A" />
              </TouchableOpacity>
            </View>
            <ScrollView style={S.modalBody} keyboardShouldPersistTaps="handled" nestedScrollEnabled>
              <Text style={S.fieldLabel}>Outcome *</Text>
              <TextInput
                style={S.input}
                value={editSlot?.outcome || ''}
                onChangeText={t => editSlot && setEditSlot({ ...editSlot, outcome: t })}
                multiline
                data-testid="edit-outcome"
              />
              <Text style={S.fieldLabel}>Description</Text>
              <TextInput
                style={S.input}
                value={editSlot?.description || ''}
                onChangeText={t => editSlot && setEditSlot({ ...editSlot, description: t })}
                multiline
              />
              <Text style={S.fieldLabel}>Key Inquiry Question (one)</Text>
              <TextInput
                style={S.input}
                value={editSlot?.key_inquiry_question || ''}
                onChangeText={t => editSlot && setEditSlot({ ...editSlot, key_inquiry_question: t })}
                placeholder="e.g. What is the value of each digit?"
              />
              <Text style={S.fieldLabel}>Learning Activities (one per line)</Text>
              <TextInput
                style={[S.input, { minHeight: 60 }]}
                value={getEditListText('learning_activities')}
                onChangeText={t => updateEditList('learning_activities', t)}
                multiline
              />
              <Text style={S.fieldLabel}>Assessment Methods (one per line)</Text>
              <TextInput
                style={[S.input, { minHeight: 60 }]}
                value={getEditListText('assessment_methods')}
                onChangeText={t => updateEditList('assessment_methods', t)}
                multiline
              />
              <Text style={S.fieldLabel}>Competencies (one per line)</Text>
              <TextInput
                style={S.input}
                value={getEditListText('competencies')}
                onChangeText={t => updateEditList('competencies', t)}
                multiline
              />
              <Text style={S.fieldLabel}>Values (one per line)</Text>
              <TextInput
                style={S.input}
                value={getEditListText('values')}
                onChangeText={t => updateEditList('values', t)}
                multiline
              />
              <Text style={S.fieldLabel}>PCIs (one per line)</Text>
              <TextInput
                style={S.input}
                value={getEditListText('pcis')}
                onChangeText={t => updateEditList('pcis', t)}
                multiline
              />
            </ScrollView>
            <View style={S.modalFooter}>
              <TouchableOpacity style={S.cancelBtn} onPress={() => setEditModalVisible(false)}>
                <Text style={S.cancelBtnText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity style={S.saveBtn} onPress={saveSlot} data-testid="save-slot-btn">
                <Ionicons name="checkmark" size={18} color="#fff" />
                <Text style={S.saveBtnText}>Save</Text>
              </TouchableOpacity>
            </View>
          </Pressable>
        </Pressable>
      </Modal>

      {/* ── Add Resource Modal ── */}
      <Modal visible={resModalVisible} animationType="fade" transparent onRequestClose={() => setResModalVisible(false)}>
        <Pressable style={S.overlay} onPress={() => setResModalVisible(false)}>
          <Pressable style={[S.modal, { maxHeight: '60%' }]} onPress={e => e.stopPropagation()}>
            <View style={S.modalHeader}>
              <Text style={S.modalTitle}>Add Resource — Lesson {resSlotIdx + 1}</Text>
              <TouchableOpacity onPress={() => setResModalVisible(false)}>
                <Ionicons name="close" size={24} color="#5A5A7A" />
              </TouchableOpacity>
            </View>
            <ScrollView style={S.modalBody} keyboardShouldPersistTaps="handled">
              {/* Type toggle */}
              <View style={{ flexDirection: 'row', gap: 8, marginBottom: 16 }}>
                <TouchableOpacity
                  style={[S.typeChip, resType === 'textbook' && S.typeChipActive]}
                  onPress={() => setResType('textbook')}
                >
                  <Ionicons name="book-outline" size={16} color={resType === 'textbook' ? '#fff' : '#5C6BC0'} />
                  <Text style={[S.typeChipText, resType === 'textbook' && { color: '#fff' }]}>Textbook</Text>
                </TouchableOpacity>
                <TouchableOpacity
                  style={[S.typeChip, resType === 'material' && S.typeChipActive]}
                  onPress={() => setResType('material')}
                >
                  <Ionicons name="cube-outline" size={16} color={resType === 'material' ? '#fff' : '#5C6BC0'} />
                  <Text style={[S.typeChipText, resType === 'material' && { color: '#fff' }]}>Material</Text>
                </TouchableOpacity>
              </View>

              {resType === 'textbook' ? (
                <>
                  <Text style={S.fieldLabel}>Textbook Title *</Text>
                  <TextInput style={S.input} value={resTitle} onChangeText={setResTitle}
                    placeholder="e.g. New Planet Mathematics Grade 4 Learner's Book" data-testid="res-title" />
                  <Text style={S.fieldLabel}>Page Range</Text>
                  <TextInput style={S.input} value={resPages} onChangeText={setResPages}
                    placeholder="e.g. 50-52" data-testid="res-pages" />
                </>
              ) : (
                <>
                  <Text style={S.fieldLabel}>Material Name *</Text>
                  <TextInput style={S.input} value={resDisplay} onChangeText={setResDisplay}
                    placeholder="e.g. Charts, Abacus, Counters" data-testid="res-display" />
                </>
              )}
            </ScrollView>
            <View style={S.modalFooter}>
              <TouchableOpacity style={S.cancelBtn} onPress={() => setResModalVisible(false)}>
                <Text style={S.cancelBtnText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[S.saveBtn, !(resType === 'textbook' ? resTitle : resDisplay) && { opacity: 0.5 }]}
                onPress={addResource}
                disabled={!(resType === 'textbook' ? resTitle : resDisplay)}
                data-testid="add-resource-btn"
              >
                <Ionicons name="add" size={18} color="#fff" />
                <Text style={S.saveBtnText}>Add Resource</Text>
              </TouchableOpacity>
            </View>
          </Pressable>
        </Pressable>
      </Modal>

      <View style={{ height: 40 }} />
    </ScrollView>
  );
}

// ── Styles ──

const S = StyleSheet.create({
  container: { flex: 1, backgroundColor: 'transparent' },
  content: { padding: 16 },
  title: { fontSize: 22, fontWeight: '700', color: '#1A1A3A', marginBottom: 4 },
  subtitle: { fontSize: 13, color: '#5A5A7A', marginBottom: 16 },

  // Pickers
  pickerWrap: { marginBottom: 12 },
  pickerLabel: { fontSize: 12, fontWeight: '600', color: '#374151', marginBottom: 6, textTransform: 'uppercase', letterSpacing: 0.5 },
  pickerScroll: { flexDirection: 'row' },
  chip: { paddingHorizontal: 14, paddingVertical: 8, borderRadius: 20, backgroundColor: '#fff', borderWidth: 1, borderColor: '#DDDDF5', marginRight: 8 },
  chipActive: { backgroundColor: '#5C6BC0', borderColor: '#5C6BC0' },
  chipText: { fontSize: 13, color: '#374151' },
  chipTextActive: { color: '#fff', fontWeight: '600' },
  pickerEmpty: { fontSize: 13, color: '#9CA3AF', paddingVertical: 8 },

  // Slots
  slotsHeader: { marginTop: 8, marginBottom: 12 },
  slotsTitle: { fontSize: 16, fontWeight: '700', color: '#1A1A3A' },
  slotsSubtitle: { fontSize: 12, color: '#5A5A7A', marginTop: 2 },

  slotCard: { backgroundColor: '#fff', borderRadius: 12, padding: 14, marginBottom: 12, borderWidth: 1, borderColor: '#DDDDF5' },
  slotCardCustom: { borderColor: '#5C6BC0', borderWidth: 1.5 },
  slotHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 },
  slotBadgeRow: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  slotBadge: { paddingHorizontal: 8, paddingVertical: 3, borderRadius: 10 },
  badgeCustom: { backgroundColor: '#F3F4FF' },
  badgeFallback: { backgroundColor: '#F3F4F6' },
  badgeText: { fontSize: 10, fontWeight: '600', color: '#5C6BC0' },
  slotNum: { fontSize: 14, fontWeight: '600', color: '#374151' },
  iconBtn: { padding: 6, borderRadius: 8, backgroundColor: '#F9FAFB' },

  slotOutcome: { fontSize: 13, color: '#1A1A3A', lineHeight: 18, marginBottom: 6 },
  infoRow: { flexDirection: 'row', alignItems: 'flex-start', gap: 6, marginBottom: 6 },
  infoText: { fontSize: 12, color: '#4B5563', flex: 1 },

  // Resources section
  resSection: { marginTop: 8, paddingTop: 8, borderTopWidth: 1, borderTopColor: '#F3F4F6' },
  resSectionHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 },
  resSectionTitle: { fontSize: 12, fontWeight: '600', color: '#374151' },
  addResBtn: { flexDirection: 'row', alignItems: 'center', gap: 4 },
  addResBtnText: { fontSize: 12, color: '#10B981', fontWeight: '600' },
  resEmpty: { fontSize: 12, color: '#9CA3AF', fontStyle: 'italic' },
  resItem: { flexDirection: 'row', alignItems: 'center', gap: 6, paddingVertical: 4 },
  resText: { fontSize: 12, color: '#374151', flex: 1 },

  // Empty state
  emptyCard: { backgroundColor: '#FFFBEB', borderRadius: 12, padding: 16, flexDirection: 'row', alignItems: 'center', gap: 10, marginTop: 16 },
  emptyText: { fontSize: 13, color: '#92400E', flex: 1 },

  // Modal
  overlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.6)', justifyContent: 'center', alignItems: 'center', padding: 16 },
  modal: { backgroundColor: '#fff', borderRadius: 16, width: '100%', maxWidth: 500, maxHeight: '85%', overflow: 'hidden', ...Platform.select({ web: { boxShadow: '0 20px 60px rgba(0,0,0,0.3)' } as any, default: { elevation: 24 } }) },
  modalHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', paddingHorizontal: 16, paddingVertical: 14, borderBottomWidth: 1, borderBottomColor: '#DDDDF5' },
  modalTitle: { fontSize: 16, fontWeight: '700', color: '#1A1A3A' },
  modalBody: { padding: 16, flexShrink: 1 },
  modalFooter: { flexDirection: 'row', padding: 16, borderTopWidth: 1, borderTopColor: '#DDDDF5', gap: 12 },

  fieldLabel: { fontSize: 12, fontWeight: '600', color: '#374151', marginBottom: 4, marginTop: 12 },
  input: { borderWidth: 1, borderColor: '#D1D5DB', borderRadius: 8, padding: 10, fontSize: 13, color: '#1A1A3A', backgroundColor: '#F9FAFB', minHeight: 40 },

  cancelBtn: { flex: 1, paddingVertical: 12, borderRadius: 10, backgroundColor: '#F3F4F6', alignItems: 'center' },
  cancelBtnText: { fontSize: 14, fontWeight: '600', color: '#374151' },
  saveBtn: { flex: 1, paddingVertical: 12, borderRadius: 10, backgroundColor: '#5C6BC0', flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 6 },
  saveBtnText: { fontSize: 14, fontWeight: '600', color: '#fff' },

  // Type chips
  typeChip: { flexDirection: 'row', alignItems: 'center', gap: 6, paddingHorizontal: 14, paddingVertical: 8, borderRadius: 20, borderWidth: 1, borderColor: '#5C6BC0' },
  typeChipActive: { backgroundColor: '#5C6BC0' },
  typeChipText: { fontSize: 13, color: '#5C6BC0' },
});
