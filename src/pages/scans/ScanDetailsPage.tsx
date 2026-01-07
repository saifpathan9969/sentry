import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Paper,
  Typography,
  Button,
  Chip,
  Grid,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress,
  Alert,
  Tabs,
  Tab,
  IconButton,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Download as DownloadIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  Psychology as BrainIcon,
} from '@mui/icons-material';
import { apiClient } from '@/api/client';
import type { Scan } from '@/types';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => (
  <div hidden={value !== index}>
    {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
  </div>
);

const ScanDetailsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [scan, setScan] = useState<Scan | null>(null);
  const [report, setReport] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [tabValue, setTabValue] = useState(0);

  useEffect(() => {
    if (id) {
      loadScanDetails();
      const interval = setInterval(() => {
        if (scan?.status === 'running' || scan?.status === 'queued') {
          loadScanDetails();
        }
      }, 5000);
      return () => clearInterval(interval);
    }
  }, [id, scan?.status]);

  const loadScanDetails = async () => {
    try {
      setLoading(true);
      const [scanData, reportResponse] = await Promise.all([
        apiClient.getScan(id!),
        apiClient.getScanReport(id!, 'json').catch(() => null),
      ]);
      setScan(scanData);
      // Extract report content from response
      if (reportResponse) {
        const reportContent = reportResponse.report || reportResponse;
        try {
          setReport(typeof reportContent === 'string' ? JSON.parse(reportContent) : reportContent);
        } catch {
          setReport(reportContent);
        }
      }
    } catch (err) {
      console.error('Failed to load scan details:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this scan?')) return;
    
    try {
      await apiClient.deleteScan(id!);
      navigate('/scans');
    } catch (err) {
      console.error('Failed to delete scan:', err);
    }
  };

  const handleDownload = async (format: 'json' | 'text') => {
    try {
      const response = await apiClient.getScanReport(id!, format);
      // Extract the report content from the response
      const reportContent = response.report || response;
      const contentType = format === 'json' ? 'application/json' : 'text/plain';
      const content = format === 'json' ? JSON.stringify(JSON.parse(reportContent), null, 2) : reportContent;
      const blob = new Blob([content], { type: contentType });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `scan-${id}.${format === 'json' ? 'json' : 'txt'}`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Failed to download report:', err);
    }
  };

  const handleBrainVisualization = () => {
    navigate(`/scans/${id}/visualization`);
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

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical': return 'error';
      case 'high': return 'warning';
      case 'medium': return 'info';
      case 'low': return 'success';
      default: return 'default';
    }
  };

  if (loading && !scan) {
    return <Box><LinearProgress /></Box>;
  }

  if (!scan) {
    return (
      <Box>
        <Alert severity="error">Scan not found</Alert>
        <Button onClick={() => navigate('/scans')} sx={{ mt: 2 }}>
          Back to Scans
        </Button>
      </Box>
    );
  }

  return (
    <Box>
      <Button
        startIcon={<ArrowBackIcon />}
        onClick={() => navigate('/scans')}
        sx={{ mb: 2 }}
      >
        Back to Scans
      </Button>

      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">Scan Details</Typography>
        <Box>
          <Button
            startIcon={<BrainIcon />}
            onClick={handleBrainVisualization}
            variant="contained"
            sx={{ 
              mr: 1,
              background: 'linear-gradient(45deg, #00ffff 30%, #0088ff 90%)',
              '&:hover': {
                background: 'linear-gradient(45deg, #00cccc 30%, #0066cc 90%)',
              }
            }}
          >
            Neural Interface
          </Button>
          <IconButton onClick={loadScanDetails} title="Refresh">
            <RefreshIcon />
          </IconButton>
          <Button
            startIcon={<DownloadIcon />}
            onClick={() => handleDownload('json')}
            variant="outlined"
            size="small"
            sx={{ mr: 1 }}
          >
            JSON
          </Button>
          <Button
            startIcon={<DownloadIcon />}
            onClick={() => handleDownload('text')}
            variant="outlined"
            size="small"
            sx={{ mr: 1 }}
          >
            Text
          </Button>
          <IconButton onClick={handleDelete} color="error" title="Delete">
            <DeleteIcon />
          </IconButton>
        </Box>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Scan Information
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">Target URL</Typography>
                <Typography variant="body1">{scan.target_url}</Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">Status</Typography>
                <Chip
                  label={scan.status}
                  color={getStatusColor(scan.status) as any}
                  size="small"
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">Scan Mode</Typography>
                <Typography variant="body1">{scan.scan_mode}</Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">Created</Typography>
                <Typography variant="body1">
                  {new Date(scan.created_at).toLocaleString()}
                </Typography>
              </Grid>
              {scan.completed_at && (
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" color="text.secondary">Completed</Typography>
                  <Typography variant="body1">
                    {new Date(scan.completed_at).toLocaleString()}
                  </Typography>
                </Grid>
              )}
            </Grid>
          </Paper>

          {scan.status === 'running' && (
            <Alert severity="info" sx={{ mb: 3 }}>
              Scan is in progress. This page will auto-refresh every 5 seconds.
            </Alert>
          )}

          {scan.status === 'completed' && report && (
            <Paper>
              <Tabs value={tabValue} onChange={(_, v) => setTabValue(v)}>
                <Tab label="Summary" />
                <Tab label="Vulnerabilities" />
                <Tab label="Raw Report" />
              </Tabs>
              
              <TabPanel value={tabValue} index={0}>
                <Typography variant="h6" gutterBottom>
                  Vulnerability Summary
                </Typography>
                <Grid container spacing={2}>
                  {Object.entries(scan.vulnerabilities_found || {}).map(([severity, count]) => (
                    <Grid item xs={6} sm={3} key={severity}>
                      <Card variant="outlined">
                        <CardContent>
                          <Typography variant="h4">{count as number}</Typography>
                          <Chip
                            label={severity}
                            color={getSeverityColor(severity) as any}
                            size="small"
                          />
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              </TabPanel>

              <TabPanel value={tabValue} index={1}>
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Severity</TableCell>
                        <TableCell>Type</TableCell>
                        <TableCell>Description</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {report.vulnerabilities?.map((vuln: any, idx: number) => (
                        <TableRow key={idx}>
                          <TableCell>
                            <Chip
                              label={vuln.severity}
                              color={getSeverityColor(vuln.severity) as any}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>{vuln.type}</TableCell>
                          <TableCell>{vuln.description}</TableCell>
                        </TableRow>
                      )) || (
                        <TableRow>
                          <TableCell colSpan={3} align="center">
                            No vulnerabilities found
                          </TableCell>
                        </TableRow>
                      )}
                    </TableBody>
                  </Table>
                </TableContainer>
              </TabPanel>

              <TabPanel value={tabValue} index={2}>
                <Box
                  component="pre"
                  sx={{
                    p: 2,
                    bgcolor: 'grey.100',
                    borderRadius: 1,
                    overflow: 'auto',
                    maxHeight: 500,
                  }}
                >
                  {JSON.stringify(report, null, 2)}
                </Box>
              </TabPanel>
            </Paper>
          )}
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Statistics
              </Typography>
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Total Vulnerabilities
                </Typography>
                <Typography variant="h4">{scan.total_vulnerabilities || 0}</Typography>
              </Box>
              {scan.vulnerabilities_found && (
                <Box>
                  {Object.entries(scan.vulnerabilities_found).map(([severity, count]) => (
                    <Box key={severity} sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                      <Chip
                        label={severity}
                        color={getSeverityColor(severity) as any}
                        size="small"
                      />
                      <Typography>{count as number}</Typography>
                    </Box>
                  ))}
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ScanDetailsPage;
