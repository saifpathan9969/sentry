import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import { AuthProvider, useAuth } from '@/contexts/AuthContext';

// Pages
import LoginPage from '@/pages/auth/LoginPage';
import RegisterPage from '@/pages/auth/RegisterPage';
import DashboardPage from '@/pages/dashboard/DashboardPage';
import ScansListPage from '@/pages/scans/ScansListPage';
import NewScanPage from '@/pages/scans/NewScanPage';
import ScanDetailsPage from '@/pages/scans/ScanDetailsPage';
import { ScanVisualizationPage } from '@/pages/scans/ScanVisualizationPage';
import { BrainTest } from '@/components/brain/BrainTest';
import SettingsPage from '@/pages/settings/SettingsPage';
import BillingPage from '@/pages/billing/BillingPage';
import LandingPage from '@/pages/public/LandingPage';
import PricingPage from '@/pages/public/PricingPage';

// Components
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import AppLayout from '@/components/layout/AppLayout';

// Sentry-inspired Modern Dark Theme
const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#6C5CE7', // Modern purple
      light: '#A29BFE',
      dark: '#5F3DC4',
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: '#00B894', // Teal accent
      light: '#55EFC4',
      dark: '#00A383',
    },
    error: {
      main: '#FF6B6B',
      light: '#FF8787',
      dark: '#EE5A52',
    },
    warning: {
      main: '#FDCB6E',
      light: '#FFEAA7',
      dark: '#F9B851',
    },
    info: {
      main: '#74B9FF',
      light: '#A8D8FF',
      dark: '#5FA3E8',
    },
    success: {
      main: '#00B894',
      light: '#55EFC4',
      dark: '#00A383',
    },
    background: {
      default: '#0F0F1E', // Deep dark blue-black
      paper: '#1A1A2E', // Slightly lighter
    },
    text: {
      primary: '#FFFFFF',
      secondary: '#A0A0B0',
    },
  },
  typography: {
    fontFamily: '"Inter", "Segoe UI", "Roboto", "Helvetica Neue", Arial, sans-serif',
    h1: {
      fontWeight: 700,
      letterSpacing: '-0.02em',
      fontSize: '2.5rem',
    },
    h2: {
      fontWeight: 700,
      letterSpacing: '-0.01em',
      fontSize: '2rem',
    },
    h3: {
      fontWeight: 600,
      letterSpacing: '-0.01em',
      fontSize: '1.75rem',
    },
    h4: {
      fontWeight: 600,
      fontSize: '1.5rem',
    },
    h5: {
      fontWeight: 600,
      fontSize: '1.25rem',
    },
    h6: {
      fontWeight: 600,
      fontSize: '1rem',
    },
    body1: {
      fontSize: '0.9375rem',
      lineHeight: 1.6,
      letterSpacing: '0.00938em',
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.5,
      letterSpacing: '0.01071em',
    },
    button: {
      textTransform: 'none',
      fontWeight: 600,
      letterSpacing: '0.02em',
      fontSize: '0.875rem',
    },
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          backgroundImage: 'radial-gradient(circle at 20% 50%, rgba(108, 92, 231, 0.05) 0%, transparent 50%), radial-gradient(circle at 80% 80%, rgba(0, 184, 148, 0.05) 0%, transparent 50%)',
          backgroundAttachment: 'fixed',
          scrollBehavior: 'smooth',
        },
        '*': {
          scrollbarWidth: 'thin',
          scrollbarColor: '#6C5CE7 #1A1A2E',
        },
        '*::-webkit-scrollbar': {
          width: '8px',
          height: '8px',
        },
        '*::-webkit-scrollbar-track': {
          background: '#1A1A2E',
        },
        '*::-webkit-scrollbar-thumb': {
          background: '#6C5CE7',
          borderRadius: '4px',
        },
        '*::-webkit-scrollbar-thumb:hover': {
          background: '#A29BFE',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'linear-gradient(rgba(255, 255, 255, 0.02), rgba(255, 255, 255, 0.02))',
          border: '1px solid rgba(108, 92, 231, 0.1)',
          boxShadow: '0 4px 24px rgba(0, 0, 0, 0.4)',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            boxShadow: '0 8px 32px rgba(108, 92, 231, 0.2)',
            borderColor: 'rgba(108, 92, 231, 0.3)',
          },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          padding: '10px 24px',
          transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: '0 8px 24px rgba(108, 92, 231, 0.3)',
          },
          '&:active': {
            transform: 'translateY(0)',
          },
        },
        contained: {
          background: 'linear-gradient(135deg, #6C5CE7 0%, #5F3DC4 100%)',
          boxShadow: '0 4px 16px rgba(108, 92, 231, 0.3)',
          '&:hover': {
            background: 'linear-gradient(135deg, #A29BFE 0%, #6C5CE7 100%)',
            boxShadow: '0 8px 24px rgba(108, 92, 231, 0.4)',
          },
        },
        outlined: {
          borderWidth: '2px',
          '&:hover': {
            borderWidth: '2px',
            backgroundColor: 'rgba(108, 92, 231, 0.08)',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          border: '1px solid rgba(108, 92, 231, 0.15)',
          boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: '0 12px 40px rgba(108, 92, 231, 0.25)',
            borderColor: 'rgba(108, 92, 231, 0.4)',
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 6,
          fontWeight: 600,
          transition: 'all 0.2s ease',
          '&:hover': {
            transform: 'scale(1.05)',
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            transition: 'all 0.2s ease',
            '& fieldset': {
              borderColor: 'rgba(108, 92, 231, 0.2)',
              borderWidth: '2px',
              transition: 'all 0.2s ease',
            },
            '&:hover fieldset': {
              borderColor: 'rgba(108, 92, 231, 0.4)',
            },
            '&.Mui-focused fieldset': {
              borderColor: '#6C5CE7',
              boxShadow: '0 0 0 4px rgba(108, 92, 231, 0.1)',
            },
          },
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        root: {
          borderBottom: '1px solid rgba(108, 92, 231, 0.1)',
        },
        head: {
          fontWeight: 700,
          color: '#6C5CE7',
          textTransform: 'uppercase',
          fontSize: '0.75rem',
          letterSpacing: '0.1em',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: 'rgba(26, 26, 46, 0.8)',
          backdropFilter: 'blur(20px)',
          borderBottom: '1px solid rgba(108, 92, 231, 0.1)',
          boxShadow: '0 4px 24px rgba(0, 0, 0, 0.2)',
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: '#1A1A2E',
          borderRight: '1px solid rgba(108, 92, 231, 0.1)',
          backgroundImage: 'linear-gradient(rgba(255, 255, 255, 0.02), rgba(255, 255, 255, 0.02))',
        },
      },
    },
    MuiLinearProgress: {
      styleOverrides: {
        root: {
          borderRadius: 4,
          height: 6,
          backgroundColor: 'rgba(108, 92, 231, 0.1)',
        },
        bar: {
          borderRadius: 4,
          background: 'linear-gradient(90deg, #6C5CE7 0%, #A29BFE 100%)',
        },
      },
    },
    MuiCircularProgress: {
      styleOverrides: {
        root: {
          color: '#6C5CE7',
        },
      },
    },
  },
});

// Root redirect component
const RootRedirect = () => {
  const { isAuthenticated, isLoading } = useAuth();
  
  if (isLoading) {
    return <div>Loading...</div>;
  }
  
  return <Navigate to={isAuthenticated ? "/dashboard" : "/"} replace />;
};

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<LandingPage />} />
            <Route path="/pricing" element={<PricingPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />

            {/* Brain visualization - full screen, no layout */}
            <Route 
              path="/scans/:scanId/visualization" 
              element={
                <ProtectedRoute>
                  <ScanVisualizationPage />
                </ProtectedRoute>
              } 
            />

            {/* Brain test page - for development */}
            <Route 
              path="/brain-test" 
              element={
                <ProtectedRoute>
                  <BrainTest />
                </ProtectedRoute>
              } 
            />

            {/* Protected routes with layout */}
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <DashboardPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/scans"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <ScansListPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/scans/new"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <NewScanPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/scans/:id"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <ScanDetailsPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/settings"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <SettingsPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/billing"
              element={
                <ProtectedRoute>
                  <AppLayout>
                    <BillingPage />
                  </AppLayout>
                </ProtectedRoute>
              }
            />

            {/* Catch all - redirect based on auth status */}
            <Route path="*" element={<RootRedirect />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
