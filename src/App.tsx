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

// Dark Purple Elegant Theme
const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#b388ff', // Light purple
      light: '#e7b9ff',
      dark: '#805acb',
      contrastText: '#000000',
    },
    secondary: {
      main: '#ea80fc', // Pink purple
      light: '#ffb2ff',
      dark: '#b64fc8',
    },
    error: {
      main: '#ff5252',
      light: '#ff867f',
      dark: '#c50e29',
    },
    warning: {
      main: '#ffab40',
      light: '#ffdd71',
      dark: '#c77c02',
    },
    info: {
      main: '#ce93d8', // Light purple info
      light: '#ffc4ff',
      dark: '#9c64a6',
    },
    success: {
      main: '#b388ff',
      light: '#e7b9ff',
      dark: '#805acb',
    },
    background: {
      default: '#000000', // Pure black
      paper: '#0d0d0d', // Slightly lighter black
    },
    text: {
      primary: '#e1bee7', // Light purple text
      secondary: '#9e9e9e', // Gray
    },
  },
  typography: {
    fontFamily: '"Times New Roman", Times, Georgia, serif',
    h1: {
      fontWeight: 700,
      letterSpacing: '0.02em',
    },
    h2: {
      fontWeight: 700,
      letterSpacing: '0.02em',
    },
    h3: {
      fontWeight: 600,
      letterSpacing: '0.02em',
    },
    h4: {
      fontWeight: 600,
    },
    h5: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 600,
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.6,
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.5,
    },
    button: {
      textTransform: 'none',
      fontWeight: 600,
      letterSpacing: '0.02em',
    },
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          backgroundImage: 'radial-gradient(circle at 50% 50%, rgba(179, 136, 255, 0.03) 0%, transparent 50%)',
          backgroundAttachment: 'fixed',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'linear-gradient(rgba(179, 136, 255, 0.02), rgba(179, 136, 255, 0.02))',
          border: '1px solid rgba(179, 136, 255, 0.15)',
          boxShadow: '0 4px 20px rgba(179, 136, 255, 0.1)',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 4,
          boxShadow: '0 2px 10px rgba(179, 136, 255, 0.2)',
          '&:hover': {
            boxShadow: '0 4px 20px rgba(179, 136, 255, 0.4)',
          },
        },
        contained: {
          background: 'linear-gradient(135deg, #b388ff 0%, #805acb 100%)',
          '&:hover': {
            background: 'linear-gradient(135deg, #e7b9ff 0%, #b388ff 100%)',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          border: '1px solid rgba(179, 136, 255, 0.2)',
          boxShadow: '0 4px 15px rgba(179, 136, 255, 0.1)',
          transition: 'all 0.3s ease',
          '&:hover': {
            boxShadow: '0 8px 30px rgba(179, 136, 255, 0.2)',
            borderColor: 'rgba(179, 136, 255, 0.4)',
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 4,
          fontWeight: 500,
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            '& fieldset': {
              borderColor: 'rgba(179, 136, 255, 0.3)',
            },
            '&:hover fieldset': {
              borderColor: 'rgba(179, 136, 255, 0.5)',
            },
            '&.Mui-focused fieldset': {
              borderColor: '#b388ff',
              boxShadow: '0 0 10px rgba(179, 136, 255, 0.2)',
            },
          },
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        root: {
          borderBottom: '1px solid rgba(179, 136, 255, 0.15)',
        },
        head: {
          fontWeight: 700,
          color: '#b388ff',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#0d0d0d',
          borderBottom: '1px solid rgba(179, 136, 255, 0.2)',
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: '#0d0d0d',
          borderRight: '1px solid rgba(179, 136, 255, 0.2)',
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
