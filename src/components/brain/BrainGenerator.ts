/**
 * AI Brain Generator - Creates the 3D neural network structure
 * Generates organic brain-like geometry with neurons and synapses
 */
import * as THREE from 'three';

export interface Neuron {
  position: THREE.Vector3;
  connections: number[];
  activity: number;
  baseActivity: number;
  cluster: number;
}

export interface Synapse {
  from: number;
  to: number;
  strength: number;
  activity: number;
  pulseTime: number;
}

export class BrainGenerator {
  private neurons: Neuron[] = [];
  private synapses: Synapse[] = [];
  private clusters: THREE.Vector3[] = [];

  constructor(
    private neuronCount: number = 800,
    private connectionDensity: number = 0.15,
    private clusterCount: number = 12
  ) {}

  /**
   * Generate the complete brain structure
   */
  generate(): { neurons: Neuron[]; synapses: Synapse[] } {
    this.generateClusters();
    this.generateNeurons();
    this.generateConnections();
    this.optimizeConnections();
    
    return {
      neurons: this.neurons,
      synapses: this.synapses
    };
  }

  /**
   * Create cluster centers for organic brain regions
   */
  private generateClusters(): void {
    this.clusters = [];
    
    // Create main brain regions with organic positioning
    const regions = [
      { pos: [0, 0.3, 0], weight: 1.5 },      // Frontal cortex
      { pos: [-0.4, 0.1, 0.2], weight: 1.2 }, // Left hemisphere
      { pos: [0.4, 0.1, 0.2], weight: 1.2 },  // Right hemisphere
      { pos: [0, -0.2, 0.3], weight: 1.0 },   // Visual cortex
      { pos: [0, -0.4, 0], weight: 0.8 },     // Cerebellum
      { pos: [0, 0, -0.3], weight: 0.9 },     // Brain stem
    ];

    // Add some random sub-clusters for complexity
    for (let i = 0; i < this.clusterCount; i++) {
      if (i < regions.length) {
        const region = regions[i];
        this.clusters.push(new THREE.Vector3(
          region.pos[0] + (Math.random() - 0.5) * 0.1,
          region.pos[1] + (Math.random() - 0.5) * 0.1,
          region.pos[2] + (Math.random() - 0.5) * 0.1
        ));
      } else {
        // Random clusters within brain bounds
        const theta = Math.random() * Math.PI * 2;
        const phi = Math.random() * Math.PI;
        const r = 0.3 + Math.random() * 0.4;
        
        this.clusters.push(new THREE.Vector3(
          r * Math.sin(phi) * Math.cos(theta),
          r * Math.cos(phi),
          r * Math.sin(phi) * Math.sin(theta)
        ));
      }
    }
  }

  /**
   * Generate neurons with organic brain-like distribution
   */
  private generateNeurons(): void {
    this.neurons = [];

    for (let i = 0; i < this.neuronCount; i++) {
      // Choose a cluster with weighted probability
      const clusterIndex = Math.floor(Math.random() * this.clusters.length);
      const cluster = this.clusters[clusterIndex];
      
      // Generate position around cluster with organic distribution
      const offset = this.generateOrganicOffset();
      const position = cluster.clone().add(offset);
      
      // Ensure neurons stay within brain bounds (organic ellipsoid)
      this.constrainToBrainShape(position);
      
      const neuron: Neuron = {
        position,
        connections: [],
        activity: Math.random() * 0.3 + 0.1,
        baseActivity: Math.random() * 0.3 + 0.1,
        cluster: clusterIndex
      };
      
      this.neurons.push(neuron);
    }
  }

  /**
   * Generate organic offset from cluster center
   */
  private generateOrganicOffset(): THREE.Vector3 {
    // Use multiple octaves of noise for organic distribution
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.random() * Math.PI;
    
    // Organic radius with clustering
    const r1 = Math.random();
    const r2 = Math.random();
    const r = Math.sqrt(r1) * 0.15 + r2 * 0.05;
    
    return new THREE.Vector3(
      r * Math.sin(phi) * Math.cos(theta),
      r * Math.cos(phi),
      r * Math.sin(phi) * Math.sin(theta)
    );
  }

  /**
   * Constrain neuron to organic brain shape
   */
  private constrainToBrainShape(position: THREE.Vector3): void {
    // Brain is roughly an ellipsoid with organic deformation
    const x = position.x;
    const y = position.y;
    const z = position.z;
    
    // Ellipsoid equation with organic scaling
    const scaleX = 0.8;
    const scaleY = 1.0;
    const scaleZ = 0.7;
    
    const distance = (x * x) / (scaleX * scaleX) + 
                    (y * y) / (scaleY * scaleY) + 
                    (z * z) / (scaleZ * scaleZ);
    
    if (distance > 1.0) {
      // Project back to surface with some organic variation
      const scale = Math.sqrt(1.0 / distance) * (0.9 + Math.random() * 0.1);
      position.multiplyScalar(scale);
    }
  }

  /**
   * Generate synaptic connections between neurons
   */
  private generateConnections(): void {
    this.synapses = [];
    
    for (let i = 0; i < this.neurons.length; i++) {
      const neuron = this.neurons[i];
      const connectionCount = Math.floor(
        this.connectionDensity * this.neuronCount * (0.5 + Math.random())
      );
      
      // Find nearby neurons for connections
      const candidates = this.findNearbyNeurons(i, connectionCount * 3);
      
      // Create connections with preference for same cluster and proximity
      for (let j = 0; j < Math.min(connectionCount, candidates.length); j++) {
        const targetIndex = candidates[j].index;
        
        if (targetIndex !== i && !neuron.connections.includes(targetIndex)) {
          neuron.connections.push(targetIndex);
          
          const synapse: Synapse = {
            from: i,
            to: targetIndex,
            strength: 0.3 + Math.random() * 0.7,
            activity: Math.random() * 0.2,
            pulseTime: Math.random() * 1000
          };
          
          this.synapses.push(synapse);
        }
      }
    }
  }

  /**
   * Find nearby neurons for connection candidates
   */
  private findNearbyNeurons(neuronIndex: number, maxCandidates: number): Array<{index: number, distance: number}> {
    const neuron = this.neurons[neuronIndex];
    const candidates: Array<{index: number, distance: number}> = [];
    
    for (let i = 0; i < this.neurons.length; i++) {
      if (i === neuronIndex) continue;
      
      const other = this.neurons[i];
      const distance = neuron.position.distanceTo(other.position);
      
      // Prefer same cluster connections
      const clusterBonus = neuron.cluster === other.cluster ? 0.5 : 1.0;
      const adjustedDistance = distance * clusterBonus;
      
      candidates.push({ index: i, distance: adjustedDistance });
    }
    
    // Sort by distance and return closest
    candidates.sort((a, b) => a.distance - b.distance);
    return candidates.slice(0, maxCandidates);
  }

  /**
   * Optimize connections for better visual flow
   */
  private optimizeConnections(): void {
    // Remove redundant connections
    const connectionMap = new Set<string>();
    this.synapses = this.synapses.filter(synapse => {
      const key1 = `${synapse.from}-${synapse.to}`;
      const key2 = `${synapse.to}-${synapse.from}`;
      
      if (connectionMap.has(key1) || connectionMap.has(key2)) {
        return false;
      }
      
      connectionMap.add(key1);
      return true;
    });
    
    // Ensure minimum connectivity for visual appeal
    this.ensureMinimumConnectivity();
  }

  /**
   * Ensure each neuron has minimum connections for visual flow
   */
  private ensureMinimumConnectivity(): void {
    const minConnections = 2;
    
    for (let i = 0; i < this.neurons.length; i++) {
      const neuron = this.neurons[i];
      
      if (neuron.connections.length < minConnections) {
        const nearby = this.findNearbyNeurons(i, 5);
        
        for (const candidate of nearby) {
          if (neuron.connections.length >= minConnections) break;
          
          if (!neuron.connections.includes(candidate.index)) {
            neuron.connections.push(candidate.index);
            
            this.synapses.push({
              from: i,
              to: candidate.index,
              strength: 0.4 + Math.random() * 0.4,
              activity: Math.random() * 0.2,
              pulseTime: Math.random() * 1000
            });
          }
        }
      }
    }
  }

  /**
   * Get cluster positions for external use
   */
  getClusters(): THREE.Vector3[] {
    return this.clusters;
  }
}