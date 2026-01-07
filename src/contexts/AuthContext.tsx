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

  // Simple computed property
  const isAuthenticated = user !== null;

  // Clear all tokens from both storages
  const clearTokens = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    sessionStorage.removeItem('access_token');
    sessionStorage.removeItem('refresh_token');
  };

  // Load user on mount
  useEffect(() => {
    const loadUser = async () => {
      try {
        console.log('🔄 AuthProvider: Loading user on mount...');
        console.log('🔧 Fixed: API client now checks both localStorage and sessionStorage for tokens');
        
        // Check for tokens
        const accessToken = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
        const refreshToken = localStorage.getItem('refresh_token') || sessionStorage.getItem('refresh_token');
        
        if (!accessToken) {
          console.log('ℹ️ AuthProvider: No access token found');
          setIsLoading(false);
          return;
        }

        console.log('🔑 AuthProvider: Found access token, loading user...');
        
        try {
          const userData = await apiClient.getCurrentUser();
          setUser(userData);
          console.log('✅ AuthProvider: User loaded successfully:', userData.email);
        } catch (error: any) {
          console.log('🔄 AuthProvider: Access token expired, trying refresh...');
          
          if (refreshToken) {
            try {
              const response = await apiClient.refreshToken(refreshToken);
              
              // Store new token in same storage as refresh token
              const storage = localStorage.getItem('refresh_token') ? localStorage : sessionStorage;
              storage.setItem('access_token', response.access_token);
              
              // Try loading user again
              const userData = await apiClient.getCurrentUser();
              setUser(userData);
              console.log('✅ AuthProvider: Token refreshed and user loaded:', userData.email);
            } catch (refreshError) {
              console.log('❌ AuthProvider: Token refresh failed, clearing tokens');
              clearTokens();
              setUser(null);
            }
          } else {
            console.log('❌ AuthProvider: No refresh token, clearing tokens');
            clearTokens();
            setUser(null);
          }
        }
      } catch (error) {
        console.error('❌ AuthProvider: Error during initialization:', error);
        clearTokens();
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };

    loadUser();
  }, []);

  const login = async (email: string, password: string, rememberMe: boolean = true) => {
    try {
      console.log('🔐 AuthProvider: Starting login for:', email);
      
      // Clear any existing state
      setUser(null);
      clearTokens();
      
      // Perform login
      const response: AuthResponse = await apiClient.login(email, password);
      
      if (!response.access_token || !response.user) {
        throw new Error('Invalid login response - missing token or user data');
      }
      
      // Store tokens
      const storage = rememberMe ? localStorage : sessionStorage;
      storage.setItem('access_token', response.access_token);
      storage.setItem('refresh_token', response.refresh_token);
      
      // Clear other storage
      const otherStorage = rememberMe ? sessionStorage : localStorage;
      otherStorage.removeItem('access_token');
      otherStorage.removeItem('refresh_token');
      
      // Set user state IMMEDIATELY and SYNCHRONOUSLY
      setUser(response.user);
      
      console.log('✅ AuthProvider: Login successful');
      console.log('✅ User:', response.user.email);
      console.log('✅ Tier:', response.user.tier);
      console.log('✅ isAuthenticated will be:', true);
      
      // Force a small delay to ensure React has processed the state update
      await new Promise(resolve => setTimeout(resolve, 50));
      
    } catch (error) {
      console.error('❌ AuthProvider: Login failed:', error);
      clearTokens();
      setUser(null);
      throw error;
    }
  };

  const register = async (email: string, password: string, fullName?: string) => {
    try {
      console.log('📝 AuthProvider: Starting registration for:', email);
      const response: AuthResponse = await apiClient.register(email, password, fullName);
      
      // Store tokens (always remember registration)
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('refresh_token', response.refresh_token);
      
      setUser(response.user);
      console.log('✅ AuthProvider: Registration successful:', response.user.email);
    } catch (error) {
      console.error('❌ AuthProvider: Registration failed:', error);
      throw error;
    }
  };

  const logout = () => {
    console.log('🚪 AuthProvider: Logging out');
    clearTokens();
    setUser(null);
    apiClient.logout();
  };

  const refreshUser = async () => {
    try {
      const userData = await apiClient.getCurrentUser();
      setUser(userData);
      console.log('🔄 AuthProvider: User refreshed:', userData.email);
    } catch (error) {
      console.error('❌ AuthProvider: Failed to refresh user:', error);
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