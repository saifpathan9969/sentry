import { Navigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { CircularProgress, Box } from '@mui/material';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, isLoading, user } = useAuth();

  // Debug logging
  console.log('🛡️ ProtectedRoute check:', {
    isLoading,
    isAuthenticated,
    hasUser: !!user,
    userEmail: user?.email
  });

  if (isLoading) {
    console.log('⏳ ProtectedRoute: Still loading auth state...');
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
      >
        <CircularProgress />
      </Box>
    );
  }

  if (!isAuthenticated) {
    console.log('🚫 ProtectedRoute: Not authenticated, redirecting to login');
    return <Navigate to="/login" replace />;
  }

  console.log('✅ ProtectedRoute: Authenticated, rendering protected content');
  return <>{children}</>;
};

export default ProtectedRoute;
