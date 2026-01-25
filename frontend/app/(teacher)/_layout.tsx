import { Tabs } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';

export default function TeacherLayout() {
  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: '#6366F1',
        tabBarInactiveTintColor: '#9CA3AF',
        tabBarStyle: {
          backgroundColor: '#FFFFFF',
          borderTopColor: '#E5E7EB',
          height: 60,
          paddingBottom: 8
        },
        headerStyle: {
          backgroundColor: '#6366F1'
        },
        headerTintColor: '#FFFFFF',
        headerTitleStyle: {
          fontWeight: 'bold'
        }
      }}
    >
      <Tabs.Screen
        name="home"
        options={{
          title: 'Create Lesson',
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="add-circle-outline" size={size} color={color} />
          )
        }}
      />
      <Tabs.Screen
        name="notes"
        options={{
          title: 'Generate Notes',
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="document-outline" size={size} color={color} />
          )
        }}
      />
      <Tabs.Screen
        name="lessons"
        options={{
          title: 'My Lessons',
          tabBarIcon: ({ color, size}) => (
            <Ionicons name="folder-outline" size={size} color={color} />
          )
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: 'Profile',
          tabBarIcon: ({ color, size }) => (
            <Ionicons name="person-outline" size={size} color={color} />
          )
        }}
      />
    </Tabs>
  );
}