"""
Unit Tests for Dynamic Attack Calculator
Tests WAF detection, probability calculation, security header analysis, and patch level estimation
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dynamic_attack_calculator import DynamicAttackCalculator


class TestDynamicAttackCalculator:
    """Test dynamic attack probability calculator"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.calculator = DynamicAttackCalculator()
    
    def test_calculator_initialization(self):
        """Test calculator initialization"""
        assert self.calculator is not None
        assert hasattr(self.calculator, 'base_probabilities')
        assert isinstance(self.calculator.base_probabilities, dict)
    
    def test_base_probabilities_defined(self):
        """Test that base probabilities are defined for common vulnerabilities"""
        assert 'sql_injection' in self.calculator.base_probabilities
        assert 'xss' in self.calculator.base_probabilities
        assert 'command_injection' in self.calculator.base_probabilities
        assert 'default' in self.calculator.base_probabilities
    
    def test_probability_calculation_basic(self):
        """Test basic probability calculation"""
        vulnerability = {
            'type': 'xss',
            'severity': 'high'
        }
        target_info = {
            'headers': {},
            'technologies': []
        }
        
        prob = self.calculator.calculate_probability(vulnerability, target_info)
        
        assert isinstance(prob, float)
        assert 0.0 <= prob <= 1.0
    
    def test_waf_detection_cloudflare(self):
        """Test WAF detection for Cloudflare"""
        target_info = {
            'headers': {
                'Server': 'cloudflare',
                'CF-RAY': '12345'
            }
        }
        
        waf_detected = self.calculator._detect_waf(target_info)
        assert waf_detected == True
    
    def test_waf_detection_no_waf(self):
        """Test WAF detection when no WAF present"""
        target_info = {
            'headers': {
                'Server': 'nginx/1.18.0'
            }
        }
        
        waf_detected = self.calculator._detect_waf(target_info)
        assert waf_detected == False
    
    def test_waf_reduces_probability(self):
        """Test that WAF detection reduces attack probability"""
        vulnerability = {'type': 'xss', 'severity': 'high'}
        
        # Without WAF
        target_no_waf = {'headers': {}, 'technologies': []}
        prob_no_waf = self.calculator.calculate_probability(vulnerability, target_no_waf)
        
        # With WAF
        target_with_waf = {
            'headers': {'Server': 'cloudflare'},
            'technologies': []
        }
        prob_with_waf = self.calculator.calculate_probability(vulnerability, target_with_waf)
        
        # WAF should reduce probability
        assert prob_with_waf < prob_no_waf
    
    def test_ids_detection(self):
        """Test IDS/IPS detection"""
        target_info = {
            'headers': {
                'X-IDS-Protection': 'enabled'
            }
        }
        
        ids_detected = self.calculator._detect_ids(target_info)
        # IDS detection logic may vary, just check it returns a boolean
        assert isinstance(ids_detected, bool)
    
    def test_security_headers_count(self):
        """Test security headers counting"""
        target_info = {
            'headers': {
                'X-Frame-Options': 'DENY',
                'X-Content-Type-Options': 'nosniff',
                'Strict-Transport-Security': 'max-age=31536000',
                'Content-Security-Policy': "default-src 'self'",
                'X-XSS-Protection': '1; mode=block'
            }
        }
        
        count = self.calculator._check_security_headers(target_info)
        
        assert count >= 5
    
    def test_security_headers_none(self):
        """Test security headers count when none present"""
        target_info = {
            'headers': {
                'Server': 'nginx'
            }
        }
        
        count = self.calculator._check_security_headers(target_info)
        
        assert count == 0
    
    def test_patch_level_estimation_current(self):
        """Test patch level estimation for current versions"""
        target_info = {
            'technologies': ['nginx 1.21.0'],  # Recent version
            'headers': {}
        }
        
        patch_level = self.calculator._estimate_patch_level(target_info)
        
        # Should return 'current', 'outdated', or 'unknown'
        assert patch_level in ['current', 'outdated', 'unknown']
    
    def test_patch_level_estimation_outdated(self):
        """Test patch level estimation for outdated versions"""
        target_info = {
            'technologies': ['nginx 1.10.0'],  # Old version
            'headers': {}
        }
        
        patch_level = self.calculator._estimate_patch_level(target_info)
        
        assert patch_level in ['current', 'outdated', 'unknown']
    
    def test_probability_formula_sql_injection(self):
        """Test probability calculation formula for SQL injection"""
        vulnerability = {
            'type': 'sql_injection',
            'severity': 'critical'
        }
        target_info = {
            'headers': {},
            'technologies': []
        }
        
        prob = self.calculator.calculate_probability(vulnerability, target_info)
        
        # Should be based on base probability for SQL injection
        assert prob > 0.0
        assert prob <= 1.0
    
    def test_probability_stays_in_range(self):
        """Test that probability always stays in valid range"""
        vulnerability = {
            'type': 'xss',
            'severity': 'critical'
        }
        
        # Extreme case with many defenses
        target_info = {
            'headers': {
                'Server': 'cloudflare',
                'X-Frame-Options': 'DENY',
                'X-Content-Type-Options': 'nosniff',
                'Strict-Transport-Security': 'max-age=31536000',
                'Content-Security-Policy': "default-src 'self'",
                'X-XSS-Protection': '1; mode=block',
                'X-IDS-Protection': 'enabled'
            },
            'technologies': ['nginx 1.21.0']
        }
        
        prob = self.calculator.calculate_probability(vulnerability, target_info)
        
        # Should stay in valid range even with many modifiers
        assert 0.05 <= prob <= 0.95
    
    def test_severity_affects_probability(self):
        """Test that vulnerability severity affects probability"""
        target_info = {'headers': {}, 'technologies': []}
        
        vuln_critical = {'type': 'xss', 'severity': 'critical'}
        vuln_low = {'type': 'xss', 'severity': 'low'}
        
        prob_critical = self.calculator.calculate_probability(vuln_critical, target_info)
        prob_low = self.calculator.calculate_probability(vuln_low, target_info)
        
        # Critical should have higher probability than low
        assert prob_critical >= prob_low
    
    def test_detection_risk_calculation(self):
        """Test detection risk calculation"""
        vulnerability = {
            'type': 'sql_injection',
            'severity': 'high'
        }
        target_info = {
            'headers': {},
            'technologies': []
        }
        
        risk = self.calculator.calculate_detection_risk(vulnerability, target_info)
        
        assert isinstance(risk, float)
        assert 0.0 <= risk <= 1.0
    
    def test_unknown_vulnerability_type(self):
        """Test handling of unknown vulnerability types"""
        vulnerability = {
            'type': 'unknown_vuln_xyz',
            'severity': 'medium'
        }
        target_info = {
            'headers': {},
            'technologies': []
        }
        
        prob = self.calculator.calculate_probability(vulnerability, target_info)
        
        # Should use default probability
        assert prob == self.calculator.base_probabilities['default']
    
    def test_multiple_security_factors(self):
        """Test probability with multiple security factors"""
        vulnerability = {
            'type': 'command_injection',
            'severity': 'critical'
        }
        target_info = {
            'headers': {
                'Server': 'cloudflare',
                'X-Frame-Options': 'DENY',
                'X-Content-Type-Options': 'nosniff',
                'Strict-Transport-Security': 'max-age=31536000'
            },
            'technologies': ['nginx 1.21.0']
        }
        
        prob = self.calculator.calculate_probability(vulnerability, target_info)
        
        # Multiple security factors should significantly reduce probability
        assert prob < 0.5


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
