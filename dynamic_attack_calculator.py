"""
Dynamic Attack Probability Calculator
Calculates realistic attack success probabilities based on multiple factors
"""

import logging
from typing import Dict, List
import re

logger = logging.getLogger(__name__)


class DynamicAttackCalculator:
    """
    Calculates dynamic attack success probabilities
    Considers WAF, IDS/IPS, patch levels, and other defense mechanisms
    """
    
    def __init__(self):
        """Initialize calculator"""
        self.base_probabilities = {
            'sql_injection': 0.75,
            'xss': 0.70,
            'command_injection': 0.65,
            'path_traversal': 0.60,
            'ssrf': 0.55,
            'xxe': 0.50,
            'csrf': 0.65,
            'idor': 0.70,
            'deserialization': 0.45,
            'default': 0.55  # Changed from 0.50 to 0.55
        }
    
    def calculate_probability(self, vulnerability: Dict, target_info: Dict) -> float:
        """
        Calculate dynamic attack success probability
        
        Args:
            vulnerability: Vulnerability dictionary
            target_info: Target information (headers, technologies, etc.)
            
        Returns:
            Success probability (0.0 to 1.0)
        """
        vuln_type = vulnerability.get('type', 'default').lower()
        base_prob = self.base_probabilities.get(vuln_type, 0.50)
        
        # Apply modifiers
        prob = base_prob
        
        # Check for WAF
        waf_detected = self._detect_waf(target_info)
        if waf_detected:
            prob *= 0.3  # WAF reduces success by 70%
            logger.debug(f"WAF detected, reducing probability to {prob:.2f}")
        
        # Check for IDS/IPS indicators
        ids_detected = self._detect_ids(target_info)
        if ids_detected:
            prob *= 0.5  # IDS reduces success by 50%
            logger.debug(f"IDS detected, reducing probability to {prob:.2f}")
        
        # Check patch level
        patch_level = self._estimate_patch_level(target_info)
        if patch_level == 'current':
            prob *= 0.6  # Current patches reduce success by 40%
        elif patch_level == 'outdated':
            prob *= 1.2  # Outdated increases success by 20%
        
        # Check security headers
        security_headers = self._check_security_headers(target_info)
        if security_headers > 5:
            prob *= 0.8  # Good security headers reduce success by 20%
        elif security_headers < 2:
            prob *= 1.1  # Poor security headers increase success by 10%
        
        # Check vulnerability severity
        severity = vulnerability.get('severity', 'medium').lower()
        if severity == 'critical':
            prob *= 1.1  # Critical vulns slightly easier to exploit
        elif severity == 'low':
            prob *= 0.9  # Low severity slightly harder
        
        # Ensure probability stays in valid range
        prob = max(0.05, min(0.95, prob))
        
        return round(prob, 2)
    
    def _detect_waf(self, target_info: Dict) -> bool:
        """
        Detect Web Application Firewall
        
        Args:
            target_info: Target information
            
        Returns:
            True if WAF detected
        """
        headers = target_info.get('headers', {})
        
        # Convert all headers to lowercase for comparison
        headers_lower = {k.lower(): v.lower() for k, v in headers.items()}
        
        # Common WAF headers
        waf_headers = [
            'x-sucuri-id',
            'x-sucuri-cache',
            'cloudflare',
            'cf-ray',
            'x-cdn',
            'server-id',
            'x-protected-by',
            'x-waf',
            'x-firewall'
        ]
        
        for header in waf_headers:
            if header in headers_lower:
                return True
        
        # Check server header for WAF signatures
        server = headers_lower.get('server', '')
        waf_signatures = ['cloudflare', 'sucuri', 'incapsula', 'akamai', 'imperva']
        
        for sig in waf_signatures:
            if sig in server:
                return True
        
        return False
    
    def _detect_ids(self, target_info: Dict) -> bool:
        """
        Detect Intrusion Detection System indicators
        
        Args:
            target_info: Target information
            
        Returns:
            True if IDS indicators found
        """
        # Check for rate limiting responses
        if target_info.get('rate_limited', False):
            return True
        
        # Check for suspicious response patterns
        response_codes = target_info.get('response_codes', [])
        if 429 in response_codes or 403 in response_codes:
            return True
        
        return False
    
    def _estimate_patch_level(self, target_info: Dict) -> str:
        """
        Estimate patch level based on version information
        
        Args:
            target_info: Target information
            
        Returns:
            'current', 'outdated', or 'unknown'
        """
        technologies = target_info.get('technologies', [])
        
        # Known outdated versions
        outdated_patterns = [
            r'nginx/1\.[0-9]\.', # nginx < 1.10
            r'apache/2\.[0-2]\.', # apache < 2.3
            r'php/[4-5]\.', # php < 6
            r'openssh/[1-6]\.', # openssh < 7
        ]
        
        for tech in technologies:
            tech_lower = tech.lower()
            for pattern in outdated_patterns:
                if re.search(pattern, tech_lower):
                    return 'outdated'
        
        # If we have version info but no outdated matches, assume current
        if technologies:
            return 'current'
        
        return 'unknown'
    
    def _check_security_headers(self, target_info: Dict) -> int:
        """
        Count security headers present
        
        Args:
            target_info: Target information
            
        Returns:
            Number of security headers found
        """
        headers = target_info.get('headers', {})
        
        security_headers = [
            'x-frame-options',
            'x-content-type-options',
            'strict-transport-security',
            'content-security-policy',
            'x-xss-protection',
            'referrer-policy',
            'permissions-policy'
        ]
        
        count = 0
        for sec_header in security_headers:
            if any(sec_header in h.lower() for h in headers.keys()):
                count += 1
        
        return count
    
    def calculate_detection_risk(self, vulnerability: Dict, target_info: Dict) -> float:
        """
        Calculate risk of detection during exploitation
        
        Args:
            vulnerability: Vulnerability dictionary
            target_info: Target information
            
        Returns:
            Detection risk (0.0 to 1.0)
        """
        base_risk = 0.3  # Base 30% detection risk
        
        # WAF increases detection risk
        if self._detect_waf(target_info):
            base_risk += 0.4
        
        # IDS increases detection risk
        if self._detect_ids(target_info):
            base_risk += 0.3
        
        # Logging increases detection risk
        if target_info.get('logging_enabled', False):
            base_risk += 0.1
        
        # Ensure risk stays in valid range
        return min(0.95, base_risk)


# Singleton instance
_calculator_instance = None


def get_attack_calculator() -> DynamicAttackCalculator:
    """Get singleton attack calculator instance"""
    global _calculator_instance
    if _calculator_instance is None:
        _calculator_instance = DynamicAttackCalculator()
    return _calculator_instance
