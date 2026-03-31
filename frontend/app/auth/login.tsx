import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  Alert,
  Modal,
  Pressable,
  Animated,
  Dimensions
} from 'react-native';
import { useRouter } from 'expo-router';
import { useAuth } from '../../contexts/AuthContext';
import { Ionicons } from '@expo/vector-icons';
import { SafeAreaView, useSafeAreaInsets } from 'react-native-safe-area-context';

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
  const insets = useSafeAreaInsets();

  // Refs for inputs to manage focus
  const emailRef = useRef<TextInput>(null);
  const passwordRef = useRef<TextInput>(null);

  // Marquee animation
  const screenWidth = Dimensions.get('window').width;
  const marqueeAnim = useRef(new Animated.Value(screenWidth)).current;
  
  useEffect(() => {
    const animation = Animated.loop(
      Animated.timing(marqueeAnim, {
        toValue: -450,
        duration: 18000,
        useNativeDriver: true,
      })
    );
    animation.start();
    return () => animation.stop();
  }, []);

  const handleLogin = async () => {
    if (!email || !password) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }

    setLoading(true);
    try {
      const verifiedUser = await signIn(email, password, rememberMe);
      if (verifiedUser) {
        if (verifiedUser.role === 'admin') {
          router.replace('/(admin)/dashboard');
        } else {
          router.replace('/(teacher)/dashboard');
        }
      }
    } catch (error: any) {
      Alert.alert('Login Failed', error.message);
      setLoading(false);
    }
  };

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
      Alert.alert(
        'Password Reset Email Sent',
        `We've sent a password reset link to ${resetEmail}. Please check your inbox and spam folder.`,
        [{ text: 'OK', onPress: () => setResetModalVisible(false) }]
      );
    } catch (error: any) {
      let message = 'Failed to send reset email';
      if (error.message.includes('user-not-found')) {
        message = 'No account found with this email address';
      } else if (error.message.includes('invalid-email')) {
        message = 'Please enter a valid email address';
      }
      Alert.alert('Error', message);
    } finally {
      setResetting(false);
    }
  };

  return (
    <SafeAreaView style={styles.safeArea} edges={['top', 'left', 'right']}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.container}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 0 : 20}
      >
        <ScrollView 
          contentContainerStyle={[styles.scrollContent, { paddingBottom: Math.max(insets.bottom, 24) }]}
          keyboardShouldPersistTaps="handled"
          showsVerticalScrollIndicator={false}
        >
          <View style={styles.header}>
            <Ionicons name="school" size={64} color="#6366F1" />
            <Text style={styles.title}>CBE Planner</Text>
            <Text style={styles.subtitle}>Kenyan Teacher Lesson Planning</Text>
            
            <View style={styles.marqueeContainer}>
              <Animated.View 
                style={[
                  styles.marqueeContent,
                  { transform: [{ translateX: marqueeAnim }] }
                ]}
              >
                <Text style={styles.marqueeText}>
                  Every lesson mapped.  Every outcome measurable.
                </Text>
              </Animated.View>
            </View>
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
              />
            </View>

            <View style={styles.inputContainer}>
              <Ionicons name="lock-closed-outline" size={20} color="#9CA3AF" style={styles.inputIcon} />
              <TextInput
                ref={passwordRef}
                style={styles.input}
                placeholder="Password"
                value={password}
                onChangeText={setPassword}
                secureTextEntry
                autoCapitalize="none"
                autoCorrect={false}
                placeholderTextColor="#9CA3AF"
                returnKeyType="done"
                onSubmitEditing={handleLogin}
                testID="login-password-input"
              />
            </View>

            <Pressable
              onPress={() => setRememberMe(!rememberMe)}
              style={styles.rememberMeRow}
            >
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
            >
              <Text style={styles.buttonText}>
                {loading ? 'Signing In...' : 'Sign In'}
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.forgotPasswordButton}
              onPress={handleForgotPassword}
            >
              <Text style={styles.forgotPasswordText}>Forgot Password?</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.linkButton}
              onPress={() => router.push('/auth/signup')}
            >
              <Text style={styles.linkText}>Don't have an account? Sign Up</Text>
            </TouchableOpacity>
          </View>

          <View style={styles.footer}>
            <Text style={styles.footerText}>KICD-Aligned Lesson Planning</Text>
            <Text style={styles.footerText}>For Kenyan Teachers</Text>
            <View style={{ width: '100%', alignItems: 'center' }}>
              <Text style={styles.developerText}>Developed by LEGIT LAB</Text>
            </View>
          </View>
        </ScrollView>
      </KeyboardAvoidingView>

      {/* Password Reset Modal */}
      <Modal
        visible={resetModalVisible}
        animationType="slide"
        transparent={true}
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
              <Text style={styles.resetButtonText}>
                {resetting ? 'Sending...' : 'Send Reset Link'}
              </Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#F9FAFB'
  },
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB'
  },
  scrollContent: {
    flexGrow: 1,
    padding: 24,
    justifyContent: 'center'
  },
  header: {
    alignItems: 'center',
    marginBottom: 48
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#111827',
    marginTop: 16
  },
  subtitle: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 8
  },
  marqueeContainer: {
    height: 36,
    width: '100%',
    marginTop: 16,
    overflow: 'hidden',
    justifyContent: 'center'
  },
  marqueeContent: {
    flexDirection: 'row',
    alignItems: 'center',
    position: 'absolute'
  },
  marqueeText: {
    fontSize: 14,
    fontWeight: '500',
    color: '#10B981',
    fontStyle: 'italic',
    letterSpacing: 0.3
  },
  form: {
    width: '100%'
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    paddingHorizontal: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#E5E7EB'
  },
  inputIcon: {
    marginRight: 12
  },
  input: {
    flex: 1,
    height: 48,
    fontSize: 16,
    color: '#111827'
  },
  button: {
    backgroundColor: '#6366F1',
    borderRadius: 12,
    paddingVertical: 16,
    alignItems: 'center',
    marginTop: 8
  },
  buttonDisabled: {
    opacity: 0.6
  },
  buttonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600'
  },
  linkButton: {
    marginTop: 24,
    alignItems: 'center'
  },
  linkText: {
    color: '#6366F1',
    fontSize: 14,
    fontWeight: '500'
  },
  forgotPasswordButton: {
    marginTop: 16,
    alignItems: 'center'
  },
  forgotPasswordText: {
    color: '#6B7280',
    fontSize: 14
  },
  footer: {
    marginTop: 48,
    padding: 16,
    backgroundColor: '#EEF2FF',
    borderRadius: 12,
    alignItems: 'center'
  },
  footerText: {
    fontSize: 12,
    color: '#4F46E5',
    textAlign: 'center',
    marginBottom: 4
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    padding: 24
  },
  modalContent: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 24
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#111827'
  },
  modalDescription: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 24,
    lineHeight: 20
  },
  modalInputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F9FAFB',
    borderRadius: 12,
    paddingHorizontal: 16,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: '#E5E7EB'
  },
  modalInput: {
    flex: 1,
    height: 48,
    fontSize: 16,
    color: '#111827'
  },
  resetButton: {
    backgroundColor: '#6366F1',
    borderRadius: 12,
    paddingVertical: 16,
    alignItems: 'center'
  },
  resetButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600'
  },
  developerText: {
    fontSize: 11,
    color: '#9CA3AF',
    marginTop: 8,
    fontWeight: '500',
    textAlign: 'center'
  },
  rememberMeRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 12,
    marginBottom: 4,
    paddingVertical: 8
  },
  checkbox: {
    width: 20,
    height: 20,
    borderRadius: 4,
    borderWidth: 2,
    borderColor: '#D1D5DB',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 8,
    backgroundColor: '#FFFFFF'
  },
  checkboxChecked: {
    backgroundColor: '#6366F1',
    borderColor: '#6366F1'
  },
  rememberMeText: {
    fontSize: 14,
    color: '#374151'
  }
});
