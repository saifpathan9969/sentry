/**
 * Brain State Manager - Controls visual states and animations
 * Manages the transition between different brain activity states
 */
import { gsap } from 'gsap';

export enum BrainState {
  IDLE = 'idle',
  SCAN_START = 'scan_start',
  SCAN_ACTIVE = 'scan_active',
  DEEP_ANALYSIS = 'deep_analysis',
  VULNERABILITY_FOUND = 'vulnerability_found',
  SCAN_COMPLETE = 'scan_complete'
}

export interface StateConfig {
  pulseSpeed: number;
  glowIntensity: number;
  energyFlowDensity: number;
  cameraMotion: number;
  neuronActivity: number;
  synapseActivity: number;
  colorIntensity: number;
  focusRegions: number[];
}

export class BrainStateManager {
  private currentState: BrainState = BrainState.IDLE;
  private stateConfigs!: Map<BrainState, StateConfig>;
  private transitionDuration: number = 2.0;
  private currentConfig!: StateConfig;
  private targetConfig!: StateConfig;
  private transitionProgress: number = 1.0;

  constructor() {
    this.initializeStateConfigs();
    this.currentConfig = this.stateConfigs.get(BrainState.IDLE)!;
    this.targetConfig = this.currentConfig;
  }

  /**
   * Initialize all state configurations
   */
  private initializeStateConfigs(): void {
    this.stateConfigs = new Map([
      [BrainState.IDLE, {
        pulseSpeed: 0.5,
        glowIntensity: 0.3,
        energyFlowDensity: 0.2,
        cameraMotion: 0.1,
        neuronActivity: 0.2,
        synapseActivity: 0.1,
        colorIntensity: 0.6,
        focusRegions: []
      }],
      
      [BrainState.SCAN_START, {
        pulseSpeed: 2.0,
        glowIntensity: 0.8,
        energyFlowDensity: 0.6,
        cameraMotion: 0.3,
        neuronActivity: 0.7,
        synapseActivity: 0.5,
        colorIntensity: 1.0,
        focusRegions: [0, 1, 2] // Frontal regions
      }],
      
      [BrainState.SCAN_ACTIVE, {
        pulseSpeed: 1.5,
        glowIntensity: 0.9,
        energyFlowDensity: 0.8,
        cameraMotion: 0.2,
        neuronActivity: 0.8,
        synapseActivity: 0.7,
        colorIntensity: 1.2,
        focusRegions: [0, 1, 2, 3]
      }],
      
      [BrainState.DEEP_ANALYSIS, {
        pulseSpeed: 3.0,
        glowIntensity: 1.2,
        energyFlowDensity: 1.0,
        cameraMotion: 0.4,
        neuronActivity: 1.0,
        synapseActivity: 0.9,
        colorIntensity: 1.5,
        focusRegions: [0, 1, 2, 3, 4]
      }],
      
      [BrainState.VULNERABILITY_FOUND, {
        pulseSpeed: 4.0,
        glowIntensity: 1.5,
        energyFlowDensity: 1.2,
        cameraMotion: 0.6,
        neuronActivity: 1.2,
        synapseActivity: 1.0,
        colorIntensity: 2.0,
        focusRegions: [Math.floor(Math.random() * 6)]
      }],
      
      [BrainState.SCAN_COMPLETE, {
        pulseSpeed: 0.8,
        glowIntensity: 0.6,
        energyFlowDensity: 0.4,
        cameraMotion: 0.15,
        neuronActivity: 0.4,
        synapseActivity: 0.3,
        colorIntensity: 0.8,
        focusRegions: []
      }]
    ]);
  }

  /**
   * Transition to a new brain state
   */
  setState(newState: BrainState, immediate: boolean = false): void {
    if (newState === this.currentState && this.transitionProgress >= 1.0) {
      return;
    }

    console.log(`🧠 Brain state: ${this.currentState} → ${newState}`);
    
    this.currentState = newState;
    this.targetConfig = this.stateConfigs.get(newState)!;
    
    if (immediate) {
      this.currentConfig = { ...this.targetConfig };
      this.transitionProgress = 1.0;
    } else {
      this.transitionProgress = 0.0;
      
      // Use GSAP for smooth state transitions
      gsap.to(this, {
        transitionProgress: 1.0,
        duration: this.getTransitionDuration(newState),
        ease: this.getTransitionEase(newState),
        onUpdate: () => this.updateCurrentConfig()
      });
    }
  }

  /**
   * Get transition duration based on state change
   */
  private getTransitionDuration(newState: BrainState): number {
    switch (newState) {
      case BrainState.SCAN_START:
        return 0.5; // Instant response
      case BrainState.VULNERABILITY_FOUND:
        return 0.3; // Quick alert
      case BrainState.SCAN_COMPLETE:
        return 3.0; // Slow wind-down
      default:
        return this.transitionDuration;
    }
  }

  /**
   * Get transition easing based on state change
   */
  private getTransitionEase(newState: BrainState): string {
    switch (newState) {
      case BrainState.SCAN_START:
        return 'power2.out';
      case BrainState.VULNERABILITY_FOUND:
        return 'elastic.out(1, 0.3)';
      case BrainState.SCAN_COMPLETE:
        return 'power3.inOut';
      default:
        return 'power2.inOut';
    }
  }

  /**
   * Update current config during transition
   */
  private updateCurrentConfig(): void {
    const t = this.transitionProgress;
    
    this.currentConfig = {
      pulseSpeed: this.lerp(this.currentConfig.pulseSpeed, this.targetConfig.pulseSpeed, t),
      glowIntensity: this.lerp(this.currentConfig.glowIntensity, this.targetConfig.glowIntensity, t),
      energyFlowDensity: this.lerp(this.currentConfig.energyFlowDensity, this.targetConfig.energyFlowDensity, t),
      cameraMotion: this.lerp(this.currentConfig.cameraMotion, this.targetConfig.cameraMotion, t),
      neuronActivity: this.lerp(this.currentConfig.neuronActivity, this.targetConfig.neuronActivity, t),
      synapseActivity: this.lerp(this.currentConfig.synapseActivity, this.targetConfig.synapseActivity, t),
      colorIntensity: this.lerp(this.currentConfig.colorIntensity, this.targetConfig.colorIntensity, t),
      focusRegions: this.targetConfig.focusRegions // Discrete property
    };
  }

  /**
   * Linear interpolation helper
   */
  private lerp(a: number, b: number, t: number): number {
    return a + (b - a) * t;
  }

  /**
   * Get current state configuration
   */
  getCurrentConfig(): StateConfig {
    return this.currentConfig;
  }

  /**
   * Get current state
   */
  getCurrentState(): BrainState {
    return this.currentState;
  }

  /**
   * Check if currently transitioning
   */
  isTransitioning(): boolean {
    return this.transitionProgress < 1.0;
  }

  /**
   * Trigger vulnerability found effect
   */
  triggerVulnerabilityFound(_severity: 'low' | 'medium' | 'high' | 'critical'): void {
    // Temporarily switch to vulnerability state
    const originalState = this.currentState;
    
    this.setState(BrainState.VULNERABILITY_FOUND, false);
    
    // Return to previous state after alert
    setTimeout(() => {
      if (originalState !== BrainState.SCAN_COMPLETE) {
        this.setState(originalState, false);
      }
    }, 2000);
  }

  /**
   * Handle backend events
   */
  handleBackendEvent(event: any): void {
    switch (event.type) {
      case 'SCAN_STARTED':
        this.setState(BrainState.SCAN_START);
        setTimeout(() => this.setState(BrainState.SCAN_ACTIVE), 1000);
        break;
        
      case 'DEEP_SCAN_PHASE':
        this.setState(BrainState.DEEP_ANALYSIS);
        break;
        
      case 'VULNERABILITY_FOUND':
        this.triggerVulnerabilityFound(event.severity || 'medium');
        break;
        
      case 'SCAN_COMPLETED':
        this.setState(BrainState.SCAN_COMPLETE);
        break;
        
      case 'SCAN_FAILED':
        this.setState(BrainState.IDLE);
        break;
        
      default:
        console.log('🧠 Unknown brain event:', event);
    }
  }

  /**
   * Manual state control for testing
   */
  startScan(): void {
    this.setState(BrainState.SCAN_START);
    
    // Simulate scan progression
    setTimeout(() => this.setState(BrainState.SCAN_ACTIVE), 500);
    setTimeout(() => this.setState(BrainState.DEEP_ANALYSIS), 3000);
    setTimeout(() => this.triggerVulnerabilityFound('high'), 5000);
    setTimeout(() => this.triggerVulnerabilityFound('critical'), 8000);
    setTimeout(() => this.setState(BrainState.SCAN_COMPLETE), 12000);
    setTimeout(() => this.setState(BrainState.IDLE), 18000);
  }

  /**
   * Reset to idle state
   */
  reset(): void {
    this.setState(BrainState.IDLE, true);
  }
}