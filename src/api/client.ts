import axios, { AxiosError, AxiosInstance } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 
  (import.meta.env.PROD 
    ? 'https://sentry-backend-1.onrender.com/api/v1' 
    : 'http://localhost:8000/api/v1');

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor to handle token refresh
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as any;

        // If 401 and not already retried, try to refresh token
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            // Check both storages for refresh token
            const refreshToken = localStorage.getItem('refresh_token') || sessionStorage.getItem('refresh_token');
            
            if (refreshToken) {
              console.log('🔄 Attempting token refresh...');
              const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
                refresh_token: refreshToken,
              });

              const { access_token } = response.data;
              
              // Store new token in the same storage as the refresh token
              const storage = localStorage.getItem('refresh_token') ? localStorage : sessionStorage;
              storage.setItem('access_token', access_token);

              originalRequest.headers.Authorization = `Bearer ${access_token}`;
              console.log('✅ Token refreshed successfully');
              return this.client(originalRequest);
            }
          } catch (refreshError) {
            console.log('❌ Token refresh failed, redirecting to login');
            // Refresh failed, logout user
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            sessionStorage.removeItem('access_token');
            sessionStorage.removeItem('refresh_token');
            
            // Only redirect if we're not already on login page
            if (!window.location.pathname.includes('/login')) {
              window.location.href = '/login';
            }
            return Promise.reject(refreshError);
          }
        }

        return Promise.reject(error);
      }
    );
  }

  // Enhanced API client with better error handling and retries
  async login(email: string, password: string) {
    try {
      const response = await this.client.post('/auth/login', { email, password });
      return response.data;
    } catch (error: any) {
      if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
        throw new Error('Backend is starting up, please wait a moment and try again');
      }
      throw error;
    }
  }

  async register(email: string, password: string, full_name?: string) {
    try {
      const response = await this.client.post('/auth/register', { email, password, full_name });
      return response.data;
    } catch (error: any) {
      if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
        throw new Error('Backend is starting up, please wait a moment and try again');
      }
      throw error;
    }
  }

  async refreshToken(refreshToken: string) {
    const response = await this.client.post('/auth/refresh', { refresh_token: refreshToken });
    return response.data;
  }

  async logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    sessionStorage.removeItem('access_token');
    sessionStorage.removeItem('refresh_token');
  }

  async getCurrentUser() {
    try {
      const response = await this.client.get('/users/me');
      return response.data;
    } catch (error: any) {
      if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
        throw new Error('Backend is starting up, please wait a moment and try again');
      }
      throw error;
    }
  }

  // Health check with retry logic
  async healthCheck(retries = 3): Promise<boolean> {
    for (let i = 0; i < retries; i++) {
      try {
        const response = await axios.get(`${API_BASE_URL.replace('/api/v1', '')}/health`, {
          timeout: 10000
        });
        return response.status === 200;
      } catch (error) {
        if (i === retries - 1) return false;
        await new Promise(resolve => setTimeout(resolve, 2000)); // Wait 2 seconds
      }
    }
    return false;
  }

  // Scan endpoints
  async createScan(targetUrl: string, scanMode: string, executionMode: string = 'report_only') {
    const response = await this.client.post('/scans/', {
      target_url: targetUrl,
      scan_mode: scanMode,
      execution_mode: executionMode,
    });
    const scan = response.data;
    // Transform backend response to match frontend expectations
    return {
      ...scan,
      target_url: scan.target,
      total_vulnerabilities: (scan.critical_count || 0) + (scan.high_count || 0) + 
                             (scan.medium_count || 0) + (scan.low_count || 0),
      vulnerabilities_found: {
        critical: scan.critical_count || 0,
        high: scan.high_count || 0,
        medium: scan.medium_count || 0,
        low: scan.low_count || 0,
      }
    };
  }

  async getScans(limit = 50, offset = 0) {
    const response = await this.client.get('/scans/', {
      params: { limit, offset },
    });
    // Transform backend response to match frontend expectations
    const data = response.data;
    return {
      items: data.scans?.map((scan: any) => ({
        ...scan,
        target_url: scan.target,
        total_vulnerabilities: (scan.critical_count || 0) + (scan.high_count || 0) + 
                               (scan.medium_count || 0) + (scan.low_count || 0),
        vulnerabilities_found: {
          critical: scan.critical_count || 0,
          high: scan.high_count || 0,
          medium: scan.medium_count || 0,
          low: scan.low_count || 0,
        }
      })) || [],
      total: data.total || 0,
      limit: data.limit,
      offset: data.offset,
    };
  }

  async getScan(scanId: string) {
    const response = await this.client.get(`/scans/${scanId}`);
    const scan = response.data;
    // Transform backend response to match frontend expectations
    return {
      ...scan,
      target_url: scan.target,
      total_vulnerabilities: (scan.critical_count || 0) + (scan.high_count || 0) + 
                             (scan.medium_count || 0) + (scan.low_count || 0),
      vulnerabilities_found: {
        critical: scan.critical_count || 0,
        high: scan.high_count || 0,
        medium: scan.medium_count || 0,
        low: scan.low_count || 0,
      }
    };
  }

  async deleteScan(scanId: string) {
    await this.client.delete(`/scans/${scanId}`);
  }

  async getScanReport(scanId: string, format: 'json' | 'text' = 'json') {
    const response = await this.client.get(`/scans/${scanId}/report`, {
      params: { format },
    });
    return response.data;
  }

  // API Key endpoints
  async getAPIKeyInfo() {
    const response = await this.client.get('/users/me/api-key');
    return response.data;
  }

  async generateAPIKey() {
    const response = await this.client.post('/users/me/api-key');
    return response.data;
  }

  async regenerateAPIKey() {
    const response = await this.client.post('/users/me/api-key/regenerate');
    return response.data;
  }

  async revokeAPIKey() {
    await this.client.delete('/users/me/api-key');
  }

  // Subscription endpoints
  async createCheckoutSession(tier: string) {
    const response = await this.client.post('/subscriptions/checkout', { 
      tier,
      success_url: `${window.location.origin}/billing?success=true`,
      cancel_url: `${window.location.origin}/billing?cancelled=true`,
    });
    return {
      checkout_url: response.data.url,
      session_id: response.data.session_id,
    };
  }

  async getSubscription() {
    const response = await this.client.get('/subscriptions/current');
    return response.data;
  }

  async cancelSubscription() {
    const response = await this.client.post('/subscriptions/cancel');
    return response.data;
  }

  // Usage endpoints
  async getUsageStatistics(days = 30) {
    const response = await this.client.get('/users/me/usage', {
      params: { days },
    });
    return response.data;
  }
}

export const apiClient = new APIClient();
