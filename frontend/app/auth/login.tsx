import React, { useState, useRef } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  Alert,
  Modal,
  Pressable,
} from 'react-native';
import { useRouter } from 'expo-router';
import { useAuth } from '../../contexts/AuthContext';
import { Ionicons } from '@expo/vector-icons';
import { LandingLayout, FeatureTiles } from '../../components/LandingLayout';
import { useDebouncedAction } from '../../hooks/useDebouncedAction';
import { PasswordInput } from '../../components/PasswordInput';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [loading, setLoading] = useState(false);
  const [resetModalVisible, setResetModalVisible] = useState(false);
  const [resetEmail, setResetEmail] = useState('');
  const [resetting, setResetting] = useState(false);
  const { signIn, resetPassword } = useAuth();
  const router = useRouter();

  const emailRef = useRef<TextInput>(null);
  const passwordRef = useRef<TextInput>(null);

  const handleLogin = useDebouncedAction(async () => {
    if (!email || !password) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }
    setLoading(true);
    try {
      const verifiedUser = await signIn(email, password, rememberMe);
      if (!verifiedUser) {
        Alert.alert('Login Failed', 'Unable to verify account. Please try again.');
        setLoading(false);
      }
    } catch (error: any) {
      Alert.alert('Login Failed', error.message || 'An error occurred');
      setLoading(false);
    }
  });

  const handleForgotPassword = () => {
    setResetEmail(email);
    setResetModalVisible(true);
  };

  const handleResetPassword = async () => {
    if (!resetEmail) {
      Alert.alert('Error', 'Please enter your email address');
      return;
    }
    setResetting(true);
    try {
      await resetPassword(resetEmail);
      // Close the modal first so the UX is responsive even if the Alert
      // callback doesn't fire (web quirk on react-native-web).
      setResetModalVisible(false);
      setResetEmail('');
      Alert.alert(
        'Password Reset Email Sent',
        `We've sent a password reset link to ${resetEmail}. Please check your inbox and spam folder.`
      );
    } catch (error: any) {
      let message = 'Failed to send reset email';
      if (error.message.includes('user-not-found')) message = 'No account found with this email address';
      else if (error.message.includes('invalid-email')) message = 'Please enter a valid email address';
      Alert.alert('Error', message);
    } finally {
      setResetting(false);
    }
  };

  return (
    <LandingLayout>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 0 : 20}
      >
        <View style={styles.header}>
          <Ionicons name="school" size={56} color="#5B5BD6" />
          <Text style={styles.title}>CBE Planner</Text>
          <Text style={styles.subtitle}>Kenyan Teacher Lesson Planning</Text>
        </View>

        <View style={styles.form}>
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
              testID="login-email-input"
              data-testid="login-email-input"
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
              returnKeyType="done"
              onSubmitEditing={handleLogin}
              testID="login-password-input"
              testIDPrefix="login-password"
              containerStyle={{ flex: 1 }}
            />
          </View>

          <Pressable onPress={() => setRememberMe(!rememberMe)} style={styles.rememberMeRow}>
            <View style={[styles.checkbox, rememberMe && styles.checkboxChecked]}>
              {rememberMe && <Ionicons name="checkmark" size={14} color="#FFFFFF" />}
            </View>
            <Text style={styles.rememberMeText}>Remember me</Text>
          </Pressable>

          <TouchableOpacity
            style={[styles.button, loading && styles.buttonDisabled]}
            onPress={handleLogin}
            disabled={loading}
            testID="login-submit-btn"
            data-testid="login-submit-btn"
          >
            <Text style={styles.buttonText}>{loading ? 'Signing In...' : 'Sign In'}</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.forgotPasswordButton} onPress={handleForgotPassword}>
            <Text style={styles.forgotPasswordText}>Forgot Password?</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.linkButton} onPress={() => router.push('/auth/signup')}>
            <Text style={styles.linkText}>Don't have an account? Sign Up</Text>
          </TouchableOpacity>
        </View>

        <FeatureTiles />

        <View style={styles.footer}>
          <Text style={styles.footerText}>KICD-Aligned Lesson Planning</Text>
          <Text style={styles.footerText}>For Kenyan Teachers</Text>
          <Text style={styles.developerText}>Developed by LEGIT LAB</Text>
        </View>
      </KeyboardAvoidingView>

      <Modal
        visible={resetModalVisible}
        animationType="slide"
        transparent
        onRequestClose={() => setResetModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Reset Password</Text>
              <TouchableOpacity onPress={() => setResetModalVisible(false)}>
                <Ionicons name="close" size={24} color="#6B7280" />
              </TouchableOpacity>
            </View>
            <Text style={styles.modalDescription}>
              Enter your email address and we'll send you a link to reset your password.
            </Text>
            <View style={styles.modalInputContainer}>
              <Ionicons name="mail-outline" size={20} color="#9CA3AF" style={styles.inputIcon} />
              <TextInput
                style={styles.modalInput}
                placeholder="Email address"
                value={resetEmail}
                onChangeText={setResetEmail}
                keyboardType="email-address"
                autoCapitalize="none"
                autoCorrect={false}
                placeholderTextColor="#9CA3AF"
              />
            </View>
            <TouchableOpacity
              style={[styles.resetButton, resetting && styles.buttonDisabled]}
              onPress={handleResetPassword}
              disabled={resetting}
            >
              <Text style={styles.resetButtonText}>{resetting ? 'Sending...' : 'Send Reset Link'}</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </LandingLayout>
  );
}

const styles = StyleSheet.create({
  header: { alignItems: 'center', marginBottom: 28 },
  title: { fontSize: 28, fontWeight: 'bold', color: '#111827', marginTop: 12 },
  subtitle: { fontSize: 13, color: '#6B7280', marginTop: 6 },
  form: { width: '100%' },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    paddingHorizontal: 14,
    marginBottom: 14,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  inputIcon: { marginRight: 10 },
  input: { flex: 1, height: 46, fontSize: 15, color: '#111827' },
  button: { backgroundColor: '#5B5BD6', borderRadius: 12, paddingVertical: 14, alignItems: 'center', marginTop: 6 },
  buttonDisabled: { opacity: 0.6 },
  buttonText: { color: '#FFFFFF', fontSize: 15, fontWeight: '600' },
  linkButton: { marginTop: 20, alignItems: 'center' },
  linkText: { color: '#5B5BD6', fontSize: 13, fontWeight: '500' },
  forgotPasswordButton: { marginTop: 14, alignItems: 'center' },
  forgotPasswordText: { color: '#6B7280', fontSize: 13 },
  footer: { marginTop: 28, padding: 14, backgroundColor: '#EEF2FF', borderRadius: 12, alignItems: 'center' },
  footerText: { fontSize: 11, color: '#4F46E5', textAlign: 'center', marginBottom: 3 },
  developerText: { fontSize: 10, color: '#9CA3AF', marginTop: 6, fontWeight: '500' },
  rememberMeRow: { flexDirection: 'row', alignItems: 'center', marginTop: 8, marginBottom: 4, paddingVertical: 6 },
  checkbox: {
    width: 18, height: 18, borderRadius: 4, borderWidth: 2, borderColor: '#D1D5DB',
    alignItems: 'center', justifyContent: 'center', marginRight: 8, backgroundColor: '#FFFFFF',
  },
  checkboxChecked: { backgroundColor: '#5B5BD6', borderColor: '#5B5BD6' },
  rememberMeText: { fontSize: 13, color: '#374151' },
  modalOverlay: { flex: 1, backgroundColor: 'rgba(0, 0, 0, 0.5)', justifyContent: 'center', padding: 24 },
  modalContent: { backgroundColor: '#FFFFFF', borderRadius: 16, padding: 24 },
  modalHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 },
  modalTitle: { fontSize: 18, fontWeight: 'bold', color: '#111827' },
  modalDescription: { fontSize: 13, color: '#6B7280', marginBottom: 20, lineHeight: 20 },
  modalInputContainer: {
    flexDirection: 'row', alignItems: 'center', backgroundColor: '#F9FAFB',
    borderRadius: 12, paddingHorizontal: 16, marginBottom: 20, borderWidth: 1, borderColor: '#E5E7EB',
  },
  modalInput: { flex: 1, height: 46, fontSize: 15, color: '#111827' },
  resetButton: { backgroundColor: '#5B5BD6', borderRadius: 12, paddingVertical: 14, alignItems: 'center' },
  resetButtonText: { color: '#FFFFFF', fontSize: 15, fontWeight: '600' },
});
