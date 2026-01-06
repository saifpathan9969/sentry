"""
Intelligent Router - Routes vulnerabilities to appropriate handler
Part of AI Pentest Brain V3.9+

Known vulnerabilities → Fast standard remedies (seconds)
Unknown vulnerabilities → Adaptive intelligence (minutes)
"""

import time
import logging
from typing import Dict, List
from datetime import datetime
from vulnerability_classifier import VulnerabilityClassifier
from known_vulnerability_handler import KnownVulnerabilityHandler

try:
    from adaptive_intelligence_engine import AdaptiveIntelligenceEngine
    ADAPTIVE_AVAILABLE = True
except ImportError:
    ADAPTIVE_AVAILABLE = False
    print("[WARNING] Adaptive Intelligence Engine not available")

logger = logging.getLogger(__name__)


class IntelligentRouter:
    """Route vulnerabilities to optimal processing path"""
    
    def __init__(self):
        self.classifier = VulnerabilityClassifier()
        self.known_handler = KnownVulnerabilityHandler()
        
        if ADAPTIVE_AVAILABLE:
            self.unknown_handler = AdaptiveIntelligenceEngine()
            logger.info("Adaptive Intelligence Engine loaded")
        else:
            self.unknown_handler = None
            logger.warning("Adaptive Intelligence not available - unknown vulns will use fallback")
        
        self.stats = {
            'total': 0,
            'known': 0,
            'unknown': 0,
            'novel_discoveries': 0,
            'time_saved': 0.0
        }
        
        logger.info("Intelligent Router initialized")
        logger.info("="*60)
        logger.info("INTELLIGENT ROUTING ACTIVE")
        logger.info("  Known vulns → Fast standard remedies (seconds)")
        logger.info("  Unknown vulns → Adaptive intelligence (minutes)")
        logger.info("="*60)
    
    def process_findings(self, findings: List[Dict]) -> Dict:
        """
        Process all findings with intelligent routing
        
        Args:
            findings: List of vulnerability dictionaries
            
        Returns:
            Comprehensive results with known/unknown breakdown
        """
        if not findings:
            return self._empty_results()
        
        results = {
            'known_vulnerabilities': [],
            'unknown_vulnerabilities': [],
            'novel_discoveries': [],
            'processing_stats': {},
            'time_breakdown': {}
        }
        
        total_start = time.time()
        
        logger.info("\n" + "="*60)
        logger.info(f"PROCESSING {len(findings)} VULNERABILITIES")
        logger.info("="*60)
        
        # ==========================================
        # PHASE 1: CLASSIFICATION
        # ==========================================
        logger.info("\n[PHASE 1] Classification...")
        
        classified = []
        for i, vuln in enumerate(findings, 1):
            vuln_type, confidence, reference = self.classifier.classify_vulnerability(vuln)
            classified.append((vuln, vuln_type, confidence, reference))
            
            status = "✓ KNOWN" if vuln_type == 'KNOWN' else "⚠ UNKNOWN"
            logger.info(f"  [{i}/{len(findings)}] {vuln.get('type', 'Unknown')} → {status} (conf: {confidence:.2f})")
        
        known_count = sum(1 for _, vtype, _, _ in classified if vtype == 'KNOWN')
        unknown_count = len(classified) - known_count
        
        logger.info(f"\nClassification complete:")
        logger.info(f"  Known: {known_count} ({known_count/len(findings)*100:.1f}%)")
        logger.info(f"  Unknown: {unknown_count} ({unknown_count/len(findings)*100:.1f}%)")
        
        # ==========================================
        # PHASE 2A: PROCESS KNOWN (FAST TRACK)
        # ==========================================
        if known_count > 0:
            logger.info("\n" + "="*60)
            logger.info("[PHASE 2A] Processing KNOWN vulnerabilities (FAST TRACK)")
            logger.info("="*60)
            
            known_start = time.time()
            
            for vuln, vuln_type, confidence, reference in classified:
                if vuln_type == 'KNOWN':
                    self.stats['known'] += 1
                    
                    start = time.time()
                    remedy = self.known_handler.get_standard_remedy(vuln, reference)
                    elapsed = time.time() - start
                    
                    results['known_vulnerabilities'].append({
                        'vulnerability': vuln,
                        'classification': 'KNOWN',
                        'confidence': confidence,
                        'reference': reference,
                        'remedy': remedy,
                        'processing_time_seconds': elapsed,
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    logger.info(f"  ✓ {vuln.get('type', 'Unknown')} - Fixed in {elapsed:.2f}s")
            
            known_total_time = time.time() - known_start
            logger.info(f"\n✓ Known vulnerabilities processed: {known_count} in {known_total_time:.2f}s")
            logger.info(f"  Average: {known_total_time/known_count:.2f}s per vulnerability")
            
            results['time_breakdown']['known_processing'] = known_total_time
        
        # ==========================================
        # PHASE 2B: PROCESS UNKNOWN (INTELLIGENCE TRACK)
        # ==========================================
        if unknown_count > 0:
            logger.info("\n" + "="*60)
            logger.info("[PHASE 2B] Processing UNKNOWN vulnerabilities (INTELLIGENCE TRACK)")
            logger.info("="*60)
            logger.info("🧠 Activating Adaptive Intelligence Engine...")
            
            unknown_start = time.time()
            
            if not self.unknown_handler:
                logger.error("⚠ Adaptive Intelligence not available - using fallback")
                
                for vuln, vuln_type, confidence, reference in classified:
                    if vuln_type == 'UNKNOWN':
                        self.stats['unknown'] += 1
                        results['unknown_vulnerabilities'].append({
                            'vulnerability': vuln,
                            'classification': 'UNKNOWN',
                            'confidence': confidence,
                            'solved': False,
                            'reason': 'Adaptive Intelligence Engine not available',
                            'requires_manual_review': True
                        })
            else:
                for vuln, vuln_type, confidence, reference in classified:
                    if vuln_type == 'UNKNOWN':
                        self.stats['unknown'] += 1
                        
                        logger.warning(f"\n[🧠 UNKNOWN] {vuln.get('type', 'Novel vulnerability')}")
                        logger.info("  Phase 1: Understanding context...")
                        logger.info("  Phase 2: Analyzing mechanism...")
                        logger.info("  Phase 3: Creating novel remedy...")
                        logger.info("  Phase 4: Validating solution...")
                        
                        start = time.time()
                        solution = self.unknown_handler.solve_unknown_threat(vuln)
                        elapsed = time.time() - start
                        
                        if solution.get('solved'):
                            results['unknown_vulnerabilities'].append({
                                'vulnerability': vuln,
                                'classification': 'UNKNOWN',
                                'confidence': confidence,
                                'solution': solution,
                                'processing_time_seconds': elapsed,
                                'timestamp': datetime.now().isoformat()
                            })
                            
                            # NOVEL DISCOVERY!
                            self.stats['novel_discoveries'] += 1
                            results['novel_discoveries'].append({
                                'vulnerability': vuln,
                                'solution': solution,
                                'timestamp': datetime.now().isoformat(),
                                'added_to_kb': False
                            })
                            
                            logger.info(f"  ✓ Novel remedy created in {elapsed:.2f}s")
                            logger.info(f"  📚 Confidence: {solution.get('confidence', 0):.2%}")
                            
                            # Add to knowledge base
                            if solution.get('confidence', 0) > 0.7:
                                vuln_id = self.classifier.add_to_knowledge_base(vuln, solution)
                                results['novel_discoveries'][-1]['added_to_kb'] = True
                                results['novel_discoveries'][-1]['vuln_id'] = vuln_id
                                logger.info(f"  📚 Added to knowledge base as: {vuln_id}")
                                logger.info(f"  📈 Next time this will be KNOWN (fast track)!")
                        else:
                            logger.error(f"  ✗ Could not solve: {solution.get('reason', 'Unknown')}")
                            results['unknown_vulnerabilities'].append({
                                'vulnerability': vuln,
                                'classification': 'UNKNOWN',
                                'solved': False,
                                'reason': solution.get('reason'),
                                'complexity': solution.get('complexity'),
                                'processing_time_seconds': elapsed,
                                'requires_manual_review': True
                            })
            
            unknown_total_time = time.time() - unknown_start
            logger.info(f"\n✓ Unknown vulnerabilities processed: {unknown_count} in {unknown_total_time:.2f}s")
            if unknown_count > 0:
                logger.info(f"  Average: {unknown_total_time/unknown_count:.2f}s per vulnerability")
            
            results['time_breakdown']['unknown_processing'] = unknown_total_time
        
        # ==========================================
        # FINAL STATISTICS
        # ==========================================
        total_time = time.time() - total_start
        
        self.stats['total'] = len(findings)
        
        # Calculate time saved vs "always use intelligence"
        # Assumption: Intelligence takes 120s per vuln, known takes 5s
        time_if_all_intelligence = len(findings) * 120  # seconds
        time_saved = time_if_all_intelligence - total_time
        self.stats['time_saved'] = time_saved
        
        results['processing_stats'] = {
            'total_vulnerabilities': self.stats['total'],
            'known_processed': self.stats['known'],
            'unknown_processed': self.stats['unknown'],
            'known_percentage': (self.stats['known'] / self.stats['total'] * 100) if self.stats['total'] > 0 else 0,
            'unknown_percentage': (self.stats['unknown'] / self.stats['total'] * 100) if self.stats['total'] > 0 else 0,
            'novel_discoveries': self.stats['novel_discoveries'],
            'total_processing_time': total_time,
            'time_saved_seconds': time_saved,
            'time_saved_minutes': time_saved / 60,
            'speedup_factor': time_if_all_intelligence / total_time if total_time > 0 else 1,
            'efficiency_gain': (time_saved / time_if_all_intelligence * 100) if time_if_all_intelligence > 0 else 0
        }
        
        results['time_breakdown']['total'] = total_time
        results['time_breakdown']['classification'] = results['time_breakdown'].get('classification', 0)
        
        self._print_final_stats(results)
        
        return results
    
    def _empty_results(self) -> Dict:
        """Return empty results structure"""
        return {
            'known_vulnerabilities': [],
            'unknown_vulnerabilities': [],
            'novel_discoveries': [],
            'processing_stats': {
                'total_vulnerabilities': 0,
                'known_processed': 0,
                'unknown_processed': 0
            },
            'time_breakdown': {}
        }
    
    def _print_final_stats(self, results: Dict):
        """Print comprehensive final statistics"""
        stats = results['processing_stats']
        
        logger.info("\n" + "="*60)
        logger.info("INTELLIGENT ROUTING - FINAL STATISTICS")
        logger.info("="*60)
        
        logger.info(f"\nVulnerabilities Processed: {stats['total_vulnerabilities']}")
        logger.info(f"  ├─ Known (fast track): {stats['known_processed']} ({stats['known_percentage']:.1f}%)")
        logger.info(f"  └─ Unknown (intelligence): {stats['unknown_processed']} ({stats['unknown_percentage']:.1f}%)")
        
        logger.info(f"\nNovel Discoveries: {stats['novel_discoveries']}")
        if stats['novel_discoveries'] > 0:
            logger.info("  └─ These are now KNOWN for future scans! 📚")
        
        logger.info(f"\nProcessing Time:")
        logger.info(f"  ├─ Total: {stats['total_processing_time']:.2f}s ({stats['total_processing_time']/60:.2f} min)")
        if 'known_processing' in results['time_breakdown']:
            logger.info(f"  ├─ Known track: {results['time_breakdown']['known_processing']:.2f}s")
        if 'unknown_processing' in results['time_breakdown']:
            logger.info(f"  └─ Unknown track: {results['time_breakdown']['unknown_processing']:.2f}s")
        
        logger.info(f"\nEfficiency Metrics:")
        logger.info(f"  ├─ Time saved: {stats['time_saved_minutes']:.1f} minutes")
        logger.info(f"  ├─ Speedup: {stats['speedup_factor']:.1f}x faster")
        logger.info(f"  └─ Efficiency gain: {stats['efficiency_gain']:.1f}%")
        
        logger.info("\n" + "="*60)
        logger.info("✓ INTELLIGENT ROUTING COMPLETE")
        logger.info("  Known → Fast remedies (seconds)")
        logger.info("  Unknown → Creative solutions (minutes)")
        logger.info("  Result → Best of both worlds! 🎯")
        logger.info("="*60)
    
    def get_stats(self) -> Dict:
        """Get current statistics"""
        return self.stats.copy()


if __name__ == '__main__':
    # Test intelligent router
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s'
    )
    
    router = IntelligentRouter()
    
    # Test findings (mix of known and unknown)
    test_findings = [
        {
            'type': 'SQL Injection',
            'url': 'http://test.com/api/user',
            'parameter': 'id',
            'payload': "' OR '1'='1",
            'severity': 'CRITICAL'
        },
        {
            'type': 'Cross-Site Scripting (XSS)',
            'url': 'http://test.com/search',
            'parameter': 'q',
            'payload': '<script>alert(1)</script>',
            'severity': 'HIGH'
        },
        {
            'type': 'CSRF (Cross-Site Request Forgery)',
            'url': 'http://test.com/transfer',
            'severity': 'MEDIUM'
        },
        {
            'type': 'Novel State Machine Bug',
            'url': 'http://test.com/banking/transfer',
            'description': 'Circular transfer A→B→A within settlement window creates race condition',
            'severity': 'HIGH',
            'payload': 'transfer(A, B, 1000); sleep(2); transfer(B, A, 1000)'
        },
        {
            'type': 'IDOR (Insecure Direct Object Reference)',
            'url': 'http://test.com/api/document/123',
            'severity': 'HIGH'
        }
    ]
    
    # Process findings
    results = router.process_findings(test_findings)
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total vulnerabilities: {len(test_findings)}")
    print(f"Known (fast): {len(results['known_vulnerabilities'])}")
    print(f"Unknown (intelligence): {len(results['unknown_vulnerabilities'])}")
    print(f"Novel discoveries: {len(results['novel_discoveries'])}")
    print(f"\nProcessing time: {results['processing_stats']['total_processing_time']:.2f}s")
    print(f"Time saved: {results['processing_stats']['time_saved_minutes']:.1f} minutes")
    print(f"Speedup: {results['processing_stats']['speedup_factor']:.1f}x")
