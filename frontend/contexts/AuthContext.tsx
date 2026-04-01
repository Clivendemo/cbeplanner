import React, { createContext, useState, useContext, useEffect, useCallback, useRef } from 'react';
import { AppState, AppStateStatus, Platform } from 'react-native';
import { auth } from '../firebaseConfig';
import {
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut as firebaseSignOut,
  onAuthStateChanged,
  sendPasswordResetEmail,
  User as FirebaseUser
} from 'firebase/auth';
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Backend URL with fallback for web
const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL || 'https://cbeplanner.onrender.com';

// The ONLY admin email - must match backend
const ADMIN_EMAIL = 'mail2clive@gmail.com';

// Inactivity timeout: 20 minutes (in milliseconds)
const INACTIVITY_TIMEOUT_MS = 20 * 60 * 1000;

interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  schoolName: string;
  role: string;
  walletBalance: number;
  freeLessonsRemaining: number;
  freeLessonUsed: boolean;
  freeNotesUsed: boolean;
}

interface AuthContextType {
  user: User | null;
  firebaseUser: FirebaseUser | null;
  loading: boolean;
  isAdmin: boolean;
  isNewUser: boolean;
  authChecked: boolean;
  signIn: (email: string, password: string, rememberMe?: boolean) => Promise<User | null>;
  signUp: (email: string, password: string, firstName: string, lastName: string, schoolName: string) => Promise<User | null>;
  signOut: () => Promise<void>;
  refreshProfile: () => Promise<void>;
  resetPassword: (email: string) => Promise<void>;
  clearNewUserFlag: () => void;
  recordActivity: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [firebaseUser, setFirebaseUser] = useState<FirebaseUser | null>(null);
  const [loading, setLoading] = useState(true);
  const [authChecked, setAuthChecked] = useState(false);
  const [isNewUser, setIsNewUser] = useState(false);
  const lastActivityRef = useRef<number>(Date.now());
  const rememberMeRef = useRef<boolean>(false);
  const authCheckedRef = useRef<boolean>(false);

  // Keep ref in sync with state
  useEffect(() => {
    authCheckedRef.current = authChecked;
  }, [authChecked]);

  // Check if user is admin by email (client-side check, backend also enforces)
  const isAdmin = user?.email?.toLowerCase().trim() === ADMIN_EMAIL;

  // Clear new user flag (call after showing welcome message)
  const clearNewUserFlag = useCallback(() => {
    setIsNewUser(false);
  }, []);

  // Record user activity (resets the inactivity timer)
  const recordActivity = useCallback(() => {
    lastActivityRef.current = Date.now();
  }, []);

  // Load rememberMe preference on mount
  useEffect(() => {
    AsyncStorage.getItem('rememberMe').then((val) => {
      rememberMeRef.current = val === 'true';
    });
  }, []);

  // Inactivity timeout: check on app foreground
  useEffect(() => {
    const handleAppStateChange = async (nextState: AppStateStatus) => {
      if (nextState === 'active' && firebaseUser && user) {
        // Reload rememberMe in case it changed
        const rememberMe = await AsyncStorage.getItem('rememberMe');
        if (rememberMe === 'true') {
          // User chose "Remember Me" — no timeout
          return;
        }

        const elapsed = Date.now() - lastActivityRef.current;
        if (elapsed >= INACTIVITY_TIMEOUT_MS) {
          
          await handleSignOut();
        }
      }
    };

    const subscription = AppState.addEventListener('change', handleAppStateChange);
    return () => subscription.remove();
  }, [firebaseUser, user]);

  // Also run a periodic check every 60s while app is active
  useEffect(() => {
    const interval = setInterval(async () => {
      if (!firebaseUser || !user) return;

      const rememberMe = await AsyncStorage.getItem('rememberMe');
      if (rememberMe === 'true') return;

      const elapsed = Date.now() - lastActivityRef.current;
      if (elapsed >= INACTIVITY_TIMEOUT_MS) {
        
        await handleSignOut();
      }
    }, 60000);

    return () => clearInterval(interval);
  }, [firebaseUser, user]);

  const verifyAndSetUser = useCallback(async (fbUser: FirebaseUser, isSignUp: boolean = false) => {
    try {
      const idToken = await fbUser.getIdToken(true);
      await AsyncStorage.setItem('userToken', idToken);
      
      const response = await axios.post(`${BACKEND_URL}/api/auth/verify`, {
        idToken
      }, {
        timeout: 15000 // 15 second timeout
      });
      
      if (response.data.success) {
        setUser(response.data.user);
        // Set isNewUser flag based on backend response or if this is a signup
        if (response.data.isNewUser || isSignUp) {
          setIsNewUser(true);
        }
        lastActivityRef.current = Date.now();
        return response.data.user;
      }
      return null;
    } catch (error: any) {
      // Clear token on error
      await AsyncStorage.removeItem('userToken');
      setUser(null);
      
      // Re-throw the error so it can be caught by the caller
      throw new Error(error.response?.data?.detail || error.message || 'Verification failed');
    }
  }, []);

  useEffect(() => {
    let isMounted = true;
    
    // Fallback timeout to prevent infinite loading (especially on web)
    const timeout = setTimeout(() => {
      if (isMounted && !authCheckedRef.current) {
        setLoading(false);
        setAuthChecked(true);
      }
    }, 3000);

    const unsubscribe = onAuthStateChanged(auth, async (fbUser) => {
      if (!isMounted) return;
      
      // Auth state changed
      setFirebaseUser(fbUser);
      
      if (fbUser) {
        // Check if rememberMe is set — if not, check if session expired
        try {
          const rememberMe = await AsyncStorage.getItem('rememberMe');
          if (rememberMe !== 'true') {
            const lastActive = await AsyncStorage.getItem('lastActivityTime');
            if (lastActive) {
              const elapsed = Date.now() - parseInt(lastActive, 10);
              if (elapsed >= INACTIVITY_TIMEOUT_MS) {
                await firebaseSignOut(auth);
                await AsyncStorage.removeItem('userToken');
                await AsyncStorage.removeItem('lastActivityTime');
                if (isMounted) {
                  setUser(null);
                  setFirebaseUser(null);
                  setLoading(false);
                  setAuthChecked(true);
                }
                return;
              }
            }
          }
          await verifyAndSetUser(fbUser);
        } catch (error) {
          // Auth check failed silently
        }
      } else {
        try {
          await AsyncStorage.removeItem('userToken');
        } catch (e) {}
        setUser(null);
      }
      
      if (isMounted) {
        setLoading(false);
        setAuthChecked(true);
      }
    });

    return () => {
      isMounted = false;
      unsubscribe();
      clearTimeout(timeout);
    };
  }, [verifyAndSetUser]);

  // Save lastActivityTime periodically so we can check on next app open
  useEffect(() => {
    const interval = setInterval(() => {
      if (user) {
        AsyncStorage.setItem('lastActivityTime', String(lastActivityRef.current));
      }
    }, 30000);
    return () => clearInterval(interval);
  }, [user]);

  const signIn = async (email: string, password: string, rememberMe: boolean = false): Promise<User | null> => {
    setLoading(true);
    try {
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      
      // Store rememberMe preference
      await AsyncStorage.setItem('rememberMe', rememberMe ? 'true' : 'false');
      rememberMeRef.current = rememberMe;
      lastActivityRef.current = Date.now();
      await AsyncStorage.setItem('lastActivityTime', String(Date.now()));
      
      const verifiedUser = await verifyAndSetUser(userCredential.user);
      setLoading(false);
      
      if (!verifiedUser) {
        throw new Error('Failed to verify user with server');
      }
      
      return verifiedUser;
    } catch (error: any) {
      setLoading(false);
      
      let message = error.message || 'Login failed. Please try again.';
      if (error.code === 'auth/user-not-found' || error.code === 'auth/wrong-password' || error.code === 'auth/invalid-credential') {
        message = 'Invalid email or password';
      } else if (error.code === 'auth/too-many-requests') {
        message = 'Too many failed attempts. Please try again later.';
      } else if (error.code === 'auth/network-request-failed') {
        message = 'Network error. Please check your connection.';
      }
      throw new Error(message);
    }
  };

  const signUp = async (email: string, password: string, firstName: string, lastName: string, schoolName: string): Promise<User | null> => {
    setLoading(true);
    try {
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      
      // New users get rememberMe by default
      await AsyncStorage.setItem('rememberMe', 'true');
      rememberMeRef.current = true;
      lastActivityRef.current = Date.now();
      
      const idToken = await userCredential.user.getIdToken();
      const response = await axios.post(`${BACKEND_URL}/api/auth/verify`, {
        idToken,
        firstName,
        lastName,
        schoolName
      });
      
      if (response.data.success) {
        setUser(response.data.user);
        setIsNewUser(true); // Always set for signups
        setLoading(false);
        return response.data.user;
      }
      setLoading(false);
      return null;
    } catch (error: any) {
      setLoading(false);
      
      let message = 'Sign up failed. Please try again.';
      if (error.code === 'auth/email-already-in-use') {
        message = 'An account with this email already exists';
      } else if (error.code === 'auth/weak-password') {
        message = 'Password should be at least 6 characters';
      } else if (error.code === 'auth/invalid-email') {
        message = 'Please enter a valid email address';
      }
      throw new Error(message);
    }
  };

  const handleSignOut = async () => {
    try {
      await firebaseSignOut(auth);
      await AsyncStorage.removeItem('userToken');
      await AsyncStorage.removeItem('lastActivityTime');
      // Keep rememberMe preference — only clear it if user explicitly unchecks
      setUser(null);
      setFirebaseUser(null);
    } catch (error: any) {
      setUser(null);
      setFirebaseUser(null);
      await AsyncStorage.removeItem('userToken');
      await AsyncStorage.removeItem('lastActivityTime');
    }
  };

  const signOutExposed = async () => {
    // When user explicitly signs out, clear rememberMe
    await AsyncStorage.setItem('rememberMe', 'false');
    rememberMeRef.current = false;
    await handleSignOut();
  };

  const refreshProfile = async () => {
    if (firebaseUser) {
      try {
        const idToken = await firebaseUser.getIdToken(true);
        const response = await axios.get(`${BACKEND_URL}/api/profile`, {
          headers: { Authorization: `Bearer ${idToken}` }
        });
        
        if (response.data.success) {
          setUser(response.data.user);
        }
      } catch (error) {
        
      }
    }
  };

  const resetPassword = async (email: string) => {
    try {
      await sendPasswordResetEmail(auth, email);
    } catch (error: any) {
      throw new Error(error.message);
    }
  };

  return (
    <AuthContext.Provider value={{ 
      user, 
      firebaseUser, 
      loading, 
      isAdmin,
      isNewUser,
      authChecked,
      signIn, 
      signUp, 
      signOut: signOutExposed, 
      refreshProfile, 
      resetPassword,
      clearNewUserFlag,
      recordActivity
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
