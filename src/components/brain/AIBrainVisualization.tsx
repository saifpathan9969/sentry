/**
 * AI Brain Visualization Component
 * React wrapper for the Three.js brain renderer with proper Jarvis-style effects
 */
import React, { useEffect, useRef, useState } from 'react';

interface AIBrainVisualizationProps {
  isScanning?: boolean;
  scanProgress?: number;
  vulnerabilities?: Array<{
    severity: 'low' | 'medium' | 'high' | 'critical';
    type: string;
  }>;
  onBrainClick?: () => void;
  className?: string;
}

export const AIBrainVisualization: React.FC<AIBrainVisualizationProps> = ({
  isScanning = false,
  scanProgress = 0,
  vulnerabilities = [],
  onBrainClick,
  className = ''
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [brainRenderer, setBrainRenderer] = useState<any>(null);

  // Initialize brain renderer
  useEffect(() => {
    if (!containerRef.current) return;

    const initBrain = async () => {
      try {
        console.log('🧠 Initializing Jarvis AI Brain...');
        
        // Import Three.js modules
        const THREE = await import('three');
        const { OrbitControls } = await import('three-stdlib');
        
        // Create scene, camera, renderer
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x000510);
        scene.fog = new THREE.Fog(0x000510, 10, 50);

        const camera = new THREE.PerspectiveCamera(
          75,
          containerRef.current!.clientWidth / containerRef.current!.clientHeight,
          0.1,
          1000
        );
        camera.position.set(0, 0, 15);

        const renderer = new THREE.WebGLRenderer({ 
          antialias: true, 
          alpha: true,
          powerPreference: 'high-performance'
        });
        renderer.setSize(containerRef.current!.clientWidth, containerRef.current!.clientHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.outputColorSpace = THREE.SRGBColorSpace;
        containerRef.current!.appendChild(renderer.domElement);

        // Add orbit controls
        const controls = new OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.minDistance = 5;
        controls.maxDistance = 30;
        controls.autoRotate = true;
        controls.autoRotateSpeed = 0.5;

        // Create neural network
        const brainGroup = new THREE.Group();
        scene.add(brainGroup);

        // Generate neurons in realistic brain structure
        const neurons: any[] = [];
        const connections: any[] = [];
        const pulses: any[] = [];
        const neuronClusters: any[] = [];
        
        // Create brain regions (clusters)
        const brainRegions = [
          { name: 'frontal', center: [2, 1, 1], size: 1.2, neurons: 80, color: 0x00ffff },
          { name: 'parietal', center: [-1, 2, 0], size: 1.0, neurons: 70, color: 0x00aaff },
          { name: 'temporal', center: [1.5, -1, 2], size: 0.8, neurons: 60, color: 0x0088ff },
          { name: 'occipital', center: [-2, 0, -1], size: 0.9, neurons: 50, color: 0x0066ff },
          { name: 'cerebellum', center: [0, -2, -1.5], size: 0.7, neurons: 40, color: 0x4400ff },
          { name: 'brainstem', center: [0, -1.5, 0], size: 0.5, neurons: 30, color: 0x6600ff },
          { name: 'hippocampus', center: [0.8, -0.5, 1.2], size: 0.4, neurons: 25, color: 0x8800ff },
          { name: 'amygdala', center: [-0.8, -0.5, 1.2], size: 0.3, neurons: 20, color: 0xaa00ff },
        ];

        // Create neurons in each brain region
        brainRegions.forEach((region, regionIndex) => {
          const cluster = new THREE.Group();
          cluster.name = region.name;
          
          for (let i = 0; i < region.neurons; i++) {
            // Create neuron with region-specific properties
            const neuronGeometry = new THREE.SphereGeometry(0.03 + Math.random() * 0.02, 8, 6);
            const neuronMaterial = new THREE.MeshBasicMaterial({
              color: region.color,
              transparent: true,
              opacity: 0.8 + Math.random() * 0.2
            });
            
            const neuron = new THREE.Mesh(neuronGeometry, neuronMaterial);
            
            // Position within region using gaussian distribution
            const gaussianRandom = () => {
              let u = 0, v = 0;
              while(u === 0) u = Math.random();
              while(v === 0) v = Math.random();
              return Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
            };
            
            neuron.position.x = region.center[0] + gaussianRandom() * region.size * 0.5;
            neuron.position.y = region.center[1] + gaussianRandom() * region.size * 0.5;
            neuron.position.z = region.center[2] + gaussianRandom() * region.size * 0.5;
            
            // Add dendrite-like extensions
            const dendriteCount = 3 + Math.floor(Math.random() * 4);
            for (let d = 0; d < dendriteCount; d++) {
              const dendriteGeometry = new THREE.CylinderGeometry(0.005, 0.001, 0.1 + Math.random() * 0.1);
              const dendriteMaterial = new THREE.MeshBasicMaterial({
                color: region.color,
                transparent: true,
                opacity: 0.4
              });
              const dendrite = new THREE.Mesh(dendriteGeometry, dendriteMaterial);
              
              dendrite.position.set(
                (Math.random() - 0.5) * 0.1,
                (Math.random() - 0.5) * 0.1,
                (Math.random() - 0.5) * 0.1
              );
              dendrite.rotation.set(
                Math.random() * Math.PI,
                Math.random() * Math.PI,
                Math.random() * Math.PI
              );
              
              neuron.add(dendrite);
            }
            
            // Add glow effect with region color
            const glowGeometry = new THREE.SphereGeometry(0.08, 8, 6);
            const glowMaterial = new THREE.MeshBasicMaterial({
              color: region.color,
              transparent: true,
              opacity: 0.2,
              blending: THREE.AdditiveBlending
            });
            const glow = new THREE.Mesh(glowGeometry, glowMaterial);
            neuron.add(glow);
            
            // Store region info
            neuron.userData = {
              region: region.name,
              regionIndex: regionIndex,
              baseColor: region.color,
              activationLevel: Math.random()
            };
            
            neurons.push(neuron);
            cluster.add(neuron);
          }
          
          neuronClusters.push(cluster);
          brainGroup.add(cluster);
        });

        // Create intelligent connections between neurons
        const connectionMaterial = new THREE.LineBasicMaterial({
          color: 0x00aaaa,
          transparent: true,
          opacity: 0.3,
          blending: THREE.AdditiveBlending
        });

        // Inter-region connections (long-range)
        brainRegions.forEach((_, i) => {
          brainRegions.forEach((_, j) => {
            if (i !== j) {
              const region1Neurons = neurons.filter(n => n.userData.regionIndex === i);
              const region2Neurons = neurons.filter(n => n.userData.regionIndex === j);
              
              // Create some connections between regions
              const connectionCount = Math.floor(Math.random() * 5) + 2;
              for (let c = 0; c < connectionCount; c++) {
                const neuron1 = region1Neurons[Math.floor(Math.random() * region1Neurons.length)];
                const neuron2 = region2Neurons[Math.floor(Math.random() * region2Neurons.length)];
                
                if (neuron1 && neuron2) {
                  // Create curved connection using QuadraticBezierCurve3
                  const start = neuron1.position.clone();
                  const end = neuron2.position.clone();
                  const mid = start.clone().lerp(end, 0.5);
                  mid.y += (Math.random() - 0.5) * 2; // Add some curve
                  
                  const curve = new (THREE as any).QuadraticBezierCurve3(start, mid, end);
                  const points = curve.getPoints(20);
                  const geometry = new (THREE as any).BufferGeometry().setFromPoints(points);
                  
                  const connectionMat = connectionMaterial.clone();
                  connectionMat.opacity = 0.2 + Math.random() * 0.2;
                  
                  const line = new (THREE as any).Line(geometry, connectionMat);
                  line.userData = {
                    type: 'inter-region',
                    from: neuron1,
                    to: neuron2,
                    curve: curve,
                    activity: Math.random()
                  };
                  
                  connections.push(line);
                  brainGroup.add(line);
                }
              }
            }
          });
        });

        // Intra-region connections (short-range)
        neurons.forEach((neuron1) => {
          const sameRegionNeurons = neurons.filter(n => 
            n.userData.regionIndex === neuron1.userData.regionIndex && n !== neuron1
          );
          
          // Connect to nearby neurons in same region
          const nearbyNeurons = sameRegionNeurons
            .map(n => ({ neuron: n, distance: neuron1.position.distanceTo(n.position) }))
            .filter(n => n.distance < 0.8)
            .sort((a, b) => a.distance - b.distance)
            .slice(0, 3 + Math.floor(Math.random() * 3));

          nearbyNeurons.forEach(({ neuron: neuron2 }) => {
            const points = [neuron1.position.clone(), neuron2.position.clone()];
            const geometry = new (THREE as any).BufferGeometry().setFromPoints(points);
            
            const connectionMat = connectionMaterial.clone();
            connectionMat.opacity = 0.4 + Math.random() * 0.3;
            
            const line = new (THREE as any).Line(geometry, connectionMat);
            line.userData = {
              type: 'intra-region',
              from: neuron1,
              to: neuron2,
              activity: Math.random()
            };
            
            connections.push(line);
            brainGroup.add(line);
          });
        });

        // Create advanced pulse system with different types
        const pulseTypes = [
          { 
            geometry: new (THREE as any).SphereGeometry(0.02, 6, 4),
            material: new (THREE as any).MeshBasicMaterial({
              color: 0x00ffff,
              transparent: true,
              opacity: 1,
              blending: (THREE as any).AdditiveBlending
            }),
            speed: 0.02,
            name: 'normal'
          },
          {
            geometry: new (THREE as any).SphereGeometry(0.03, 8, 6),
            material: new (THREE as any).MeshBasicMaterial({
              color: 0xff4444,
              transparent: true,
              opacity: 1,
              blending: (THREE as any).AdditiveBlending
            }),
            speed: 0.04,
            name: 'alert'
          },
          {
            geometry: new (THREE as any).SphereGeometry(0.015, 4, 4),
            material: new (THREE as any).MeshBasicMaterial({
              color: 0x44ff44,
              transparent: true,
              opacity: 1,
              blending: (THREE as any).AdditiveBlending
            }),
            speed: 0.01,
            name: 'background'
          }
        ];

        for (let i = 0; i < 100; i++) {
          const pulseType = pulseTypes[Math.floor(Math.random() * pulseTypes.length)];
          const pulse = new (THREE as any).Mesh(pulseType.geometry, pulseType.material.clone());
          pulse.visible = false;
          pulse.userData = {
            type: pulseType.name,
            speed: pulseType.speed + (Math.random() - 0.5) * 0.01
          };
          pulses.push(pulse);
          brainGroup.add(pulse);
        }

        // Animation state
        let time = 0;
        let brainActivity = 0.5;
        let activePulses: Array<{
          mesh: any;
          connection: any;
          progress: number;
          speed: number;
          type: string;
        }> = [];

        // Regional activation patterns
        const regionActivation = brainRegions.map(() => ({
          level: Math.random(),
          phase: Math.random() * Math.PI * 2,
          frequency: 0.5 + Math.random() * 2
        }));

        // Animation loop
        const animate = () => {
          requestAnimationFrame(animate);
          time += 0.016;

          // Update controls
          controls.update();

          // Update brain activity based on scan state
          const targetActivity = isScanning ? 1.5 : 0.3;
          brainActivity += (targetActivity - brainActivity) * 0.02;

          // Update regional activation
          regionActivation.forEach((region, i) => {
            region.level = 0.3 + 0.7 * Math.sin(time * region.frequency + region.phase);
            if (isScanning) {
              region.level *= 1.5 + 0.5 * Math.sin(time * 3 + i);
            }
          });

          // Animate neurons with regional patterns
          neurons.forEach((neuron, i) => {
            const regionIndex = neuron.userData.regionIndex;
            const regionAct = regionActivation[regionIndex];
            
            // Base pulsing with regional modulation
            const basePulse = Math.sin(time * 2 + i * 0.1) * 0.3 + 0.7;
            const regionalPulse = regionAct.level;
            const finalPulse = basePulse * regionalPulse * brainActivity;
            
            neuron.scale.setScalar(0.8 + finalPulse * 0.4);
            
            // Color animation with regional colors
            const material = neuron.material as any;
            const baseColor = new (THREE as any).Color(neuron.userData.baseColor);
            
            if (isScanning) {
              // Scanning mode: dynamic color shifts
              const hueShift = Math.sin(time * 1.5 + i * 0.05) * 0.1;
              baseColor.offsetHSL(hueShift, 0, finalPulse * 0.3);
              
              if (vulnerabilities.length > 0) {
                // Alert mode: red tinting
                const alertIntensity = Math.sin(time * 8) * 0.5 + 0.5;
                baseColor.lerp(new (THREE as any).Color(0xff4444), alertIntensity * 0.3);
              }
            }
            
            material.color.copy(baseColor);
            material.opacity = 0.6 + finalPulse * 0.4;
            
            // Update glow
            const glow = neuron.children[neuron.children.length - 1] as any;
            if (glow) {
              const glowMaterial = glow.material as any;
              glowMaterial.opacity = 0.1 + finalPulse * 0.3;
              glowMaterial.color.copy(baseColor);
            }
          });

          // Animate connections with activity waves
          connections.forEach((connection) => {
            const material = connection.material as any;
            const connectionUserData = connection.userData;
            
            // Base activity level
            let activityLevel = connectionUserData.activity;
            
            // Regional influence
            if (connectionUserData.from && connectionUserData.to) {
              const fromRegion = regionActivation[connectionUserData.from.userData.regionIndex];
              const toRegion = regionActivation[connectionUserData.to.userData.regionIndex];
              activityLevel *= (fromRegion.level + toRegion.level) * 0.5;
            }
            
            // Scanning boost
            if (isScanning) {
              activityLevel *= 1.5 + 0.5 * Math.sin(time * 2);
            }
            
            // Vulnerability alert
            if (vulnerabilities.length > 0) {
              const alertWave = Math.sin(time * 6) * 0.5 + 0.5;
              material.color.setHex(0xff4444);
              activityLevel *= 1 + alertWave;
            } else {
              // Normal colors based on connection type
              if (connectionUserData.type === 'inter-region') {
                material.color.setHex(0x00aaff);
              } else {
                material.color.setHex(0x00ffaa);
              }
            }
            
            material.opacity = Math.max(0.1, Math.min(0.8, activityLevel * 0.6));
          });

          // Spawn intelligent pulses
          if (isScanning && Math.random() < 0.15) {
            const availablePulse = pulses.find(p => !p.visible);
            if (availablePulse && connections.length > 0) {
              // Choose connection based on activity level
              const activeConnections = connections.filter(c => {
                const material = c.material as any;
                return material.opacity > 0.3;
              });
              
              const connection = activeConnections.length > 0 
                ? activeConnections[Math.floor(Math.random() * activeConnections.length)]
                : connections[Math.floor(Math.random() * connections.length)];
              
              // Determine pulse type based on scan state
              let pulseType = 'normal';
              if (vulnerabilities.length > 0) {
                pulseType = Math.random() < 0.4 ? 'alert' : 'normal';
              } else if (Math.random() < 0.3) {
                pulseType = 'background';
              }
              
              availablePulse.userData.type = pulseType;
              availablePulse.visible = true;
              
              // Set pulse color based on type
              const pulseMaterial = availablePulse.material as any;
              switch (pulseType) {
                case 'alert':
                  pulseMaterial.color.setHex(0xff4444);
                  break;
                case 'background':
                  pulseMaterial.color.setHex(0x44ff44);
                  break;
                default:
                  pulseMaterial.color.setHex(0x00ffff);
              }
              
              activePulses.push({
                mesh: availablePulse,
                connection: connection,
                progress: 0,
                speed: availablePulse.userData.speed,
                type: pulseType
              });
            }
          }

          // Update active pulses with intelligent movement
          activePulses = activePulses.filter(pulse => {
            pulse.progress += pulse.speed;
            
            if (pulse.progress >= 1) {
              pulse.mesh.visible = false;
              return false;
            }
            
            // Move pulse along connection
            const connection = pulse.connection;
            const userData = connection.userData;
            
            if (userData.curve) {
              // Curved connection (inter-region)
              const point = userData.curve.getPoint(pulse.progress);
              pulse.mesh.position.copy(point);
            } else {
              // Straight connection (intra-region)
              const geometry = connection.geometry as any;
              const positions = geometry.attributes.position.array as Float32Array;
              const startPos = new (THREE as any).Vector3(positions[0], positions[1], positions[2]);
              const endPos = new (THREE as any).Vector3(positions[3], positions[4], positions[5]);
              pulse.mesh.position.lerpVectors(startPos, endPos, pulse.progress);
            }
            
            // Dynamic scaling and opacity
            const scale = Math.sin(pulse.progress * Math.PI) * 2;
            pulse.mesh.scale.setScalar(scale);
            
            const material = pulse.mesh.material as any;
            material.opacity = Math.sin(pulse.progress * Math.PI) * 0.8;
            
            // Special effects for alert pulses
            if (pulse.type === 'alert') {
              const alertScale = 1 + Math.sin(time * 10) * 0.3;
              pulse.mesh.scale.multiplyScalar(alertScale);
            }
            
            return true;
          });

          // Enhanced vulnerability alert effects
          if (vulnerabilities.length > 0) {
            const alertIntensity = Math.sin(time * 8) * 0.5 + 0.5;
            const criticalCount = vulnerabilities.filter(v => v.severity === 'critical').length;
            
            // Scene-wide alert effects
            if (criticalCount > 0) {
              scene.fog!.color.setHex(0x400510 + Math.floor(alertIntensity * 0x200000));
              
              // Add screen shake effect to camera
              camera.position.x += (Math.random() - 0.5) * 0.02;
              camera.position.y += (Math.random() - 0.5) * 0.02;
            } else {
              scene.fog!.color.setHex(0x200510 + Math.floor(alertIntensity * 0x100000));
            }
            
            // Regional alert patterns
            regionActivation.forEach((region) => {
              if (Math.random() < 0.1) {
                region.level = Math.max(region.level, 0.8 + alertIntensity * 0.2);
              }
            });
          } else {
            scene.fog!.color.setHex(0x000510);
          }

          renderer.render(scene, camera);
        };

        // Handle resize
        const handleResize = () => {
          if (!containerRef.current) return;
          
          camera.aspect = containerRef.current.clientWidth / containerRef.current.clientHeight;
          camera.updateProjectionMatrix();
          renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight);
        };

        window.addEventListener('resize', handleResize);

        // Start animation
        animate();

        // Store renderer for cleanup
        const brainSystem = {
          scene,
          camera,
          renderer,
          controls,
          neurons,
          connections,
          pulses,
          dispose: () => {
            window.removeEventListener('resize', handleResize);
            renderer.dispose();
            controls.dispose();
            if (containerRef.current && renderer.domElement.parentNode) {
              containerRef.current.removeChild(renderer.domElement);
            }
          }
        };

        setBrainRenderer(brainSystem);
        setIsLoaded(true);
        console.log('✅ Jarvis AI Brain loaded successfully');

      } catch (err) {
        console.error('❌ Failed to initialize brain:', err);
        setError('Failed to load 3D brain visualization');
      }
    };

    initBrain();

    return () => {
      if (brainRenderer) {
        brainRenderer.dispose();
      }
    };
  }, []);

  // Handle container click
  const handleContainerClick = () => {
    if (onBrainClick) {
      onBrainClick();
    }
  };

  if (error) {
    return (
      <div className={`brain-error ${className}`}>
        <div className="error-content">
          <h3>🧠 Neural Interface Offline</h3>
          <p>{error}</p>
          <p>WebGL support required for full experience</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`brain-container ${className}`}>
      <div
        ref={containerRef}
        className="brain-canvas"
        onClick={handleContainerClick}
        style={{
          width: '100%',
          height: '100%',
          cursor: 'pointer',
          position: 'relative'
        }}
      />
      
      {!isLoaded && (
        <div className="brain-loading">
          <div className="loading-content">
            <div className="loading-spinner"></div>
            <p>Initializing Neural Interface...</p>
          </div>
        </div>
      )}
      
      {isLoaded && (
        <div className="brain-overlay">
          <div className="brain-status">
            <div className={`status-dot ${isScanning ? 'active' : 'idle'}`}></div>
            <span className="status-text">
              {isScanning ? 'NEURAL SCAN ACTIVE' : 'NEURAL INTERFACE READY'}
            </span>
          </div>
          
          {isScanning && scanProgress > 0 && (
            <div className="scan-progress">
              <div className="progress-bar">
                <div 
                  className="progress-fill"
                  style={{ width: `${scanProgress * 100}%` }}
                ></div>
              </div>
              <span className="progress-text">
                {Math.round(scanProgress * 100)}%
              </span>
            </div>
          )}
          
          {vulnerabilities.length > 0 && (
            <div className="vulnerability-counter">
              <div className="vuln-count">
                {vulnerabilities.length}
              </div>
              <span className="vuln-label">THREATS DETECTED</span>
            </div>
          )}
          
          <div className="controls-hint">
            <span>MOUSE: Rotate • SCROLL: Zoom • DRAG: Pan</span>
          </div>
        </div>
      )}
      
      <style>{`
        .brain-container {
          position: relative;
          width: 100%;
          height: 100%;
          background: radial-gradient(circle at center, #001122 0%, #000000 100%);
          overflow: hidden;
        }
        
        .brain-canvas {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
        }
        
        .brain-loading {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          background: rgba(0, 0, 0, 0.9);
          z-index: 10;
        }
        
        .loading-content {
          text-align: center;
          color: #00ffff;
          font-family: 'Courier New', monospace;
        }
        
        .loading-spinner {
          width: 50px;
          height: 50px;
          border: 3px solid rgba(0, 255, 255, 0.3);
          border-top: 3px solid #00ffff;
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin: 0 auto 20px;
        }
        
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        
        .brain-overlay {
          position: absolute;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          pointer-events: none;
          z-index: 5;
        }
        
        .brain-status {
          position: absolute;
          top: 20px;
          left: 20px;
          display: flex;
          align-items: center;
          gap: 12px;
          color: #00ffff;
          font-family: 'Courier New', monospace;
          font-size: 14px;
          text-shadow: 0 0 10px rgba(0, 255, 255, 0.8);
          background: rgba(0, 0, 0, 0.5);
          padding: 8px 12px;
          border-radius: 4px;
          border: 1px solid rgba(0, 255, 255, 0.3);
        }
        
        .status-dot {
          width: 10px;
          height: 10px;
          border-radius: 50%;
          background: #00ffff;
          box-shadow: 0 0 15px rgba(0, 255, 255, 0.8);
        }
        
        .status-dot.active {
          animation: pulse 1s ease-in-out infinite;
          background: #ff4444;
          box-shadow: 0 0 15px rgba(255, 68, 68, 0.8);
        }
        
        @keyframes pulse {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.7; transform: scale(1.3); }
        }
        
        .scan-progress {
          position: absolute;
          top: 20px;
          right: 20px;
          display: flex;
          align-items: center;
          gap: 15px;
          color: #00ffff;
          font-family: 'Courier New', monospace;
          font-size: 12px;
          background: rgba(0, 0, 0, 0.5);
          padding: 8px 12px;
          border-radius: 4px;
          border: 1px solid rgba(0, 255, 255, 0.3);
        }
        
        .progress-bar {
          width: 120px;
          height: 6px;
          background: rgba(0, 255, 255, 0.2);
          border-radius: 3px;
          overflow: hidden;
        }
        
        .progress-fill {
          height: 100%;
          background: linear-gradient(90deg, #00ffff, #00aaff, #0088ff);
          border-radius: 3px;
          box-shadow: 0 0 10px rgba(0, 255, 255, 0.6);
          transition: width 0.5s ease;
        }
        
        .vulnerability-counter {
          position: absolute;
          bottom: 80px;
          right: 20px;
          text-align: center;
          color: #ff4444;
          font-family: 'Courier New', monospace;
          background: rgba(0, 0, 0, 0.7);
          padding: 12px;
          border-radius: 4px;
          border: 1px solid rgba(255, 68, 68, 0.5);
        }
        
        .vuln-count {
          font-size: 28px;
          font-weight: bold;
          text-shadow: 0 0 20px rgba(255, 68, 68, 1);
          animation: glow 2s ease-in-out infinite;
        }
        
        .vuln-label {
          font-size: 10px;
          opacity: 0.9;
          margin-top: 4px;
          display: block;
        }
        
        @keyframes glow {
          0%, 100% { text-shadow: 0 0 20px rgba(255, 68, 68, 1); }
          50% { text-shadow: 0 0 30px rgba(255, 68, 68, 1), 0 0 40px rgba(255, 68, 68, 0.8); }
        }
        
        .controls-hint {
          position: absolute;
          bottom: 20px;
          left: 50%;
          transform: translateX(-50%);
          color: rgba(0, 255, 255, 0.6);
          font-family: 'Courier New', monospace;
          font-size: 11px;
          text-align: center;
          background: rgba(0, 0, 0, 0.5);
          padding: 6px 12px;
          border-radius: 4px;
          border: 1px solid rgba(0, 255, 255, 0.2);
        }
        
        .brain-error {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 100%;
          height: 100%;
          background: #0a0a0f;
          color: #ff4444;
          font-family: 'Courier New', monospace;
        }
        
        .error-content {
          text-align: center;
          padding: 20px;
        }
        
        .error-content h3 {
          margin-bottom: 16px;
          font-size: 18px;
        }
        
        .error-content p {
          margin-bottom: 8px;
          font-size: 14px;
          opacity: 0.8;
        }
      `}</style>
    </div>
  );
};