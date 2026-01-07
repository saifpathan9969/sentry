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
    localStorage.removeItem('user_email');
    sessionStorage.removeItem('access_token');
    sessionStorage.removeItem('refresh_token');
  };

  // Load user on mount
  useEffect(() => {
    const loadUser = async () => {
      try {
        console.log('🔄 AuthProvider: Loading user on mount...');
        
        // Check for tokens - prioritize localStorage for persistence
        const accessToken = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
        const refreshToken = localStorage.getItem('refresh_token') || sessionStorage.getItem('refresh_token');
        const savedEmail = localStorage.getItem('user_email');
        
        if (!accessToken) {
          console.log('ℹ️ AuthProvider: No access token found, user needs to login');
          setIsLoading(false);
          return;
        }

        console.log('🔑 AuthProvider: Found access token, loading user...');
        if (savedEmail) {
          console.log('📧 AuthProvider: Saved email:', savedEmail);
        }
        
        try {
          const userData = await apiClient.getCurrentUser();
          setUser(userData);
          console.log('✅ AuthProvider: User loaded successfully:', userData.email);
          console.log('✅ User will stay logged in across browser sessions');
        } catch (error: any) {
          console.log('🔄 AuthProvider: Access token expired or invalid, trying refresh...');
          
          if (refreshToken) {
            try {
              console.log('🔄 AuthProvider: Attempting token refresh...');
              const response = await apiClient.refreshToken(refreshToken);
              
              // Always store in localStorage for persistence
              localStorage.setItem('access_token', response.access_token);
              
              // Try loading user again
              const userData = await apiClient.getCurrentUser();
              setUser(userData);
              console.log('✅ AuthProvider: Token refreshed and user loaded:', userData.email);
              console.log('✅ User will stay logged in');
            } catch (refreshError) {
              console.log('❌ AuthProvider: Token refresh failed, user needs to login again');
              console.error('Refresh error:', refreshError);
              clearTokens();
              setUser(null);
            }
          } else {
            console.log('❌ AuthProvider: No refresh token, user needs to login');
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
      console.log('🔐 Remember me:', rememberMe);
      
      // Clear any existing state
      setUser(null);
      clearTokens();
      
      // Perform login
      const response: AuthResponse = await apiClient.login(email, password);
      
      if (!response.access_token || !response.user) {
        throw new Error('Invalid login response - missing token or user data');
      }
      
      // ALWAYS use localStorage for persistence (ignore rememberMe for now)
      // This ensures users stay logged in across browser sessions
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('refresh_token', response.refresh_token);
      localStorage.setItem('user_email', response.user.email);
      
      // Clear sessionStorage to avoid conflicts
      sessionStorage.removeItem('access_token');
      sessionStorage.removeItem('refresh_token');
      
      // Set user state IMMEDIATELY and SYNCHRONOUSLY
      setUser(response.user);
      
      console.log('✅ AuthProvider: Login successful');
      console.log('✅ User:', response.user.email);
      console.log('✅ Tier:', response.user.tier);
      console.log('✅ Tokens stored in localStorage for persistence');
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
      
      // ALWAYS use localStorage for persistence
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('refresh_token', response.refresh_token);
      localStorage.setItem('user_email', response.user.email);
      
      // Clear sessionStorage to avoid conflicts
      sessionStorage.removeItem('access_token');
      sessionStorage.removeItem('refresh_token');
      
      setUser(response.user);
      console.log('✅ AuthProvider: Registration successful:', response.user.email);
      console.log('✅ Tokens stored in localStorage for persistence');
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