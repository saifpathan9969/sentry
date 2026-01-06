/**
 * Scan Visualization Page - Full-screen AI Brain interface
 * Shows the Jarvis-style brain during active scans
 */
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { AIBrainVisualization } from '../../components/brain/AIBrainVisualization';
import { apiClient } from '../../api/client';

interface ScanData {
  id: string;
  target_url: string;
  scan_mode: string;
  status: string;
  vulnerabilities_found?: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
  created_at: string;
  started_at?: string;
  completed_at?: string;
}

export const ScanVisualizationPage: React.FC = () => {
  const { scanId } = useParams<{ scanId: string }>();
  const navigate = useNavigate();
  
  const [scan, setScan] = useState<ScanData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [scanProgress, setScanProgress] = useState(0);
  const [vulnerabilities, setVulnerabilities] = useState<Array<{
    severity: 'low' | 'medium' | 'high' | 'critical';
    type: string;
  }>>([]);

  // Fetch scan data with improved polling
  useEffect(() => {
    if (!scanId) {
      setError('No scan ID provided');
      setLoading(false);
      return;
    }

    console.log('🧠 Starting neural brain visualization for scan:', scanId);
    fetchScanData();
    
    // More aggressive polling for active scans
    const interval = setInterval(() => {
      if (scan?.status === 'running' || scan?.status === 'queued') {
        console.log('🔄 Polling scan status...');
        fetchScanData();
      } else if (scan?.status === 'completed') {
        console.log('✅ Scan completed, stopping polling');
        clearInterval(interval);
      }
    }, 1000); // Poll every second for better responsiveness

    return () => {
      console.log('🛑 Cleaning up scan polling');
      clearInterval(interval);
    };
  }, [scanId, scan?.status]); // Also depend on scan status

  const fetchScanData = async () => {
    try {
      console.log('🔍 Fetching scan data for ID:', scanId);
      const scanData = await apiClient.getScan(scanId!);
      console.log('📊 Scan data received:', scanData);
      setScan(scanData);
      
      // Calculate progress based on status
      let progress = 0;
      switch (scanData.status) {
        case 'queued':
          progress = 0.1;
          console.log('⏳ Scan queued, progress: 10%');
          break;
        case 'running':
          // Simulate realistic progress for running scans
          const elapsed = scanData.started_at ? 
            (Date.now() - new Date(scanData.started_at).getTime()) / 1000 : 0;
          progress = Math.min(0.9, 0.2 + (elapsed / 300) * 0.7); // Progress over 5 minutes
          console.log('🔄 Scan running, progress:', Math.round(progress * 100) + '%');
          break;
        case 'completed':
          progress = 1.0;
          console.log('✅ Scan completed');
          break;
        case 'failed':
          progress = 0;
          console.log('❌ Scan failed');
          break;
        default:
          console.log('❓ Unknown scan status:', scanData.status);
      }
      setScanProgress(progress);
      
      // Generate vulnerability data for visualization
      if (scanData.vulnerabilities_found) {
        const vulns: Array<{ severity: 'low' | 'medium' | 'high' | 'critical'; type: string }> = [];
        
        // Add vulnerabilities based on counts
        for (let i = 0; i < scanData.vulnerabilities_found.critical; i++) {
          vulns.push({ severity: 'critical', type: 'Critical Security Flaw' });
        }
        for (let i = 0; i < scanData.vulnerabilities_found.high; i++) {
          vulns.push({ severity: 'high', type: 'High Risk Vulnerability' });
        }
        for (let i = 0; i < scanData.vulnerabilities_found.medium; i++) {
          vulns.push({ severity: 'medium', type: 'Medium Risk Issue' });
        }
        for (let i = 0; i < scanData.vulnerabilities_found.low; i++) {
          vulns.push({ severity: 'low', type: 'Low Risk Finding' });
        }
        
        console.log('🚨 Vulnerabilities for neural brain:', vulns.length);
        setVulnerabilities(vulns);
      } else {
        // For running scans, simulate some vulnerabilities being found
        if (scanData.status === 'running' && progress > 0.3) {
          const mockVulns: Array<{ severity: 'low' | 'medium' | 'high' | 'critical'; type: string }> = [
            { severity: 'medium', type: 'Missing Security Headers' },
            { severity: 'low', type: 'Information Disclosure' },
          ];
          if (progress > 0.6) {
            mockVulns.push({ severity: 'high', type: 'Potential XSS Vulnerability' });
          }
          setVulnerabilities(mockVulns);
          console.log('🧪 Mock vulnerabilities for running scan:', mockVulns.length);
        }
      }
      
      setLoading(false);
    } catch (err) {
      console.error('❌ Failed to fetch scan data:', err);
      setError('Failed to load scan data');
      setLoading(false);
    }
  };

  const handleExitVisualization = () => {
    if (scan) {
      navigate(`/scans/${scan.id}`);
    } else {
      navigate('/scans');
    }
  };

  const handleBrainClick = () => {
    // Brain interaction - could trigger manual analysis phases
    console.log('🧠 Brain interaction detected');
  };

  if (loading) {
    return (
      <div className="scan-viz-loading">
        <div className="loading-content">
          <div className="loading-spinner"></div>
          <p>Initializing Neural Interface...</p>
        </div>
      </div>
    );
  }

  if (error || !scan) {
    return (
      <div className="scan-viz-error">
        <div className="error-content">
          <h2>⚠️ Neural Interface Error</h2>
          <p>{error || 'Scan not found'}</p>
          <button onClick={() => navigate('/scans')} className="error-button">
            Return to Scans
          </button>
        </div>
      </div>
    );
  }

  const isScanning = scan.status === 'running' || scan.status === 'queued';

  return (
    <div className="scan-visualization-page">
      {/* Full-screen Brain Visualization */}
      <AIBrainVisualization
        isScanning={isScanning}
        scanProgress={scanProgress}
        vulnerabilities={vulnerabilities}
        onBrainClick={handleBrainClick}
        className="fullscreen-brain"
      />
      
      {/* Holographic HUD Overlay */}
      <div className="hud-overlay">
        {/* Top Bar */}
        <div className="hud-top">
          <div className="scan-info">
            <h1 className="scan-title">NEURAL SCAN INTERFACE</h1>
            <div className="scan-details">
              <span className="target">TARGET: {scan.target_url}</span>
              <span className="mode">MODE: {scan.scan_mode.toUpperCase()}</span>
              <span className="status">STATUS: {scan.status.toUpperCase()}</span>
            </div>
          </div>
          
          <button onClick={handleExitVisualization} className="exit-button">
            <span>EXIT</span>
          </button>
        </div>
        
        {/* Side Panel - Scan Metrics */}
        <div className="hud-side">
          <div className="metrics-panel">
            <h3>SCAN METRICS</h3>
            
            {/* Progress */}
            <div className="metric">
              <label>PROGRESS</label>
              <div className="progress-display">
                <div className="progress-bar">
                  <div 
                    className="progress-fill"
                    style={{ width: `${scanProgress * 100}%` }}
                  ></div>
                </div>
                <span>{Math.round(scanProgress * 100)}%</span>
              </div>
            </div>
            
            {/* Vulnerabilities */}
            {scan.vulnerabilities_found && (
              <div className="metric">
                <label>THREATS DETECTED</label>
                <div className="threat-counts">
                  <div className="threat-item critical">
                    <span className="count">{scan.vulnerabilities_found.critical}</span>
                    <span className="label">CRITICAL</span>
                  </div>
                  <div className="threat-item high">
                    <span className="count">{scan.vulnerabilities_found.high}</span>
                    <span className="label">HIGH</span>
                  </div>
                  <div className="threat-item medium">
                    <span className="count">{scan.vulnerabilities_found.medium}</span>
                    <span className="label">MEDIUM</span>
                  </div>
                  <div className="threat-item low">
                    <span className="count">{scan.vulnerabilities_found.low}</span>
                    <span className="label">LOW</span>
                  </div>
                </div>
              </div>
            )}
            
            {/* Timing */}
            <div className="metric">
              <label>SCAN TIME</label>
              <div className="time-display">
                {scan.started_at ? (
                  <span>
                    {Math.round((Date.now() - new Date(scan.started_at).getTime()) / 1000)}s
                  </span>
                ) : (
                  <span>--</span>
                )}
              </div>
            </div>
          </div>
        </div>
        
        {/* Bottom Bar - Instructions */}
        <div className="hud-bottom">
          <div className="instructions">
            <div className="instruction">
              <span className="key">MOUSE</span>
              <span className="action">Rotate & Zoom</span>
            </div>
            <div className="instruction">
              <span className="key">CLICK</span>
              <span className="action">Interact with Brain</span>
            </div>
            <div className="instruction">
              <span className="key">ESC</span>
              <span className="action">Exit Interface</span>
            </div>
          </div>
        </div>
      </div>
      
      {/* Keyboard shortcuts */}
      <div className="keyboard-handler" tabIndex={0} onKeyDown={(e) => {
        if (e.key === 'Escape') {
          handleExitVisualization();
        }
      }} />
      
      <style>{`
        .scan-visualization-page {
          position: fixed;
          top: 0;
          left: 0;
          width: 100vw;
          height: 100vh;
          background: #000;
          overflow: hidden;
          z-index: 1000;
        }
        
        .fullscreen-brain {
          width: 100%;
          height: 100%;
        }
        
        .hud-overlay {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          pointer-events: none;
          z-index: 10;
        }
        
        .hud-top {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          padding: 20px;
          background: linear-gradient(180deg, rgba(0,0,0,0.8) 0%, transparent 100%);
        }
        
        .scan-info {
          color: #00ffff;
          font-family: 'Courier New', monospace;
        }
        
        .scan-title {
          font-size: 24px;
          font-weight: bold;
          margin-bottom: 8px;
          text-shadow: 0 0 20px rgba(0, 255, 255, 0.8);
        }
        
        .scan-details {
          display: flex;
          gap: 20px;
          font-size: 12px;
          opacity: 0.8;
        }
        
        .exit-button {
          pointer-events: auto;
          background: rgba(255, 0, 0, 0.2);
          border: 1px solid #ff4444;
          color: #ff4444;
          padding: 8px 16px;
          font-family: 'Courier New', monospace;
          font-size: 12px;
          cursor: pointer;
          transition: all 0.3s ease;
        }
        
        .exit-button:hover {
          background: rgba(255, 0, 0, 0.4);
          box-shadow: 0 0 15px rgba(255, 68, 68, 0.6);
        }
        
        .hud-side {
          position: absolute;
          right: 20px;
          top: 50%;
          transform: translateY(-50%);
          width: 250px;
        }
        
        .metrics-panel {
          background: rgba(0, 0, 0, 0.8);
          border: 1px solid rgba(0, 255, 255, 0.3);
          padding: 20px;
          color: #00ffff;
          font-family: 'Courier New', monospace;
          font-size: 12px;
        }
        
        .metrics-panel h3 {
          margin-bottom: 16px;
          font-size: 14px;
          text-align: center;
          text-shadow: 0 0 10px rgba(0, 255, 255, 0.8);
        }
        
        .metric {
          margin-bottom: 16px;
        }
        
        .metric label {
          display: block;
          margin-bottom: 4px;
          opacity: 0.7;
          font-size: 10px;
        }
        
        .progress-display {
          display: flex;
          align-items: center;
          gap: 8px;
        }
        
        .progress-bar {
          flex: 1;
          height: 4px;
          background: rgba(0, 255, 255, 0.2);
          border-radius: 2px;
          overflow: hidden;
        }
        
        .progress-fill {
          height: 100%;
          background: linear-gradient(90deg, #00ffff, #00aaff);
          border-radius: 2px;
          box-shadow: 0 0 10px rgba(0, 255, 255, 0.6);
          transition: width 0.5s ease;
        }
        
        .threat-counts {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 8px;
        }
        
        .threat-item {
          display: flex;
          flex-direction: column;
          align-items: center;
          padding: 8px;
          border-radius: 4px;
          background: rgba(255, 255, 255, 0.05);
        }
        
        .threat-item.critical {
          border-left: 3px solid #ff0000;
        }
        
        .threat-item.high {
          border-left: 3px solid #ff6600;
        }
        
        .threat-item.medium {
          border-left: 3px solid #ffaa00;
        }
        
        .threat-item.low {
          border-left: 3px solid #00ff00;
        }
        
        .threat-item .count {
          font-size: 16px;
          font-weight: bold;
        }
        
        .threat-item .label {
          font-size: 8px;
          opacity: 0.7;
        }
        
        .time-display {
          font-size: 14px;
          text-align: center;
        }
        
        .hud-bottom {
          position: absolute;
          bottom: 0;
          left: 0;
          width: 100%;
          padding: 20px;
          background: linear-gradient(0deg, rgba(0,0,0,0.8) 0%, transparent 100%);
        }
        
        .instructions {
          display: flex;
          justify-content: center;
          gap: 40px;
          color: rgba(0, 255, 255, 0.6);
          font-family: 'Courier New', monospace;
          font-size: 11px;
        }
        
        .instruction {
          display: flex;
          align-items: center;
          gap: 8px;
        }
        
        .instruction .key {
          background: rgba(0, 255, 255, 0.2);
          padding: 2px 6px;
          border-radius: 2px;
          font-weight: bold;
        }
        
        .keyboard-handler {
          position: absolute;
          top: 0;
          left: 0;
          width: 1px;
          height: 1px;
          opacity: 0;
          pointer-events: none;
        }
        
        .scan-viz-loading,
        .scan-viz-error {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 100vw;
          height: 100vh;
          background: #0a0a0f;
          color: #00ffff;
          font-family: 'Courier New', monospace;
        }
        
        .loading-content,
        .error-content {
          text-align: center;
        }
        
        .loading-spinner {
          width: 40px;
          height: 40px;
          border: 2px solid rgba(0, 255, 255, 0.3);
          border-top: 2px solid #00ffff;
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin: 0 auto 16px;
        }
        
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        
        .error-button {
          background: rgba(0, 255, 255, 0.2);
          border: 1px solid #00ffff;
          color: #00ffff;
          padding: 8px 16px;
          margin-top: 16px;
          cursor: pointer;
          font-family: 'Courier New', monospace;
        }
        
        .error-button:hover {
          background: rgba(0, 255, 255, 0.4);
        }
      `}</style>
    </div>
  );
};