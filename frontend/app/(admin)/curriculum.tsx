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
      const response = await axios.get(`${BACKEND_URL}/api/admin/subjects`, { headers });
      if (response.data.success) {
        const allSubjects = response.data.subjects;
        if (gradeId) {
          setSubjects(allSubjects.filter((s: any) => s.gradeIds?.includes(gradeId)));
        } else {
          setSubjects(allSubjects);
        }
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
      const response = await axios.get(`${BACKEND_URL}/api/admin/subjects`, { headers });
      if (response.data.success) {
        const filtered = response.data.subjects.filter((s: any) => s.gradeIds?.includes(grade.id));
        setData(filtered);
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
    
    return (
      <TouchableOpacity 
        style={styles.listItem}
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
        
        <TouchableOpacity style={styles.editButton} onPress={() => openEditModal(item)}>
          <Ionicons name="pencil" size={18} color="#6366F1" />
        </TouchableOpacity>
        <TouchableOpacity style={styles.deleteButton} onPress={() => handleDelete(item)}>
          <Ionicons name="trash" size={18} color="#EF4444" />
        </TouchableOpacity>
      </TouchableOpacity>
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
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8
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
  editButton: {
    padding: 8,
    marginRight: 4
  },
  deleteButton: {
    padding: 8
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
  }
});
