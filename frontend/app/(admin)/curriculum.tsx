import React, { useState, useEffect, useCallback } from 'react';
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
  FlatList,
  Platform,
  RefreshControl,
  Pressable
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../../contexts/AuthContext';
import { useFocusEffect } from 'expo-router';
import axios from 'axios';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

type EntityType = 'grades' | 'subjects' | 'strands' | 'substrands' | 'slos' | 'learning_activities' | 'competencies' | 'values' | 'pcis' | 'assessment_methods';

interface Entity {
  id: string;
  name?: string;
  description?: string;
  order?: number;
  gradeIds?: string[];
  subjectId?: string;
  strandId?: string;
  substrandId?: string;
  introduction_activities?: string[];
  development_activities?: string[];
  conclusion_activities?: string[];
  extended_activities?: string[];
}

interface Breadcrumb {
  type: EntityType;
  id: string;
  name: string;
}

const ENTITY_CONFIG: Record<EntityType, { 
  title: string; 
  singularTitle: string;
  icon: string; 
  color: string; 
  fields: string[]; 
  parent?: EntityType;
  apiPath: string;
}> = {
  grades: { title: 'Grades', singularTitle: 'Grade', icon: 'school', color: '#5C6BC0', fields: ['name', 'order'], apiPath: 'grades' },
  subjects: { title: 'Subjects', singularTitle: 'Subject', icon: 'book', color: '#10B981', fields: ['name'], parent: 'grades', apiPath: 'subjects' },
  strands: { title: 'Strands', singularTitle: 'Strand', icon: 'git-branch', color: '#F59E0B', fields: ['name', 'order'], parent: 'subjects', apiPath: 'strands' },
  substrands: { title: 'Sub-strands', singularTitle: 'Sub-strand', icon: 'git-merge', color: '#EF4444', fields: ['name', 'number_of_lessons', 'order'], parent: 'strands', apiPath: 'substrands' },
  slos: { title: 'SLOs', singularTitle: 'SLO', icon: 'checkmark-circle', color: '#5C6BC0', fields: ['name', 'description', 'key_inquiry_questions'], parent: 'substrands', apiPath: 'slos' },
  learning_activities: { title: 'Learning Activities', singularTitle: 'Learning Activities', icon: 'flash', color: '#84CC16', fields: ['introduction_activities', 'development_activities', 'conclusion_activities', 'extended_activities'], parent: 'substrands', apiPath: 'learning-activities' },
  competencies: { title: 'Competencies', singularTitle: 'Competency', icon: 'star', color: '#EC4899', fields: ['name', 'description'], apiPath: 'competencies' },
  values: { title: 'Values', singularTitle: 'Value', icon: 'heart', color: '#14B8A6', fields: ['name', 'description'], apiPath: 'values' },
  pcis: { title: 'PCIs', singularTitle: 'PCI', icon: 'globe', color: '#F97316', fields: ['name', 'description'], apiPath: 'pcis' },
  assessment_methods: { title: 'Assessment Methods', singularTitle: 'Assessment Method', icon: 'clipboard', color: '#0EA5E9', fields: ['name', 'description'], apiPath: 'assessments' }
};

const showAlert = (title: string, message: string, buttons?: any[]) => {
  if (Platform.OS === 'web') {
    if (buttons && buttons.length > 1) {
      const confirmBtn = buttons.find(b => b.style === 'destructive' || b.text === 'Delete');
      if (confirmBtn && window.confirm(`${title}\n\n${message}`)) {
        confirmBtn.onPress?.();
      }
    } else {
      window.alert(`${title}\n\n${message}`);
    }
  } else {
    Alert.alert(title, message, buttons);
  }
};

export default function Curriculum() {
  const { firebaseUser } = useAuth();
  const [currentView, setCurrentView] = useState<'main' | 'hierarchy'>('main');
  const [selectedEntity, setSelectedEntity] = useState<EntityType>('grades');
  const [data, setData] = useState<Entity[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingItem, setEditingItem] = useState<Entity | null>(null);
  const [formData, setFormData] = useState<Record<string, any>>({});
  
  // Hierarchical navigation
  const [breadcrumbs, setBreadcrumbs] = useState<Breadcrumb[]>([]);
  const [currentParentId, setCurrentParentId] = useState<string>('');
  
  // Parent data for modal selection
  const [grades, setGrades] = useState<Entity[]>([]);
  const [subjects, setSubjects] = useState<Entity[]>([]);
  const [strands, setStrands] = useState<Entity[]>([]);
  const [substrands, setSubstrands] = useState<Entity[]>([]);
  const [selectedParentId, setSelectedParentId] = useState<string>('');
  
  // Learning activities specific
  const [learningActivitiesModalVisible, setLearningActivitiesModalVisible] = useState(false);
  const [currentSubstrandForActivities, setCurrentSubstrandForActivities] = useState<Entity | null>(null);
  const [activitiesFormData, setActivitiesFormData] = useState({
    introduction_activities: [''],
    development_activities: [''],
    conclusion_activities: [''],
    extended_activities: ['']
  });
  const [existingActivityId, setExistingActivityId] = useState<string | null>(null);

  // Move modal state
  const [moveModalVisible, setMoveModalVisible] = useState(false);
  const [movingItem, setMovingItem] = useState<Entity | null>(null);
  const [moveTargetGrade, setMoveTargetGrade] = useState<string>('');
  const [moveTargetSubject, setMoveTargetSubject] = useState<string>('');
  const [moveTargetStrand, setMoveTargetStrand] = useState<string>('');
  const [moveTargetSubstrand, setMoveTargetSubstrand] = useState<string>('');
  const [allGrades, setAllGrades] = useState<Entity[]>([]);
  const [allSubjects, setAllSubjects] = useState<Entity[]>([]);
  const [allStrands, setAllStrands] = useState<Entity[]>([]);
  const [allSubstrands, setAllSubstrands] = useState<Entity[]>([]);
  const [moveStrandsForSubject, setMoveStrandsForSubject] = useState<Entity[]>([]);
  const [moveSubstrandsForStrand, setMoveSubstrandsForStrand] = useState<Entity[]>([]);

  // Bulk add modal state
  const [bulkAddModalVisible, setBulkAddModalVisible] = useState(false);
  const [bulkAddMode, setBulkAddMode] = useState<'textarea' | 'table'>('textarea');
  const [bulkTextValue, setBulkTextValue] = useState('');
  const [bulkTableRows, setBulkTableRows] = useState<{name: string, description: string}[]>([
    { name: '', description: '' },
    { name: '', description: '' },
    { name: '', description: '' }
  ]);

  // SLO Mapping Editor state
  const [mappingModalVisible, setMappingModalVisible] = useState(false);
  const [mappingSlo, setMappingSlo] = useState<Entity | null>(null);
  const [selectedCompetencies, setSelectedCompetencies] = useState<string[]>([]);
  const [selectedValues, setSelectedValues] = useState<string[]>([]);
  const [selectedPcis, setSelectedPcis] = useState<string[]>([]);
  const [allCompetencies, setAllCompetencies] = useState<Entity[]>([]);
  const [allValues, setAllValues] = useState<Entity[]>([]);
  const [allPcis, setAllPcis] = useState<Entity[]>([]);

  // Bulk Mapping Editor state
  const [bulkMappingModalVisible, setBulkMappingModalVisible] = useState(false);
  const [selectedSlosForMapping, setSelectedSlosForMapping] = useState<string[]>([]);
  const [bulkSelectedCompetencies, setBulkSelectedCompetencies] = useState<string[]>([]);
  const [bulkSelectedValues, setBulkSelectedValues] = useState<string[]>([]);
  const [bulkSelectedPcis, setBulkSelectedPcis] = useState<string[]>([]);

  // Bulk Edit Mode state
  const [bulkEditMode, setBulkEditMode] = useState(false);
  const [selectedItems, setSelectedItems] = useState<Set<string>>(new Set());
  const [bulkEditModalVisible, setBulkEditModalVisible] = useState(false);
  const [bulkEditFormData, setBulkEditFormData] = useState<Record<string, any>>({});

  // KIQ coverage stats per substrand — populated when navigating into a
  // strand so each substrand row can show how many of its SLOs are
  // missing Key Inquiry Questions. Map: { [substrandId]: { total, missing } }.
  const [substrandKiqStats, setSubstrandKiqStats] = useState<Record<string, { total: number; missing: number }>>({});
  
  // Pull-to-refresh state
  const [refreshing, setRefreshing] = useState(false);

  // Substrand Lessons configuration state
  const [lessonsModalVisible, setLessonsModalVisible] = useState(false);
  const [lessonsSubstrand, setLessonsSubstrand] = useState<Entity | null>(null);
  const [substrandLessons, setSubstrandLessons] = useState<any[]>([]);
  const [lessonsLoading, setLessonsLoading] = useState(false);

  const getHeaders = async () => {
    if (firebaseUser) {
      const token = await firebaseUser.getIdToken();
      return { Authorization: `Bearer ${token}` };
    }
    return {};
  };

  // Load initial data
  useEffect(() => {
    loadGrades();
  }, []);

  useEffect(() => {
    if (currentView === 'main') {
      loadData();
    }
  }, [selectedEntity, currentView]);

  // Auto-refresh when screen comes into focus (detects external DB changes)
  useFocusEffect(
    useCallback(() => {
      // Refresh data when screen is focused
      
      refreshCurrentView();
    }, [currentView, selectedEntity, currentParentId])
  );

  // Pull-to-refresh handler
  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    try {
      await refreshCurrentView();
    } finally {
      setRefreshing(false);
    }
  }, [currentView, selectedEntity, currentParentId]);

  // Auto-refresh: Universal refresh function for current view
  const refreshCurrentView = async () => {
    setLoading(true);
    try {
      const headers = await getHeaders();
      
      if (currentView === 'main') {
        // In main view, reload all data for current entity type
        await loadData();
      } else if (currentView === 'hierarchy') {
        // In hierarchy view, reload data based on current level
        if (selectedEntity === 'grades') {
          const gradesRes = await axios.get(`${BACKEND_URL}/api/admin/grades`, { headers });
          if (gradesRes.data.success) {
            setData(gradesRes.data.grades);
            setGrades(gradesRes.data.grades);
          }
        } else if (selectedEntity === 'subjects' && currentParentId) {
          const response = await axios.get(`${BACKEND_URL}/api/admin/subjects?gradeId=${currentParentId}`, { headers });
          if (response.data.success) {
            setData(response.data.subjects);
          }
        } else if (selectedEntity === 'strands' && currentParentId) {
          const response = await axios.get(`${BACKEND_URL}/api/admin/strands?subjectId=${currentParentId}`, { headers });
          if (response.data.success) {
            setData(response.data.strands);
          }
        } else if (selectedEntity === 'substrands' && currentParentId) {
          const response = await axios.get(`${BACKEND_URL}/api/admin/substrands?strandId=${currentParentId}`, { headers });
          if (response.data.success) {
            setData(response.data.substrands);
          }
        } else if (selectedEntity === 'slos' && currentParentId) {
          const response = await axios.get(`${BACKEND_URL}/api/admin/slos?substrandId=${currentParentId}`, { headers });
          if (response.data.success) {
            setData(response.data.slos);
          }
        }
      }
    } catch (error) {
      
    } finally {
      setLoading(false);
    }
  };

  const loadGrades = async () => {
    try {
      const headers = await getHeaders();
      const response = await axios.get(`${BACKEND_URL}/api/admin/grades`, { headers });
      if (response.data.success) {
        setGrades(response.data.grades);
      }
    } catch (error) {
      
    }
  };

  const loadSubjects = async (gradeId?: string) => {
    try {
      const headers = await getHeaders();
      // Use server-side filtering with gradeId query parameter
      const url = gradeId 
        ? `${BACKEND_URL}/api/admin/subjects?gradeId=${gradeId}`
        : `${BACKEND_URL}/api/admin/subjects`;
      const response = await axios.get(url, { headers });
      if (response.data.success) {
        setSubjects(response.data.subjects);
      }
    } catch (error) {
      
    }
  };

  const loadStrands = async (subjectId?: string) => {
    try {
      const headers = await getHeaders();
      const url = subjectId 
        ? `${BACKEND_URL}/api/admin/strands?subjectId=${subjectId}`
        : `${BACKEND_URL}/api/admin/strands`;
      const response = await axios.get(url, { headers });
      if (response.data.success) {
        setStrands(response.data.strands);
      }
    } catch (error) {
      
    }
  };

  const loadSubstrands = async (strandId?: string) => {
    try {
      const headers = await getHeaders();
      const url = strandId 
        ? `${BACKEND_URL}/api/admin/substrands?strandId=${strandId}`
        : `${BACKEND_URL}/api/admin/substrands`;
      const response = await axios.get(url, { headers });
      if (response.data.success) {
        setSubstrands(response.data.substrands);
      }
    } catch (error) {
      
    }
  };

  const loadSlos = async (substrandId: string) => {
    try {
      const headers = await getHeaders();
      const response = await axios.get(`${BACKEND_URL}/api/admin/slos?substrandId=${substrandId}`, { headers });
      if (response.data.success) {
        setData(response.data.slos);
      }
    } catch (error) {
      
    }
  };

  const loadData = async () => {
    setLoading(true);
    try {
      const headers = await getHeaders();
      const config = ENTITY_CONFIG[selectedEntity];
      const response = await axios.get(`${BACKEND_URL}/api/admin/${config.apiPath}`, { headers });
      if (response.data.success) {
        const key = selectedEntity === 'slos' ? 'slos' : 
                    selectedEntity === 'learning_activities' ? 'learning_activities' : 
                    selectedEntity === 'assessment_methods' ? 'assessments' :
                    selectedEntity;
        setData(response.data[key] || []);
      }
      
      // Load parent data if needed
      if (selectedEntity === 'subjects') {
        loadGrades();
      } else if (selectedEntity === 'strands') {
        loadSubjects();
      } else if (selectedEntity === 'substrands') {
        loadStrands();
      } else if (selectedEntity === 'slos' || selectedEntity === 'learning_activities') {
        loadSubstrands();
      }
    } catch (error: any) {
      
      showAlert('Error', 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  // Hierarchical navigation functions
  const navigateToGrades = () => {
    setBreadcrumbs([]);
    setCurrentParentId('');
    setCurrentView('hierarchy');
    setSelectedEntity('grades');
    loadGrades().then(() => setData(grades));
  };

  const navigateToSubjects = async (grade: Entity) => {
    setBreadcrumbs([{ type: 'grades', id: grade.id, name: grade.name || '' }]);
    setCurrentParentId(grade.id);
    setSelectedEntity('subjects');
    setLoading(true);
    try {
      const headers = await getHeaders();
      // Use server-side filtering with gradeId query parameter
      const response = await axios.get(`${BACKEND_URL}/api/admin/subjects?gradeId=${grade.id}`, { headers });
      if (response.data.success) {
        setData(response.data.subjects);
      }
    } catch (error) {
      
    } finally {
      setLoading(false);
    }
  };

  const navigateToStrands = async (subject: Entity) => {
    const newBreadcrumbs = [...breadcrumbs, { type: 'subjects' as EntityType, id: subject.id, name: subject.name || '' }];
    setBreadcrumbs(newBreadcrumbs);
    setCurrentParentId(subject.id);
    setSelectedEntity('strands');
    setLoading(true);
    try {
      const headers = await getHeaders();
      const response = await axios.get(`${BACKEND_URL}/api/admin/strands?subjectId=${subject.id}`, { headers });
      if (response.data.success) {
        setData(response.data.strands);
      }
    } catch (error) {
      
    } finally {
      setLoading(false);
    }
  };

  const navigateToSubstrands = async (strand: Entity) => {
    const newBreadcrumbs = [...breadcrumbs, { type: 'strands' as EntityType, id: strand.id, name: strand.name || '' }];
    setBreadcrumbs(newBreadcrumbs);
    setCurrentParentId(strand.id);
    setSelectedEntity('substrands');
    setLoading(true);
    // Reset stats — they're scoped to the strand we're entering.
    setSubstrandKiqStats({});
    try {
      const headers = await getHeaders();
      const response = await axios.get(`${BACKEND_URL}/api/admin/substrands?strandId=${strand.id}`, { headers });
      if (response.data.success) {
        setData(response.data.substrands);
      }
      // Fetch KIQ coverage stats in parallel — best-effort, doesn't block
      // the list from rendering. Used by the substrand row badge.
      try {
        const statsRes = await axios.get(
          `${BACKEND_URL}/api/admin/strands/${strand.id}/kiq-stats`,
          { headers },
        );
        if (statsRes.data?.success) {
          setSubstrandKiqStats(statsRes.data.stats || {});
        }
      } catch {
        // non-fatal — list still renders, badge just won't show
      }
    } catch (error) {
      
    } finally {
      setLoading(false);
    }
  };

  const navigateToSlosAndActivities = async (substrand: Entity) => {
    const newBreadcrumbs = [...breadcrumbs, { type: 'substrands' as EntityType, id: substrand.id, name: substrand.name || '' }];
    setBreadcrumbs(newBreadcrumbs);
    setCurrentParentId(substrand.id);
    setSelectedEntity('slos');
    setLoading(true);
    try {
      const headers = await getHeaders();
      const response = await axios.get(`${BACKEND_URL}/api/admin/slos?substrandId=${substrand.id}`, { headers });
      if (response.data.success) {
        setData(response.data.slos);
      }
    } catch (error) {
      
    } finally {
      setLoading(false);
    }
  };

  const navigateToBreadcrumb = (index: number) => {
    if (index === -1) {
      // Go to main view
      setCurrentView('main');
      setBreadcrumbs([]);
      return;
    }
    
    const crumb = breadcrumbs[index];
    const newBreadcrumbs = breadcrumbs.slice(0, index);
    setBreadcrumbs(newBreadcrumbs);
    
    if (crumb.type === 'grades') {
      navigateToSubjects({ id: crumb.id, name: crumb.name });
    } else if (crumb.type === 'subjects') {
      navigateToStrands({ id: crumb.id, name: crumb.name });
    } else if (crumb.type === 'strands') {
      navigateToSubstrands({ id: crumb.id, name: crumb.name });
    }
  };

  // Back button navigation - goes to previous level in hierarchy
  const navigateBack = () => {
    if (breadcrumbs.length === 0) {
      // Already at grades, do nothing
      return;
    }
    
    if (breadcrumbs.length === 1) {
      // On subjects, go back to grades
      setBreadcrumbs([]);
      setSelectedEntity('grades');
      setCurrentParentId('');
      setData(grades);
    } else {
      // Go back one level
      const previousCrumb = breadcrumbs[breadcrumbs.length - 2];
      const newBreadcrumbs = breadcrumbs.slice(0, -1);
      setBreadcrumbs(newBreadcrumbs);
      
      // Navigate to the previous level
      if (selectedEntity === 'slos') {
        // Going back from SLOs to substrands
        const strand = newBreadcrumbs.find(b => b.type === 'strands');
        if (strand) {
          navigateToSubstrands({ id: strand.id, name: strand.name });
        }
      } else if (selectedEntity === 'substrands') {
        // Going back from substrands to strands
        const subject = newBreadcrumbs.find(b => b.type === 'subjects');
        if (subject) {
          navigateToStrands({ id: subject.id, name: subject.name });
        }
      } else if (selectedEntity === 'strands') {
        // Going back from strands to subjects
        const grade = newBreadcrumbs.find(b => b.type === 'grades');
        if (grade) {
          navigateToSubjects({ id: grade.id, name: grade.name });
        }
      } else if (selectedEntity === 'subjects') {
        // Going back from subjects to grades
        setBreadcrumbs([]);
        setSelectedEntity('grades');
        setCurrentParentId('');
        setData(grades);
      }
    }
  };

  const openAddModal = () => {
    setEditingItem(null);
    setFormData({});
    setSelectedParentId(currentParentId || '');
    setModalVisible(true);
  };

  const openEditModal = (item: Entity) => {
    setEditingItem(item);
    const initialData: Record<string, string> = {};
    ENTITY_CONFIG[selectedEntity].fields.forEach(field => {
      const raw = (item as any)[field];
      // KIQs are stored as an array on the SLO row; render them as one
      // question per line in the textarea so admins can edit naturally.
      if (field === 'key_inquiry_questions' && Array.isArray(raw)) {
        initialData[field] = raw.join('\n');
      } else {
        initialData[field] = raw?.toString() || '';
      }
    });
    setFormData(initialData);
    
    // Set parent ID for editing
    if (item.subjectId) setSelectedParentId(item.subjectId);
    else if (item.strandId) setSelectedParentId(item.strandId);
    else if (item.substrandId) setSelectedParentId(item.substrandId);
    else if (item.gradeIds && item.gradeIds.length > 0) setSelectedParentId(item.gradeIds[0]);
    
    setModalVisible(true);
  };

  const openLearningActivitiesModal = async (substrand: Entity) => {
    setCurrentSubstrandForActivities(substrand);
    setLoading(true);
    
    try {
      const headers = await getHeaders();
      const response = await axios.get(
        `${BACKEND_URL}/api/admin/learning-activities/by-substrand/${substrand.id}`,
        { headers }
      );
      
      if (response.data.success && response.data.exists) {
        const activity = response.data.learning_activity;
        setExistingActivityId(activity.id);
        setActivitiesFormData({
          introduction_activities: activity.introduction_activities?.length > 0 ? activity.introduction_activities : [''],
          development_activities: activity.development_activities?.length > 0 ? activity.development_activities : [''],
          conclusion_activities: activity.conclusion_activities?.length > 0 ? activity.conclusion_activities : [''],
          extended_activities: activity.extended_activities?.length > 0 ? activity.extended_activities : ['']
        });
      } else {
        setExistingActivityId(null);
        setActivitiesFormData({
          introduction_activities: [''],
          development_activities: [''],
          conclusion_activities: [''],
          extended_activities: ['']
        });
      }
    } catch (error) {
      
      setExistingActivityId(null);
      setActivitiesFormData({
        introduction_activities: [''],
        development_activities: [''],
        conclusion_activities: [''],
        extended_activities: ['']
      });
    } finally {
      setLoading(false);
      setLearningActivitiesModalVisible(true);
    }
  };

  // ── Substrand Lessons Configuration ──
  const openLessonsConfigModal = async (substrand: Entity) => {
    setLessonsSubstrand(substrand);
    setLessonsLoading(true);
    setLessonsModalVisible(true);
    try {
      const headers = await getHeaders();
      // Fetch existing lessons
      const res = await axios.get(
        `${BACKEND_URL}/api/substrands/${substrand.id}/lessons`,
        { headers }
      );
      if (res.data.success) {
        setSubstrandLessons(res.data.lessons || []);
      }
    } catch (_) {
      setSubstrandLessons([]);
    } finally {
      setLessonsLoading(false);
    }
  };

  const handleGenerateLessonSlots = async () => {
    if (!lessonsSubstrand) return;
    setLessonsLoading(true);
    try {
      const headers = await getHeaders();
      const res = await axios.post(
        `${BACKEND_URL}/api/substrands/${lessonsSubstrand.id}/lessons/generate`,
        {},
        { headers }
      );
      if (res.data.success) {
        setSubstrandLessons(res.data.lessons || []);
        Alert.alert('Success', res.data.message);
      }
    } catch (err: any) {
      Alert.alert('Error', err.response?.data?.detail || 'Failed to generate lesson slots');
    } finally {
      setLessonsLoading(false);
    }
  };

  const handleUpdateLessonOutcome = (lessonIndex: number, outcomeIndex: number, text: string) => {
    setSubstrandLessons(prev => {
      const updated = [...prev];
      const lesson = { ...updated[lessonIndex] };
      const outcomes = [...(lesson.specific_outcomes || [])];
      outcomes[outcomeIndex] = text;
      lesson.specific_outcomes = outcomes;
      updated[lessonIndex] = lesson;
      return updated;
    });
  };

  const handleAddOutcome = (lessonIndex: number) => {
    setSubstrandLessons(prev => {
      const updated = [...prev];
      const lesson = { ...updated[lessonIndex] };
      if ((lesson.specific_outcomes || []).length >= 2) return prev;
      lesson.specific_outcomes = [...(lesson.specific_outcomes || []), ''];
      updated[lessonIndex] = lesson;
      return updated;
    });
  };

  const handleRemoveOutcome = (lessonIndex: number, outcomeIndex: number) => {
    setSubstrandLessons(prev => {
      const updated = [...prev];
      const lesson = { ...updated[lessonIndex] };
      lesson.specific_outcomes = (lesson.specific_outcomes || []).filter((_: string, i: number) => i !== outcomeIndex);
      updated[lessonIndex] = lesson;
      return updated;
    });
  };

  const handleSaveLessons = async () => {
    if (!lessonsSubstrand) return;
    setLessonsLoading(true);
    try {
      const headers = await getHeaders();
      let saved = 0;
      for (const lesson of substrandLessons) {
        const outcomes = (lesson.specific_outcomes || []).filter((o: string) => o.trim());
        if (outcomes.length === 0) continue;
        await axios.patch(
          `${BACKEND_URL}/api/substrand-lessons/${lesson.id}`,
          {
            substrand_id: lessonsSubstrand.id,
            lesson_number: lesson.lesson_number,
            specific_outcomes: outcomes,
          },
          { headers }
        );
        saved++;
      }
      Alert.alert('Saved', `Updated ${saved} lesson(s) successfully.`);
    } catch (err: any) {
      Alert.alert('Error', err.response?.data?.detail || 'Failed to save lessons');
    } finally {
      setLessonsLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      const headers = await getHeaders();
      const config = ENTITY_CONFIG[selectedEntity];
      
      let payload: any = { ...formData };
      
      // Add parent relationships
      if (selectedEntity === 'subjects' && (selectedParentId || currentParentId)) {
        payload.gradeIds = [selectedParentId || currentParentId];
      } else if (selectedEntity === 'strands' && (selectedParentId || currentParentId)) {
        payload.subjectId = selectedParentId || currentParentId;
      } else if (selectedEntity === 'substrands' && (selectedParentId || currentParentId)) {
        payload.strandId = selectedParentId || currentParentId;
        if (payload.number_of_lessons) {
          payload.number_of_lessons = parseInt(payload.number_of_lessons);
        }
      } else if (selectedEntity === 'slos' && (selectedParentId || currentParentId)) {
        payload.substrandId = selectedParentId || currentParentId;
      }

      // KIQs (SLO only) come from the textarea as a newline-joined string;
      // split, trim, and drop empties before sending to the API. Pulled out
      // of the parent-relationship block above so it always runs on SLO
      // edit/create regardless of whether a new parent was picked.
      if (selectedEntity === 'slos') {
        if (typeof payload.key_inquiry_questions === 'string') {
          payload.key_inquiry_questions = payload.key_inquiry_questions
            .split('\n')
            .map((q: string) => q.trim())
            .filter((q: string) => q.length > 0);
        } else if (!Array.isArray(payload.key_inquiry_questions)) {
          payload.key_inquiry_questions = [];
        }
      }
      
      // Convert order to number if present
      if (payload.order) {
        payload.order = parseInt(payload.order);
      }

      if (editingItem) {
        // Update
        await axios.put(
          `${BACKEND_URL}/api/admin/${config.apiPath}/${editingItem.id}`,
          payload,
          { headers }
        );
        showAlert('Success', 'Updated successfully');
      } else {
        // Create
        await axios.post(
          `${BACKEND_URL}/api/admin/${config.apiPath}`,
          payload,
          { headers }
        );
        showAlert('Success', 'Created successfully');
      }
      
      setModalVisible(false);
      
      // Reload data based on current view
      if (currentView === 'hierarchy' && currentParentId) {
        // Reload hierarchy data
        if (selectedEntity === 'subjects') {
          const grade = breadcrumbs.find(b => b.type === 'grades');
          if (grade) navigateToSubjects({ id: grade.id, name: grade.name });
        } else if (selectedEntity === 'strands') {
          const subject = breadcrumbs.find(b => b.type === 'subjects');
          if (subject) navigateToStrands({ id: subject.id, name: subject.name });
        } else if (selectedEntity === 'substrands') {
          const strand = breadcrumbs.find(b => b.type === 'strands');
          if (strand) navigateToSubstrands({ id: strand.id, name: strand.name });
        } else if (selectedEntity === 'slos') {
          const substrand = breadcrumbs.find(b => b.type === 'substrands');
          if (substrand) navigateToSlosAndActivities({ id: substrand.id, name: substrand.name });
        }
      } else {
        loadData();
      }
    } catch (error: any) {
      
      showAlert('Error', error.response?.data?.detail || 'Failed to save');
    }
  };

  const handleSaveLearningActivities = async () => {
    if (!currentSubstrandForActivities) return;
    
    try {
      const headers = await getHeaders();
      
      // Filter out empty strings
      const payload = {
        substrandId: currentSubstrandForActivities.id,
        introduction_activities: activitiesFormData.introduction_activities.filter(a => a.trim() !== ''),
        development_activities: activitiesFormData.development_activities.filter(a => a.trim() !== ''),
        conclusion_activities: activitiesFormData.conclusion_activities.filter(a => a.trim() !== ''),
        extended_activities: activitiesFormData.extended_activities.filter(a => a.trim() !== '')
      };
      
      // Use upsert endpoint
      await axios.put(
        `${BACKEND_URL}/api/admin/learning-activities/by-substrand/${currentSubstrandForActivities.id}`,
        payload,
        { headers }
      );
      
      showAlert('Success', 'Learning activities saved successfully');
      setLearningActivitiesModalVisible(false);
    } catch (error: any) {
      
      showAlert('Error', error.response?.data?.detail || 'Failed to save learning activities');
    }
  };

  const handleDelete = (item: Entity) => {
    showAlert(
      'Confirm Delete',
      `Are you sure you want to delete "${item.name || item.description}"?`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              const headers = await getHeaders();
              const config = ENTITY_CONFIG[selectedEntity];
              await axios.delete(
                `${BACKEND_URL}/api/admin/${config.apiPath}/${item.id}`,
                { headers }
              );
              showAlert('Success', 'Deleted successfully');
              
              if (currentView === 'hierarchy') {
                // Reload hierarchy data
                const lastBreadcrumb = breadcrumbs[breadcrumbs.length - 1];
                if (lastBreadcrumb) {
                  if (selectedEntity === 'slos') {
                    navigateToSlosAndActivities({ id: lastBreadcrumb.id, name: lastBreadcrumb.name });
                  } else if (selectedEntity === 'substrands') {
                    const strand = breadcrumbs.find(b => b.type === 'strands');
                    if (strand) navigateToSubstrands({ id: strand.id, name: strand.name });
                  }
                }
              } else {
                loadData();
              }
            } catch (error: any) {
              showAlert('Error', error.response?.data?.detail || 'Failed to delete');
            }
          }
        }
      ]
    );
  };

  const addActivityField = (type: keyof typeof activitiesFormData) => {
    setActivitiesFormData(prev => ({
      ...prev,
      [type]: [...prev[type], '']
    }));
  };

  // Load all curriculum data for move modal
  const loadAllCurriculumData = async () => {
    try {
      const headers = await getHeaders();
      
      const [gradesRes, subjectsRes, strandsRes, substrandsRes] = await Promise.all([
        axios.get(`${BACKEND_URL}/api/admin/grades`, { headers }),
        axios.get(`${BACKEND_URL}/api/admin/subjects`, { headers }),
        axios.get(`${BACKEND_URL}/api/admin/strands`, { headers }),
        axios.get(`${BACKEND_URL}/api/admin/substrands`, { headers })
      ]);
      
      setAllGrades(gradesRes.data.grades || []);
      setAllSubjects(subjectsRes.data.subjects || []);
      setAllStrands(strandsRes.data.strands || []);
      setAllSubstrands(substrandsRes.data.substrands || []);
    } catch (error) {
      
    }
  };

  // Open move modal
  const handleOpenMoveModal = async (item: Entity) => {
    setMovingItem(item);
    setMoveTargetGrade('');
    setMoveTargetSubject('');
    setMoveTargetStrand('');
    setMoveTargetSubstrand('');
    await loadAllCurriculumData();
    setMoveModalVisible(true);
  };

  // Execute move
  const handleExecuteMove = async () => {
    if (!movingItem) return;
    
    try {
      const headers = await getHeaders();
      let endpoint = '';
      let payload: any = {};
      
      if (selectedEntity === 'strands') {
        if (!moveTargetSubject) {
          showAlert('Error', 'Please select a target subject');
          return;
        }
        endpoint = `${BACKEND_URL}/api/admin/strands/${movingItem.id}/move`;
        payload = { targetSubjectId: moveTargetSubject };
      } else if (selectedEntity === 'substrands') {
        if (!moveTargetStrand) {
          showAlert('Error', 'Please select a target strand');
          return;
        }
        endpoint = `${BACKEND_URL}/api/admin/substrands/${movingItem.id}/move`;
        payload = { targetStrandId: moveTargetStrand };
      } else if (selectedEntity === 'slos') {
        if (!moveTargetSubstrand) {
          showAlert('Error', 'Please select a target sub-strand');
          return;
        }
        endpoint = `${BACKEND_URL}/api/admin/slos/${movingItem.id}/move`;
        payload = { targetSubstrandId: moveTargetSubstrand };
      } else if (selectedEntity === 'subjects') {
        if (!moveTargetGrade) {
          showAlert('Error', 'Please select a target grade');
          return;
        }
        endpoint = `${BACKEND_URL}/api/admin/subjects/${movingItem.id}/change-grade`;
        payload = { targetGradeId: moveTargetGrade, removeFromOtherGrades: true };
      } else {
        showAlert('Error', 'Cannot move this type of item');
        return;
      }
      
      const response = await axios.put(endpoint, payload, { headers });
      
      if (response.data.success) {
        showAlert('Success', response.data.message);
        setMoveModalVisible(false);
        if (currentView === 'hierarchy') {
          // Refresh hierarchy
          const lastBreadcrumb = breadcrumbs[breadcrumbs.length - 1];
          if (lastBreadcrumb) {
            if (selectedEntity === 'slos') {
              navigateToSlosAndActivities({ id: lastBreadcrumb.id, name: lastBreadcrumb.name });
            } else if (selectedEntity === 'substrands') {
              const strand = breadcrumbs.find(b => b.type === 'strands');
              if (strand) navigateToSubstrands({ id: strand.id, name: strand.name });
            } else if (selectedEntity === 'strands') {
              const subject = breadcrumbs.find(b => b.type === 'subjects');
              if (subject) navigateToStrands({ id: subject.id, name: subject.name });
            }
          }
        } else {
          loadData();
        }
      }
    } catch (error: any) {
      showAlert('Error', error.response?.data?.detail || 'Failed to move item');
    }
  };

  // Open bulk add modal
  const handleOpenBulkAddModal = () => {
    setBulkTextValue('');
    setBulkTableRows([
      { name: '', description: '' },
      { name: '', description: '' },
      { name: '', description: '' }
    ]);
    setBulkAddModalVisible(true);
  };

  // Add row to bulk table
  const addBulkTableRow = () => {
    setBulkTableRows([...bulkTableRows, { name: '', description: '' }]);
  };

  // Update bulk table row
  const updateBulkTableRow = (index: number, field: 'name' | 'description', value: string) => {
    const newRows = [...bulkTableRows];
    newRows[index][field] = value;
    setBulkTableRows(newRows);
  };

  // Remove bulk table row
  const removeBulkTableRow = (index: number) => {
    if (bulkTableRows.length > 1) {
      setBulkTableRows(bulkTableRows.filter((_, i) => i !== index));
    }
  };

  // Execute bulk add
  const handleExecuteBulkAdd = async () => {
    let items: { name: string; description?: string }[] = [];
    
    if (bulkAddMode === 'textarea') {
      items = bulkTextValue
        .split('\n')
        .map(line => line.trim())
        .filter(line => line.length > 0)
        .map(name => ({ name }));
    } else {
      items = bulkTableRows
        .filter(row => row.name.trim().length > 0)
        .map(row => ({
          name: row.name.trim(),
          description: row.description.trim() || undefined
        }));
    }
    
    if (items.length === 0) {
      showAlert('Error', 'Please enter at least one item');
      return;
    }
    
    try {
      const headers = await getHeaders();
      const config = ENTITY_CONFIG[selectedEntity];
      
      // Use the appropriate parent ID
      let parentId = currentParentId;
      if (!parentId) {
        showAlert('Error', 'Please select a parent first');
        return;
      }
      
      const response = await axios.post(
        `${BACKEND_URL}/api/admin/${config.apiPath}/bulk`,
        { items, parentId },
        { headers }
      );
      
      if (response.data.success) {
        showAlert('Success', `Created ${response.data.createdIds?.length || items.length} items`);
        setBulkAddModalVisible(false);
        
        // Refresh data
        if (currentView === 'hierarchy') {
          const lastBreadcrumb = breadcrumbs[breadcrumbs.length - 1];
          if (lastBreadcrumb) {
            if (selectedEntity === 'slos') {
              navigateToSlosAndActivities({ id: lastBreadcrumb.id, name: lastBreadcrumb.name });
            } else if (selectedEntity === 'substrands') {
              const strand = breadcrumbs.find(b => b.type === 'strands');
              if (strand) navigateToSubstrands({ id: strand.id, name: strand.name });
            } else if (selectedEntity === 'strands') {
              const subject = breadcrumbs.find(b => b.type === 'subjects');
              if (subject) navigateToStrands({ id: subject.id, name: subject.name });
            } else if (selectedEntity === 'subjects') {
              const grade = breadcrumbs.find(b => b.type === 'grades');
              if (grade) navigateToSubjects({ id: grade.id, name: grade.name });
            }
          }
        } else {
          loadData();
        }
      }
    } catch (error: any) {
      showAlert('Error', error.response?.data?.detail || 'Failed to create items');
    }
  };

  // Get filtered subjects for move modal
  const getFilteredSubjectsForMove = () => {
    if (!moveTargetGrade) return allSubjects;
    return allSubjects.filter(s => {
      const gids = s.gradeIds;
      if (Array.isArray(gids)) return gids.includes(moveTargetGrade);
      if (typeof gids === 'string') return gids === moveTargetGrade;
      return false;
    });
  };

  // Get filtered strands for move modal — use dynamically fetched data
  const getFilteredStrandsForMove = () => {
    if (moveTargetSubject && moveStrandsForSubject.length > 0) {
      return moveStrandsForSubject;
    }
    if (!moveTargetSubject) return allStrands;
    return allStrands.filter(s => s.subjectId === moveTargetSubject);
  };

  // Get filtered substrands for move modal — use dynamically fetched data
  const getFilteredSubstrandsForMove = () => {
    if (moveTargetStrand && moveSubstrandsForStrand.length > 0) {
      return moveSubstrandsForStrand;
    }
    if (!moveTargetStrand) return allSubstrands;
    return allSubstrands.filter(s => s.strandId === moveTargetStrand);
  };

  // Fetch strands for a specific subject (dynamic, for move modal)
  const fetchStrandsForSubject = async (subjectId: string) => {
    try {
      const headers = await getHeaders();
      const res = await axios.get(`${BACKEND_URL}/api/admin/strands?subjectId=${subjectId}`, { headers });
      setMoveStrandsForSubject(res.data.strands || []);
    } catch { setMoveStrandsForSubject([]); }
  };

  // Fetch substrands for a specific strand (dynamic, for move modal)
  const fetchSubstrandsForStrand = async (strandId: string) => {
    try {
      const headers = await getHeaders();
      const res = await axios.get(`${BACKEND_URL}/api/admin/substrands?strandId=${strandId}`, { headers });
      setMoveSubstrandsForStrand(res.data.substrands || []);
    } catch { setMoveSubstrandsForStrand([]); }
  };

  // ==================== SLO MAPPING FUNCTIONS ====================

  // Load reference data (competencies, values, PCIs)
  const loadReferenceData = async () => {
    try {
      const headers = await getHeaders();
      const response = await axios.get(`${BACKEND_URL}/api/admin/reference-data`, { headers });
      if (response.data.success) {
        setAllCompetencies(response.data.competencies || []);
        setAllValues(response.data.values || []);
        setAllPcis(response.data.pcis || []);
      }
    } catch (error) {
      
    }
  };

  // Open single SLO mapping editor
  const handleOpenMappingModal = async (slo: Entity) => {
    setMappingSlo(slo);
    setSelectedCompetencies([]);
    setSelectedValues([]);
    setSelectedPcis([]);
    
    await loadReferenceData();
    
    // Load existing mapping
    try {
      const headers = await getHeaders();
      const response = await axios.get(`${BACKEND_URL}/api/admin/slo-mappings/${slo.id}`, { headers });
      if (response.data.success && response.data.mapping) {
        const mapping = response.data.mapping;
        setSelectedCompetencies(mapping.competencyIds || []);
        setSelectedValues(mapping.valueIds || []);
        setSelectedPcis(mapping.pciIds || []);
      }
    } catch (error) {
      
    }
    
    setMappingModalVisible(true);
  };

  // Save single SLO mapping
  const handleSaveSloMapping = async () => {
    if (!mappingSlo) return;
    
    try {
      const headers = await getHeaders();
      const payload = {
        sloId: mappingSlo.id,
        competencyIds: selectedCompetencies,
        valueIds: selectedValues,
        pciIds: selectedPcis,
        assessmentIds: []
      };
      
      await axios.post(`${BACKEND_URL}/api/admin/slo-mappings`, payload, { headers });
      showAlert('Success', 'SLO mapping saved successfully');
      setMappingModalVisible(false);
    } catch (error: any) {
      showAlert('Error', error.response?.data?.detail || 'Failed to save mapping');
    }
  };

  // Toggle checkbox selection
  const toggleSelection = (id: string, current: string[], setter: (val: string[]) => void) => {
    if (current.includes(id)) {
      setter(current.filter(i => i !== id));
    } else {
      setter([...current, id]);
    }
  };

  // Open bulk mapping editor
  const handleOpenBulkMappingModal = async () => {
    setSelectedSlosForMapping([]);
    setBulkSelectedCompetencies([]);
    setBulkSelectedValues([]);
    setBulkSelectedPcis([]);
    await loadReferenceData();
    setBulkMappingModalVisible(true);
  };

  // Toggle SLO selection for bulk mapping
  const toggleSloSelection = (sloId: string) => {
    if (selectedSlosForMapping.includes(sloId)) {
      setSelectedSlosForMapping(selectedSlosForMapping.filter(id => id !== sloId));
    } else {
      setSelectedSlosForMapping([...selectedSlosForMapping, sloId]);
    }
  };

  // Select all SLOs for bulk mapping
  const selectAllSlos = () => {
    const sloIds = data.filter(item => selectedEntity === 'slos').map(item => item.id);
    setSelectedSlosForMapping(sloIds);
  };

  // Deselect all SLOs
  const deselectAllSlos = () => {
    setSelectedSlosForMapping([]);
  };

  // Save bulk SLO mappings
  const handleSaveBulkMapping = async () => {
    if (selectedSlosForMapping.length === 0) {
      showAlert('Error', 'Please select at least one SLO');
      return;
    }
    
    try {
      const headers = await getHeaders();
      const payload = {
        sloIds: selectedSlosForMapping,
        competencyIds: bulkSelectedCompetencies,
        valueIds: bulkSelectedValues,
        pciIds: bulkSelectedPcis
      };
      
      const response = await axios.put(`${BACKEND_URL}/api/admin/slo-mappings/bulk`, payload, { headers });
      
      if (response.data.success) {
        showAlert('Success', response.data.message);
        setBulkMappingModalVisible(false);
      }
    } catch (error: any) {
      showAlert('Error', error.response?.data?.detail || 'Failed to save mappings');
    }
  };

  const removeActivityField = (type: keyof typeof activitiesFormData, index: number) => {
    setActivitiesFormData(prev => ({
      ...prev,
      [type]: prev[type].filter((_, i) => i !== index)
    }));
  };

  const updateActivityField = (type: keyof typeof activitiesFormData, index: number, value: string) => {
    setActivitiesFormData(prev => ({
      ...prev,
      [type]: prev[type].map((item, i) => i === index ? value : item)
    }));
  };

  const getParentOptions = () => {
    switch (selectedEntity) {
      case 'subjects': return grades;
      case 'strands': return subjects;
      case 'substrands': return strands;
      case 'slos':
      case 'learning_activities': return substrands;
      default: return [];
    }
  };

  const getParentLabel = () => {
    switch (selectedEntity) {
      case 'subjects': return 'Select Grade';
      case 'strands': return 'Select Subject';
      case 'substrands': return 'Select Strand';
      case 'slos':
      case 'learning_activities': return 'Select Sub-strand';
      default: return '';
    }
  };

  const handleItemPress = (item: Entity) => {
    if (currentView === 'hierarchy') {
      if (selectedEntity === 'grades') {
        navigateToSubjects(item);
      } else if (selectedEntity === 'subjects') {
        navigateToStrands(item);
      } else if (selectedEntity === 'strands') {
        navigateToSubstrands(item);
      } else if (selectedEntity === 'substrands') {
        navigateToSlosAndActivities(item);
      }
    }
  };

  // ==================== BULK EDIT FUNCTIONS ====================

  const toggleItemSelection = (itemId: string) => {
    const newSelected = new Set(selectedItems);
    if (newSelected.has(itemId)) {
      newSelected.delete(itemId);
    } else {
      newSelected.add(itemId);
    }
    setSelectedItems(newSelected);
  };

  const toggleSelectAll = () => {
    if (selectedItems.size === data.length) {
      setSelectedItems(new Set());
    } else {
      setSelectedItems(new Set(data.map(item => item.id)));
    }
  };

  const handleBulkDelete = async () => {
    if (selectedItems.size === 0) return;
    
    const itemType = selectedEntity === 'strands' ? 'strand' 
      : selectedEntity === 'substrands' ? 'substrand' 
      : selectedEntity === 'slos' ? 'slo' : '';
    
    if (!itemType) {
      showAlert('Error', 'Bulk delete is only available for strands, substrands, and SLOs');
      return;
    }
    
    const confirmDelete = () => {
      performBulkDelete(itemType);
    };
    
    showAlert(
      'Confirm Bulk Delete',
      `Are you sure you want to delete ${selectedItems.size} ${selectedEntity}? This will also delete all child items.`,
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Delete', style: 'destructive', onPress: confirmDelete }
      ]
    );
  };

  const performBulkDelete = async (itemType: string) => {
    try {
      setLoading(true);
      const headers = await getHeaders();
      const response = await axios.post(`${BACKEND_URL}/api/admin/bulk-delete`, {
        item_type: itemType,
        item_ids: Array.from(selectedItems)
      }, { headers });
      
      if (response.data.success) {
        showAlert('Success', response.data.message);
        setSelectedItems(new Set());
        setBulkEditMode(false);
        loadData();
      }
    } catch (error: any) {
      showAlert('Error', error.response?.data?.detail || 'Failed to delete items');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenBulkEditModal = () => {
    if (selectedItems.size === 0) return;
    setBulkEditFormData({});
    setBulkEditModalVisible(true);
  };

  const handleSaveBulkEdit = async () => {
    if (Object.keys(bulkEditFormData).length === 0) {
      showAlert('Error', 'Please enter at least one field to update');
      return;
    }
    
    const itemType = selectedEntity === 'strands' ? 'strand' 
      : selectedEntity === 'substrands' ? 'substrand' 
      : selectedEntity === 'slos' ? 'slo' : '';
    
    if (!itemType) {
      showAlert('Error', 'Bulk edit is only available for strands, substrands, and SLOs');
      return;
    }
    
    try {
      setLoading(true);
      const headers = await getHeaders();
      const response = await axios.post(`${BACKEND_URL}/api/admin/bulk-update`, {
        item_type: itemType,
        item_ids: Array.from(selectedItems),
        updates: bulkEditFormData
      }, { headers });
      
      if (response.data.success) {
        showAlert('Success', response.data.message);
        setBulkEditModalVisible(false);
        setSelectedItems(new Set());
        setBulkEditMode(false);
        loadData();
      }
    } catch (error: any) {
      showAlert('Error', error.response?.data?.detail || 'Failed to update items');
    } finally {
      setLoading(false);
    }
  };

  // ==================== REORDER FUNCTIONS ====================

  const handleMoveItem = async (item: Entity, direction: 'up' | 'down') => {
    const itemType = selectedEntity === 'strands' ? 'strand' 
      : selectedEntity === 'substrands' ? 'substrand' 
      : selectedEntity === 'slos' ? 'slo' : '';
    
    if (!itemType) return;
    
    try {
      setLoading(true);
      const headers = await getHeaders();
      const response = await axios.post(
        `${BACKEND_URL}/api/admin/move-item-order?item_type=${itemType}&item_id=${item.id}&direction=${direction}`,
        {},
        { headers }
      );
      
      if (response.data.success) {
        // Auto-refresh: Use refreshCurrentView for proper refresh in all views
        await refreshCurrentView();
      } else {
        showAlert('Info', response.data.message);
      }
    } catch (error: any) {
      showAlert('Error', error.response?.data?.detail || 'Failed to move item');
    } finally {
      setLoading(false);
    }
  };

  const canReorder = selectedEntity === 'strands' || selectedEntity === 'substrands' || selectedEntity === 'slos';

  const renderItem = ({ item }: { item: Entity }) => {
    const config = ENTITY_CONFIG[selectedEntity];
    const canNavigate = currentView === 'hierarchy' && selectedEntity !== 'slos';
    const canMove = selectedEntity !== 'grades' && selectedEntity !== 'competencies' && selectedEntity !== 'values' && selectedEntity !== 'pcis' && selectedEntity !== 'learning_activities';
    const canEditMapping = selectedEntity === 'slos';
    const isSelected = selectedItems.has(item.id);
    
    return (
      <View style={styles.listItem}>
        {/* Bulk Edit Checkbox */}
        {bulkEditMode && (
          <TouchableOpacity 
            style={styles.checkboxContainer}
            onPress={() => toggleItemSelection(item.id)}
          >
            <View style={[styles.checkbox, isSelected && styles.checkboxSelected]}>
              {isSelected && <Ionicons name="checkmark" size={14} color="#FFFFFF" />}
            </View>
          </TouchableOpacity>
        )}
        
        {/* Reorder Buttons */}
        {canReorder && !bulkEditMode && (
          <View style={styles.reorderButtons}>
            <TouchableOpacity 
              style={styles.reorderBtn}
              onPress={() => handleMoveItem(item, 'up')}
            >
              <Ionicons name="chevron-up" size={16} color="#5C6BC0" />
            </TouchableOpacity>
            <TouchableOpacity 
              style={styles.reorderBtn}
              onPress={() => handleMoveItem(item, 'down')}
            >
              <Ionicons name="chevron-down" size={16} color="#5C6BC0" />
            </TouchableOpacity>
          </View>
        )}
        
        <TouchableOpacity 
          style={[styles.listItemContent, bulkEditMode && { flex: 1 }]}
          onPress={() => bulkEditMode ? toggleItemSelection(item.id) : (canNavigate ? handleItemPress(item) : null)}
          activeOpacity={canNavigate || bulkEditMode ? 0.7 : 1}
        >
          <View style={[styles.itemIcon, { backgroundColor: config.color + '20' }]}>
            <Ionicons name={config.icon as any} size={20} color={config.color} />
          </View>
          <View style={styles.itemContent}>
            <Text style={styles.itemName}>{item.name || item.description}</Text>
            {item.description && item.name && (
              <Text style={styles.itemDescription} numberOfLines={2}>{item.description}</Text>
            )}
            {item.order !== undefined && (
              <Text style={styles.itemMeta}>Order: {item.order}</Text>
            )}
            {/* Substrand KIQ-coverage badge — red when at least one of
                the substrand's SLOs is missing Key Inquiry Questions, so
                admins can spot weak substrands without drilling all the
                way down to each SLO row. Hidden when stats haven't loaded
                yet or when the substrand has zero SLOs. */}
            {selectedEntity === 'substrands' && substrandKiqStats[item.id] && substrandKiqStats[item.id].total > 0 && (
              <View style={{ flexDirection: 'row', alignItems: 'center', marginTop: 4 }}>
                <Ionicons
                  name={substrandKiqStats[item.id].missing > 0 ? 'alert-circle' : 'checkmark-circle'}
                  size={12}
                  color={substrandKiqStats[item.id].missing > 0 ? '#DC2626' : '#10B981'}
                />
                <Text style={{
                  fontSize: 11,
                  marginLeft: 4,
                  color: substrandKiqStats[item.id].missing > 0 ? '#DC2626' : '#10B981',
                  fontWeight: '600',
                }}>
                  {substrandKiqStats[item.id].missing > 0
                    ? `${substrandKiqStats[item.id].missing} of ${substrandKiqStats[item.id].total} SLOs missing KIQs`
                    : `All ${substrandKiqStats[item.id].total} SLOs have KIQs`}
                </Text>
              </View>
            )}
            {/* KIQ status badge — only on SLO rows so admins can see at a
                glance which SLOs already have Key Inquiry Questions stored
                and which need to be filled in via the Edit modal. */}
            {selectedEntity === 'slos' && (
              <View style={{ flexDirection: 'row', alignItems: 'center', marginTop: 4 }}>
                <Ionicons
                  name={Array.isArray(item.key_inquiry_questions) && item.key_inquiry_questions.length > 0 ? 'help-circle' : 'help-circle-outline'}
                  size={12}
                  color={Array.isArray(item.key_inquiry_questions) && item.key_inquiry_questions.length > 0 ? '#10B981' : '#9CA3AF'}
                />
                <Text style={{
                  fontSize: 11,
                  marginLeft: 4,
                  color: Array.isArray(item.key_inquiry_questions) && item.key_inquiry_questions.length > 0 ? '#10B981' : '#9CA3AF',
                  fontWeight: '600',
                }}>
                  {Array.isArray(item.key_inquiry_questions) && item.key_inquiry_questions.length > 0
                    ? `${item.key_inquiry_questions.length} KIQ${item.key_inquiry_questions.length === 1 ? '' : 's'}`
                    : 'No KIQs — tap Edit to add'}
                </Text>
              </View>
            )}
          </View>
          
          {canNavigate && !bulkEditMode && (
            <Ionicons name="chevron-forward" size={20} color="#9CA3AF" style={{ marginRight: 8 }} />
          )}
        </TouchableOpacity>
        
        {!bulkEditMode && (
          <View style={styles.itemActions}>
            {/* Mapping Button - Only for SLOs */}
            {canEditMapping && (
              <TouchableOpacity style={styles.mappingButton} onPress={() => handleOpenMappingModal(item)}>
                <Ionicons name="link" size={18} color="#5C6BC0" />
              </TouchableOpacity>
            )}
            {canMove && (
              <TouchableOpacity style={styles.moveButton} onPress={() => handleOpenMoveModal(item)}>
                <Ionicons name="swap-horizontal" size={18} color="#5C6BC0" />
              </TouchableOpacity>
            )}
            <TouchableOpacity style={styles.editButton} onPress={() => openEditModal(item)}>
              <Ionicons name="pencil" size={18} color="#F59E0B" />
            </TouchableOpacity>
            <TouchableOpacity style={styles.deleteButton} onPress={() => handleDelete(item)}>
              <Ionicons name="trash" size={18} color="#EF4444" />
            </TouchableOpacity>
          </View>
        )}
      </View>
    );
  };

  const renderActivitySection = (
    title: string, 
    type: keyof typeof activitiesFormData, 
    color: string,
    icon: string
  ) => (
    <View style={styles.activitySection}>
      <View style={styles.activitySectionHeader}>
        <Ionicons name={icon as any} size={20} color={color} />
        <Text style={[styles.activitySectionTitle, { color }]}>{title}</Text>
        <TouchableOpacity 
          style={[styles.addActivityButton, { backgroundColor: color + '20' }]}
          onPress={() => addActivityField(type)}
        >
          <Ionicons name="add" size={18} color={color} />
        </TouchableOpacity>
      </View>
      {activitiesFormData[type].map((activity, index) => (
        <View key={index} style={styles.activityInputRow}>
          <TextInput
            style={styles.activityInput}
            value={activity}
            onChangeText={(text) => updateActivityField(type, index, text)}
            placeholder={`Enter ${title.toLowerCase()} activity ${index + 1}`}
            multiline
            numberOfLines={2}
          />
          {activitiesFormData[type].length > 1 && (
            <TouchableOpacity 
              style={styles.removeActivityButton}
              onPress={() => removeActivityField(type, index)}
            >
              <Ionicons name="close-circle" size={24} color="#EF4444" />
            </TouchableOpacity>
          )}
        </View>
      ))}
    </View>
  );

  return (
    <View style={styles.container}>
      {/* View Toggle */}
      <View style={styles.viewToggle}>
        <TouchableOpacity
          style={[styles.viewToggleButton, currentView === 'main' && styles.viewToggleButtonActive]}
          onPress={() => setCurrentView('main')}
        >
          <Ionicons name="grid" size={18} color={currentView === 'main' ? '#FFFFFF' : '#5C6BC0'} />
          <Text style={[styles.viewToggleText, currentView === 'main' && styles.viewToggleTextActive]}>
            All Data
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.viewToggleButton, currentView === 'hierarchy' && styles.viewToggleButtonActive]}
          onPress={() => {
            setCurrentView('hierarchy');
            setSelectedEntity('grades');
            setBreadcrumbs([]);
            setData(grades);
          }}
        >
          <Ionicons name="git-network" size={18} color={currentView === 'hierarchy' ? '#FFFFFF' : '#5C6BC0'} />
          <Text style={[styles.viewToggleText, currentView === 'hierarchy' && styles.viewToggleTextActive]}>
            Navigate Hierarchy
          </Text>
        </TouchableOpacity>
      </View>

      {/* Breadcrumbs for hierarchy view */}
      {currentView === 'hierarchy' && breadcrumbs.length > 0 && (
        <View style={styles.breadcrumbContainer}>
          <ScrollView horizontal showsHorizontalScrollIndicator={false}>
            <TouchableOpacity 
              style={styles.breadcrumb}
              onPress={() => {
                setBreadcrumbs([]);
                setSelectedEntity('grades');
                setData(grades);
              }}
            >
              <Ionicons name="home" size={16} color="#5C6BC0" />
            </TouchableOpacity>
            {breadcrumbs.map((crumb, index) => (
              <React.Fragment key={crumb.id}>
                <Ionicons name="chevron-forward" size={16} color="#9CA3AF" style={{ marginHorizontal: 4 }} />
                <TouchableOpacity 
                  style={styles.breadcrumb}
                  onPress={() => {
                    const newBreadcrumbs = breadcrumbs.slice(0, index);
                    setBreadcrumbs(newBreadcrumbs);
                    
                    if (crumb.type === 'grades') {
                      navigateToSubjects({ id: crumb.id, name: crumb.name });
                    } else if (crumb.type === 'subjects') {
                      navigateToStrands({ id: crumb.id, name: crumb.name });
                    } else if (crumb.type === 'strands') {
                      navigateToSubstrands({ id: crumb.id, name: crumb.name });
                    } else if (crumb.type === 'substrands') {
                      navigateToSlosAndActivities({ id: crumb.id, name: crumb.name });
                    }
                  }}
                >
                  <Text style={styles.breadcrumbText} numberOfLines={1}>{crumb.name}</Text>
                </TouchableOpacity>
              </React.Fragment>
            ))}
          </ScrollView>
        </View>
      )}

      {/* Entity Selector - Only show in main view */}
      {currentView === 'main' && (
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.entitySelector}>
          {(Object.keys(ENTITY_CONFIG) as EntityType[])
            .filter(e => e !== 'learning_activities') // Learning activities managed through hierarchy
            .map((entity) => {
            const config = ENTITY_CONFIG[entity];
            const isSelected = selectedEntity === entity;
            return (
              <TouchableOpacity
                key={entity}
                style={[styles.entityTab, isSelected && { backgroundColor: config.color }]}
                onPress={() => setSelectedEntity(entity)}
              >
                <Ionicons 
                  name={config.icon as any} 
                  size={16} 
                  color={isSelected ? '#FFFFFF' : config.color} 
                />
                <Text style={[styles.entityTabText, isSelected && { color: '#FFFFFF' }]}>
                  {config.title}
                </Text>
              </TouchableOpacity>
            );
          })}
        </ScrollView>
      )}

      {/* Header */}
      <View style={styles.header}>
        {/* Back Button - Show in hierarchy view when not on grades */}
        {currentView === 'hierarchy' && selectedEntity !== 'grades' && (
          <TouchableOpacity style={styles.backButton} onPress={navigateBack}>
            <Ionicons name="arrow-back" size={20} color="#5C6BC0" />
          </TouchableOpacity>
        )}
        
        <Text style={styles.headerTitle}>{ENTITY_CONFIG[selectedEntity].title}</Text>
        <Text style={styles.headerCount}>{data.length} items</Text>
        
        {/* Refresh Button */}
        <TouchableOpacity 
          style={styles.refreshButton} 
          onPress={onRefresh}
          disabled={refreshing}
        >
          <Ionicons 
            name="refresh" 
            size={18} 
            color={refreshing ? "#9CA3AF" : "#5C6BC0"} 
          />
        </TouchableOpacity>
        
        {/* Bulk Edit Mode Toggle - Only for strands, substrands, slos */}
        {canReorder && (
          <TouchableOpacity 
            style={[styles.bulkEditToggle, bulkEditMode && styles.bulkEditToggleActive]} 
            onPress={() => {
              setBulkEditMode(!bulkEditMode);
              setSelectedItems(new Set());
            }}
          >
            <Ionicons name={bulkEditMode ? "checkmark-done" : "checkbox-outline"} size={18} color={bulkEditMode ? "#FFFFFF" : "#5C6BC0"} />
            <Text style={[styles.bulkEditToggleText, bulkEditMode && styles.bulkEditToggleTextActive]}>
              {bulkEditMode ? 'Done' : 'Bulk'}
            </Text>
          </TouchableOpacity>
        )}
        
        {/* Bulk Add Button - Show when in hierarchy with parent selected */}
        {currentView === 'hierarchy' && currentParentId && selectedEntity !== 'grades' && !bulkEditMode && (
          <TouchableOpacity style={styles.bulkAddButton} onPress={handleOpenBulkAddModal}>
            <Ionicons name="layers" size={18} color="#10B981" />
            <Text style={styles.bulkAddButtonText}>Add</Text>
          </TouchableOpacity>
        )}
        
        {!bulkEditMode && (
          <TouchableOpacity style={styles.addButton} onPress={openAddModal}>
            <Ionicons name="add" size={24} color="#FFFFFF" />
          </TouchableOpacity>
        )}
      </View>

      {/* Bulk Edit Action Bar */}
      {bulkEditMode && selectedItems.size > 0 && (
        <View style={styles.bulkActionBar}>
          <TouchableOpacity style={styles.selectAllBtn} onPress={toggleSelectAll}>
            <Ionicons 
              name={selectedItems.size === data.length ? "checkbox" : "square-outline"} 
              size={20} 
              color="#5C6BC0" 
            />
            <Text style={styles.selectAllText}>
              {selectedItems.size === data.length ? 'Deselect All' : 'Select All'}
            </Text>
          </TouchableOpacity>
          
          <View style={styles.bulkActionButtons}>
            <Text style={styles.selectedCount}>{selectedItems.size} selected</Text>
            
            <TouchableOpacity style={styles.bulkEditBtn} onPress={handleOpenBulkEditModal}>
              <Ionicons name="pencil" size={18} color="#FFFFFF" />
              <Text style={styles.bulkBtnText}>Edit</Text>
            </TouchableOpacity>
            
            {selectedEntity === 'slos' && (
              <TouchableOpacity 
                style={[styles.bulkEditBtn, { backgroundColor: '#5C6BC0' }]} 
                onPress={() => {
                  setSelectedSlosForMapping(Array.from(selectedItems));
                  handleOpenBulkMappingModal();
                }}
              >
                <Ionicons name="link" size={18} color="#FFFFFF" />
                <Text style={styles.bulkBtnText}>Map</Text>
              </TouchableOpacity>
            )}
            
            <TouchableOpacity style={styles.bulkDeleteBtn} onPress={handleBulkDelete}>
              <Ionicons name="trash" size={18} color="#FFFFFF" />
              <Text style={styles.bulkBtnText}>Delete</Text>
            </TouchableOpacity>
          </View>
        </View>
      )}

      {/* Learning Activities Button - Show when viewing substrands in hierarchy */}
      {currentView === 'hierarchy' && selectedEntity === 'slos' && breadcrumbs.length > 0 && (
        <View style={styles.sloActionsRow}>
          <TouchableOpacity 
            style={styles.learningActivitiesButton}
            onPress={() => {
              const substrand = breadcrumbs.find(b => b.type === 'substrands');
              if (substrand) {
                openLearningActivitiesModal({ id: substrand.id, name: substrand.name });
              }
            }}
          >
            <Ionicons name="flash" size={20} color="#84CC16" />
            <Text style={styles.learningActivitiesButtonText}>Learning Activities</Text>
          </TouchableOpacity>

          <TouchableOpacity 
            style={[styles.learningActivitiesButton, { backgroundColor: '#EFF6FF', borderColor: '#3B82F6' }]}
            onPress={() => {
              const substrand = breadcrumbs.find(b => b.type === 'substrands');
              if (substrand) {
                openLessonsConfigModal(substrand);
              }
            }}
          >
            <Ionicons name="school" size={20} color="#3B82F6" />
            <Text style={[styles.learningActivitiesButtonText, { color: '#3B82F6' }]}>Configure Lessons</Text>
          </TouchableOpacity>

          <TouchableOpacity 
            style={styles.bulkMappingButton}
            onPress={handleOpenBulkMappingModal}
          >
            <Ionicons name="link" size={20} color="#5C6BC0" />
            <Text style={styles.bulkMappingButtonText}>Bulk Edit Mappings</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* Data List */}
      {loading && !refreshing ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#5C6BC0" />
        </View>
      ) : (
        <FlatList
          data={data}
          renderItem={renderItem}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.listContent}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={onRefresh}
              colors={['#5C6BC0']}
              tintColor="#5C6BC0"
              title="Pull to refresh from database..."
              titleColor="#5A5A7A"
            />
          }
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <Ionicons name="folder-open-outline" size={64} color="#D1D5DB" />
              <Text style={styles.emptyText}>No {ENTITY_CONFIG[selectedEntity].title.toLowerCase()} found</Text>
              <Text style={styles.emptySubtext}>Tap + to add one, or pull down to refresh</Text>
            </View>
          }
        />
      )}

      {/* Add/Edit Modal */}
      <Modal
        visible={modalVisible}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>
                {editingItem ? 'Edit' : 'Add'} {ENTITY_CONFIG[selectedEntity].singularTitle}
              </Text>
              <TouchableOpacity onPress={() => setModalVisible(false)}>
                <Ionicons name="close" size={24} color="#5A5A7A" />
              </TouchableOpacity>
            </View>

            <ScrollView style={styles.modalBody}>
              {/* Parent Selector - Only show in main view or when adding new in hierarchy without parent */}
              {ENTITY_CONFIG[selectedEntity].parent && currentView === 'main' && (
                <View style={styles.inputGroup}>
                  <Text style={styles.inputLabel}>{getParentLabel()} *</Text>
                  <ScrollView horizontal showsHorizontalScrollIndicator={false}>
                    {getParentOptions().map((option) => (
                      <TouchableOpacity
                        key={option.id}
                        style={[
                          styles.parentOption,
                          selectedParentId === option.id && styles.parentOptionSelected
                        ]}
                        onPress={() => setSelectedParentId(option.id)}
                      >
                        <Text style={[
                          styles.parentOptionText,
                          selectedParentId === option.id && styles.parentOptionTextSelected
                        ]}>
                          {option.name || option.description}
                        </Text>
                      </TouchableOpacity>
                    ))}
                  </ScrollView>
                </View>
              )}

              {/* Form Fields */}
              {/* For SLOs: render the Key Inquiry Questions textarea FIRST so
                  it's prominently visible — this is the manual-entry surface
                  admins use to populate ``slos.key_inquiry_questions`` for
                  subjects whose KIQs weren't captured by the curriculum
                  extractor. */}
              {selectedEntity === 'slos' && (
                <View
                  style={[
                    styles.inputGroup,
                    {
                      backgroundColor: '#F0FDF4',
                      borderWidth: 1,
                      borderColor: '#10B981',
                      borderRadius: 8,
                      padding: 12,
                      marginBottom: 16,
                    },
                  ]}
                >
                  <Text style={[styles.inputLabel, { color: '#065F46' }]}>
                    Key Inquiry Questions{editingItem ? '' : ' (optional)'}
                  </Text>
                  <Text style={{ fontSize: 11, color: '#047857', marginBottom: 6 }}>
                    One question per line. Leave blank if the curriculum design has none for this SLO.
                  </Text>
                  <TextInput
                    style={[styles.input, styles.textArea, { minHeight: 100, backgroundColor: '#FFFFFF' }]}
                    value={formData['key_inquiry_questions']?.toString() || ''}
                    onChangeText={(text) => setFormData({ ...formData, key_inquiry_questions: text })}
                    placeholder={'e.g.\nWhy is this skill important?\nHow can it be applied in everyday life?'}
                    multiline
                    numberOfLines={4}
                    data-testid="admin-slo-kiq-input"
                    testID="admin-slo-kiq-input"
                  />
                </View>
              )}

              {ENTITY_CONFIG[selectedEntity].fields
                .filter(f => !f.includes('activities') && f !== 'key_inquiry_questions') // Filter out activity fields and KIQ (rendered above)
                .map((field) => {
                  return (
                    <View key={field} style={styles.inputGroup}>
                      <Text style={styles.inputLabel}>
                        {field === 'number_of_lessons' ? 'Number of Lessons' : field.charAt(0).toUpperCase() + field.slice(1)} {field === 'number_of_lessons' ? '' : '*'}
                      </Text>
                      <TextInput
                        style={[styles.input, field === 'description' && styles.textArea]}
                        value={formData[field]?.toString() || ''}
                        onChangeText={(text) => setFormData({ ...formData, [field]: text })}
                        placeholder={field === 'number_of_lessons' ? 'e.g. 10 (lessons in this substrand)' : `Enter ${field}`}
                        multiline={field === 'description'}
                        numberOfLines={field === 'description' ? 4 : 1}
                        keyboardType={field === 'order' || field === 'number_of_lessons' ? 'numeric' : 'default'}
                      />
                    </View>
                  );
                })}
            </ScrollView>

            <View style={styles.modalFooter}>
              <TouchableOpacity 
                style={styles.cancelButton} 
                onPress={() => setModalVisible(false)}
              >
                <Text style={styles.cancelButtonText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.saveButton} onPress={handleSave}>
                <Text style={styles.saveButtonText}>
                  {editingItem ? 'Update' : 'Create'}
                </Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>

      {/* Learning Activities Modal */}
      <Modal
        visible={learningActivitiesModalVisible}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setLearningActivitiesModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={[styles.modalContent, { maxHeight: '90%' }]}>
            <View style={styles.modalHeader}>
              <View>
                <Text style={styles.modalTitle}>Learning Activities</Text>
                <Text style={styles.modalSubtitle}>{currentSubstrandForActivities?.name}</Text>
              </View>
              <TouchableOpacity onPress={() => setLearningActivitiesModalVisible(false)}>
                <Ionicons name="close" size={24} color="#5A5A7A" />
              </TouchableOpacity>
            </View>

            <ScrollView style={styles.modalBody}>
              {renderActivitySection('Introduction', 'introduction_activities', '#10B981', 'play-circle')}
              {renderActivitySection('Development', 'development_activities', '#5C6BC0', 'construct')}
              {renderActivitySection('Conclusion', 'conclusion_activities', '#F59E0B', 'checkmark-done-circle')}
              {renderActivitySection('Extended', 'extended_activities', '#5C6BC0', 'extension-puzzle')}
            </ScrollView>

            <View style={styles.modalFooter}>
              <TouchableOpacity 
                style={styles.cancelButton} 
                onPress={() => setLearningActivitiesModalVisible(false)}
              >
                <Text style={styles.cancelButtonText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.saveButton} onPress={handleSaveLearningActivities}>
                <Text style={styles.saveButtonText}>Save Activities</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>

      {/* Move Item Modal */}
      <Modal
        visible={moveModalVisible}
        animationType="fade"
        transparent={true}
        onRequestClose={() => setMoveModalVisible(false)}
      >
        <Pressable
          style={styles.moveModalOverlay}
          onPress={() => setMoveModalVisible(false)}
        >
          <Pressable style={styles.moveModalContainer} onPress={(e) => e.stopPropagation()}>
            {/* Fixed Header */}
            <View style={styles.moveModalHeader}>
              <View style={{ flexDirection: 'row', alignItems: 'center', gap: 12, flex: 1 }}>
                <View style={[styles.moveIconContainer, { backgroundColor: '#F3F4FF' }]}>
                  <Ionicons name="swap-horizontal" size={24} color="#5C6BC0" />
                </View>
                <Text style={styles.modalTitle} numberOfLines={1}>Move {ENTITY_CONFIG[selectedEntity].singularTitle}</Text>
              </View>
              <TouchableOpacity
                onPress={() => setMoveModalVisible(false)}
                hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
                data-testid="move-modal-close-btn"
              >
                <Ionicons name="close" size={24} color="#5A5A7A" />
              </TouchableOpacity>
            </View>

            {/* Scrollable Body */}
            <ScrollView
              style={styles.moveModalBody}
              contentContainerStyle={{ paddingBottom: 8 }}
              keyboardShouldPersistTaps="handled"
              showsVerticalScrollIndicator={true}
              nestedScrollEnabled={true}
              data-testid="move-modal-scroll-body"
            >
              {/* Current Item */}
              <View style={styles.moveCurrentItem}>
                <Text style={styles.moveCurrentItemLabel}>Moving:</Text>
                <Text style={styles.moveCurrentItemName} numberOfLines={2}>
                  {movingItem?.name || movingItem?.description || 'Unknown'}
                </Text>
              </View>

              {/* Cascade Warning */}
              {(selectedEntity === 'strands' || selectedEntity === 'substrands') && (
                <View style={styles.moveWarning}>
                  <Ionicons name="information-circle" size={20} color="#F59E0B" />
                  <Text style={styles.moveWarningText}>
                    All child items will be moved automatically (cascade move)
                  </Text>
                </View>
              )}

              {/* Grade Selector (for filtering) */}
              {(selectedEntity === 'strands' || selectedEntity === 'substrands' || selectedEntity === 'slos' || selectedEntity === 'subjects') && (
                <View style={styles.moveSelectorContainer}>
                  <Text style={styles.moveSelectorLabel}>
                    {selectedEntity === 'subjects' ? 'Select Target Grade *' : 'Filter by Grade'}
                  </Text>
                  <ScrollView style={styles.moveOptionsList} nestedScrollEnabled>
                    <TouchableOpacity
                      style={[styles.moveOption, !moveTargetGrade && styles.moveOptionSelected]}
                      onPress={() => {
                        setMoveTargetGrade('');
                        setMoveTargetSubject('');
                        setMoveTargetStrand('');
                        setMoveTargetSubstrand('');
                      }}
                    >
                      <Text style={[styles.moveOptionText, !moveTargetGrade && styles.moveOptionTextSelected]}>
                        -- {selectedEntity === 'subjects' ? 'Select Grade' : 'All Grades'} --
                      </Text>
                    </TouchableOpacity>
                    {allGrades.map((grade) => (
                      <TouchableOpacity
                        key={grade.id}
                        style={[styles.moveOption, moveTargetGrade === grade.id && styles.moveOptionSelected]}
                        onPress={() => {
                          setMoveTargetGrade(grade.id);
                          setMoveTargetSubject('');
                          setMoveTargetStrand('');
                          setMoveTargetSubstrand('');
                        }}
                      >
                        <Text style={[styles.moveOptionText, moveTargetGrade === grade.id && styles.moveOptionTextSelected]}>
                          {grade.name}
                        </Text>
                        {moveTargetGrade === grade.id && <Ionicons name="checkmark" size={18} color="#10B981" />}
                      </TouchableOpacity>
                    ))}
                  </ScrollView>
                </View>
              )}

              {/* Subject Selector */}
              {(selectedEntity === 'strands' || selectedEntity === 'substrands' || selectedEntity === 'slos') && (
                <View style={styles.moveSelectorContainer}>
                  <Text style={styles.moveSelectorLabel}>
                    {selectedEntity === 'strands' ? 'Select Target Subject *' : 'Filter by Subject'}
                  </Text>
                  <ScrollView style={styles.moveOptionsList} nestedScrollEnabled>
                    <TouchableOpacity
                      style={[styles.moveOption, !moveTargetSubject && styles.moveOptionSelected]}
                      onPress={() => {
                        setMoveTargetSubject('');
                        setMoveTargetStrand('');
                        setMoveTargetSubstrand('');
                        setMoveStrandsForSubject([]);
                        setMoveSubstrandsForStrand([]);
                      }}
                    >
                      <Text style={[styles.moveOptionText, !moveTargetSubject && styles.moveOptionTextSelected]}>
                        -- {selectedEntity === 'strands' ? 'Select Subject' : 'All Subjects'} --
                      </Text>
                    </TouchableOpacity>
                    {getFilteredSubjectsForMove().map((subject) => (
                      <TouchableOpacity
                        key={subject.id}
                        style={[styles.moveOption, moveTargetSubject === subject.id && styles.moveOptionSelected]}
                        onPress={() => {
                          setMoveTargetSubject(subject.id);
                          setMoveTargetStrand('');
                          setMoveTargetSubstrand('');
                          setMoveSubstrandsForStrand([]);
                          fetchStrandsForSubject(subject.id);
                        }}
                      >
                        <Text style={[styles.moveOptionText, moveTargetSubject === subject.id && styles.moveOptionTextSelected]}>
                          {subject.name}
                        </Text>
                        {moveTargetSubject === subject.id && <Ionicons name="checkmark" size={18} color="#10B981" />}
                      </TouchableOpacity>
                    ))}
                  </ScrollView>
                </View>
              )}

              {/* Strand Selector */}
              {(selectedEntity === 'substrands' || selectedEntity === 'slos') && (
                <View style={styles.moveSelectorContainer}>
                  <Text style={styles.moveSelectorLabel}>
                    {selectedEntity === 'substrands' ? 'Select Target Strand *' : 'Filter by Strand'}
                  </Text>
                  <ScrollView style={styles.moveOptionsList} nestedScrollEnabled>
                    <TouchableOpacity
                      style={[styles.moveOption, !moveTargetStrand && styles.moveOptionSelected]}
                      onPress={() => {
                        setMoveTargetStrand('');
                        setMoveTargetSubstrand('');
                      }}
                    >
                      <Text style={[styles.moveOptionText, !moveTargetStrand && styles.moveOptionTextSelected]}>
                        -- {selectedEntity === 'substrands' ? 'Select Strand' : 'All Strands'} --
                      </Text>
                    </TouchableOpacity>
                    {getFilteredStrandsForMove().map((strand) => (
                      <TouchableOpacity
                        key={strand.id}
                        style={[styles.moveOption, moveTargetStrand === strand.id && styles.moveOptionSelected]}
                        onPress={() => {
                          setMoveTargetStrand(strand.id);
                          setMoveTargetSubstrand('');
                          fetchSubstrandsForStrand(strand.id);
                        }}
                      >
                        <Text style={[styles.moveOptionText, moveTargetStrand === strand.id && styles.moveOptionTextSelected]}>
                          {strand.name}
                        </Text>
                        {moveTargetStrand === strand.id && <Ionicons name="checkmark" size={18} color="#10B981" />}
                      </TouchableOpacity>
                    ))}
                  </ScrollView>
                </View>
              )}

              {/* Substrand Selector */}
              {selectedEntity === 'slos' && (
                <View style={styles.moveSelectorContainer}>
                  <Text style={styles.moveSelectorLabel}>Select Target Sub-strand *</Text>
                  <ScrollView style={styles.moveOptionsList} nestedScrollEnabled>
                    <TouchableOpacity
                      style={[styles.moveOption, !moveTargetSubstrand && styles.moveOptionSelected]}
                      onPress={() => setMoveTargetSubstrand('')}
                    >
                      <Text style={[styles.moveOptionText, !moveTargetSubstrand && styles.moveOptionTextSelected]}>
                        -- Select Sub-strand --
                      </Text>
                    </TouchableOpacity>
                    {getFilteredSubstrandsForMove().map((substrand) => (
                      <TouchableOpacity
                        key={substrand.id}
                        style={[styles.moveOption, moveTargetSubstrand === substrand.id && styles.moveOptionSelected]}
                        onPress={() => setMoveTargetSubstrand(substrand.id)}
                      >
                        <Text style={[styles.moveOptionText, moveTargetSubstrand === substrand.id && styles.moveOptionTextSelected]}>
                          {substrand.name}
                        </Text>
                        {moveTargetSubstrand === substrand.id && <Ionicons name="checkmark" size={18} color="#10B981" />}
                      </TouchableOpacity>
                    ))}
                  </ScrollView>
                </View>
              )}
            </ScrollView>

            {/* Fixed Footer */}
            <View style={styles.moveModalFooter}>
              <TouchableOpacity
                style={styles.cancelButton}
                onPress={() => setMoveModalVisible(false)}
                data-testid="move-modal-cancel-btn"
              >
                <Text style={styles.cancelButtonText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.saveButton, { backgroundColor: '#5C6BC0' }]}
                onPress={handleExecuteMove}
                data-testid="move-modal-confirm-btn"
              >
                <Ionicons name="swap-horizontal" size={18} color="#FFFFFF" style={{ marginRight: 6 }} />
                <Text style={styles.saveButtonText}>Move Item</Text>
              </TouchableOpacity>
            </View>
          </Pressable>
        </Pressable>
      </Modal>

      {/* Bulk Add Modal */}
      <Modal
        visible={bulkAddModalVisible}
        animationType="fade"
        transparent={true}
        onRequestClose={() => setBulkAddModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={[styles.modalContent, { maxWidth: 600 }]}>
            <View style={styles.modalHeader}>
              <View style={{ flexDirection: 'row', alignItems: 'center', gap: 12 }}>
                <View style={[styles.moveIconContainer, { backgroundColor: '#ECFDF5' }]}>
                  <Ionicons name="layers" size={24} color="#10B981" />
                </View>
                <View>
                  <Text style={styles.modalTitle}>Bulk Add {ENTITY_CONFIG[selectedEntity].title}</Text>
                  <Text style={styles.modalSubtitle}>Add multiple items at once</Text>
                </View>
              </View>
              <TouchableOpacity onPress={() => setBulkAddModalVisible(false)}>
                <Ionicons name="close" size={24} color="#5A5A7A" />
              </TouchableOpacity>
            </View>

            {/* Mode Tabs */}
            <View style={styles.bulkModeTabs}>
              <TouchableOpacity
                style={[styles.bulkModeTab, bulkAddMode === 'textarea' && styles.bulkModeTabActive]}
                onPress={() => setBulkAddMode('textarea')}
              >
                <Ionicons name="document-text" size={18} color={bulkAddMode === 'textarea' ? '#5C6BC0' : '#5A5A7A'} />
                <Text style={[styles.bulkModeTabText, bulkAddMode === 'textarea' && styles.bulkModeTabTextActive]}>
                  Text Input
                </Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.bulkModeTab, bulkAddMode === 'table' && styles.bulkModeTabActive]}
                onPress={() => setBulkAddMode('table')}
              >
                <Ionicons name="grid" size={18} color={bulkAddMode === 'table' ? '#5C6BC0' : '#5A5A7A'} />
                <Text style={[styles.bulkModeTabText, bulkAddMode === 'table' && styles.bulkModeTabTextActive]}>
                  Table Input
                </Text>
              </TouchableOpacity>
            </View>

            {/* Guide Section */}
            <View style={styles.mappingGuide}>
              <Ionicons name="help-circle" size={20} color="#3B82F6" />
              <View style={{ flex: 1 }}>
                <Text style={[styles.mappingGuideText, { fontWeight: '700', marginBottom: 4 }]}>
                  Quick Guide for Adding {ENTITY_CONFIG[selectedEntity].title}
                </Text>
                <Text style={styles.mappingGuideText}>
                  {selectedEntity === 'strands' && "Strands are the main topics/themes in a subject. Example: 'Listening and Speaking', 'Reading', 'Writing'."}
                  {selectedEntity === 'substrands' && "Sub-strands are specific areas within a strand. Example: Under 'Reading' strand → 'Comprehension Skills', 'Vocabulary Development'."}
                  {selectedEntity === 'slos' && "SLOs (Specific Learning Outcomes) describe what learners should achieve. Example: 'By the end of the lesson, the learner should be able to identify the main idea in a passage.'"}
                  {selectedEntity === 'subjects' && "Subjects are the main areas of study. Example: 'Mathematics', 'English', 'Science'."}
                </Text>
              </View>
            </View>

            <ScrollView style={styles.modalBody}>
              {bulkAddMode === 'textarea' ? (
                <View>
                  <Text style={styles.inputLabel}>Enter one {ENTITY_CONFIG[selectedEntity].singularTitle.toLowerCase()} per line:</Text>
                  <TextInput
                    style={styles.bulkTextarea}
                    multiline
                    numberOfLines={10}
                    value={bulkTextValue}
                    onChangeText={setBulkTextValue}
                    placeholder={`Example:\nFirst ${ENTITY_CONFIG[selectedEntity].singularTitle.toLowerCase()}\nSecond ${ENTITY_CONFIG[selectedEntity].singularTitle.toLowerCase()}\nThird ${ENTITY_CONFIG[selectedEntity].singularTitle.toLowerCase()}`}
                    placeholderTextColor="#9CA3AF"
                    textAlignVertical="top"
                  />
                  <Text style={styles.bulkHelperText}>
                    Tip: You can copy and paste directly from Word documents, PDFs, or Excel spreadsheets. Each line becomes one item.
                  </Text>
                </View>
              ) : (
                <View>
                  {/* Table Header */}
                  <View style={styles.bulkTableHeader}>
                    <Text style={[styles.bulkTableHeaderCell, { flex: 2 }]}>Name *</Text>
                    <Text style={[styles.bulkTableHeaderCell, { flex: 2 }]}>Description</Text>
                    <Text style={[styles.bulkTableHeaderCell, { width: 40 }]}></Text>
                  </View>

                  {/* Table Rows */}
                  {bulkTableRows.map((row, index) => (
                    <View key={index} style={styles.bulkTableRow}>
                      <TextInput
                        style={[styles.bulkTableInput, { flex: 2 }]}
                        value={row.name}
                        onChangeText={(val) => updateBulkTableRow(index, 'name', val)}
                        placeholder="Enter name"
                        placeholderTextColor="#9CA3AF"
                      />
                      <TextInput
                        style={[styles.bulkTableInput, { flex: 2 }]}
                        value={row.description}
                        onChangeText={(val) => updateBulkTableRow(index, 'description', val)}
                        placeholder="Optional"
                        placeholderTextColor="#9CA3AF"
                      />
                      <TouchableOpacity
                        style={styles.bulkRemoveRowBtn}
                        onPress={() => removeBulkTableRow(index)}
                      >
                        <Ionicons name="trash-outline" size={18} color="#EF4444" />
                      </TouchableOpacity>
                    </View>
                  ))}

                  {/* Add Row Button */}
                  <TouchableOpacity style={styles.bulkAddRowBtn} onPress={addBulkTableRow}>
                    <Ionicons name="add" size={20} color="#5C6BC0" />
                    <Text style={styles.bulkAddRowBtnText}>Add Row</Text>
                  </TouchableOpacity>
                </View>
              )}
            </ScrollView>

            {/* Item Count */}
            <View style={styles.bulkItemCount}>
              <Ionicons name="layers" size={16} color="#5A5A7A" />
              <Text style={styles.bulkItemCountText}>
                {bulkAddMode === 'textarea'
                  ? bulkTextValue.split('\n').filter(l => l.trim()).length
                  : bulkTableRows.filter(r => r.name.trim()).length
                } items to create
              </Text>
            </View>

            <View style={styles.modalFooter}>
              <TouchableOpacity style={styles.cancelButton} onPress={() => setBulkAddModalVisible(false)}>
                <Text style={styles.cancelButtonText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity style={[styles.saveButton, { backgroundColor: '#10B981' }]} onPress={handleExecuteBulkAdd}>
                <Ionicons name="checkmark-circle" size={18} color="#FFFFFF" style={{ marginRight: 6 }} />
                <Text style={styles.saveButtonText}>Create Items</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>

      {/* SLO Mapping Editor Modal */}
      <Modal
        visible={mappingModalVisible}
        animationType="fade"
        transparent={true}
        onRequestClose={() => setMappingModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={[styles.modalContent, { maxWidth: 600 }]}>
            <View style={styles.modalHeader}>
              <View style={{ flexDirection: 'row', alignItems: 'center', gap: 12 }}>
                <View style={[styles.moveIconContainer, { backgroundColor: '#F3E8FF' }]}>
                  <Ionicons name="link" size={24} color="#5C6BC0" />
                </View>
                <View>
                  <Text style={styles.modalTitle}>Edit SLO Mapping</Text>
                  <Text style={styles.modalSubtitle} numberOfLines={2}>{mappingSlo?.name}</Text>
                </View>
              </View>
              <TouchableOpacity onPress={() => setMappingModalVisible(false)}>
                <Ionicons name="close" size={24} color="#5A5A7A" />
              </TouchableOpacity>
            </View>

            {/* Guide Section */}
            <View style={styles.mappingGuide}>
              <Ionicons name="information-circle" size={20} color="#3B82F6" />
              <Text style={styles.mappingGuideText}>
                Select the Core Competencies, Values, and PCIs that relate to this SLO. These will be used when generating lesson plans.
              </Text>
            </View>

            <ScrollView style={styles.modalBody}>
              {/* Core Competencies */}
              <View style={styles.mappingSection}>
                <Text style={styles.mappingSectionTitle}>
                  <Ionicons name="star" size={16} color="#5C6BC0" /> Core Competencies
                </Text>
                <Text style={styles.mappingSectionDesc}>Select skills this SLO develops</Text>
                {allCompetencies.map((comp) => (
                  <TouchableOpacity
                    key={comp.id}
                    style={[styles.mappingCheckbox, selectedCompetencies.includes(comp.id) && styles.mappingCheckboxSelected]}
                    onPress={() => toggleSelection(comp.id, selectedCompetencies, setSelectedCompetencies)}
                  >
                    <View style={[styles.checkbox, selectedCompetencies.includes(comp.id) && styles.checkboxChecked]}>
                      {selectedCompetencies.includes(comp.id) && <Ionicons name="checkmark" size={14} color="#FFFFFF" />}
                    </View>
                    <Text style={styles.mappingCheckboxText}>{comp.name}</Text>
                  </TouchableOpacity>
                ))}
              </View>

              {/* Core Values */}
              <View style={styles.mappingSection}>
                <Text style={styles.mappingSectionTitle}>
                  <Ionicons name="heart" size={16} color="#EF4444" /> Core Values
                </Text>
                <Text style={styles.mappingSectionDesc}>Select values this SLO promotes</Text>
                {allValues.map((val) => (
                  <TouchableOpacity
                    key={val.id}
                    style={[styles.mappingCheckbox, selectedValues.includes(val.id) && styles.mappingCheckboxSelected]}
                    onPress={() => toggleSelection(val.id, selectedValues, setSelectedValues)}
                  >
                    <View style={[styles.checkbox, selectedValues.includes(val.id) && styles.checkboxChecked]}>
                      {selectedValues.includes(val.id) && <Ionicons name="checkmark" size={14} color="#FFFFFF" />}
                    </View>
                    <Text style={styles.mappingCheckboxText}>{val.name}</Text>
                  </TouchableOpacity>
                ))}
              </View>

              {/* PCIs */}
              <View style={styles.mappingSection}>
                <Text style={styles.mappingSectionTitle}>
                  <Ionicons name="globe" size={16} color="#10B981" /> Pertinent & Contemporary Issues (PCIs)
                </Text>
                <Text style={styles.mappingSectionDesc}>Select issues this SLO addresses</Text>
                {allPcis.map((pci) => (
                  <TouchableOpacity
                    key={pci.id}
                    style={[styles.mappingCheckbox, selectedPcis.includes(pci.id) && styles.mappingCheckboxSelected]}
                    onPress={() => toggleSelection(pci.id, selectedPcis, setSelectedPcis)}
                  >
                    <View style={[styles.checkbox, selectedPcis.includes(pci.id) && styles.checkboxChecked]}>
                      {selectedPcis.includes(pci.id) && <Ionicons name="checkmark" size={14} color="#FFFFFF" />}
                    </View>
                    <Text style={styles.mappingCheckboxText}>{pci.name}</Text>
                  </TouchableOpacity>
                ))}
              </View>
            </ScrollView>

            {/* Summary */}
            <View style={styles.mappingSummary}>
              <Text style={styles.mappingSummaryText}>
                Selected: {selectedCompetencies.length} competencies, {selectedValues.length} values, {selectedPcis.length} PCIs
              </Text>
            </View>

            <View style={styles.modalFooter}>
              <TouchableOpacity style={styles.cancelButton} onPress={() => setMappingModalVisible(false)}>
                <Text style={styles.cancelButtonText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity style={[styles.saveButton, { backgroundColor: '#5C6BC0' }]} onPress={handleSaveSloMapping}>
                <Ionicons name="save" size={18} color="#FFFFFF" style={{ marginRight: 6 }} />
                <Text style={styles.saveButtonText}>Save Mapping</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>

      {/* Bulk SLO Mapping Modal */}
      <Modal
        visible={bulkMappingModalVisible}
        animationType="fade"
        transparent={true}
        onRequestClose={() => setBulkMappingModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={[styles.modalContent, { maxWidth: 700, maxHeight: '95%' }]}>
            <View style={styles.modalHeader}>
              <View style={{ flexDirection: 'row', alignItems: 'center', gap: 12 }}>
                <View style={[styles.moveIconContainer, { backgroundColor: '#FEF3C7' }]}>
                  <Ionicons name="layers" size={24} color="#F59E0B" />
                </View>
                <View>
                  <Text style={styles.modalTitle}>Bulk Edit SLO Mappings</Text>
                  <Text style={styles.modalSubtitle}>Apply same mappings to multiple SLOs</Text>
                </View>
              </View>
              <TouchableOpacity onPress={() => setBulkMappingModalVisible(false)}>
                <Ionicons name="close" size={24} color="#5A5A7A" />
              </TouchableOpacity>
            </View>

            {/* Guide Section */}
            <View style={styles.mappingGuide}>
              <Ionicons name="bulb" size={20} color="#F59E0B" />
              <Text style={styles.mappingGuideText}>
                Step 1: Select SLOs below. Step 2: Choose competencies, values, and PCIs. Step 3: Click "Apply to Selected" to update all at once.
              </Text>
            </View>

            <ScrollView style={styles.modalBody}>
              {/* SLO Selection */}
              <View style={styles.mappingSection}>
                <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Text style={styles.mappingSectionTitle}>
                    <Ionicons name="checkbox" size={16} color="#5C6BC0" /> Select SLOs ({selectedSlosForMapping.length} selected)
                  </Text>
                  <View style={{ flexDirection: 'row', gap: 8 }}>
                    <TouchableOpacity style={styles.selectAllBtn} onPress={selectAllSlos}>
                      <Text style={styles.selectAllBtnText}>Select All</Text>
                    </TouchableOpacity>
                    <TouchableOpacity style={styles.selectAllBtn} onPress={deselectAllSlos}>
                      <Text style={styles.selectAllBtnText}>Deselect All</Text>
                    </TouchableOpacity>
                  </View>
                </View>
                <ScrollView style={styles.sloListContainer} nestedScrollEnabled>
                  {data.filter(item => selectedEntity === 'slos').map((slo) => (
                    <TouchableOpacity
                      key={slo.id}
                      style={[styles.mappingCheckbox, selectedSlosForMapping.includes(slo.id) && styles.mappingCheckboxSelected]}
                      onPress={() => toggleSloSelection(slo.id)}
                    >
                      <View style={[styles.checkbox, selectedSlosForMapping.includes(slo.id) && styles.checkboxChecked]}>
                        {selectedSlosForMapping.includes(slo.id) && <Ionicons name="checkmark" size={14} color="#FFFFFF" />}
                      </View>
                      <Text style={styles.mappingCheckboxText} numberOfLines={2}>{slo.name}</Text>
                    </TouchableOpacity>
                  ))}
                </ScrollView>
              </View>

              {/* Core Competencies */}
              <View style={styles.mappingSection}>
                <Text style={styles.mappingSectionTitle}>
                  <Ionicons name="star" size={16} color="#5C6BC0" /> Core Competencies
                </Text>
                {allCompetencies.map((comp) => (
                  <TouchableOpacity
                    key={comp.id}
                    style={[styles.mappingCheckbox, bulkSelectedCompetencies.includes(comp.id) && styles.mappingCheckboxSelected]}
                    onPress={() => toggleSelection(comp.id, bulkSelectedCompetencies, setBulkSelectedCompetencies)}
                  >
                    <View style={[styles.checkbox, bulkSelectedCompetencies.includes(comp.id) && styles.checkboxChecked]}>
                      {bulkSelectedCompetencies.includes(comp.id) && <Ionicons name="checkmark" size={14} color="#FFFFFF" />}
                    </View>
                    <Text style={styles.mappingCheckboxText}>{comp.name}</Text>
                  </TouchableOpacity>
                ))}
              </View>

              {/* Core Values */}
              <View style={styles.mappingSection}>
                <Text style={styles.mappingSectionTitle}>
                  <Ionicons name="heart" size={16} color="#EF4444" /> Core Values
                </Text>
                {allValues.map((val) => (
                  <TouchableOpacity
                    key={val.id}
                    style={[styles.mappingCheckbox, bulkSelectedValues.includes(val.id) && styles.mappingCheckboxSelected]}
                    onPress={() => toggleSelection(val.id, bulkSelectedValues, setBulkSelectedValues)}
                  >
                    <View style={[styles.checkbox, bulkSelectedValues.includes(val.id) && styles.checkboxChecked]}>
                      {bulkSelectedValues.includes(val.id) && <Ionicons name="checkmark" size={14} color="#FFFFFF" />}
                    </View>
                    <Text style={styles.mappingCheckboxText}>{val.name}</Text>
                  </TouchableOpacity>
                ))}
              </View>

              {/* PCIs */}
              <View style={styles.mappingSection}>
                <Text style={styles.mappingSectionTitle}>
                  <Ionicons name="globe" size={16} color="#10B981" /> Pertinent & Contemporary Issues
                </Text>
                {allPcis.map((pci) => (
                  <TouchableOpacity
                    key={pci.id}
                    style={[styles.mappingCheckbox, bulkSelectedPcis.includes(pci.id) && styles.mappingCheckboxSelected]}
                    onPress={() => toggleSelection(pci.id, bulkSelectedPcis, setBulkSelectedPcis)}
                  >
                    <View style={[styles.checkbox, bulkSelectedPcis.includes(pci.id) && styles.checkboxChecked]}>
                      {bulkSelectedPcis.includes(pci.id) && <Ionicons name="checkmark" size={14} color="#FFFFFF" />}
                    </View>
                    <Text style={styles.mappingCheckboxText}>{pci.name}</Text>
                  </TouchableOpacity>
                ))}
              </View>
            </ScrollView>

            {/* Summary */}
            <View style={styles.mappingSummary}>
              <Text style={styles.mappingSummaryText}>
                Will update {selectedSlosForMapping.length} SLOs with {bulkSelectedCompetencies.length} competencies, {bulkSelectedValues.length} values, {bulkSelectedPcis.length} PCIs
              </Text>
            </View>

            <View style={styles.modalFooter}>
              <TouchableOpacity style={styles.cancelButton} onPress={() => setBulkMappingModalVisible(false)}>
                <Text style={styles.cancelButtonText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity 
                style={[styles.saveButton, { backgroundColor: '#F59E0B' }, selectedSlosForMapping.length === 0 && { opacity: 0.5 }]} 
                onPress={handleSaveBulkMapping}
                disabled={selectedSlosForMapping.length === 0}
              >
                <Ionicons name="checkmark-done" size={18} color="#FFFFFF" style={{ marginRight: 6 }} />
                <Text style={styles.saveButtonText}>Apply to Selected</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>

      {/* Bulk Edit Modal */}
      <Modal
        visible={bulkEditModalVisible}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setBulkEditModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Bulk Edit {selectedItems.size} Items</Text>
              <TouchableOpacity onPress={() => setBulkEditModalVisible(false)}>
                <Ionicons name="close" size={24} color="#5A5A7A" />
              </TouchableOpacity>
            </View>
            
            <ScrollView style={styles.modalBody}>
              <Text style={styles.bulkEditNote}>
                Leave fields empty to keep existing values. Only filled fields will be updated.
              </Text>
              
              {/* Name field - for strands and substrands */}
              {(selectedEntity === 'strands' || selectedEntity === 'substrands') && (
                <View style={styles.inputGroup}>
                  <Text style={styles.inputLabel}>Name (append to existing)</Text>
                  <TextInput
                    style={styles.textInput}
                    value={bulkEditFormData.name || ''}
                    onChangeText={(text) => setBulkEditFormData({ ...bulkEditFormData, name: text })}
                    placeholder="Leave empty to keep existing names"
                  />
                </View>
              )}
              
              {/* Description field - for SLOs */}
              {selectedEntity === 'slos' && (
                <>
                  <View style={styles.inputGroup}>
                    <Text style={styles.inputLabel}>Name</Text>
                    <TextInput
                      style={styles.textInput}
                      value={bulkEditFormData.name || ''}
                      onChangeText={(text) => setBulkEditFormData({ ...bulkEditFormData, name: text })}
                      placeholder="Leave empty to keep existing"
                    />
                  </View>
                  <View style={styles.inputGroup}>
                    <Text style={styles.inputLabel}>Description</Text>
                    <TextInput
                      style={[styles.textInput, { minHeight: 80, textAlignVertical: 'top' }]}
                      value={bulkEditFormData.description || ''}
                      onChangeText={(text) => setBulkEditFormData({ ...bulkEditFormData, description: text })}
                      placeholder="Leave empty to keep existing"
                      multiline
                    />
                  </View>
                </>
              )}
            </ScrollView>

            <View style={styles.modalFooter}>
              <TouchableOpacity style={styles.cancelButton} onPress={() => setBulkEditModalVisible(false)}>
                <Text style={styles.cancelButtonText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity 
                style={[styles.saveButton, loading && { opacity: 0.5 }]} 
                onPress={handleSaveBulkEdit}
                disabled={loading}
              >
                {loading ? (
                  <ActivityIndicator size="small" color="#FFFFFF" />
                ) : (
                  <Text style={styles.saveButtonText}>Update All</Text>
                )}
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>

      {/* Substrand Lessons Configuration Modal */}
      <Modal
        visible={lessonsModalVisible}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setLessonsModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={[styles.modalContent, { maxHeight: '85%' }]}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>
                Configure Lessons{lessonsSubstrand ? `: ${lessonsSubstrand.name}` : ''}
              </Text>
              <TouchableOpacity onPress={() => setLessonsModalVisible(false)}>
                <Ionicons name="close" size={24} color="#5A5A7A" />
              </TouchableOpacity>
            </View>

            <ScrollView style={styles.modalBody} keyboardShouldPersistTaps="always">
              {lessonsLoading ? (
                <ActivityIndicator size="large" color="#3B82F6" style={{ marginTop: 20 }} />
              ) : substrandLessons.length === 0 ? (
                <View style={{ alignItems: 'center', padding: 20 }}>
                  <Ionicons name="school-outline" size={48} color="#9CA3AF" />
                  <Text style={{ color: '#5A5A7A', marginTop: 12, textAlign: 'center', fontSize: 14 }}>
                    No lessons configured yet.{'\n'}Set "Number of Lessons" on the substrand, then click "Generate Lesson Slots".
                  </Text>
                  <TouchableOpacity
                    style={{ backgroundColor: '#3B82F6', paddingHorizontal: 20, paddingVertical: 10, borderRadius: 8, marginTop: 16 }}
                    onPress={handleGenerateLessonSlots}
                  >
                    <Text style={{ color: '#FFF', fontWeight: '600' }}>Generate Lesson Slots</Text>
                  </TouchableOpacity>
                </View>
              ) : (
                <>
                  <TouchableOpacity
                    style={{ backgroundColor: '#EFF6FF', padding: 10, borderRadius: 8, marginBottom: 12, flexDirection: 'row', alignItems: 'center', justifyContent: 'center' }}
                    onPress={handleGenerateLessonSlots}
                  >
                    <Ionicons name="refresh" size={18} color="#3B82F6" />
                    <Text style={{ color: '#3B82F6', fontWeight: '600', marginLeft: 6 }}>Regenerate Missing Slots</Text>
                  </TouchableOpacity>

                  {substrandLessons.map((lesson: any, idx: number) => (
                    <View key={lesson.id || idx} style={{ backgroundColor: '#F9FAFB', borderRadius: 10, padding: 14, marginBottom: 10, borderWidth: 1, borderColor: '#DDDDF5' }}>
                      <Text style={{ fontWeight: 'bold', color: '#1F2937', marginBottom: 8, fontSize: 14 }}>
                        Lesson {lesson.lesson_number}
                      </Text>
                      {(lesson.specific_outcomes || []).map((outcome: string, oi: number) => (
                        <View key={oi} style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 6 }}>
                          <TextInput
                            style={{ flex: 1, backgroundColor: '#FFF', borderWidth: 1, borderColor: '#D1D5DB', borderRadius: 8, padding: 10, fontSize: 13 }}
                            value={outcome}
                            onChangeText={(t) => handleUpdateLessonOutcome(idx, oi, t)}
                            placeholder={`Specific outcome ${oi + 1}`}
                          />
                          <TouchableOpacity onPress={() => handleRemoveOutcome(idx, oi)} style={{ marginLeft: 8 }}>
                            <Ionicons name="close-circle" size={22} color="#EF4444" />
                          </TouchableOpacity>
                        </View>
                      ))}
                      {(lesson.specific_outcomes || []).length < 2 && (
                        <TouchableOpacity
                          onPress={() => handleAddOutcome(idx)}
                          style={{ flexDirection: 'row', alignItems: 'center', marginTop: 4 }}
                        >
                          <Ionicons name="add-circle-outline" size={18} color="#3B82F6" />
                          <Text style={{ color: '#3B82F6', marginLeft: 4, fontSize: 13 }}>Add outcome</Text>
                        </TouchableOpacity>
                      )}
                    </View>
                  ))}
                </>
              )}
            </ScrollView>

            {substrandLessons.length > 0 && (
              <View style={styles.modalFooter}>
                <TouchableOpacity
                  style={[styles.saveButton, lessonsLoading && { opacity: 0.6 }]}
                  onPress={handleSaveLessons}
                  disabled={lessonsLoading}
                >
                  {lessonsLoading ? (
                    <ActivityIndicator color="#FFF" size="small" />
                  ) : (
                    <Text style={styles.saveButtonText}>Save All Lessons</Text>
                  )}
                </TouchableOpacity>
              </View>
            )}
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB'
  },
  viewToggle: {
    flexDirection: 'row',
    backgroundColor: '#FFFFFF',
    padding: 12,
    gap: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#DDDDF5'
  },
  viewToggleButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 10,
    paddingHorizontal: 16,
    borderRadius: 8,
    backgroundColor: '#F3F4F6',
    gap: 8
  },
  viewToggleButtonActive: {
    backgroundColor: '#5C6BC0'
  },
  viewToggleText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#5C6BC0'
  },
  viewToggleTextActive: {
    color: '#FFFFFF'
  },
  breadcrumbContainer: {
    backgroundColor: '#FFFFFF',
    paddingVertical: 10,
    paddingHorizontal: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#DDDDF5'
  },
  breadcrumb: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    backgroundColor: '#F3F4FF',
    borderRadius: 4
  },
  breadcrumbText: {
    fontSize: 13,
    color: '#5C6BC0',
    fontWeight: '500',
    maxWidth: 120
  },
  entitySelector: {
    backgroundColor: '#FFFFFF',
    paddingVertical: 12,
    paddingHorizontal: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#DDDDF5',
    maxHeight: 60
  },
  entityTab: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 20,
    marginHorizontal: 4,
    backgroundColor: '#F3F4F6'
  },
  entityTabText: {
    fontSize: 12,
    fontWeight: '600',
    marginLeft: 6,
    color: '#374151'
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#DDDDF5'
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1A1A3A',
    flex: 1
  },
  headerCount: {
    fontSize: 14,
    color: '#5A5A7A',
    marginRight: 12
  },
  addButton: {
    backgroundColor: '#5C6BC0',
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center'
  },
  backButton: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: '#F3F4FF',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12
  },
  refreshButton: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#F3F4FF',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 8
  },
  learningActivitiesButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#ECFDF5',
    paddingVertical: 10,
    paddingHorizontal: 14,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#84CC16',
    gap: 8
  },
  learningActivitiesButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#3F6212'
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center'
  },
  listContent: {
    padding: 16
  },
  listItem: {
    flexDirection: 'column',
    backgroundColor: '#FFFFFF',
    borderRadius: 8,
    marginBottom: 8,
    overflow: 'hidden'
  },
  listItemContent: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12
  },
  itemIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12
  },
  itemContent: {
    flex: 1
  },
  itemName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1A1A3A'
  },
  itemDescription: {
    fontSize: 12,
    color: '#5A5A7A',
    marginTop: 2
  },
  itemMeta: {
    fontSize: 11,
    color: '#9CA3AF',
    marginTop: 2
  },
  itemActions: {
    flexDirection: 'row',
    borderTopWidth: 1,
    borderTopColor: '#F3F4F6',
    backgroundColor: '#FAFAFA'
  },
  moveButton: {
    flex: 1,
    padding: 10,
    alignItems: 'center',
    borderRightWidth: 1,
    borderRightColor: '#DDDDF5'
  },
  editButton: {
    flex: 1,
    padding: 10,
    alignItems: 'center',
    borderRightWidth: 1,
    borderRightColor: '#DDDDF5'
  },
  deleteButton: {
    flex: 1,
    padding: 10,
    alignItems: 'center'
  },
  bulkAddButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 8,
    backgroundColor: '#ECFDF5',
    borderWidth: 1,
    borderColor: '#10B981',
    marginRight: 8
  },
  bulkAddButtonText: {
    fontSize: 13,
    fontWeight: '600',
    color: '#10B981'
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 64
  },
  emptyText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#5A5A7A',
    marginTop: 16
  },
  emptySubtext: {
    fontSize: 14,
    color: '#9CA3AF',
    marginTop: 4
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
    borderBottomColor: '#DDDDF5'
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1A1A3A'
  },
  modalSubtitle: {
    fontSize: 14,
    color: '#5A5A7A',
    marginTop: 2
  },
  modalBody: {
    padding: 16,
    maxHeight: 500
  },
  inputGroup: {
    marginBottom: 16
  },
  inputLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 8
  },
  input: {
    backgroundColor: '#F9FAFB',
    borderWidth: 1,
    borderColor: '#DDDDF5',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 12,
    fontSize: 16,
    color: '#1A1A3A'
  },
  textArea: {
    minHeight: 100,
    textAlignVertical: 'top'
  },
  parentOption: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: '#F3F4F6',
    marginRight: 8
  },
  parentOptionSelected: {
    backgroundColor: '#5C6BC0'
  },
  parentOptionText: {
    fontSize: 14,
    color: '#374151'
  },
  parentOptionTextSelected: {
    color: '#FFFFFF',
    fontWeight: '600'
  },
  modalFooter: {
    flexDirection: 'row',
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: '#DDDDF5',
    gap: 12
  },
  cancelButton: {
    flex: 1,
    paddingVertical: 14,
    borderRadius: 8,
    backgroundColor: '#F3F4F6',
    alignItems: 'center'
  },
  cancelButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151'
  },
  saveButton: {
    flex: 1,
    paddingVertical: 14,
    borderRadius: 8,
    backgroundColor: '#5C6BC0',
    alignItems: 'center'
  },
  saveButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFFFFF'
  },
  activitySection: {
    marginBottom: 24,
    backgroundColor: '#FAFAFA',
    borderRadius: 12,
    padding: 12
  },
  activitySectionHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
    gap: 8
  },
  activitySectionTitle: {
    flex: 1,
    fontSize: 16,
    fontWeight: '700'
  },
  addActivityButton: {
    width: 32,
    height: 32,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center'
  },
  activityInputRow: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 8
  },
  activityInput: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#DDDDF5',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 14,
    color: '#1A1A3A',
    minHeight: 60,
    textAlignVertical: 'top'
  },
  removeActivityButton: {
    padding: 8,
    marginLeft: 4
  },
  // Move Modal Styles
  moveIconContainer: {
    width: 44,
    height: 44,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center'
  },
  moveCurrentItem: {
    padding: 14,
    backgroundColor: '#F9FAFB',
    borderRadius: 10,
    marginBottom: 16
  },
  moveCurrentItemLabel: {
    fontSize: 12,
    fontWeight: '600',
    color: '#5A5A7A',
    marginBottom: 4
  },
  moveCurrentItemName: {
    fontSize: 15,
    fontWeight: '600',
    color: '#1A1A3A'
  },
  moveWarning: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    padding: 12,
    backgroundColor: '#FEF3C7',
    borderRadius: 8,
    marginBottom: 16
  },
  moveWarningText: {
    flex: 1,
    fontSize: 13,
    color: '#92400E'
  },
  moveSelectorContainer: {
    marginBottom: 16
  },
  moveSelectorLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 8
  },
  moveOptionsList: {
    maxHeight: 140,
    backgroundColor: '#F9FAFB',
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#DDDDF5'
  },
  moveOption: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#DDDDF5'
  },
  moveOptionSelected: {
    backgroundColor: '#ECFDF5'
  },
  moveOptionText: {
    fontSize: 14,
    color: '#374151',
    flex: 1
  },
  moveOptionTextSelected: {
    fontWeight: '600',
    color: '#059669'
  },
  // Move Modal Layout Styles
  moveModalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.6)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 16
  },
  moveModalContainer: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    width: '100%',
    maxWidth: 500,
    maxHeight: '85%',
    overflow: 'hidden',
    ...Platform.select({
      web: { boxShadow: '0 20px 60px rgba(0,0,0,0.3)' },
      default: { elevation: 24 }
    })
  },
  moveModalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 14,
    borderBottomWidth: 1,
    borderBottomColor: '#DDDDF5',
    backgroundColor: '#FFFFFF'
  },
  moveModalBody: {
    paddingHorizontal: 16,
    paddingTop: 16,
    flexShrink: 1
  },
  moveModalFooter: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    paddingVertical: 14,
    borderTopWidth: 1,
    borderTopColor: '#DDDDF5',
    gap: 12,
    backgroundColor: '#FFFFFF'
  },
  // Bulk Add Modal Styles
  bulkModeTabs: {
    flexDirection: 'row',
    padding: 12,
    gap: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#DDDDF5'
  },
  bulkModeTab: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    padding: 12,
    borderRadius: 10,
    backgroundColor: '#F9FAFB'
  },
  bulkModeTabActive: {
    backgroundColor: '#F3F4FF'
  },
  bulkModeTabText: {
    fontSize: 14,
    fontWeight: '500',
    color: '#5A5A7A'
  },
  bulkModeTabTextActive: {
    color: '#5C6BC0',
    fontWeight: '600'
  },
  bulkTextarea: {
    borderWidth: 1,
    borderColor: '#DDDDF5',
    borderRadius: 12,
    padding: 16,
    fontSize: 14,
    color: '#1A1A3A',
    backgroundColor: '#F9FAFB',
    minHeight: 180,
    textAlignVertical: 'top'
  },
  bulkHelperText: {
    fontSize: 12,
    color: '#5A5A7A',
    marginTop: 8
  },
  bulkTableHeader: {
    flexDirection: 'row',
    gap: 8,
    paddingBottom: 8,
    borderBottomWidth: 2,
    borderBottomColor: '#DDDDF5',
    marginBottom: 8
  },
  bulkTableHeaderCell: {
    fontSize: 13,
    fontWeight: '600',
    color: '#374151'
  },
  bulkTableRow: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 8
  },
  bulkTableInput: {
    borderWidth: 1,
    borderColor: '#DDDDF5',
    borderRadius: 8,
    padding: 12,
    fontSize: 14,
    color: '#1A1A3A',
    backgroundColor: '#F9FAFB'
  },
  bulkRemoveRowBtn: {
    width: 40,
    justifyContent: 'center',
    alignItems: 'center'
  },
  bulkAddRowBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    padding: 12,
    borderWidth: 2,
    borderColor: '#DDDDF5',
    borderStyle: 'dashed',
    borderRadius: 10,
    marginTop: 8
  },
  bulkAddRowBtnText: {
    fontSize: 14,
    fontWeight: '500',
    color: '#5C6BC0'
  },
  bulkItemCount: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 6,
    paddingVertical: 12,
    borderTopWidth: 1,
    borderTopColor: '#DDDDF5',
    backgroundColor: '#F9FAFB'
  },
  bulkItemCountText: {
    fontSize: 13,
    color: '#5A5A7A'
  },
  // Mapping Modal Styles
  mappingButton: {
    flex: 1,
    padding: 10,
    alignItems: 'center',
    borderRightWidth: 1,
    borderRightColor: '#DDDDF5'
  },
  mappingGuide: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 10,
    padding: 14,
    backgroundColor: '#EFF6FF',
    marginHorizontal: 16,
    marginTop: 12,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#BFDBFE'
  },
  mappingGuideText: {
    flex: 1,
    fontSize: 13,
    color: '#1E40AF',
    lineHeight: 18
  },
  mappingSection: {
    marginBottom: 20
  },
  mappingSectionTitle: {
    fontSize: 15,
    fontWeight: '700',
    color: '#1A1A3A',
    marginBottom: 4
  },
  mappingSectionDesc: {
    fontSize: 12,
    color: '#5A5A7A',
    marginBottom: 10
  },
  mappingCheckbox: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
    padding: 10,
    backgroundColor: '#F9FAFB',
    borderRadius: 8,
    marginBottom: 6,
    borderWidth: 1,
    borderColor: '#DDDDF5'
  },
  mappingCheckboxSelected: {
    backgroundColor: '#ECFDF5',
    borderColor: '#10B981'
  },
  mappingCheckboxText: {
    flex: 1,
    fontSize: 14,
    color: '#374151'
  },
  checkbox: {
    width: 22,
    height: 22,
    borderRadius: 6,
    borderWidth: 2,
    borderColor: '#D1D5DB',
    justifyContent: 'center',
    alignItems: 'center'
  },
  checkboxChecked: {
    backgroundColor: '#10B981',
    borderColor: '#10B981'
  },
  mappingSummary: {
    paddingVertical: 10,
    paddingHorizontal: 16,
    backgroundColor: '#F3F4F6',
    borderTopWidth: 1,
    borderTopColor: '#DDDDF5'
  },
  mappingSummaryText: {
    fontSize: 13,
    color: '#5A5A7A',
    textAlign: 'center'
  },
  selectAllBtn: {
    paddingVertical: 6,
    paddingHorizontal: 10,
    backgroundColor: '#F3F4FF',
    borderRadius: 6
  },
  selectAllBtnText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#5C6BC0'
  },
  sloListContainer: {
    maxHeight: 150,
    marginTop: 8
  },
  sloActionsRow: {
    flexDirection: 'row',
    gap: 8,
    paddingHorizontal: 16,
    paddingVertical: 10,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#DDDDF5'
  },
  bulkMappingButton: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    paddingVertical: 10,
    paddingHorizontal: 14,
    borderRadius: 10,
    backgroundColor: '#F3E8FF',
    borderWidth: 1,
    borderColor: '#5C6BC0'
  },
  bulkMappingButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#5C6BC0'
  },
  // Bulk Edit Mode Styles
  bulkEditToggle: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    backgroundColor: '#F3F4FF',
    borderWidth: 1,
    borderColor: '#5C6BC0',
    gap: 4
  },
  bulkEditToggleActive: {
    backgroundColor: '#5C6BC0'
  },
  bulkEditToggleText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#5C6BC0'
  },
  bulkEditToggleTextActive: {
    color: '#FFFFFF'
  },
  bulkActionBar: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#F3F4FF',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#C7D2FE'
  },
  selectAllBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8
  },
  selectAllText: {
    fontSize: 14,
    fontWeight: '500',
    color: '#5C6BC0'
  },
  bulkActionButtons: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8
  },
  selectedCount: {
    fontSize: 13,
    fontWeight: '600',
    color: '#4F46E5',
    marginRight: 8
  },
  bulkEditBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 8,
    backgroundColor: '#F59E0B',
    gap: 4
  },
  bulkDeleteBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 8,
    backgroundColor: '#EF4444',
    gap: 4
  },
  bulkBtnText: {
    fontSize: 13,
    fontWeight: '600',
    color: '#FFFFFF'
  },
  checkboxContainer: {
    padding: 8,
    justifyContent: 'center'
  },
  checkbox: {
    width: 22,
    height: 22,
    borderRadius: 4,
    borderWidth: 2,
    borderColor: '#D1D5DB',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#FFFFFF'
  },
  checkboxSelected: {
    backgroundColor: '#5C6BC0',
    borderColor: '#5C6BC0'
  },
  reorderButtons: {
    flexDirection: 'column',
    paddingHorizontal: 4,
    gap: 2
  },
  reorderBtn: {
    padding: 4,
    borderRadius: 4,
    backgroundColor: '#F3F4FF'
  },
  bulkEditNote: {
    fontSize: 13,
    color: '#5A5A7A',
    backgroundColor: '#FEF3C7',
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
    textAlign: 'center'
  }
});
