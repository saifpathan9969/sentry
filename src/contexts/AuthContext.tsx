import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { apiClient } from '@/api/client';
import { User, AuthResponse } from '@/types';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string, rememberMe?: boolean) => Promise<void>;
  register: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = !!user;

  // Load user on mount with better token management
  useEffect(() => {
    const loadUser = async () => {
      try {
        // Check both localStorage and sessionStorage for tokens
        const accessToken = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
        const refreshToken = localStorage.getItem('refresh_token') || sessionStorage.getItem('refresh_token');
        
        if (accessToken) {
          console.log('🔑 Found stored token, attempting to load user...');
          try {
            const userData = await apiClient.getCurrentUser();
            setUser(userData);
            console.log('✅ User loaded successfully:', userData.email);
          } catch (error: any) {
            console.log('🔄 Access token expired, trying refresh...');
            
            // Try to refresh token
            if (refreshToken) {
              try {
                const response = await apiClient.refreshToken(refreshToken);
                
                // Store new tokens in the same storage as before
                const storage = localStorage.getItem('access_token') ? localStorage : sessionStorage;
                storage.setItem('access_token', response.access_token);
                
                // Try loading user again
                const userData = await apiClient.getCurrentUser();
                setUser(userData);
                console.log('✅ Token refreshed and user loaded:', userData.email);
              } catch (refreshError) {
                console.log('❌ Token refresh failed, clearing storage');
                clearTokens();
              }
            } else {
              console.log('❌ No refresh token available, clearing storage');
              clearTokens();
            }
          }
        } else {
          console.log('ℹ️ No stored tokens found');
        }
      } catch (error) {
        console.error('❌ Error loading user:', error);
        clearTokens();
      } finally {
        setIsLoading(false);
      }
    };

    loadUser();
  }, []);

  const clearTokens = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    sessionStorage.removeItem('access_token');
    sessionStorage.removeItem('refresh_token');
  };

  const login = async (email: string, password: string, rememberMe: boolean = true) => {
    try {
      console.log('🔐 Attempting login for:', email);
      const response: AuthResponse = await apiClient.login(email, password);
      
      // Choose storage based on rememberMe preference
      const storage = rememberMe ? localStorage : sessionStorage;
      
      storage.setItem('access_token', response.access_token);
      storage.setItem('refresh_token', response.refresh_token);
      
      // Clear the other storage to avoid conflicts
      const otherStorage = rememberMe ? sessionStorage : localStorage;
      otherStorage.removeItem('access_token');
      otherStorage.removeItem('refresh_token');
      
      // CRITICAL: Always set user state immediately after successful login
      if (response.user) {
        setUser(response.user);
        console.log('✅ Login successful - user state set:', response.user.email);
        console.log('✅ User tier:', response.user.tier);
        console.log('✅ User active:', response.user.is_active);
      } else {
        // If user not in response, fetch it immediately
        console.log('🔄 User not in login response, fetching...');
        const userData = await apiClient.getCurrentUser();
        setUser(userData);
        console.log('✅ User data fetched after login:', userData.email);
      }
      
      // Double-check authentication state
      console.log('🔍 Final auth state check - isAuthenticated will be:', !!response.user);
      
    } catch (error) {
      console.error('❌ Login failed:', error);
      clearTokens();
      setUser(null); // Ensure user state is cleared on failure
      throw error;
    }
  };

  const register = async (email: string, password: string, fullName?: string) => {
    try {
      console.log('📝 Attempting registration for:', email);
      const response: AuthResponse = await apiClient.register(email, password, fullName);
      
      // Always remember registration (use localStorage)
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('refresh_token', response.refresh_token);
      
      setUser(response.user);
      console.log('✅ Registration successful:', response.user.email);
    } catch (error) {
      console.error('❌ Registration failed:', error);
      throw error;
    }
  };

  const logout = () => {
    console.log('🚪 Logging out user');
    apiClient.logout();
    setUser(null);
    clearTokens();
  };

  const refreshUser = async () => {
    try {
      const userData = await apiClient.getCurrentUser();
      setUser(userData);
      console.log('🔄 User data refreshed:', userData.email);
    } catch (error) {
      console.error('❌ Failed to refresh user:', error);
      logout();
    }
  };

  const value = {
    user,
    isAuthenticated,
    isLoading,
    login,
    register,
    logout,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
