/**
 * Brain Test Component - Simple test interface for brain visualization
 * Use this to test the brain without needing a full scan
 */
import React, { useState } from 'react';
import { Box, Button, Typography, Paper, Grid, Chip } from '@mui/material';
import { AIBrainVisualization } from './AIBrainVisualization';
// import { BrainState } from './BrainStateManager'; // Removed unused import

export const BrainTest: React.FC = () => {
  const [isScanning, setIsScanning] = useState(false);
  const [scanProgress, setScanProgress] = useState(0);
  const [vulnerabilities, setVulnerabilities] = useState<Array<{
    severity: 'low' | 'medium' | 'high' | 'critical';
    type: string;
  }>>([]);

  const startTestScan = () => {
    setIsScanning(true);
    setScanProgress(0);
    setVulnerabilities([]);

    // Simulate scan progression
    const progressInterval = setInterval(() => {
      setScanProgress(prev => {
        const newProgress = prev + 0.1;
        if (newProgress >= 1.0) {
          clearInterval(progressInterval);
          setIsScanning(false);
          return 1.0;
        }
        return newProgress;
      });
    }, 500);

    // Simulate vulnerability discoveries
    setTimeout(() => {
      setVulnerabilities([{ severity: 'medium', type: 'XSS Vulnerability' }]);
    }, 2000);

    setTimeout(() => {
      setVulnerabilities(prev => [...prev, { severity: 'high', type: 'SQL Injection' }]);
    }, 4000);

    setTimeout(() => {
      setVulnerabilities(prev => [...prev, { severity: 'critical', type: 'Remote Code Execution' }]);
    }, 6000);
  };

  const stopScan = () => {
    setIsScanning(false);
    setScanProgress(0);
    setVulnerabilities([]);
  };

  const addVulnerability = (severity: 'low' | 'medium' | 'high' | 'critical') => {
    const types = {
      low: 'Information Disclosure',
      medium: 'Cross-Site Scripting',
      high: 'SQL Injection',
      critical: 'Remote Code Execution'
    };

    setVulnerabilities(prev => [...prev, {
      severity,
      type: types[severity]
    }]);
  };

  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Controls */}
      <Paper sx={{ p: 2, mb: 2 }}>
        <Typography variant="h6" gutterBottom>
          🧠 Brain Visualization Test
        </Typography>
        
        <Grid container spacing={2} alignItems="center">
          <Grid item>
            <Button
              variant="contained"
              onClick={startTestScan}
              disabled={isScanning}
              color="primary"
            >
              Start Test Scan
            </Button>
          </Grid>
          
          <Grid item>
            <Button
              variant="outlined"
              onClick={stopScan}
              disabled={!isScanning}
            >
              Stop Scan
            </Button>
          </Grid>
          
          <Grid item>
            <Typography variant="body2">
              Progress: {Math.round(scanProgress * 100)}%
            </Typography>
          </Grid>
          
          <Grid item>
            <Typography variant="body2">
              Vulnerabilities: {vulnerabilities.length}
            </Typography>
          </Grid>
        </Grid>

        {/* Manual Vulnerability Buttons */}
        <Box sx={{ mt: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            Add Vulnerabilities:
          </Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button size="small" onClick={() => addVulnerability('low')} color="success">
              Low
            </Button>
            <Button size="small" onClick={() => addVulnerability('medium')} color="warning">
              Medium
            </Button>
            <Button size="small" onClick={() => addVulnerability('high')} color="error">
              High
            </Button>
            <Button size="small" onClick={() => addVulnerability('critical')} sx={{ bgcolor: '#d32f2f' }}>
              Critical
            </Button>
          </Box>
        </Box>

        {/* Vulnerability List */}
        {vulnerabilities.length > 0 && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Found Vulnerabilities:
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {vulnerabilities.map((vuln, index) => (
                <Chip
                  key={index}
                  label={`${vuln.severity.toUpperCase()}: ${vuln.type}`}
                  color={
                    vuln.severity === 'critical' ? 'error' :
                    vuln.severity === 'high' ? 'error' :
                    vuln.severity === 'medium' ? 'warning' : 'success'
                  }
                  size="small"
                />
              ))}
            </Box>
          </Box>
        )}
      </Paper>

      {/* Brain Visualization */}
      <Box sx={{ flex: 1, position: 'relative' }}>
        <AIBrainVisualization
          isScanning={isScanning}
          scanProgress={scanProgress}
          vulnerabilities={vulnerabilities}
          onBrainClick={() => console.log('🧠 Brain clicked!')}
          className="test-brain"
        />
      </Box>
    </Box>
  );
};