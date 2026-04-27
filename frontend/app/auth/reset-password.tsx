/**
 * Custom Firebase password reset handler.
 *
 * Firebase's password-reset email can be pointed at this route (via the
 * Firebase Console → Authentication → Templates → "Customize action URL"),
 * so that instead of using Firebase's default hosted reset page, the user
 * lands here and is asked for BOTH a new password AND a confirm-password
 * inside CBE Planner, with the reveal-password eye toggle.
 *
 * The URL looks like:
 *   /auth/reset-password?mode=resetPassword&oobCode=XXXX
 *
 * We verify the oobCode with Firebase, display the associated email, collect
 * + confirm the new password, then submit via confirmPasswordReset.
 */
import React, { useEffect, useRef, useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  KeyboardAvoidingView,
  Platform,
  Alert,
  ActivityIndicator,
  TextInput,
} from 'react-native';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { LandingLayout } from '../../components/LandingLayout';
import { useAuth } from '../../contexts/AuthContext';
import { useDebouncedAction } from '../../hooks/useDebouncedAction';
import { PasswordInput } from '../../components/PasswordInput';

export default function ResetPassword() {
  const params = useLocalSearchParams<{ oobCode?: string; mode?: string }>();
  const router = useRouter();
  const { verifyResetCode, confirmReset } = useAuth();

  const [oobCode, setOobCode] = useState<string | null>(null);
  const [email, setEmail] = useState<string | null>(null);
  const [verifyState, setVerifyState] = useState<'pending' | 'ok' | 'error'>('pending');
  const [verifyError, setVerifyError] = useState<string | null>(null);

  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [done, setDone] = useState(false);

  const confirmRef = useRef<TextInput>(null);

  // Verify the oobCode as soon as we land.
  useEffect(() => {
    const code = typeof params.oobCode === 'string' ? params.oobCode : null;
    if (!code) {
      // Support the case where the URL has hash-style params (rare with Firebase but defensive)
      setVerifyState('error');
      setVerifyError('Missing or invalid reset link. Please request a new password reset email.');
      return;
    }
    setOobCode(code);
    (async () => {
      try {
        const resolvedEmail = await verifyResetCode(code);
        setEmail(resolvedEmail);
        setVerifyState('ok');
      } catch (err: any) {
        setVerifyState('error');
        const msg = err?.message || '';
        if (msg.includes('expired-action-code')) {
          setVerifyError('This reset link has expired. Please request a new password reset email.');
        } else if (msg.includes('invalid-action-code')) {
          setVerifyError('This reset link is invalid or has already been used. Please request a new one.');
        } else {
          setVerifyError('Unable to verify reset link. Please request a new password reset email.');
        }
      }
    })();
  }, [params.oobCode]);

  const handleSubmit = useDebouncedAction(async () => {
    if (!oobCode) return;
    if (!password || !confirmPassword) {
      Alert.alert('Error', 'Please fill in both password fields');
      return;
    }
    if (password.length < 6) {
      Alert.alert('Error', 'Password must be at least 6 characters');
      return;
    }
    if (password !== confirmPassword) {
      Alert.alert('Error', 'Passwords do not match');
      return;
    }
    setSubmitting(true);
    try {
      await confirmReset(oobCode, password);
      setDone(true);
    } catch (err: any) {
      const msg = err?.message || '';
      let friendly = 'Failed to reset password. Please try again.';
      if (msg.includes('weak-password')) friendly = 'Password is too weak. Use at least 6 characters.';
      else if (msg.includes('expired-action-code')) friendly = 'Reset link has expired. Request a new one.';
      else if (msg.includes('invalid-action-code')) friendly = 'Reset link is invalid or already used.';
      Alert.alert('Reset Failed', friendly);
    } finally {
      setSubmitting(false);
    }
  });

  // Success screen
  if (done) {
    return (
      <LandingLayout>
        <View style={styles.header}>
          <Ionicons name="checkmark-circle" size={56} color="#10B981" />
          <Text style={styles.title}>Password Updated</Text>
          <Text style={styles.subtitle}>
            Your password has been reset successfully. You can now sign in with your new password.
          </Text>
        </View>
        <TouchableOpacity
          style={styles.button}
          onPress={() => router.replace('/auth/login')}
          testID="reset-done-signin-btn"
          data-testid="reset-done-signin-btn"
        >
          <Text style={styles.buttonText}>Go to Sign In</Text>
        </TouchableOpacity>
      </LandingLayout>
    );
  }

  // Verifying oobCode
  if (verifyState === 'pending') {
    return (
      <LandingLayout>
        <View style={styles.centered}>
          <ActivityIndicator size="large" color="#5C6BC0" />
          <Text style={styles.subtitle}>Verifying reset link…</Text>
        </View>
      </LandingLayout>
    );
  }

  // Invalid / expired link
  if (verifyState === 'error') {
    return (
      <LandingLayout>
        <View style={styles.header}>
          <Ionicons name="alert-circle" size={56} color="#EF4444" />
          <Text style={styles.title}>Reset Link Problem</Text>
          <Text style={styles.subtitle}>{verifyError}</Text>
        </View>
        <TouchableOpacity
          style={styles.button}
          onPress={() => router.replace('/auth/login')}
          testID="reset-error-back-btn"
          data-testid="reset-error-back-btn"
        >
          <Text style={styles.buttonText}>Back to Sign In</Text>
        </TouchableOpacity>
      </LandingLayout>
    );
  }

  return (
    <LandingLayout>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 0 : 20}
      >
        <View style={styles.header}>
          <Ionicons name="lock-open" size={56} color="#5C6BC0" />
          <Text style={styles.title}>Set a New Password</Text>
          {email ? (
            <Text style={styles.subtitle}>
              For <Text style={styles.emailEmphasis}>{email}</Text>
            </Text>
          ) : (
            <Text style={styles.subtitle}>Enter a new password for your account.</Text>
          )}
        </View>

        <View style={styles.form}>
          <View style={styles.inputContainer}>
            <Ionicons name="lock-closed-outline" size={20} color="#9CA3AF" style={styles.inputIcon} />
            <PasswordInput
              inputStyle={styles.input}
              placeholder="New Password"
              value={password}
              onChangeText={setPassword}
              autoCapitalize="none"
              autoCorrect={false}
              placeholderTextColor="#9CA3AF"
              returnKeyType="next"
              onSubmitEditing={() => confirmRef.current?.focus()}
              blurOnSubmit={false}
              testID="reset-new-password-input"
              testIDPrefix="reset-new-password"
              containerStyle={{ flex: 1 }}
            />
          </View>

          <View style={styles.inputContainer}>
            <Ionicons name="lock-closed-outline" size={20} color="#9CA3AF" style={styles.inputIcon} />
            <PasswordInput
              ref={confirmRef}
              inputStyle={styles.input}
              placeholder="Confirm New Password"
              value={confirmPassword}
              onChangeText={setConfirmPassword}
              autoCapitalize="none"
              autoCorrect={false}
              placeholderTextColor="#9CA3AF"
              returnKeyType="done"
              onSubmitEditing={handleSubmit}
              testID="reset-confirm-password-input"
              testIDPrefix="reset-confirm-password"
              containerStyle={{ flex: 1 }}
            />
          </View>

          <TouchableOpacity
            style={[styles.button, submitting && styles.buttonDisabled]}
            onPress={handleSubmit}
            disabled={submitting}
            testID="reset-submit-btn"
            data-testid="reset-submit-btn"
          >
            <Text style={styles.buttonText}>
              {submitting ? 'Updating Password…' : 'Update Password'}
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.linkButton}
            onPress={() => router.replace('/auth/login')}
            testID="reset-cancel-btn"
          >
            <Text style={styles.linkText}>Back to Sign In</Text>
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </LandingLayout>
  );
}

const styles = StyleSheet.create({
  header: { alignItems: 'center', marginBottom: 24 },
  title: { fontSize: 26, fontWeight: 'bold', color: '#1A1A3A', marginTop: 12, textAlign: 'center' },
  subtitle: { fontSize: 13, color: '#5A5A7A', marginTop: 6, textAlign: 'center', paddingHorizontal: 12 },
  emailEmphasis: { color: '#5C6BC0', fontWeight: '600' },
  form: { width: '100%' },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    paddingHorizontal: 14,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#DDDDF5',
  },
  inputIcon: { marginRight: 10 },
  input: { flex: 1, height: 46, fontSize: 15, color: '#1A1A3A' },
  button: { backgroundColor: '#E65100', borderRadius: 12, paddingVertical: 14, alignItems: 'center', marginTop: 6 },
  buttonDisabled: { opacity: 0.6 },
  buttonText: { color: '#FFFFFF', fontSize: 15, fontWeight: '600' },
  linkButton: { marginTop: 18, alignItems: 'center' },
  linkText: { color: '#5C6BC0', fontSize: 13, fontWeight: '500' },
  centered: { alignItems: 'center', paddingVertical: 40 },
});
