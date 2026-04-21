import { View, ActivityIndicator, StyleSheet, Text } from 'react-native';

export default function Index() {
  // AuthGate in _layout.tsx handles all navigation.
  // This page just shows a loading spinner until redirect happens.
  return (
    <View style={styles.container}>
      <ActivityIndicator size="large" color="#6366F1" />
      <Text style={styles.text}>Loading CBE Planner...</Text>
      <Text style={styles.subtext}>Developed by LEGIT LAB</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'transparent'
  },
  text: {
    marginTop: 16,
    color: '#6B7280',
    fontSize: 14
  },
  subtext: {
    marginTop: 8,
    color: '#9CA3AF',
    fontSize: 12
  }
});
