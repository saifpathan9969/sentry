import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { CircularProgress, Box } from '@mui/material';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, isLoading, user } = useAuth();
  const location = useLocation();

  console.log('🛡️ ProtectedRoute check:', {
    path: location.pathname,
    isLoading,
    isAuthenticated,
    hasUser: !!user,
    userEmail: user?.email,
    userTier: user?.tier
  });

  // Show loading spinner while checking authentication
  if (isLoading) {
    console.log('⏳ ProtectedRoute: Still loading authentication state...');
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
        sx={{ backgroundColor: '#000000' }}
      >
        <CircularProgress sx={{ color: '#b388ff' }} />
      </Box>
    );
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated || !user) {
    console.log('🚫 ProtectedRoute: Not authenticated, redirecting to login');
    console.log('   Current path:', location.pathname);
    console.log('   Will redirect to: /login');
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  console.log('✅ ProtectedRoute: User authenticated, rendering protected content');
  console.log('   User:', user.email);
  console.log('   Tier:', user.tier);
  
  return <>{children}</>;
};

export default ProtectedRoute;