/**
 * Top-level React error boundary — catches any render-phase crash that would
 * otherwise white-screen the app and replaces it with a friendly fallback.
 *
 * Intentionally simple: no external telemetry deps, no auto-reload. We only
 * surface the error to the user and log it to the console so platform/tools
 * (Vercel, browser devtools) can pick it up.
 *
 * Keeps the user inside the app — a full-viewport fallback with a "Try again"
 * button that resets the boundary and re-mounts children.
 */
import React from 'react';
import { Platform, View, Text, Pressable, StyleSheet } from 'react-native';

interface Props {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends React.Component<Props, State> {
  state: State = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    // eslint-disable-next-line no-console
    console.error('[ErrorBoundary]', error, info?.componentStack);
    if (Platform.OS === 'web' && typeof window !== 'undefined') {
      try {
        // Expose the last crash for debugging without leaking details to users.
        (window as any).__lastCbePlError = { message: error.message, stack: error.stack };
      } catch {
        /* noop */
      }
    }
  }

  reset = () => this.setState({ hasError: false, error: null });

  render() {
    if (!this.state.hasError) return this.props.children;
    if (this.props.fallback) return this.props.fallback;

    const message = this.state.error?.message || 'Something went wrong.';

    return (
      <View style={styles.root} data-testid="error-boundary">
        <View style={styles.card}>
          <Text style={styles.emoji}>⚠️</Text>
          <Text style={styles.title}>Something went wrong</Text>
          <Text style={styles.body}>{message}</Text>
          <Text style={styles.hint}>
            This has been logged. You can try again, or refresh the page.
          </Text>
          <Pressable
            onPress={this.reset}
            style={({ pressed }) => [styles.btn, pressed && { opacity: 0.85 }]}
            data-testid="error-boundary-retry"
          >
            <Text style={styles.btnText}>Try again</Text>
          </Pressable>
        </View>
      </View>
    );
  }
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
    minHeight: '100vh' as any,
    backgroundColor: '#F8F7FF',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
  },
  card: {
    maxWidth: 420,
    width: '100%',
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 28,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  emoji: { fontSize: 48, marginBottom: 12 },
  title: { fontSize: 18, fontWeight: '700', color: '#111827', marginBottom: 8 },
  body: { fontSize: 14, color: '#6B7280', textAlign: 'center', marginBottom: 12 },
  hint: { fontSize: 12, color: '#9CA3AF', textAlign: 'center', marginBottom: 18 },
  btn: {
    backgroundColor: '#6D28D9',
    borderRadius: 10,
    paddingHorizontal: 20,
    paddingVertical: 10,
  },
  btnText: { color: '#FFFFFF', fontSize: 14, fontWeight: '600' },
});

export default ErrorBoundary;
