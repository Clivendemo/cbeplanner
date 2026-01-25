import React, { createContext, useState, useContext, useEffect } from 'react';
import { auth } from '../firebaseConfig';
import {
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut as firebaseSignOut,
  onAuthStateChanged,
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
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string, firstName: string, lastName: string, schoolName: string) => Promise<void>;
  signOut: () => Promise<void>;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [firebaseUser, setFirebaseUser] = useState<FirebaseUser | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      console.log('Auth state changed:', firebaseUser?.email);
      setFirebaseUser(firebaseUser);
      
      if (firebaseUser) {
        try {
          const idToken = await firebaseUser.getIdToken(true); // Force refresh
          await AsyncStorage.setItem('userToken', idToken);
          
          // Verify token with backend
          const response = await axios.post(`${BACKEND_URL}/api/auth/verify`, {
            idToken
          });
          
          if (response.data.success) {
            console.log('User verified:', response.data.user.email);
            setUser(response.data.user);
          }
        } catch (error: any) {
          console.error('Error verifying token:', error.response?.data || error.message);
          // Clear invalid token
          await AsyncStorage.removeItem('userToken');
          await firebaseSignOut(auth);
          setUser(null);
        }
      } else {
        await AsyncStorage.removeItem('userToken');
        setUser(null);
      }
      
      setLoading(false);
    });

    return unsubscribe;
  }, []);

  const signIn = async (email: string, password: string) => {
    try {
      await signInWithEmailAndPassword(auth, email, password);
    } catch (error: any) {
      throw new Error(error.message);
    }
  };

  const signUp = async (email: string, password: string, firstName: string, lastName: string, schoolName: string) => {
    try {
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      
      // Send profile data to backend
      const idToken = await userCredential.user.getIdToken();
      await axios.post(`${BACKEND_URL}/api/auth/verify`, {
        idToken,
        firstName,
        lastName,
        schoolName
      });
    } catch (error: any) {
      throw new Error(error.message);
    }
  };

  const signOut = async () => {
    try {
      await firebaseSignOut(auth);
      await AsyncStorage.removeItem('userToken');
      setUser(null);
      setFirebaseUser(null);
    } catch (error: any) {
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

  return (
    <AuthContext.Provider value={{ user, firebaseUser, loading, signIn, signUp, signOut, refreshProfile }}>
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