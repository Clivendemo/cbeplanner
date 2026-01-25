import { initializeApp } from 'firebase/app';
import { getAuth, initializeAuth, getReactNativePersistence } from 'firebase/auth';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Platform } from 'react-native';

const firebaseConfig = {
  apiKey: "AIzaSyBalkTy90NBRs7Qky_VPTlikVP6UD69-p8",
  authDomain: "cbeplanner.firebaseapp.com",
  projectId: "cbeplanner",
  storageBucket: "cbeplanner.firebasestorage.app",
  messagingSenderId: "894369640507",
  appId: "1:894369640507:web:74bab72c3d76b135176c1e",
  measurementId: "G-74L90635K6"
};

const app = initializeApp(firebaseConfig);

// Initialize Auth with persistence for React Native
let auth;
if (Platform.OS === 'web') {
  auth = getAuth(app);
} else {
  auth = initializeAuth(app, {
    persistence: getReactNativePersistence(AsyncStorage)
  });
}

export { auth };
