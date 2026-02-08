import { Stack } from 'expo-router';

export default function TeacherLayout() {
  return (
    <Stack
      screenOptions={{
        headerStyle: {
          backgroundColor: '#6366F1'
        },
        headerTintColor: '#FFFFFF',
        headerTitleStyle: {
          fontWeight: 'bold'
        }
      }}
    >
      <Stack.Screen
        name="dashboard"
        options={{
          title: 'CBE Planner',
          headerShown: true
        }}
      />
      <Stack.Screen
        name="home"
        options={{
          title: 'Create Lesson Plan'
        }}
      />
      <Stack.Screen
        name="notes"
        options={{
          title: 'Generate Notes'
        }}
      />
      <Stack.Screen
        name="lessons"
        options={{
          title: 'My Lesson Plans'
        }}
      />
      <Stack.Screen
        name="profile"
        options={{
          title: 'Profile'
        }}
      />
      <Stack.Screen
        name="schemes"
        options={{
          title: 'Schemes of Work'
        }}
      />
      <Stack.Screen
        name="revision"
        options={{
          title: 'Revision Papers'
        }}
      />
    </Stack>
  );
}
