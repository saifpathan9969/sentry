/**
 * Brain Renderer - Main Three.js rendering system
 * Handles WebGL rendering, animations, and visual effects
 */
import * as THREE from 'three';
import { OrbitControls } from 'three-stdlib';
import { BrainGenerator, Neuron, Synapse } from './BrainGenerator';
import { BrainStateManager, BrainState } from './BrainStateManager';

export class BrainRenderer {
  private scene!: THREE.Scene;
  private camera!: THREE.PerspectiveCamera;
  private renderer!: THREE.WebGLRenderer;
  private controls!: OrbitControls;
  private stateManager!: BrainStateManager;
  
  // Brain components
  private neurons: Neuron[] = [];
  private synapses: Synapse[] = [];
  private neuronMeshes!: THREE.InstancedMesh;
  private synapseMeshes!: THREE.LineSegments;
  private pulseMeshes!: THREE.InstancedMesh;
  
  // Animation
  private animationId: number = 0;
  private time: number = 0;
  private pulseTime: number = 0;
  
  // Materials
  private neuronMaterial!: THREE.MeshBasicMaterial;
  private synapseMaterial!: THREE.LineBasicMaterial;
  private pulseMaterial!: THREE.MeshBasicMaterial;
  
  // Geometry
  private neuronGeometry!: THREE.SphereGeometry;
  private pulseGeometry!: THREE.SphereGeometry;
  
  // Performance
  private readonly maxPulses = 200;
  private activePulses: Array<{
    synapseIndex: number;
    progress: number;
    intensity: number;
  }> = [];

  constructor(container: HTMLElement) {
    this.initializeScene();
    this.initializeCamera();
    this.initializeRenderer(container);
    this.initializeControls();
    this.initializeMaterials();
    this.initializeGeometry();
    this.stateManager = new BrainStateManager();
    
    this.generateBrain();
    this.setupLighting();
    this.startAnimation();
    
    // Handle window resize
    window.addEventListener('resize', this.handleResize.bind(this));
  }

  /**
   * Initialize Three.js scene
   */
  private initializeScene(): void {
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x0a0a0f); // Deep space blue
    this.scene.fog = new THREE.Fog(0x0a0a0f, 2, 8);
  }

  /**
   * Initialize camera
   */
  private initializeCamera(): void {
    this.camera = new THREE.PerspectiveCamera(
      60,
      window.innerWidth / window.innerHeight,
      0.1,
      100
    );
    this.camera.position.set(2, 1, 3);
    this.camera.lookAt(0, 0, 0);
  }

  /**
   * Initialize WebGL renderer
   */
  private initializeRenderer(container: HTMLElement): void {
    this.renderer = new THREE.WebGLRenderer({
      antialias: true,
      alpha: true,
      powerPreference: 'high-performance'
    });
    
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.2;
    
    container.appendChild(this.renderer.domElement);
  }

  /**
   * Initialize orbit controls
   */
  private initializeControls(): void {
    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.05;
    this.controls.minDistance = 1.5;
    this.controls.maxDistance = 8;
    this.controls.autoRotate = true;
    this.controls.autoRotateSpeed = 0.5;
  }

  /**
   * Initialize materials with Jarvis-style colors
   */
  private initializeMaterials(): void {
    // Neuron material - cyan glow
    this.neuronMaterial = new THREE.MeshBasicMaterial({
      color: 0x00ffff,
      transparent: true,
      opacity: 0.8,
      blending: THREE.AdditiveBlending
    });

    // Synapse material - teal connections
    this.synapseMaterial = new THREE.LineBasicMaterial({
      color: 0x008888,
      transparent: true,
      opacity: 0.3,
      blending: THREE.AdditiveBlending
    });

    // Pulse material - bright cyan energy
    this.pulseMaterial = new THREE.MeshBasicMaterial({
      color: 0x00ffff,
      transparent: true,
      opacity: 1.0,
      blending: THREE.AdditiveBlending
    });
  }

  /**
   * Initialize geometry
   */
  private initializeGeometry(): void {
    this.neuronGeometry = new THREE.SphereGeometry(0.008, 8, 6);
    this.pulseGeometry = new THREE.SphereGeometry(0.004, 6, 4);
  }

  /**
   * Generate brain structure
   */
  private generateBrain(): void {
    const generator = new BrainGenerator(600, 0.12, 8);
    const brainData = generator.generate();
    
    this.neurons = brainData.neurons;
    this.synapses = brainData.synapses;
    
    this.createNeuronMeshes();
    this.createSynapseMeshes();
    this.createPulseMeshes();
  }

  /**
   * Create instanced neuron meshes
   */
  private createNeuronMeshes(): void {
    this.neuronMeshes = new THREE.InstancedMesh(
      this.neuronGeometry,
      this.neuronMaterial,
      this.neurons.length
    );

    const matrix = new THREE.Matrix4();
    const color = new THREE.Color();

    for (let i = 0; i < this.neurons.length; i++) {
      const neuron = this.neurons[i];
      
      // Set position
      matrix.setPosition(neuron.position);
      this.neuronMeshes.setMatrixAt(i, matrix);
      
      // Set initial color
      color.setHSL(0.5, 0.8, 0.5 + neuron.activity * 0.5);
      this.neuronMeshes.setColorAt(i, color);
    }

    this.neuronMeshes.instanceMatrix.needsUpdate = true;
    this.neuronMeshes.instanceColor!.needsUpdate = true;
    this.scene.add(this.neuronMeshes);
  }

  /**
   * Create synapse line meshes
   */
  private createSynapseMeshes(): void {
    const positions: number[] = [];
    const colors: number[] = [];

    for (const synapse of this.synapses) {
      const fromPos = this.neurons[synapse.from].position;
      const toPos = this.neurons[synapse.to].position;
      
      // Create curved connection using quadratic bezier
      const midPoint = fromPos.clone().add(toPos).multiplyScalar(0.5);
      const offset = new THREE.Vector3(
        (Math.random() - 0.5) * 0.2,
        (Math.random() - 0.5) * 0.2,
        (Math.random() - 0.5) * 0.2
      );
      midPoint.add(offset);
      
      // Create curve segments
      const segments = 8;
      for (let i = 0; i < segments; i++) {
        const t1 = i / segments;
        const t2 = (i + 1) / segments;
        
        const p1 = this.quadraticBezier(fromPos, midPoint, toPos, t1);
        const p2 = this.quadraticBezier(fromPos, midPoint, toPos, t2);
        
        positions.push(p1.x, p1.y, p1.z);
        positions.push(p2.x, p2.y, p2.z);
        
        // Color based on activity
        const intensity = synapse.activity * 0.5 + 0.2;
        colors.push(0, intensity, intensity);
        colors.push(0, intensity, intensity);
      }
    }

    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));

    this.synapseMaterial.vertexColors = true;
    this.synapseMeshes = new THREE.LineSegments(geometry, this.synapseMaterial);
    this.scene.add(this.synapseMeshes);
  }

  /**
   * Create pulse effect meshes
   */
  private createPulseMeshes(): void {
    this.pulseMeshes = new THREE.InstancedMesh(
      this.pulseGeometry,
      this.pulseMaterial,
      this.maxPulses
    );
    
    // Hide all pulses initially
    const matrix = new THREE.Matrix4();
    matrix.makeScale(0, 0, 0);
    for (let i = 0; i < this.maxPulses; i++) {
      this.pulseMeshes.setMatrixAt(i, matrix);
    }
    
    this.pulseMeshes.instanceMatrix.needsUpdate = true;
    this.scene.add(this.pulseMeshes);
  }

  /**
   * Quadratic bezier curve helper
   */
  private quadraticBezier(p0: THREE.Vector3, p1: THREE.Vector3, p2: THREE.Vector3, t: number): THREE.Vector3 {
    const result = new THREE.Vector3();
    const oneMinusT = 1 - t;
    
    result.x = oneMinusT * oneMinusT * p0.x + 2 * oneMinusT * t * p1.x + t * t * p2.x;
    result.y = oneMinusT * oneMinusT * p0.y + 2 * oneMinusT * t * p1.y + t * t * p2.y;
    result.z = oneMinusT * oneMinusT * p0.z + 2 * oneMinusT * t * p1.z + t * t * p2.z;
    
    return result;
  }

  /**
   * Setup lighting
   */
  private setupLighting(): void {
    // Ambient light for base illumination
    const ambientLight = new THREE.AmbientLight(0x004466, 0.3);
    this.scene.add(ambientLight);

    // Point lights for dramatic effect
    const light1 = new THREE.PointLight(0x00ffff, 1, 10);
    light1.position.set(2, 2, 2);
    this.scene.add(light1);

    const light2 = new THREE.PointLight(0x0088ff, 0.5, 8);
    light2.position.set(-2, -1, 1);
    this.scene.add(light2);
  }

  /**
   * Start animation loop
   */
  private startAnimation(): void {
    const animate = () => {
      this.animationId = requestAnimationFrame(animate);
      this.update();
      this.render();
    };
    animate();
  }

  /**
   * Update animation
   */
  private update(): void {
    this.time += 0.016; // ~60fps
    this.pulseTime += 0.016;
    
    const config = this.stateManager.getCurrentConfig();
    
    this.updateNeurons(config);
    this.updateSynapses(config);
    this.updatePulses(config);
    this.updateCamera(config);
    this.controls.update();
  }

  /**
   * Update neuron animations
   */
  private updateNeurons(config: any): void {
    const matrix = new THREE.Matrix4();
    const color = new THREE.Color();
    
    for (let i = 0; i < this.neurons.length; i++) {
      const neuron = this.neurons[i];
      
      // Update activity based on state
      const targetActivity = neuron.baseActivity * config.neuronActivity;
      neuron.activity += (targetActivity - neuron.activity) * 0.1;
      
      // Pulsing scale
      const pulse = Math.sin(this.time * config.pulseSpeed + i * 0.1) * 0.3 + 1.0;
      const scale = (0.8 + neuron.activity * 0.4) * pulse;
      
      matrix.setPosition(neuron.position);
      matrix.scale(new THREE.Vector3(scale, scale, scale));
      this.neuronMeshes.setMatrixAt(i, matrix);
      
      // Dynamic color based on activity
      const hue = 0.5 + neuron.activity * 0.1;
      const lightness = 0.3 + neuron.activity * config.glowIntensity;
      color.setHSL(hue, 0.9, lightness);
      this.neuronMeshes.setColorAt(i, color);
    }
    
    this.neuronMeshes.instanceMatrix.needsUpdate = true;
    this.neuronMeshes.instanceColor!.needsUpdate = true;
  }

  /**
   * Update synapse animations
   */
  private updateSynapses(config: any): void {
    // Update synapse opacity based on activity
    this.synapseMaterial.opacity = 0.2 + config.synapseActivity * 0.3;
    
    // Spawn new pulses
    if (Math.random() < config.energyFlowDensity * 0.1) {
      this.spawnPulse();
    }
  }

  /**
   * Update pulse animations
   */
  private updatePulses(config: any): void {
    const matrix = new THREE.Matrix4();
    
    // Update existing pulses
    for (let i = this.activePulses.length - 1; i >= 0; i--) {
      const pulse = this.activePulses[i];
      pulse.progress += 0.02 * config.pulseSpeed;
      
      if (pulse.progress >= 1.0) {
        // Remove completed pulse
        this.activePulses.splice(i, 1);
        matrix.makeScale(0, 0, 0);
        this.pulseMeshes.setMatrixAt(i, matrix);
      } else {
        // Update pulse position along synapse
        const synapse = this.synapses[pulse.synapseIndex];
        if (synapse) {
          const fromPos = this.neurons[synapse.from].position;
          const toPos = this.neurons[synapse.to].position;
          
          const position = fromPos.clone().lerp(toPos, pulse.progress);
          const scale = pulse.intensity * (1.0 - pulse.progress * 0.5);
          
          matrix.setPosition(position);
          matrix.scale(new THREE.Vector3(scale, scale, scale));
          this.pulseMeshes.setMatrixAt(i, matrix);
        }
      }
    }
    
    this.pulseMeshes.instanceMatrix.needsUpdate = true;
  }

  /**
   * Spawn a new energy pulse
   */
  private spawnPulse(): void {
    if (this.activePulses.length < this.maxPulses && this.synapses.length > 0) {
      const synapseIndex = Math.floor(Math.random() * this.synapses.length);
      
      this.activePulses.push({
        synapseIndex,
        progress: 0,
        intensity: 0.5 + Math.random() * 0.5
      });
    }
  }

  /**
   * Update camera motion
   */
  private updateCamera(config: any): void {
    // Subtle camera breathing
    const breathe = Math.sin(this.time * 0.5) * config.cameraMotion * 0.1;
    this.controls.autoRotateSpeed = 0.5 + breathe;
  }

  /**
   * Render frame
   */
  private render(): void {
    this.renderer.render(this.scene, this.camera);
  }

  /**
   * Handle window resize
   */
  private handleResize(): void {
    this.camera.aspect = window.innerWidth / window.innerHeight;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(window.innerWidth, window.innerHeight);
  }

  /**
   * Public API methods
   */
  
  startScan(): void {
    this.stateManager.startScan();
  }

  setState(state: BrainState): void {
    this.stateManager.setState(state);
  }

  handleBackendEvent(event: any): void {
    this.stateManager.handleBackendEvent(event);
  }

  dispose(): void {
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
    }
    
    this.renderer.dispose();
    this.neuronGeometry.dispose();
    this.pulseGeometry.dispose();
    this.neuronMaterial.dispose();
    this.synapseMaterial.dispose();
    this.pulseMaterial.dispose();
    
    window.removeEventListener('resize', this.handleResize.bind(this));
  }
}