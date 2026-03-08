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
  Platform
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../../contexts/AuthContext';
import axios from 'axios';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

type EntityType = 'grades' | 'subjects' | 'strands' | 'substrands' | 'slos' | 'learning_activities' | 'competencies' | 'values' | 'pcis';

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
  grades: { title: 'Grades', singularTitle: 'Grade', icon: 'school', color: '#6366F1', fields: ['name', 'order'], apiPath: 'grades' },
  subjects: { title: 'Subjects', singularTitle: 'Subject', icon: 'book', color: '#10B981', fields: ['name'], parent: 'grades', apiPath: 'subjects' },
  strands: { title: 'Strands', singularTitle: 'Strand', icon: 'git-branch', color: '#F59E0B', fields: ['name'], parent: 'subjects', apiPath: 'strands' },
  substrands: { title: 'Sub-strands', singularTitle: 'Sub-strand', icon: 'git-merge', color: '#EF4444', fields: ['name'], parent: 'strands', apiPath: 'substrands' },
  slos: { title: 'SLOs', singularTitle: 'SLO', icon: 'checkmark-circle', color: '#8B5CF6', fields: ['name', 'description'], parent: 'substrands', apiPath: 'slos' },
  learning_activities: { title: 'Learning Activities', singularTitle: 'Learning Activities', icon: 'flash', color: '#84CC16', fields: ['introduction_activities', 'development_activities', 'conclusion_activities', 'extended_activities'], parent: 'substrands', apiPath: 'learning-activities' },
  competencies: { title: 'Competencies', singularTitle: 'Competency', icon: 'star', color: '#EC4899', fields: ['name', 'description'], apiPath: 'competencies' },
  values: { title: 'Values', singularTitle: 'Value', icon: 'heart', color: '#14B8A6', fields: ['name', 'description'], apiPath: 'values' },
  pcis: { title: 'PCIs', singularTitle: 'PCI', icon: 'globe', color: '#F97316', fields: ['name', 'description'], apiPath: 'pcis' }
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

  // Bulk add modal state
  const [bulkAddModalVisible, setBulkAddModalVisible] = useState(false);
  const [bulkAddMode, setBulkAddMode] = useState<'textarea' | 'table'>('textarea');
  const [bulkTextValue, setBulkTextValue] = useState('');
  const [bulkTableRows, setBulkTableRows] = useState<{name: string, description: string}[]>([
    { name: '', description: '' },
    { name: '', description: '' },
    { name: '', description: '' }
  ]);

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

  const loadGrades = async () => {
    try {
      const headers = await getHeaders();
      const response = await axios.get(`${BACKEND_URL}/api/admin/grades`, { headers });
      if (response.data.success) {
        setGrades(response.data.grades);
      }
    } catch (error) {
      console.error('Error loading grades:', error);
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
      console.error('Error loading subjects:', error);
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
      console.error('Error loading strands:', error);
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
      console.error('Error loading substrands:', error);
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
      console.error('Error loading SLOs:', error);
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
      console.error('Error loading data:', error);
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
      console.error('Error:', error);
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
      console.error('Error:', error);
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
    try {
      const headers = await getHeaders();
      const response = await axios.get(`${BACKEND_URL}/api/admin/substrands?strandId=${strand.id}`, { headers });
      if (response.data.success) {
        setData(response.data.substrands);
      }
    } catch (error) {
      console.error('Error:', error);
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
      console.error('Error:', error);
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
      initialData[field] = (item as any)[field]?.toString() || '';
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
      console.error('Error loading activities:', error);
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
      } else if (selectedEntity === 'slos' && (selectedParentId || currentParentId)) {
        payload.substrandId = selectedParentId || currentParentId;
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
      console.error('Error saving:', error.response?.data || error);
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
      console.error('Error saving activities:', error.response?.data || error);
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
      console.error('Error loading curriculum data:', error);
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
    return allSubjects.filter(s => s.gradeIds?.includes(moveTargetGrade));
  };

  // Get filtered strands for move modal
  const getFilteredStrandsForMove = () => {
    if (!moveTargetSubject) return allStrands;
    return allStrands.filter(s => s.subjectId === moveTargetSubject);
  };

  // Get filtered substrands for move modal
  const getFilteredSubstrandsForMove = () => {
    if (!moveTargetStrand) return allSubstrands;
    return allSubstrands.filter(s => s.strandId === moveTargetStrand);
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

  const renderItem = ({ item }: { item: Entity }) => {
    const config = ENTITY_CONFIG[selectedEntity];
    const canNavigate = currentView === 'hierarchy' && selectedEntity !== 'slos';
    const canMove = selectedEntity !== 'grades' && selectedEntity !== 'competencies' && selectedEntity !== 'values' && selectedEntity !== 'pcis' && selectedEntity !== 'learning_activities';
    
    return (
      <View style={styles.listItem}>
        <TouchableOpacity 
          style={styles.listItemContent}
          onPress={() => canNavigate ? handleItemPress(item) : null}
          activeOpacity={canNavigate ? 0.7 : 1}
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
          </View>
          
          {canNavigate && (
            <Ionicons name="chevron-forward" size={20} color="#9CA3AF" style={{ marginRight: 8 }} />
          )}
        </TouchableOpacity>
        
        <View style={styles.itemActions}>
          {canMove && (
            <TouchableOpacity style={styles.moveButton} onPress={() => handleOpenMoveModal(item)}>
              <Ionicons name="swap-horizontal" size={18} color="#6366F1" />
            </TouchableOpacity>
          )}
          <TouchableOpacity style={styles.editButton} onPress={() => openEditModal(item)}>
            <Ionicons name="pencil" size={18} color="#F59E0B" />
          </TouchableOpacity>
          <TouchableOpacity style={styles.deleteButton} onPress={() => handleDelete(item)}>
            <Ionicons name="trash" size={18} color="#EF4444" />
          </TouchableOpacity>
        </View>
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
          <Ionicons name="grid" size={18} color={currentView === 'main' ? '#FFFFFF' : '#6366F1'} />
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
          <Ionicons name="git-network" size={18} color={currentView === 'hierarchy' ? '#FFFFFF' : '#6366F1'} />
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
              <Ionicons name="home" size={16} color="#6366F1" />
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
        <Text style={styles.headerTitle}>{ENTITY_CONFIG[selectedEntity].title}</Text>
        <Text style={styles.headerCount}>{data.length} items</Text>
        
        {/* Bulk Add Button - Show when in hierarchy with parent selected */}
        {currentView === 'hierarchy' && currentParentId && selectedEntity !== 'grades' && (
          <TouchableOpacity style={styles.bulkAddButton} onPress={handleOpenBulkAddModal}>
            <Ionicons name="layers" size={18} color="#10B981" />
            <Text style={styles.bulkAddButtonText}>Bulk</Text>
          </TouchableOpacity>
        )}
        
        <TouchableOpacity style={styles.addButton} onPress={openAddModal}>
          <Ionicons name="add" size={24} color="#FFFFFF" />
        </TouchableOpacity>
      </View>

      {/* Learning Activities Button - Show when viewing substrands in hierarchy */}
      {currentView === 'hierarchy' && selectedEntity === 'slos' && breadcrumbs.length > 0 && (
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
          <Text style={styles.learningActivitiesButtonText}>Manage Learning Activities</Text>
          <Ionicons name="chevron-forward" size={20} color="#84CC16" />
        </TouchableOpacity>
      )}

      {/* Data List */}
      {loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#6366F1" />
        </View>
      ) : (
        <FlatList
          data={data}
          renderItem={renderItem}
          keyExtractor={(item) => item.id}
          contentContainerStyle={styles.listContent}
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <Ionicons name="folder-open-outline" size={64} color="#D1D5DB" />
              <Text style={styles.emptyText}>No {ENTITY_CONFIG[selectedEntity].title.toLowerCase()} found</Text>
              <Text style={styles.emptySubtext}>Tap + to add one</Text>
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
                <Ionicons name="close" size={24} color="#6B7280" />
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
              {ENTITY_CONFIG[selectedEntity].fields
                .filter(f => !f.includes('activities')) // Filter out activity fields for regular modal
                .map((field) => (
                <View key={field} style={styles.inputGroup}>
                  <Text style={styles.inputLabel}>
                    {field.charAt(0).toUpperCase() + field.slice(1)} *
                  </Text>
                  <TextInput
                    style={[styles.input, field === 'description' && styles.textArea]}
                    value={formData[field] || ''}
                    onChangeText={(text) => setFormData({ ...formData, [field]: text })}
                    placeholder={`Enter ${field}`}
                    multiline={field === 'description'}
                    numberOfLines={field === 'description' ? 4 : 1}
                    keyboardType={field === 'order' ? 'numeric' : 'default'}
                  />
                </View>
              ))}
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
                <Ionicons name="close" size={24} color="#6B7280" />
              </TouchableOpacity>
            </View>

            <ScrollView style={styles.modalBody}>
              {renderActivitySection('Introduction', 'introduction_activities', '#10B981', 'play-circle')}
              {renderActivitySection('Development', 'development_activities', '#6366F1', 'construct')}
              {renderActivitySection('Conclusion', 'conclusion_activities', '#F59E0B', 'checkmark-done-circle')}
              {renderActivitySection('Extended', 'extended_activities', '#8B5CF6', 'extension-puzzle')}
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
        <View style={styles.modalOverlay}>
          <View style={[styles.modalContent, { maxWidth: 500 }]}>
            <View style={styles.modalHeader}>
              <View style={{ flexDirection: 'row', alignItems: 'center', gap: 12 }}>
                <View style={[styles.moveIconContainer, { backgroundColor: '#EEF2FF' }]}>
                  <Ionicons name="swap-horizontal" size={24} color="#6366F1" />
                </View>
                <Text style={styles.modalTitle}>Move {ENTITY_CONFIG[selectedEntity].singularTitle}</Text>
              </View>
              <TouchableOpacity onPress={() => setMoveModalVisible(false)}>
                <Ionicons name="close" size={24} color="#6B7280" />
              </TouchableOpacity>
            </View>

            <View style={styles.modalBody}>
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
            </View>

            <View style={styles.modalFooter}>
              <TouchableOpacity style={styles.cancelButton} onPress={() => setMoveModalVisible(false)}>
                <Text style={styles.cancelButtonText}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity style={[styles.saveButton, { backgroundColor: '#6366F1' }]} onPress={handleExecuteMove}>
                <Ionicons name="swap-horizontal" size={18} color="#FFFFFF" style={{ marginRight: 6 }} />
                <Text style={styles.saveButtonText}>Move Item</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
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
                <Ionicons name="close" size={24} color="#6B7280" />
              </TouchableOpacity>
            </View>

            {/* Mode Tabs */}
            <View style={styles.bulkModeTabs}>
              <TouchableOpacity
                style={[styles.bulkModeTab, bulkAddMode === 'textarea' && styles.bulkModeTabActive]}
                onPress={() => setBulkAddMode('textarea')}
              >
                <Ionicons name="document-text" size={18} color={bulkAddMode === 'textarea' ? '#6366F1' : '#6B7280'} />
                <Text style={[styles.bulkModeTabText, bulkAddMode === 'textarea' && styles.bulkModeTabTextActive]}>
                  Text Input
                </Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.bulkModeTab, bulkAddMode === 'table' && styles.bulkModeTabActive]}
                onPress={() => setBulkAddMode('table')}
              >
                <Ionicons name="grid" size={18} color={bulkAddMode === 'table' ? '#6366F1' : '#6B7280'} />
                <Text style={[styles.bulkModeTabText, bulkAddMode === 'table' && styles.bulkModeTabTextActive]}>
                  Table Input
                </Text>
              </TouchableOpacity>
            </View>

            <ScrollView style={styles.modalBody}>
              {bulkAddMode === 'textarea' ? (
                <View>
                  <Text style={styles.inputLabel}>Enter one item per line:</Text>
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
                    Tip: Copy and paste from a document or spreadsheet
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
                    <Ionicons name="add" size={20} color="#6366F1" />
                    <Text style={styles.bulkAddRowBtnText}>Add Row</Text>
                  </TouchableOpacity>
                </View>
              )}
            </ScrollView>

            {/* Item Count */}
            <View style={styles.bulkItemCount}>
              <Ionicons name="layers" size={16} color="#6B7280" />
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
    borderBottomColor: '#E5E7EB'
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
    backgroundColor: '#6366F1'
  },
  viewToggleText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#6366F1'
  },
  viewToggleTextActive: {
    color: '#FFFFFF'
  },
  breadcrumbContainer: {
    backgroundColor: '#FFFFFF',
    paddingVertical: 10,
    paddingHorizontal: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB'
  },
  breadcrumb: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    backgroundColor: '#EEF2FF',
    borderRadius: 4
  },
  breadcrumbText: {
    fontSize: 13,
    color: '#6366F1',
    fontWeight: '500',
    maxWidth: 120
  },
  entitySelector: {
    backgroundColor: '#FFFFFF',
    paddingVertical: 12,
    paddingHorizontal: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
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
    borderBottomColor: '#E5E7EB'
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#111827',
    flex: 1
  },
  headerCount: {
    fontSize: 14,
    color: '#6B7280',
    marginRight: 12
  },
  addButton: {
    backgroundColor: '#6366F1',
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center'
  },
  learningActivitiesButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#ECFDF5',
    marginHorizontal: 16,
    marginTop: 12,
    padding: 14,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#84CC16',
    gap: 10
  },
  learningActivitiesButtonText: {
    flex: 1,
    fontSize: 15,
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
    color: '#111827'
  },
  itemDescription: {
    fontSize: 12,
    color: '#6B7280',
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
    borderRightColor: '#E5E7EB'
  },
  editButton: {
    flex: 1,
    padding: 10,
    alignItems: 'center',
    borderRightWidth: 1,
    borderRightColor: '#E5E7EB'
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
    color: '#6B7280',
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
    borderBottomColor: '#E5E7EB'
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#111827'
  },
  modalSubtitle: {
    fontSize: 14,
    color: '#6B7280',
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
    borderColor: '#E5E7EB',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 12,
    fontSize: 16,
    color: '#111827'
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
    backgroundColor: '#6366F1'
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
    borderTopColor: '#E5E7EB',
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
    backgroundColor: '#6366F1',
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
    borderColor: '#E5E7EB',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 14,
    color: '#111827',
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
    color: '#6B7280',
    marginBottom: 4
  },
  moveCurrentItemName: {
    fontSize: 15,
    fontWeight: '600',
    color: '#111827'
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
    borderColor: '#E5E7EB'
  },
  moveOption: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB'
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
  // Bulk Add Modal Styles
  bulkModeTabs: {
    flexDirection: 'row',
    padding: 12,
    gap: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB'
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
    backgroundColor: '#EEF2FF'
  },
  bulkModeTabText: {
    fontSize: 14,
    fontWeight: '500',
    color: '#6B7280'
  },
  bulkModeTabTextActive: {
    color: '#6366F1',
    fontWeight: '600'
  },
  bulkTextarea: {
    borderWidth: 1,
    borderColor: '#E5E7EB',
    borderRadius: 12,
    padding: 16,
    fontSize: 14,
    color: '#111827',
    backgroundColor: '#F9FAFB',
    minHeight: 180,
    textAlignVertical: 'top'
  },
  bulkHelperText: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 8
  },
  bulkTableHeader: {
    flexDirection: 'row',
    gap: 8,
    paddingBottom: 8,
    borderBottomWidth: 2,
    borderBottomColor: '#E5E7EB',
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
    borderColor: '#E5E7EB',
    borderRadius: 8,
    padding: 12,
    fontSize: 14,
    color: '#111827',
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
    borderColor: '#E5E7EB',
    borderStyle: 'dashed',
    borderRadius: 10,
    marginTop: 8
  },
  bulkAddRowBtnText: {
    fontSize: 14,
    fontWeight: '500',
    color: '#6366F1'
  },
  bulkItemCount: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 6,
    paddingVertical: 12,
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
    backgroundColor: '#F9FAFB'
  },
  bulkItemCountText: {
    fontSize: 13,
    color: '#6B7280'
  }
});
