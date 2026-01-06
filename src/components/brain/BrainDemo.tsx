/**
 * Brain Demo Component - Compact version for dashboard
 * Shows a dynamic preview of the AI brain for dashboard
 */
import React, { useState, useEffect, useRef } from 'react';
import { Box, Button, Typography, Card, CardContent } from '@mui/material';
import { Psychology as BrainIcon } from '@mui/icons-material';

interface BrainDemoProps {
  onLaunchFullscreen?: () => void;
}

export const BrainDemo: React.FC<BrainDemoProps> = ({ onLaunchFullscreen }) => {
  const [isActive, setIsActive] = useState(false);
  const [demoVulns, setDemoVulns] = useState<Array<{
    severity: 'low' | 'medium' | 'high' | 'critical';
    type: string;
  }>>([]);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>();

  // Simple 2D brain visualization
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size
    const resizeCanvas = () => {
      const rect = canvas.getBoundingClientRect();
      canvas.width = rect.width * window.devicePixelRatio;
      canvas.height = rect.height * window.devicePixelRatio;
      ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    };

    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Neural network data with brain regions
    const neurons: Array<{
      x: number;
      y: number;
      size: number;
      pulse: number;
      connections: number[];
      region: string;
      color: [number, number, number];
    }> = [];

    const pulses: Array<{
      from: number;
      to: number;
      progress: number;
      speed: number;
      active: boolean;
      type: 'normal' | 'alert' | 'background';
    }> = [];

    // Generate neurons in brain-like regions
    const centerX = canvas.clientWidth / 2;
    const centerY = canvas.clientHeight / 2;
    // const neuronCount = 35; // Removed unused variable
    
    const brainRegions = [
      { name: 'frontal', center: [0.3, -0.2], color: [0, 255, 255], count: 8 },
      { name: 'parietal', center: [-0.2, -0.3], color: [0, 170, 255], count: 7 },
      { name: 'temporal', center: [0.4, 0.2], color: [0, 136, 255], count: 6 },
      { name: 'occipital', center: [-0.4, 0.1], color: [0, 102, 255], count: 5 },
      { name: 'cerebellum', center: [0, 0.4], color: [68, 0, 255], count: 4 },
      { name: 'brainstem', center: [0, 0.1], color: [102, 0, 255], count: 3 },
      { name: 'hippocampus', center: [0.15, 0.05], color: [136, 0, 255], count: 2 }
    ];

    brainRegions.forEach((region) => {
      for (let i = 0; i < region.count; i++) {
        const angle = (i / region.count) * Math.PI * 2 + Math.random() * 0.5;
        const regionOffset = 20 + Math.random() * 15;
        
        neurons.push({
          x: centerX + region.center[0] * 80 + Math.cos(angle) * regionOffset,
          y: centerY + region.center[1] * 60 + Math.sin(angle) * regionOffset,
          size: 2 + Math.random() * 2,
          pulse: Math.random() * Math.PI * 2,
          connections: [],
          region: region.name,
          color: region.color as [number, number, number]
        });
      }
    });

    // Create intelligent connections
    neurons.forEach((neuron) => {
      // Intra-region connections (same region)
      const sameRegionNeurons = neurons
        .map((n, idx) => ({ index: idx, neuron: n, distance: Math.sqrt((neuron.x - n.x) ** 2 + (neuron.y - n.y) ** 2) }))
        .filter(n => n.neuron.region === neuron.region && n.distance > 0 && n.distance < 60)
        .sort((a, b) => a.distance - b.distance)
        .slice(0, 2);

      // Inter-region connections (different regions)
      const otherRegionNeurons = neurons
        .map((n, idx) => ({ index: idx, neuron: n, distance: Math.sqrt((neuron.x - n.x) ** 2 + (neuron.y - n.y) ** 2) }))
        .filter(n => n.neuron.region !== neuron.region && n.distance < 100)
        .sort((a, b) => a.distance - b.distance)
        .slice(0, 1);

      neuron.connections = [...sameRegionNeurons.map(n => n.index), ...otherRegionNeurons.map(n => n.index)];
    });

    let time = 0;

    const animate = () => {
      time += 0.02;
      
      // Clear canvas
      ctx.fillStyle = 'rgba(0, 5, 16, 0.1)';
      ctx.fillRect(0, 0, canvas.clientWidth, canvas.clientHeight);

      const intensity = isActive ? 1.5 : 0.5;
      const alertMode = demoVulns.length > 0;

      // Draw connections with regional colors
      ctx.lineWidth = 1;
      ctx.beginPath();

      neurons.forEach((neuron) => {
        neuron.connections.forEach(targetIndex => {
          const target = neurons[targetIndex];
          if (target) {
            const sameRegion = neuron.region === target.region;
            const alpha = sameRegion ? 0.4 : 0.2;
            const baseAlpha = alpha + Math.sin(time * 2) * 0.1;
            
            if (alertMode) {
              ctx.strokeStyle = `rgba(255, 68, 68, ${baseAlpha * intensity})`;
            } else if (sameRegion) {
              ctx.strokeStyle = `rgba(0, 255, 255, ${baseAlpha * intensity})`;
            } else {
              ctx.strokeStyle = `rgba(0, 170, 255, ${baseAlpha * intensity * 0.7})`;
            }
            
            ctx.globalAlpha = baseAlpha * intensity;
            ctx.moveTo(neuron.x, neuron.y);
            ctx.lineTo(target.x, target.y);
          }
        });
      });

      ctx.stroke();
      ctx.globalAlpha = 1;

      // Spawn intelligent pulses
      if (isActive && Math.random() < 0.08) {
        const fromIndex = Math.floor(Math.random() * neurons.length);
        const fromNeuron = neurons[fromIndex];
        if (fromNeuron.connections.length > 0) {
          const toIndex = fromNeuron.connections[Math.floor(Math.random() * fromNeuron.connections.length)];
          
          // Determine pulse type
          let pulseType: 'normal' | 'alert' | 'background' = 'normal';
          if (alertMode && Math.random() < 0.4) {
            pulseType = 'alert';
          } else if (Math.random() < 0.3) {
            pulseType = 'background';
          }
          
          pulses.push({
            from: fromIndex,
            to: toIndex,
            progress: 0,
            speed: 0.015 + Math.random() * 0.02,
            active: true,
            type: pulseType
          });
        }
      }

      // Update and draw pulses with types
      pulses.forEach((pulse) => {
        if (!pulse.active) return;

        pulse.progress += pulse.speed;
        
        if (pulse.progress >= 1) {
          pulse.active = false;
          return;
        }

        const fromNeuron = neurons[pulse.from];
        const toNeuron = neurons[pulse.to];
        
        if (fromNeuron && toNeuron) {
          const x = fromNeuron.x + (toNeuron.x - fromNeuron.x) * pulse.progress;
          const y = fromNeuron.y + (toNeuron.y - fromNeuron.y) * pulse.progress;
          
          const baseSize = Math.sin(pulse.progress * Math.PI) * 3;
          const alpha = Math.sin(pulse.progress * Math.PI);
          
          // Pulse color and size based on type
          let color: [number, number, number];
          let size = baseSize;
          
          switch (pulse.type) {
            case 'alert':
              color = [255, 68, 68];
              size *= 1.5;
              break;
            case 'background':
              color = [68, 255, 68];
              size *= 0.7;
              break;
            default:
              color = alertMode ? [255, 68, 68] : [0, 255, 255];
          }
          
          ctx.fillStyle = `rgba(${color[0]}, ${color[1]}, ${color[2]}, ${alpha})`;
          ctx.beginPath();
          ctx.arc(x, y, size, 0, Math.PI * 2);
          ctx.fill();
          
          // Enhanced glow effect
          ctx.shadowBlur = 15;
          ctx.shadowColor = `rgb(${color[0]}, ${color[1]}, ${color[2]})`;
          ctx.beginPath();
          ctx.arc(x, y, size * 0.5, 0, Math.PI * 2);
          ctx.fill();
          ctx.shadowBlur = 0;
        }
      });

      // Clean up inactive pulses
      pulses.splice(0, pulses.length, ...pulses.filter(p => p.active));

      // Draw neurons with regional colors
      neurons.forEach((neuron) => {
        neuron.pulse += 0.05;
        const pulseSize = 1 + Math.sin(neuron.pulse) * 0.3;
        const size = neuron.size * pulseSize * intensity;
        
        const baseColor = alertMode ? [255, 68, 68] : neuron.color;
        const alpha = 0.6 + Math.sin(time * 2) * 0.2;
        
        // Regional color variation
        const colorVariation = Math.sin(time + neuron.pulse) * 0.1;
        const finalColor = [
          Math.max(0, Math.min(255, baseColor[0] + colorVariation * 50)),
          Math.max(0, Math.min(255, baseColor[1] + colorVariation * 30)),
          Math.max(0, Math.min(255, baseColor[2] + colorVariation * 20))
        ];
        
        // Enhanced glow with regional colors
        ctx.shadowBlur = 20;
        ctx.shadowColor = `rgb(${finalColor[0]}, ${finalColor[1]}, ${finalColor[2]})`;
        ctx.fillStyle = `rgba(${finalColor[0]}, ${finalColor[1]}, ${finalColor[2]}, ${alpha})`;
        ctx.beginPath();
        ctx.arc(neuron.x, neuron.y, size, 0, Math.PI * 2);
        ctx.fill();
        
        // Core with brighter color
        ctx.shadowBlur = 8;
        ctx.fillStyle = `rgba(${finalColor[0]}, ${finalColor[1]}, ${finalColor[2]}, 1)`;
        ctx.beginPath();
        ctx.arc(neuron.x, neuron.y, size * 0.6, 0, Math.PI * 2);
        ctx.fill();
        ctx.shadowBlur = 0;
      });

      animationRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      window.removeEventListener('resize', resizeCanvas);
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [isActive, demoVulns]);

  const startDemo = () => {
    setIsActive(true);
    setDemoVulns([]);
    
    // Simulate vulnerability discoveries
    setTimeout(() => {
      setDemoVulns([{ severity: 'medium', type: 'XSS Vulnerability' }]);
    }, 2000);
    
    setTimeout(() => {
      setDemoVulns(prev => [...prev, { severity: 'high', type: 'SQL Injection' }]);
    }, 4000);
    
    setTimeout(() => {
      setDemoVulns(prev => [...prev, { severity: 'critical', type: 'RCE Vulnerability' }]);
    }, 6000);
    
    // Stop demo after 10 seconds
    setTimeout(() => {
      setIsActive(false);
      setDemoVulns([]);
    }, 10000);
  };

  return (
    <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardContent sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <BrainIcon sx={{ mr: 1, color: '#00ffff' }} />
          <Typography variant="h6">AI Neural Interface</Typography>
        </Box>
        
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Experience the Jarvis-style AI brain visualization during security scans.
        </Typography>
        
        {/* Dynamic Brain Canvas */}
        <Box 
          sx={{ 
            flex: 1, 
            minHeight: 200,
            position: 'relative',
            borderRadius: 1,
            overflow: 'hidden',
            background: 'radial-gradient(circle at center, #001122 0%, #000510 100%)',
            border: '1px solid rgba(0, 255, 255, 0.2)'
          }}
        >
          <canvas
            ref={canvasRef}
            style={{
              width: '100%',
              height: '100%',
              display: 'block'
            }}
          />
          
          {/* Status overlay */}
          <Box
            sx={{
              position: 'absolute',
              top: 8,
              left: 8,
              display: 'flex',
              alignItems: 'center',
              gap: 1,
              color: isActive ? '#ff4444' : '#00ffff',
              fontFamily: 'monospace',
              fontSize: '10px',
              background: 'rgba(0, 0, 0, 0.7)',
              padding: '4px 8px',
              borderRadius: '4px',
              border: `1px solid ${isActive ? 'rgba(255, 68, 68, 0.3)' : 'rgba(0, 255, 255, 0.3)'}`
            }}
          >
            <Box
              sx={{
                width: 6,
                height: 6,
                borderRadius: '50%',
                background: isActive ? '#ff4444' : '#00ffff',
                boxShadow: `0 0 8px ${isActive ? '#ff4444' : '#00ffff'}`,
                animation: isActive ? 'pulse 1s ease-in-out infinite' : 'none'
              }}
            />
            <span>{isActive ? 'SCANNING' : 'READY'}</span>
          </Box>
          
          {demoVulns.length > 0 && (
            <Box
              sx={{
                position: 'absolute',
                bottom: 8,
                right: 8,
                color: '#ff4444',
                fontFamily: 'monospace',
                fontSize: '10px',
                background: 'rgba(0, 0, 0, 0.7)',
                padding: '4px 8px',
                borderRadius: '4px',
                border: '1px solid rgba(255, 68, 68, 0.3)',
                textAlign: 'center'
              }}
            >
              <div style={{ fontSize: '14px', fontWeight: 'bold' }}>{demoVulns.length}</div>
              <div>THREATS</div>
            </Box>
          )}
        </Box>
        
        {/* Controls */}
        <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            size="small"
            onClick={startDemo}
            disabled={isActive}
            sx={{ flex: 1 }}
          >
            {isActive ? 'Demo Running...' : 'Start Demo'}
          </Button>
          
          {onLaunchFullscreen && (
            <Button
              variant="contained"
              size="small"
              onClick={onLaunchFullscreen}
              sx={{ 
                flex: 1,
                background: 'linear-gradient(45deg, #00ffff 30%, #0088ff 90%)',
                '&:hover': {
                  background: 'linear-gradient(45deg, #00cccc 30%, #0066cc 90%)',
                }
              }}
            >
              Full Interface
            </Button>
          )}
        </Box>
        
        {/* Status */}
        {isActive && (
          <Typography 
            variant="caption" 
            sx={{ 
              mt: 1, 
              textAlign: 'center',
              color: demoVulns.length > 0 ? '#ff4444' : '#00ffff',
              fontFamily: 'monospace'
            }}
          >
            Neural activity detected • {demoVulns.length} threats found
          </Typography>
        )}
      </CardContent>
      
      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.7; transform: scale(1.2); }
        }
      `}</style>
    </Card>
  );
};