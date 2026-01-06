import React, { useEffect, useState } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Card,
  CardContent,
  CardActions,
  Chip,
  LinearProgress,
  Alert,
} from '@mui/material';
import {
  Add as AddIcon,
  TrendingUp as TrendingUpIcon,
  Security as SecurityIcon,
  Speed as SpeedIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';
import { apiClient } from '@/api/client';
import { useAuth } from '@/contexts/AuthContext';
import { BrainDemo } from '@/components/brain/BrainDemo';
import type { Scan } from '@/types';

const COLORS = ['#f44336', '#ff9800', '#ffeb3b', '#4caf50', '#2196f3'];

const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [recentScans, setRecentScans] = useState<Scan[]>([]);
  const [loading, setLoading] = useState(true);
  const [targetUrl, setTargetUrl] = useState('');
  const [scanMode, setScanMode] = useState('common');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [usageStats, setUsageStats] = useState<any>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [scansData, usage] = await Promise.all([
        apiClient.getScans(5, 0).catch(() => ({ items: [], total: 0, limit: 5, offset: 0 })),
        apiClient.getUsageStatistics(30).catch(() => null),
      ]);
      setRecentScans(scansData.items || []);
      setUsageStats(usage);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
      // Set empty state on error
      setRecentScans([]);
      setUsageStats(null);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickScan = async () => {
    if (!targetUrl) {
      setError('Please enter a target URL');
      return;
    }

    try {
      setSubmitting(true);
      setError('');
      const scan = await apiClient.createScan(targetUrl, scanMode);
      navigate(`/scans/${scan.id}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create scan');
    } finally {
      setSubmitting(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'running': return 'info';
      case 'failed': return 'error';
      case 'queued': return 'warning';
      default: return 'default';
    }
  };

  const getSeverityData = () => {
    if (!recentScans.length) return [];
    const severityCounts: any = { critical: 0, high: 0, medium: 0, low: 0, info: 0 };
    recentScans.forEach(scan => {
      if (scan.vulnerabilities_found) {
        Object.entries(scan.vulnerabilities_found).forEach(([severity, count]) => {
          severityCounts[severity] = (severityCounts[severity] || 0) + (count as number);
        });
      }
    });
    return Object.entries(severityCounts).map(([name, value]) => ({ name, value }));
  };

  const getTierLimits = () => {
    const limits: any = {
      free: { daily: 10, monthly: 100 },
      premium: { daily: 100, monthly: 3000 },
      enterprise: { daily: 1000, monthly: 30000 },
    };
    // Check if user email is in owner emails for enterprise access
    const ownerEmails = ['saifullahpathan49@gmail.com', 'saifullah.pathan24@sanjivani.edu.in'];
    const userTier = user?.email && ownerEmails.includes(user.email.toLowerCase()) ? 'enterprise' : (user?.tier || 'free');
    return limits[userTier];
  };

  const tierLimits = getTierLimits();
  const dailyUsage = usageStats?.scans_today || 0;
  // monthlyUsage available for future use
  const _monthlyUsage = usageStats?.scans_this_month || 0;
  void _monthlyUsage; // Suppress unused warning

  if (loading) {
    return <Box sx={{ width: '100%' }}><LinearProgress /></Box>;
  }

  // Check if user email is in owner emails for enterprise access
  const ownerEmails = ['saifullahpathan49@gmail.com', 'saifullah.pathan24@sanjivani.edu.in'];
  const effectiveTier = user?.email && ownerEmails.includes(user.email.toLowerCase()) ? 'enterprise' : (user?.tier || 'free');

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Welcome back{user?.full_name ? `, ${user.full_name}` : ''}!
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        {effectiveTier === 'enterprise' && '🔐 Creator Access: Full Enterprise Features Enabled'}
      </Typography>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <SecurityIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">{recentScans.length}</Typography>
              </Box>
              <Typography color="text.secondary">Recent Scans</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <TrendingUpIcon color="error" sx={{ mr: 1 }} />
                <Typography variant="h6">
                  {recentScans.reduce((sum, s) => sum + (s.total_vulnerabilities || 0), 0)}
                </Typography>
              </Box>
              <Typography color="text.secondary">Total Vulnerabilities</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <SpeedIcon color="success" sx={{ mr: 1 }} />
                <Typography variant="h6">{dailyUsage}/{tierLimits.daily}</Typography>
              </Box>
              <Typography color="text.secondary">Daily Scans</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Chip label={effectiveTier.toUpperCase()} color="primary" />
              <Typography color="text.secondary" sx={{ mt: 1 }}>Current Tier</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* AI Brain Demo */}
        <Grid item xs={12} md={6}>
          <BrainDemo 
            onLaunchFullscreen={() => navigate('/scans/new')}
          />
        </Grid>

        {/* Quick Scan */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Quick Scan
            </Typography>
            {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
            <TextField
              fullWidth
              label="Target URL"
              value={targetUrl}
              onChange={(e) => setTargetUrl(e.target.value)}
              placeholder="https://example.com"
              sx={{ mb: 2 }}
            />
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Scan Mode</InputLabel>
              <Select value={scanMode} onChange={(e) => setScanMode(e.target.value)}>
                <MenuItem value="common">Common (Fast)</MenuItem>
                <MenuItem value="fast">Fast</MenuItem>
                <MenuItem value="full">Full (Comprehensive)</MenuItem>
              </Select>
            </FormControl>
            <Button
              fullWidth
              variant="contained"
              startIcon={<AddIcon />}
              onClick={handleQuickScan}
              disabled={submitting}
            >
              {submitting ? 'Creating...' : 'Start Scan'}
            </Button>
          </Paper>
        </Grid>

        {/* Vulnerability Distribution */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Vulnerability Distribution
            </Typography>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={getSeverityData()}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry) => `${entry.name}: ${entry.value}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {getSeverityData().map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Recent Scans */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">Recent Scans</Typography>
              <Button onClick={() => navigate('/scans')}>View All</Button>
            </Box>
            {recentScans.length === 0 ? (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  No scans yet
                </Typography>
                <Typography color="text.secondary" paragraph>
                  Start your first penetration test using the Quick Scan form above!
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => navigate('/scans/new')}
                  sx={{ mt: 2 }}
                >
                  Create New Scan
                </Button>
              </Box>
            ) : (
              <Grid container spacing={2}>
                {recentScans.map((scan) => (
                  <Grid item xs={12} key={scan.id}>
                    <Card variant="outlined">
                      <CardContent>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <Box>
                            <Typography variant="subtitle1">{scan.target_url}</Typography>
                            <Typography variant="body2" color="text.secondary">
                              {new Date(scan.created_at).toLocaleString()}
                            </Typography>
                          </Box>
                          <Box sx={{ textAlign: 'right' }}>
                            <Chip
                              label={scan.status}
                              color={getStatusColor(scan.status) as any}
                              size="small"
                              sx={{ mb: 1 }}
                            />
                            <Typography variant="body2">
                              {scan.total_vulnerabilities || 0} vulnerabilities
                            </Typography>
                          </Box>
                        </Box>
                      </CardContent>
                      <CardActions>
                        <Button size="small" onClick={() => navigate(`/scans/${scan.id}`)}>
                          View Details
                        </Button>
                      </CardActions>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DashboardPage;
