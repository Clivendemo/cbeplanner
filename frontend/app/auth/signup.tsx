import React, { useState, useRef } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  Alert
} from 'react-native';
import { useRouter } from 'expo-router';
import { useAuth } from '../../contexts/AuthContext';
import { Ionicons } from '@expo/vector-icons';
import { LandingLayout, FeatureTiles } from '../../components/LandingLayout';
import { useDebouncedAction } from '../../hooks/useDebouncedAction';
import { PasswordInput } from '../../components/PasswordInput';

export default function SignUp() {
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [schoolName, setSchoolName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { signUp } = useAuth();
  const router = useRouter();

  // Refs for inputs to manage focus
  const lastNameRef = useRef<TextInput>(null);
  const schoolRef = useRef<TextInput>(null);
  const emailRef = useRef<TextInput>(null);
  const passwordRef = useRef<TextInput>(null);
  const confirmPasswordRef = useRef<TextInput>(null);

  const handleSignUp = useDebouncedAction(async () => {
    if (!firstName || !lastName || !schoolName || !email || !password || !confirmPassword) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }

    if (password !== confirmPassword) {
      Alert.alert('Error', 'Passwords do not match');
      return;
    }

    if (password.length < 6) {
      Alert.alert('Error', 'Password must be at least 6 characters');
      return;
    }

    setLoading(true);
    try {
      const verifiedUser = await signUp(email, password, firstName, lastName, schoolName);
      if (!verifiedUser) {
        Alert.alert('Sign Up Failed', 'Unable to create account. Please try again.');
        setLoading(false);
      }
      // Navigation is handled by AuthGate in _layout.tsx
    } catch (error: any) {
      Alert.alert('Sign Up Failed', error.message);
      setLoading(false);
    }
  });

  return (
    <LandingLayout>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 0 : 20}
      >
        <View style={styles.header}>
          <Ionicons name="school" size={56} color="#5C6BC0" />
          <Text style={styles.title}>Create Account</Text>
          <Text style={styles.subtitle}>Join CBE Planner today</Text>
        </View>

        <View style={styles.form}>
            <View style={styles.inputContainer}>
              <Ionicons name="person-outline" size={20} color="#9CA3AF" style={styles.inputIcon} />
              <TextInput
                style={styles.input}
                placeholder="First Name"
                value={firstName}
                onChangeText={setFirstName}
                autoCapitalize="words"
                autoCorrect={false}
                placeholderTextColor="#9CA3AF"
                returnKeyType="next"
                onSubmitEditing={() => lastNameRef.current?.focus()}
                blurOnSubmit={false}
                testID="signup-firstname-input"
              />
            </View>

            <View style={styles.inputContainer}>
              <Ionicons name="person-outline" size={20} color="#9CA3AF" style={styles.inputIcon} />
              <TextInput
                ref={lastNameRef}
                style={styles.input}
                placeholder="Last Name"
                value={lastName}
                onChangeText={setLastName}
                autoCapitalize="words"
                autoCorrect={false}
                placeholderTextColor="#9CA3AF"
                returnKeyType="next"
                onSubmitEditing={() => schoolRef.current?.focus()}
                blurOnSubmit={false}
                testID="signup-lastname-input"
              />
            </View>

            <View style={styles.inputContainer}>
              <Ionicons name="business-outline" size={20} color="#9CA3AF" style={styles.inputIcon} />
              <TextInput
                ref={schoolRef}
                style={styles.input}
                placeholder="School Name"
                value={schoolName}
                onChangeText={setSchoolName}
                autoCapitalize="words"
                autoCorrect={false}
                placeholderTextColor="#9CA3AF"
                returnKeyType="next"
                onSubmitEditing={() => emailRef.current?.focus()}
                blurOnSubmit={false}
                testID="signup-school-input"
              />
            </View>

            <View style={styles.inputContainer}>
              <Ionicons name="mail-outline" size={20} color="#9CA3AF" style={styles.inputIcon} />
              <TextInput
                ref={emailRef}
                style={styles.input}
                placeholder="Email"
                value={email}
                onChangeText={setEmail}
                keyboardType="email-address"
                autoCapitalize="none"
                autoCorrect={false}
                placeholderTextColor="#9CA3AF"
                returnKeyType="next"
                onSubmitEditing={() => passwordRef.current?.focus()}
                blurOnSubmit={false}
                testID="signup-email-input"
              />
            </View>

            <View style={styles.inputContainer}>
              <Ionicons name="lock-closed-outline" size={20} color="#9CA3AF" style={styles.inputIcon} />
              <PasswordInput
                ref={passwordRef as any}
                inputStyle={styles.input}
                placeholder="Password"
                value={password}
                onChangeText={setPassword}
                autoCapitalize="none"
                autoCorrect={false}
                placeholderTextColor="#9CA3AF"
                returnKeyType="next"
                onSubmitEditing={() => confirmPasswordRef.current?.focus()}
                blurOnSubmit={false}
                testID="signup-password-input"
                testIDPrefix="signup-password"
                containerStyle={{ flex: 1 }}
              />
            </View>

            <View style={styles.inputContainer}>
              <Ionicons name="lock-closed-outline" size={20} color="#9CA3AF" style={styles.inputIcon} />
              <PasswordInput
                ref={confirmPasswordRef as any}
                inputStyle={styles.input}
                placeholder="Confirm Password"
                value={confirmPassword}
                onChangeText={setConfirmPassword}
                autoCapitalize="none"
                autoCorrect={false}
                placeholderTextColor="#9CA3AF"
                returnKeyType="done"
                onSubmitEditing={handleSignUp}
                testID="signup-confirm-password-input"
                testIDPrefix="signup-confirm-password"
                containerStyle={{ flex: 1 }}
              />
            </View>

            <TouchableOpacity
              style={[styles.button, loading && styles.buttonDisabled]}
              onPress={handleSignUp}
              disabled={loading}
              testID="signup-submit-btn"
            >
              <Text style={styles.buttonText}>
                {loading ? 'Creating Account...' : 'Sign Up'}
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.linkButton}
              onPress={() => router.push('/auth/login')}
            >
              <Text style={styles.linkText}>Already have an account? Sign In</Text>
            </TouchableOpacity>
          </View>

        <FeatureTiles />
      </KeyboardAvoidingView>
    </LandingLayout>
  );
}

const styles = StyleSheet.create({
  header: { alignItems: 'center', marginBottom: 24 },
  title: { fontSize: 26, fontWeight: 'bold', color: '#1A1A3A', marginTop: 12 },
  subtitle: { fontSize: 13, color: '#5A5A7A', marginTop: 6 },
  form: { width: '100%' },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    paddingHorizontal: 14,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#DDDDF5'
  },
  inputIcon: { marginRight: 10 },
  input: { flex: 1, height: 46, fontSize: 15, color: '#1A1A3A' },
  button: { backgroundColor: '#E65100', borderRadius: 12, paddingVertical: 14, alignItems: 'center', marginTop: 6 },
  buttonDisabled: { opacity: 0.6 },
  buttonText: { color: '#FFFFFF', fontSize: 15, fontWeight: '600' },
  linkButton: { marginTop: 18, alignItems: 'center' },
  linkText: { color: '#5C6BC0', fontSize: 13, fontWeight: '500' }
});
