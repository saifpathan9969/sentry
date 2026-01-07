import { useEffect, useState, useRef } from 'react';
import { Box, Paper, Typography } from '@mui/material';

interface ScanTerminalProps {
  scanId: string;
  status: string;
  target: string;
}

export const ScanTerminal: React.FC<ScanTerminalProps> = ({ scanId, status, target }) => {
  const [logs, setLogs] = useState<string[]>([]);
  const terminalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Initialize with scan start message
    const startTime = new Date().toLocaleTimeString();
    setLogs([
      `[${startTime}] ================================================================================`,
      `[${startTime}] AI PENETRATION TESTING BRAIN - LIVE SCAN OUTPUT`,
      `[${startTime}] ================================================================================`,
      `[${startTime}] `,
      `[${startTime}] 🎯 Target: ${target}`,
      `[${startTime}] 📊 Scan ID: ${scanId}`,
      `[${startTime}] 🚀 Initializing security scan...`,
      `[${startTime}] `,
    ]);
  }, [scanId, target]);

  useEffect(() => {
    // Simulate scan progress based on status
    const currentTime = new Date().toLocaleTimeString();
    
    if (status === 'queued') {
      setLogs(prev => [...prev, `[${currentTime}] ⏳ Scan queued, waiting for available scanner...`]);
    } else if (status === 'running') {
      // Add progressive scan messages
      const messages = [
        `[${currentTime}] ✅ Scanner initialized`,
        `[${currentTime}] 🔍 Phase 1: Reconnaissance`,
        `[${currentTime}]    - Analyzing target architecture...`,
        `[${currentTime}]    - Detecting web technologies...`,
        `[${currentTime}]    - Mapping attack surface...`,
        `[${currentTime}] `,
        `[${currentTime}] 🔍 Phase 2: Vulnerability Detection`,
        `[${currentTime}]    - Testing for SQL injection...`,
        `[${currentTime}]    - Checking XSS vulnerabilities...`,
        `[${currentTime}]    - Analyzing authentication mechanisms...`,
        `[${currentTime}]    - Testing for CSRF protection...`,
        `[${currentTime}]    - Checking security headers...`,
        `[${currentTime}] `,
        `[${currentTime}] 🔍 Phase 3: Deep Analysis`,
        `[${currentTime}]    - Running AI-powered threat detection...`,
        `[${currentTime}]    - Analyzing business logic flaws...`,
        `[${currentTime}]    - Testing API endpoints...`,
        `[${currentTime}] `,
        `[${currentTime}] 📊 Scan in progress... Please wait`,
      ];
      
      // Add messages progressively
      let index = 0;
      const interval = setInterval(() => {
        if (index < messages.length) {
          setLogs(prev => [...prev, messages[index]]);
          index++;
        } else {
          clearInterval(interval);
        }
      }, 800);
      
      return () => clearInterval(interval);
    } else if (status === 'completed') {
      setLogs(prev => [
        ...prev,
        `[${currentTime}] `,
        `[${currentTime}] ✅ Scan completed successfully!`,
        `[${currentTime}] 📊 Generating detailed report...`,
        `[${currentTime}] 🧠 Activating Neural Brain visualization...`,
        `[${currentTime}] `,
        `[${currentTime}] ================================================================================`,
        `[${currentTime}] View detailed results below`,
        `[${currentTime}] ================================================================================`,
      ]);
    } else if (status === 'failed') {
      setLogs(prev => [
        ...prev,
        `[${currentTime}] `,
        `[${currentTime}] ❌ Scan failed`,
        `[${currentTime}] Please check the error details and try again`,
      ]);
    }
  }, [status]);

  // Auto-scroll to bottom
  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <Paper
      ref={terminalRef}
      sx={{
        bgcolor: '#0a0a0a',
        p: 2,
        fontFamily: '"Courier New", Courier, monospace',
        fontSize: '0.875rem',
        maxHeight: 500,
        overflow: 'auto',
        border: '1px solid #00ff00',
        boxShadow: '0 0 20px rgba(0, 255, 0, 0.3)',
        '&::-webkit-scrollbar': {
          width: '8px',
        },
        '&::-webkit-scrollbar-track': {
          background: '#1a1a1a',
        },
        '&::-webkit-scrollbar-thumb': {
          background: '#00ff00',
          borderRadius: '4px',
        },
      }}
    >
      {logs.map((log, i) => (
        <Typography
          key={i}
          sx={{
            color: log.includes('❌') ? '#ff4444' :
                   log.includes('✅') ? '#00ff00' :
                   log.includes('⏳') ? '#ffaa00' :
                   log.includes('🔍') ? '#00aaff' :
                   log.includes('📊') ? '#aa00ff' :
                   log.includes('🎯') || log.includes('🚀') ? '#00ffff' :
                   '#00ff00',
            fontSize: '0.875rem',
            lineHeight: 1.6,
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word',
          }}
        >
          {log}
        </Typography>
      ))}
      {status === 'running' && (
        <Typography
          sx={{
            color: '#00ff00',
            fontSize: '0.875rem',
            animation: 'blink 1s infinite',
            '@keyframes blink': {
              '0%, 49%': { opacity: 1 },
              '50%, 100%': { opacity: 0 },
            },
          }}
        >
          ▊
        </Typography>
      )}
    </Paper>
  );
};
