import React, { createContext, useContext, useState, useEffect } from 'react';
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  updateProfile,
  GoogleAuthProvider,
  signInWithPopup
} from 'firebase/auth';
import { doc, setDoc, getDoc } from 'firebase/firestore';
import { auth, db } from '../config/firebase';

const AuthContext = createContext();

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [userProfile, setUserProfile] = useState(null);

  // Register user
  async function signup(email, password, username) {
    try {
      const result = await createUserWithEmailAndPassword(auth, email, password);
      
      // Update display name
      await updateProfile(result.user, {
        displayName: username
      });

      // Save user profile to Firestore
      await setDoc(doc(db, 'users', result.user.uid), {
        uid: result.user.uid,
        email: email,
        username: username,
        role: 'user',
        createdAt: new Date().toISOString(),
        lastLogin: new Date().toISOString()
      });

      return result;
    } catch (error) {
      throw error;
    }
  }

  // Login user
  async function login(email, password) {
    try {
      const result = await signInWithEmailAndPassword(auth, email, password);
      
      // Update last login
      await setDoc(doc(db, 'users', result.user.uid), {
        lastLogin: new Date().toISOString()
      }, { merge: true });

      return result;
    } catch (error) {
      throw error;
    }
  }

  // Google Sign In
  async function signInWithGoogle() {
    try {
      const provider = new GoogleAuthProvider();
      const result = await signInWithPopup(auth, provider);
      
      // Check if user exists in Firestore
      const userDoc = await getDoc(doc(db, 'users', result.user.uid));
      
      if (!userDoc.exists()) {
        // Create new user profile
        await setDoc(doc(db, 'users', result.user.uid), {
          uid: result.user.uid,
          email: result.user.email,
          username: result.user.displayName,
          role: 'user',
          createdAt: new Date().toISOString(),
          lastLogin: new Date().toISOString()
        });
      } else {
        // Update last login
        await setDoc(doc(db, 'users', result.user.uid), {
          lastLogin: new Date().toISOString()
        }, { merge: true });
      }

      return result;
    } catch (error) {
      throw error;
    }
  }

  // Logout user
  function logout() {
    return signOut(auth);
  }

  // Get user profile from Firestore
  async function getUserProfile(uid) {
    try {
      const docRef = doc(db, 'users', uid);
      const docSnap = await getDoc(docRef);
      
      if (docSnap.exists()) {
        return docSnap.data();
      } else {
        return null;
      }
    } catch (error) {
      console.error('Error getting user profile:', error);
      return null;
    }
  }

  // Update user profile
  async function updateUserProfile(updates) {
    try {
      if (currentUser) {
        await setDoc(doc(db, 'users', currentUser.uid), updates, { merge: true });
        const updatedProfile = await getUserProfile(currentUser.uid);
        setUserProfile(updatedProfile);
        return updatedProfile;
      }
    } catch (error) {
      throw error;
    }
  }

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      setCurrentUser(user);
      
      if (user) {
        // Get user profile from Firestore
        const profile = await getUserProfile(user.uid);
        setUserProfile(profile);
      } else {
        setUserProfile(null);
      }
      
      setLoading(false);
    });

    return unsubscribe;
  }, []);

  const value = {
    currentUser,
    userProfile,
    signup,
    login,
    logout,
    signInWithGoogle,
    getUserProfile,
    updateUserProfile
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
}