import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Alert,
  Card,
  CardContent,
  Grid,
  Chip,
} from '@mui/material';
import { ArrowBack as ArrowBackIcon, PlayArrow as PlayArrowIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '@/api/client';
import { useAuth } from '@/contexts/AuthContext';

const scanModes = [
  {
    value: 'common',
    label: 'Quick Scan',
    description: 'Fast scan for common vulnerabilities',
    duration: '~5 minutes',
  },
  {
    value: 'fast',
    label: 'Standard Scan',
    description: 'Comprehensive scan with moderate depth',
    duration: '~15 minutes',
  },
  {
    value: 'full',
    label: 'Deep Scan',
    description: 'Thorough comprehensive security assessment',
    duration: '~30-60 minutes',
  },
  {
    value: 'stealth',
    label: 'Stealth Scan',
    description: 'Low-profile scan to avoid detection',
    duration: '~45-90 minutes',
  },
  {
    value: 'aggressive',
    label: 'Aggressive Scan',
    description: 'High-intensity scan with all techniques',
    duration: '~60-120 minutes',
  },
];

const executionModes = [
  {
    value: 'report_only',
    label: 'Report Only',
    description: 'Generate vulnerability report without remediation',
    icon: '📊',
    tiers: ['free', 'premium', 'enterprise'],
  },
  {
    value: 'dry_run',
    label: 'Dry Run',
    description: 'Simulate fixes without applying changes',
    icon: '🧪',
    tiers: ['premium', 'enterprise'],
  },
  {
    value: 'apply_fixes',
    label: 'Apply Fixes',
    description: 'Automatically apply remediation fixes',
    icon: '🔧',
    tiers: ['enterprise'],
  },
];

const NewScanPage: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [targetUrl, setTargetUrl] = useState('');
  const [scanMode, setScanMode] = useState('common');
  const [executionMode, setExecutionMode] = useState('report_only');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent, withVisualization: boolean = false) => {
    e.preventDefault();
    
    if (!targetUrl) {
      setError('Please enter a target URL');
      return;
    }

    // Basic URL validation
    try {
      new URL(targetUrl);
    } catch {
      setError('Please enter a valid URL (e.g., https://example.com)');
      return;
    }

    try {
      setSubmitting(true);
      setError('');
      const scan = await apiClient.createScan(targetUrl, scanMode, executionMode);
      
      if (withVisualization) {
        // Navigate directly to brain visualization
        navigate(`/scans/${scan.id}/visualization`);
      } else {
        // Show success message and navigate to scan details
        alert('Scan created successfully! Redirecting to scan details...');
        setTimeout(() => {
          navigate(`/scans/${scan.id}`);
        }, 1000);
      }
      
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create scan');
    } finally {
      setSubmitting(false);
    }
  };

  const selectedMode = scanModes.find((m) => m.value === scanMode);
  const selectedExecution = executionModes.find((m) => m.value === executionMode);
  
  // Filter scan modes and execution modes based on user tier
  const userTier = user?.tier || 'free';
  const availableScanModes = scanModes.filter(mode => {
    if (userTier === 'free') return ['common', 'fast'].includes(mode.value);
    if (userTier === 'premium') return ['common', 'fast', 'full', 'stealth'].includes(mode.value);
    return true; // enterprise gets all modes
  });
  
  const availableExecutionModes = executionModes.filter(mode => 
    mode.tiers.includes(userTier)
  );

  return (
    <Box>
      <Button
        startIcon={<ArrowBackIcon />}
        onClick={() => navigate('/scans')}
        sx={{ mb: 2 }}
      >
        Back to Scans
      </Button>

      <Typography variant="h4" gutterBottom>
        Create New Scan
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <form onSubmit={handleSubmit}>
              {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {error}
                </Alert>
              )}

              <TextField
                fullWidth
                label="Target URL"
                value={targetUrl}
                onChange={(e) => setTargetUrl(e.target.value)}
                placeholder="https://example.com"
                helperText="Enter the URL you want to scan for vulnerabilities"
                sx={{ mb: 3 }}
                required
              />

              <FormControl fullWidth sx={{ mb: 3 }}>
                <InputLabel>Scan Type</InputLabel>
                <Select
                  value={scanMode}
                  onChange={(e) => setScanMode(e.target.value)}
                  label="Scan Type"
                >
                  {availableScanModes.map((mode) => (
                    <MenuItem key={mode.value} value={mode.value}>
                      {mode.label} - {mode.description}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <FormControl fullWidth sx={{ mb: 3 }}>
                <InputLabel>Execution Mode</InputLabel>
                <Select
                  value={executionMode}
                  onChange={(e) => setExecutionMode(e.target.value)}
                  label="Execution Mode"
                >
                  {availableExecutionModes.map((mode) => (
                    <MenuItem key={mode.value} value={mode.value}>
                      {mode.icon} {mode.label} - {mode.description}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              {selectedMode && (
                <Card variant="outlined" sx={{ mb: 2 }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {selectedMode.label}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" paragraph>
                      {selectedMode.description}
                    </Typography>
                    <Typography variant="body2">
                      Estimated duration: <strong>{selectedMode.duration}</strong>
                    </Typography>
                  </CardContent>
                </Card>
              )}

              {selectedExecution && (
                <Card variant="outlined" sx={{ mb: 3 }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>
                      {selectedExecution.icon} {selectedExecution.label}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {selectedExecution.description}
                    </Typography>
                    {selectedExecution.value === 'apply_fixes' && (
                      <Alert severity="warning" sx={{ mt: 2 }}>
                        <strong>Warning:</strong> This mode will automatically apply fixes to your target system. 
                        Use with caution and ensure you have proper backups.
                      </Alert>
                    )}
                  </CardContent>
                </Card>
              )}

              <Box sx={{ display: 'flex', gap: 2 }}>
                <Button
                  type="submit"
                  variant="contained"
                  size="large"
                  startIcon={<PlayArrowIcon />}
                  disabled={submitting}
                  onClick={(e) => handleSubmit(e, false)}
                  sx={{ flex: 1 }}
                >
                  {submitting ? 'Creating Scan...' : 'Start Scan'}
                </Button>
                
                <Button
                  variant="contained"
                  size="large"
                  disabled={submitting}
                  onClick={(e) => handleSubmit(e, true)}
                  sx={{ 
                    flex: 1,
                    background: 'linear-gradient(45deg, #00ffff 30%, #0088ff 90%)',
                    '&:hover': {
                      background: 'linear-gradient(45deg, #00cccc 30%, #0066cc 90%)',
                    }
                  }}
                >
                  🧠 Neural Interface
                </Button>
              </Box>
            </form>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Your Plan
            </Typography>
            <Chip
              label={user?.tier?.toUpperCase()}
              color="primary"
              sx={{ mb: 2 }}
            />
            <Typography variant="body2" color="text.secondary" paragraph>
              You are on the {user?.tier} plan.
            </Typography>
            {user?.tier === 'free' && (
              <Alert severity="info" sx={{ mt: 2 }}>
                Upgrade to Premium for faster scans and more features!
                <Button
                  size="small"
                  onClick={() => navigate('/billing')}
                  sx={{ mt: 1 }}
                >
                  Upgrade Now
                </Button>
              </Alert>
            )}
          </Paper>

          <Paper sx={{ p: 3, mt: 2 }}>
            <Typography variant="h6" gutterBottom>
              Tips
            </Typography>
            <Typography variant="body2" paragraph>
              • Make sure you have permission to scan the target
            </Typography>
            <Typography variant="body2" paragraph>
              • Start with a Common scan for quick results
            </Typography>
            <Typography variant="body2">
              • Use Full scan for comprehensive security assessment
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default NewScanPage;
