"""
AI Learning Engine for Zero-Day Detection
Continuously learns from vulnerability discoveries and attack patterns
Enables detection of previously unknown vulnerabilities
"""

import os
import json
import logging
import numpy as np
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import defaultdict
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AILearningEngine:
    """
    Advanced AI learning system that improves vulnerability detection over time
    Learns from:
    - Discovered vulnerabilities
    - Attack patterns
    - Remediation results
    - False positives/negatives
    - Zero-day indicators
    """
    
    def __init__(self, knowledge_base_path: str = "knowledge_base"):
        self.knowledge_base_path = Path(knowledge_base_path)
        self.knowledge_base_path.mkdir(exist_ok=True)
        
        # Learning components
        self.pattern_database = self._load_pattern_database()
        self.attack_signatures = self._load_attack_signatures()
        self.vulnerability_profiles = self._load_vulnerability_profiles()
        self.false_positive_patterns = self._load_false_positive_patterns()
        self.zero_day_indicators = self._load_zero_day_indicators()
        
        # Learning statistics
        self.learning_stats = {
            'total_vulnerabilities_learned': 0,
            'patterns_discovered': 0,
            'zero_days_detected': 0,
            'accuracy_improvement': 0.0,
            'last_training': None
        }
    
    def learn_from_scan(self, scan_results: Dict) -> Dict:
        """
        Learn from a completed scan
        
        Args:
            scan_results: Complete scan results including vulnerabilities found
            
        Returns:
            Learning summary
        """
        logger.info("Starting learning phase from scan results")
        
        learning_summary = {
            'timestamp': datetime.now().isoformat(),
            'vulnerabilities_analyzed': 0,
            'new_patterns_learned': 0,
            'patterns_updated': 0,
            'zero_day_patterns': 0
        }
        
        try:
            vulnerabilities = scan_results.get('findings', [])
            
            for vuln in vulnerabilities:
                # Extract and learn patterns
                patterns = self._extract_vulnerability_patterns(vuln)
                
                for pattern in patterns:
                    if self._is_new_pattern(pattern):
                        self._add_pattern(pattern)
                        learning_summary['new_patterns_learned'] += 1
                    else:
                        self._update_pattern(pattern)
                        learning_summary['patterns_updated'] += 1
                
                # Learn attack signatures
                self._learn_attack_signature(vuln)
                
                # Check for zero-day indicators
                if self._is_potential_zero_day(vuln):
                    self._add_zero_day_indicator(vuln)
                    learning_summary['zero_day_patterns'] += 1
                
                learning_summary['vulnerabilities_analyzed'] += 1
            
            # Learn from remediation results
            if 'remediation' in scan_results:
                self._learn_from_remediation(scan_results['remediation'])
            
            # Update vulnerability profiles
            self._update_vulnerability_profiles(vulnerabilities)
            
            # Optimize pattern matching
            self._optimize_patterns()
            
            # Save updated knowledge
            self._save_knowledge_base()
            
            # Update statistics
            self.learning_stats['total_vulnerabilities_learned'] += len(vulnerabilities)
            self.learning_stats['patterns_discovered'] += learning_summary['new_patterns_learned']
            self.learning_stats['zero_days_detected'] += learning_summary['zero_day_patterns']
            self.learning_stats['last_training'] = datetime.now().isoformat()
            
            logger.info(f"Learning complete: {learning_summary['new_patterns_learned']} new patterns learned")
            
        except Exception as e:
            logger.error(f"Learning error: {str(e)}")
            learning_summary['error'] = str(e)
        
        return learning_summary
    
    def _extract_vulnerability_patterns(self, vulnerability: Dict) -> List[Dict]:
        """Extract patterns from vulnerability"""
        patterns = []
        
        # Pattern 1: Payload signature
        if 'payload' in vulnerability:
            pattern = {
                'type': 'payload_signature',
                'vulnerability_type': vulnerability.get('type'),
                'signature': self._create_signature(vulnerability['payload']),
                'payload': vulnerability['payload'],
                'severity': vulnerability.get('severity'),
                'confidence': 0.8
            }
            patterns.append(pattern)
        
        # Pattern 2: Response pattern
        if 'evidence' in vulnerability:
            pattern = {
                'type': 'response_pattern',
                'vulnerability_type': vulnerability.get('type'),
                'indicators': self._extract_indicators(vulnerability['evidence']),
                'severity': vulnerability.get('severity'),
                'confidence': 0.7
            }
            patterns.append(pattern)
        
        # Pattern 3: Endpoint pattern
        if 'endpoint' in vulnerability:
            pattern = {
                'type': 'endpoint_pattern',
                'vulnerability_type': vulnerability.get('type'),
                'endpoint_signature': self._create_endpoint_signature(vulnerability['endpoint']),
                'parameters': self._extract_parameters(vulnerability['endpoint']),
                'confidence': 0.6
            }
            patterns.append(pattern)
        
        # Pattern 4: Behavior pattern (for zero-day detection)
        behavior_pattern = self._analyze_behavior(vulnerability)
        if behavior_pattern:
            patterns.append(behavior_pattern)
        
        return patterns
    
    def _create_signature(self, payload: str) -> str:
        """Create unique signature for payload"""
        # Normalize payload
        normalized = payload.lower().strip()
        
        # Extract key elements (SQL keywords, special chars, etc.)
        elements = []
        
        # SQL keywords
        sql_keywords = ['select', 'union', 'insert', 'update', 'delete', 'drop', 'create']
        for keyword in sql_keywords:
            if keyword in normalized:
                elements.append(f'sql:{keyword}')
        
        # Special characters
        special_chars = ["'", '"', ';', '--', '/*', '*/', '<', '>', '&', '|']
        for char in special_chars:
            if char in payload:
                elements.append(f'char:{char}')
        
        # Create signature hash
        signature_str = '|'.join(sorted(elements))
        return hashlib.md5(signature_str.encode()).hexdigest()
    
    def _create_endpoint_signature(self, endpoint: str) -> str:
        """Create signature for endpoint pattern"""
        # Extract structure (remove parameter values)
        import re
        
        # Remove parameter values
        normalized = re.sub(r'=[^&]*', '={value}', endpoint)
        
        # Remove specific IDs
        normalized = re.sub(r'/\d+', '/{id}', normalized)
        
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def _extract_indicators(self, evidence: str) -> List[str]:
        """Extract key indicators from evidence"""
        import re
        
        indicators = []
        
        # Error messages
        error_patterns = [
            r'SQL.*error',
            r'syntax.*error',
            r'Exception',
            r'Warning',
            r'Fatal error'
        ]
        
        for pattern in error_patterns:
            matches = re.findall(pattern, evidence, re.IGNORECASE)
            indicators.extend(matches[:3])  # Top 3 matches
        
        # Extract quoted strings (potential vulnerable parameters)
        quoted = re.findall(r"'([^']*)'", evidence)
        indicators.extend(quoted[:3])
        
        return list(set(indicators))  # Remove duplicates
    
    def _extract_parameters(self, endpoint: str) -> List[str]:
        """Extract parameter names from endpoint"""
        import re
        from urllib.parse import urlparse, parse_qs
        
        try:
            parsed = urlparse(endpoint)
            params = parse_qs(parsed.query)
            return list(params.keys())
        except:
            return []
    
    def _analyze_behavior(self, vulnerability: Dict) -> Optional[Dict]:
        """Analyze vulnerability behavior for zero-day detection"""
        # Look for unusual patterns that might indicate zero-day
        
        behavior_indicators = []
        
        # Unusual response times
        if 'response_time' in vulnerability:
            if vulnerability['response_time'] > 5.0:
                behavior_indicators.append('slow_response')
        
        # Unusual error patterns
        if 'evidence' in vulnerability:
            # Check for non-standard errors
            standard_errors = ['SQL', 'syntax', 'Warning', 'Exception']
            has_standard = any(err in vulnerability['evidence'] for err in standard_errors)
            
            if not has_standard and len(vulnerability['evidence']) > 50:
                behavior_indicators.append('unusual_error')
        
        # Complex payload structure
        if 'payload' in vulnerability:
            if len(vulnerability['payload']) > 100:
                behavior_indicators.append('complex_payload')
        
        if behavior_indicators:
            return {
                'type': 'behavior_pattern',
                'vulnerability_type': vulnerability.get('type'),
                'indicators': behavior_indicators,
                'confidence': 0.5,
                'requires_analysis': True
            }
        
        return None
    
    def _is_new_pattern(self, pattern: Dict) -> bool:
        """Check if pattern is new"""
        pattern_type = pattern.get('type')
        signature = pattern.get('signature') or pattern.get('endpoint_signature')
        
        if not signature:
            return True
        
        # Check against existing patterns
        existing = self.pattern_database.get(pattern_type, {})
        return signature not in existing
    
    def _add_pattern(self, pattern: Dict):
        """Add new pattern to database"""
        pattern_type = pattern.get('type')
        signature = pattern.get('signature') or pattern.get('endpoint_signature')
        
        if pattern_type not in self.pattern_database:
            self.pattern_database[pattern_type] = {}
        
        self.pattern_database[pattern_type][signature] = {
            'pattern': pattern,
            'discovered': datetime.now().isoformat(),
            'occurrences': 1,
            'last_seen': datetime.now().isoformat()
        }
    
    def _update_pattern(self, pattern: Dict):
        """Update existing pattern"""
        pattern_type = pattern.get('type')
        signature = pattern.get('signature') or pattern.get('endpoint_signature')
        
        if pattern_type in self.pattern_database:
            if signature in self.pattern_database[pattern_type]:
                existing = self.pattern_database[pattern_type][signature]
                existing['occurrences'] += 1
                existing['last_seen'] = datetime.now().isoformat()
                
                # Update confidence based on frequency
                pattern_data = existing['pattern']
                pattern_data['confidence'] = min(0.95, pattern_data['confidence'] + 0.05)
    
    def _learn_attack_signature(self, vulnerability: Dict):
        """Learn attack signature for improved detection"""
        vuln_type = vulnerability.get('type')
        
        if vuln_type not in self.attack_signatures:
            self.attack_signatures[vuln_type] = {
                'count': 0,
                'payloads': [],
                'success_rate': 0.0,
                'severity_distribution': defaultdict(int)
            }
        
        sig = self.attack_signatures[vuln_type]
        sig['count'] += 1
        
        # Store unique payloads
        if 'payload' in vulnerability:
            if vulnerability['payload'] not in sig['payloads']:
                sig['payloads'].append(vulnerability['payload'])
        
        # Track severity
        severity = vulnerability.get('severity', 'unknown')
        sig['severity_distribution'][severity] += 1
    
    def _is_potential_zero_day(self, vulnerability: Dict) -> bool:
        """Determine if vulnerability might be a zero-day"""
        
        # Check if it's a known type
        known_types = list(self.attack_signatures.keys())
        
        vuln_type = vulnerability.get('type')
        
        # New vulnerability type
        if vuln_type not in known_types:
            return True
        
        # Known type but unusual characteristics
        if 'payload' in vulnerability:
            known_payloads = self.attack_signatures.get(vuln_type, {}).get('payloads', [])
            
            # Payload similarity check
            is_similar = False
            for known_payload in known_payloads:
                similarity = self._calculate_similarity(vulnerability['payload'], known_payload)
                if similarity > 0.7:
                    is_similar = True
                    break
            
            # If not similar to any known payload, might be zero-day
            if not is_similar and len(known_payloads) > 5:
                return True
        
        return False
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings"""
        # Simple character-based similarity
        set1 = set(str1.lower())
        set2 = set(str2.lower())
        
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _add_zero_day_indicator(self, vulnerability: Dict):
        """Add zero-day indicator for future detection"""
        indicator = {
            'vulnerability': vulnerability.get('type'),
            'payload': vulnerability.get('payload'),
            'evidence': vulnerability.get('evidence'),
            'discovered': datetime.now().isoformat(),
            'confidence': 0.6,
            'verified': False
        }
        
        self.zero_day_indicators.append(indicator)
        
        logger.info(f"Zero-day indicator added: {vulnerability.get('type')}")
    
    def _learn_from_remediation(self, remediation_results: Dict):
        """Learn from remediation success/failure"""
        # Track which fixes work well
        successful = remediation_results.get('successful_remediations', [])
        failed = remediation_results.get('failed_remediations', [])
        
        # Update success rates
        for vuln_type in successful:
            if vuln_type not in self.vulnerability_profiles:
                self.vulnerability_profiles[vuln_type] = {}
            
            profile = self.vulnerability_profiles[vuln_type]
            profile['remediation_success_rate'] = profile.get('remediation_success_rate', 0.5) + 0.1
            profile['remediation_success_rate'] = min(0.95, profile['remediation_success_rate'])
        
        for vuln_type in failed:
            if vuln_type not in self.vulnerability_profiles:
                self.vulnerability_profiles[vuln_type] = {}
            
            profile = self.vulnerability_profiles[vuln_type]
            profile['remediation_success_rate'] = profile.get('remediation_success_rate', 0.5) - 0.05
            profile['remediation_success_rate'] = max(0.1, profile['remediation_success_rate'])
    
    def _update_vulnerability_profiles(self, vulnerabilities: List[Dict]):
        """Update vulnerability profiles with new data"""
        for vuln in vulnerabilities:
            vuln_type = vuln.get('type')
            
            if vuln_type not in self.vulnerability_profiles:
                self.vulnerability_profiles[vuln_type] = {
                    'count': 0,
                    'severity_distribution': defaultdict(int),
                    'common_endpoints': [],
                    'detection_confidence': 0.5
                }
            
            profile = self.vulnerability_profiles[vuln_type]
            profile['count'] += 1
            
            severity = vuln.get('severity', 'unknown')
            profile['severity_distribution'][severity] += 1
            
            # Update detection confidence based on successful detections
            profile['detection_confidence'] = min(0.95, profile['detection_confidence'] + 0.01)
    
    def _optimize_patterns(self):
        """Optimize patterns by removing duplicates and low-confidence patterns"""
        # Remove patterns with very low confidence
        for pattern_type in list(self.pattern_database.keys()):
            patterns = self.pattern_database[pattern_type]
            
            # Remove patterns seen only once in last 30 days
            to_remove = []
            for sig, data in patterns.items():
                if data['occurrences'] == 1:
                    # Check if old
                    last_seen = datetime.fromisoformat(data['last_seen'])
                    age_days = (datetime.now() - last_seen).days
                    
                    if age_days > 30:
                        to_remove.append(sig)
            
            for sig in to_remove:
                del patterns[sig]
    
    def _load_pattern_database(self) -> Dict:
        """Load pattern database"""
        try:
            pattern_file = self.knowledge_base_path / 'pattern_database.json'
            if pattern_file.exists():
                with open(pattern_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load pattern database: {str(e)}")
        
        return {}
    
    def _load_attack_signatures(self) -> Dict:
        """Load attack signatures"""
        try:
            sig_file = self.knowledge_base_path / 'attack_signatures.json'
            if sig_file.exists():
                with open(sig_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load attack signatures: {str(e)}")
        
        return {}
    
    def _load_vulnerability_profiles(self) -> Dict:
        """Load vulnerability profiles"""
        try:
            profile_file = self.knowledge_base_path / 'vulnerability_profiles.json'
            if profile_file.exists():
                with open(profile_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load vulnerability profiles: {str(e)}")
        
        return {}
    
    def _load_false_positive_patterns(self) -> List:
        """Load false positive patterns"""
        try:
            fp_file = self.knowledge_base_path / 'false_positives.json'
            if fp_file.exists():
                with open(fp_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load false positive patterns: {str(e)}")
        
        return []
    
    def _load_zero_day_indicators(self) -> List:
        """Load zero-day indicators"""
        try:
            zd_file = self.knowledge_base_path / 'zero_day_indicators.json'
            if zd_file.exists():
                with open(zd_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load zero-day indicators: {str(e)}")
        
        return []
    
    def _save_knowledge_base(self):
        """Save all learning data"""
        try:
            # Pattern database
            with open(self.knowledge_base_path / 'pattern_database.json', 'w') as f:
                json.dump(self.pattern_database, f, indent=2)
            
            # Attack signatures
            with open(self.knowledge_base_path / 'attack_signatures.json', 'w') as f:
                json.dump(self.attack_signatures, f, indent=2)
            
            # Vulnerability profiles
            with open(self.knowledge_base_path / 'vulnerability_profiles.json', 'w') as f:
                json.dump(self.vulnerability_profiles, f, indent=2)
            
            # Zero-day indicators
            with open(self.knowledge_base_path / 'zero_day_indicators.json', 'w') as f:
                json.dump(self.zero_day_indicators, f, indent=2)
            
            # Learning statistics
            with open(self.knowledge_base_path / 'learning_stats.json', 'w') as f:
                json.dump(self.learning_stats, f, indent=2)
            
            logger.info("Knowledge base saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save knowledge base: {str(e)}")
    
    def get_learning_stats(self) -> Dict:
        """Get current learning statistics"""
        return self.learning_stats.copy()
    
    def export_knowledge_summary(self, output_file: str):
        """Export knowledge base summary"""
        try:
            summary = {
                'timestamp': datetime.now().isoformat(),
                'statistics': self.learning_stats,
                'pattern_count': sum(len(patterns) for patterns in self.pattern_database.values()),
                'attack_signatures_count': len(self.attack_signatures),
                'vulnerability_profiles_count': len(self.vulnerability_profiles),
                'zero_day_indicators_count': len(self.zero_day_indicators),
                'top_vulnerabilities': sorted(
                    [(vtype, data['count']) for vtype, data in self.vulnerability_profiles.items()],
                    key=lambda x: x[1],
                    reverse=True
                )[:10]
            }
            
            with open(output_file, 'w') as f:
                json.dump(summary, f, indent=2)
            
            logger.info(f"Knowledge summary exported to {output_file}")
            
        except Exception as e:
            logger.error(f"Failed to export knowledge summary: {str(e)}")
