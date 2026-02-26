import React, { createContext, useState, useContext, useEffect, useCallback } from 'react';
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

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  schoolName: string;
  role: string;
  walletBalance: number;
  freeLessonUsed: boolean;
  freeNotesUsed: boolean;
}

interface AuthContextType {
  user: User | null;
  firebaseUser: FirebaseUser | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<User | null>;
  signUp: (email: string, password: string, firstName: string, lastName: string, schoolName: string) => Promise<User | null>;
  signOut: () => Promise<void>;
  refreshProfile: () => Promise<void>;
  resetPassword: (email: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [firebaseUser, setFirebaseUser] = useState<FirebaseUser | null>(null);
  const [loading, setLoading] = useState(true);

  const verifyAndSetUser = useCallback(async (fbUser: FirebaseUser) => {
    try {
      console.log('Verifying user with backend:', fbUser.email);
      const idToken = await fbUser.getIdToken(true);
      await AsyncStorage.setItem('userToken', idToken);
      
      const response = await axios.post(`${BACKEND_URL}/api/auth/verify`, {
        idToken
      });
      
      if (response.data.success) {
        console.log('User verified successfully:', response.data.user.email);
        setUser(response.data.user);
        return response.data.user;
      }
      return null;
    } catch (error: any) {
      console.error('Error verifying token:', error.response?.data || error.message);
      await AsyncStorage.removeItem('userToken');
      setUser(null);
      return null;
    }
  }, []);

  useEffect(() => {
    console.log('Setting up auth listener...');
    const unsubscribe = onAuthStateChanged(auth, async (fbUser) => {
      console.log('Auth state changed:', fbUser?.email || 'No user');
      setFirebaseUser(fbUser);
      
      if (fbUser) {
        await verifyAndSetUser(fbUser);
      } else {
        await AsyncStorage.removeItem('userToken');
        setUser(null);
      }
      
      setLoading(false);
    });

    return () => unsubscribe();
  }, [verifyAndSetUser]);

  const signIn = async (email: string, password: string): Promise<User | null> => {
    console.log('Attempting sign in for:', email);
    setLoading(true);
    try {
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      console.log('Firebase sign in successful');
      
      // Manually verify and set user since onAuthStateChanged might be delayed
      const verifiedUser = await verifyAndSetUser(userCredential.user);
      setLoading(false);
      return verifiedUser;
    } catch (error: any) {
      console.error('Sign in error:', error.code, error.message);
      setLoading(false);
      
      // Provide user-friendly error messages
      let message = 'Login failed. Please try again.';
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
    console.log('Attempting sign up for:', email);
    setLoading(true);
    try {
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      console.log('Firebase sign up successful');
      
      // Send profile data to backend
      const idToken = await userCredential.user.getIdToken();
      const response = await axios.post(`${BACKEND_URL}/api/auth/verify`, {
        idToken,
        firstName,
        lastName,
        schoolName
      });
      
      if (response.data.success) {
        console.log('User profile created:', response.data.user.email);
        setUser(response.data.user);
        setLoading(false);
        return response.data.user;
      }
      setLoading(false);
      return null;
    } catch (error: any) {
      console.error('Sign up error:', error.code, error.message);
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

  const signOut = async () => {
    console.log('Signing out...');
    try {
      await firebaseSignOut(auth);
      await AsyncStorage.removeItem('userToken');
      setUser(null);
      setFirebaseUser(null);
    } catch (error: any) {
      console.error('Sign out error:', error);
      throw new Error(error.message);
    }
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
        console.error('Error refreshing profile:', error);
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
    <AuthContext.Provider value={{ user, firebaseUser, loading, signIn, signUp, signOut, refreshProfile, resetPassword }}>
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
