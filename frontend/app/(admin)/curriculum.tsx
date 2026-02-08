import React, { useState, useEffect } from 'react';
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
  FlatList
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../../contexts/AuthContext';
import axios from 'axios';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

type EntityType = 'grades' | 'subjects' | 'strands' | 'substrands' | 'slos' | 'competencies' | 'values' | 'pcis' | 'assessments' | 'activities';

interface Entity {
  id: string;
  name?: string;
  description?: string;
  order?: number;
  gradeIds?: string[];
  subjectId?: string;
  strandId?: string;
  substrandId?: string;
}

const ENTITY_CONFIG: Record<EntityType, { title: string; icon: string; color: string; fields: string[]; parent?: EntityType }> = {
  grades: { title: 'Grades', icon: 'school', color: '#6366F1', fields: ['name', 'order'] },
  subjects: { title: 'Subjects', icon: 'book', color: '#10B981', fields: ['name'], parent: 'grades' },
  strands: { title: 'Strands', icon: 'git-branch', color: '#F59E0B', fields: ['name'], parent: 'subjects' },
  substrands: { title: 'Sub-strands', icon: 'git-merge', color: '#EF4444', fields: ['name'], parent: 'strands' },
  slos: { title: 'SLOs', icon: 'checkmark-circle', color: '#8B5CF6', fields: ['name', 'description'], parent: 'substrands' },
  competencies: { title: 'Competencies', icon: 'star', color: '#EC4899', fields: ['name', 'description'] },
  values: { title: 'Values', icon: 'heart', color: '#14B8A6', fields: ['name', 'description'] },
  pcis: { title: 'PCIs', icon: 'globe', color: '#F97316', fields: ['name', 'description'] },
  assessments: { title: 'Assessments', icon: 'clipboard', color: '#06B6D4', fields: ['name', 'description'] },
  activities: { title: 'Activities', icon: 'flash', color: '#84CC16', fields: ['description'], parent: 'strands' }
};

export default function Curriculum() {
  const { firebaseUser } = useAuth();
  const [selectedEntity, setSelectedEntity] = useState<EntityType>('grades');
  const [data, setData] = useState<Entity[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingItem, setEditingItem] = useState<Entity | null>(null);
  const [formData, setFormData] = useState<Record<string, string>>({});
  
  // Parent data for cascading
  const [grades, setGrades] = useState<Entity[]>([]);
  const [subjects, setSubjects] = useState<Entity[]>([]);
  const [strands, setStrands] = useState<Entity[]>([]);
  const [substrands, setSubstrands] = useState<Entity[]>([]);
  const [selectedParentId, setSelectedParentId] = useState<string>('');

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
    loadData();
  }, [selectedEntity]);

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

  const loadSubjects = async () => {
    try {
      const headers = await getHeaders();
      const response = await axios.get(`${BACKEND_URL}/api/admin/subjects`, { headers });
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

  const loadData = async () => {
    setLoading(true);
    try {
      const headers = await getHeaders();
      const response = await axios.get(`${BACKEND_URL}/api/admin/${selectedEntity}`, { headers });
      if (response.data.success) {
        const key = selectedEntity === 'slos' ? 'slos' : selectedEntity;
        setData(response.data[key] || []);
      }
      
      // Load parent data if needed
      if (selectedEntity === 'subjects') {
        loadGrades();
      } else if (selectedEntity === 'strands') {
        loadSubjects();
      } else if (selectedEntity === 'substrands' || selectedEntity === 'activities') {
        loadStrands();
      } else if (selectedEntity === 'slos') {
        loadSubstrands();
      }
    } catch (error: any) {
      console.error('Error loading data:', error);
      Alert.alert('Error', 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const openAddModal = () => {
    setEditingItem(null);
    setFormData({});
    setSelectedParentId('');
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
    
    setModalVisible(true);
  };

  const handleSave = async () => {
    try {
      const headers = await getHeaders();
      const config = ENTITY_CONFIG[selectedEntity];
      
      let payload: any = { ...formData };
      
      // Add parent relationships
      if (selectedEntity === 'subjects' && selectedParentId) {
        payload.gradeIds = [selectedParentId];
      } else if (selectedEntity === 'strands' && selectedParentId) {
        payload.subjectId = selectedParentId;
      } else if ((selectedEntity === 'substrands' || selectedEntity === 'activities') && selectedParentId) {
        payload.strandId = selectedParentId;
        if (selectedEntity === 'activities') {
          // Activities need both strandId and substrandId
          payload.substrandId = selectedParentId;
        }
      } else if (selectedEntity === 'slos' && selectedParentId) {
        payload.substrandId = selectedParentId;
      }
      
      // Convert order to number if present
      if (payload.order) {
        payload.order = parseInt(payload.order);
      }

      if (editingItem) {
        // Update
        await axios.put(
          `${BACKEND_URL}/api/admin/${selectedEntity}/${editingItem.id}`,
          payload,
          { headers }
        );
        Alert.alert('Success', 'Updated successfully');
      } else {
        // Create
        await axios.post(
          `${BACKEND_URL}/api/admin/${selectedEntity}`,
          payload,
          { headers }
        );
        Alert.alert('Success', 'Created successfully');
      }
      
      setModalVisible(false);
      loadData();
    } catch (error: any) {
      console.error('Error saving:', error.response?.data || error);
      Alert.alert('Error', error.response?.data?.detail || 'Failed to save');
    }
  };

  const handleDelete = (item: Entity) => {
    Alert.alert(
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
              await axios.delete(
                `${BACKEND_URL}/api/admin/${selectedEntity}/${item.id}`,
                { headers }
              );
              Alert.alert('Success', 'Deleted successfully');
              loadData();
            } catch (error: any) {
              Alert.alert('Error', error.response?.data?.detail || 'Failed to delete');
            }
          }
        }
      ]
    );
  };

  const getParentOptions = () => {
    switch (selectedEntity) {
      case 'subjects': return grades;
      case 'strands': return subjects;
      case 'substrands':
      case 'activities': return strands;
      case 'slos': return substrands;
      default: return [];
    }
  };

  const getParentLabel = () => {
    switch (selectedEntity) {
      case 'subjects': return 'Select Grade';
      case 'strands': return 'Select Subject';
      case 'substrands':
      case 'activities': return 'Select Strand';
      case 'slos': return 'Select Sub-strand';
      default: return '';
    }
  };

  const renderItem = ({ item }: { item: Entity }) => {
    const config = ENTITY_CONFIG[selectedEntity];
    return (
      <View style={styles.listItem}>
        <View style={[styles.itemIcon, { backgroundColor: config.color + '20' }]}>
          <Ionicons name={config.icon as any} size={20} color={config.color} />
        </View>
        <View style={styles.itemContent}>
          <Text style={styles.itemName}>{item.name || item.description}</Text>
          {item.description && item.name && (
            <Text style={styles.itemDescription} numberOfLines={1}>{item.description}</Text>
          )}
          {item.order !== undefined && (
            <Text style={styles.itemMeta}>Order: {item.order}</Text>
          )}
        </View>
        <TouchableOpacity style={styles.editButton} onPress={() => openEditModal(item)}>
          <Ionicons name="pencil" size={18} color="#6366F1" />
        </TouchableOpacity>
        <TouchableOpacity style={styles.deleteButton} onPress={() => handleDelete(item)}>
          <Ionicons name="trash" size={18} color="#EF4444" />
        </TouchableOpacity>
      </View>
    );
  };

  return (
    <View style={styles.container}>
      {/* Entity Selector */}
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.entitySelector}>
        {(Object.keys(ENTITY_CONFIG) as EntityType[]).map((entity) => {
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

      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>{ENTITY_CONFIG[selectedEntity].title}</Text>
        <Text style={styles.headerCount}>{data.length} items</Text>
        <TouchableOpacity style={styles.addButton} onPress={openAddModal}>
          <Ionicons name="add" size={24} color="#FFFFFF" />
        </TouchableOpacity>
      </View>

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
                {editingItem ? 'Edit' : 'Add'} {ENTITY_CONFIG[selectedEntity].title.slice(0, -1)}
              </Text>
              <TouchableOpacity onPress={() => setModalVisible(false)}>
                <Ionicons name="close" size={24} color="#6B7280" />
              </TouchableOpacity>
            </View>

            <ScrollView style={styles.modalBody}>
              {/* Parent Selector */}
              {ENTITY_CONFIG[selectedEntity].parent && (
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
              {ENTITY_CONFIG[selectedEntity].fields.map((field) => (
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
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB'
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
  modalBody: {
    padding: 16,
    maxHeight: 400
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
  }
});
