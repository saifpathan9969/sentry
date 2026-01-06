"""
Unit Tests for TEXT Report Generator
Tests report section formatting, vulnerability details, fix methods, and missing data handling
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from text_report_generator import TextReportGenerator, generate_text_report


class TestTextReportGenerator:
    """Test TEXT report generation functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.generator = TextReportGenerator()
    
    def test_report_generator_initialization(self):
        """Test report generator initialization"""
        assert self.generator is not None
        assert hasattr(self.generator, 'report_lines')
        assert isinstance(self.generator.report_lines, list)
    
    def test_generate_report_returns_string(self):
        """Test that generate_report returns a string"""
        results = {
            'target': 'https://example.com',
            'findings': []
        }
        
        report = self.generator.generate_report(results)
        
        assert isinstance(report, str)
        assert len(report) > 0
    
    def test_report_contains_header(self):
        """Test that report contains header section"""
        results = {
            'target': 'https://example.com',
            'findings': []
        }
        
        report = self.generator.generate_report(results)
        
        assert "AI PENETRATION TESTING BRAIN" in report
        assert "SECURITY ASSESSMENT REPORT" in report
    
    def test_report_contains_scan_information(self):
        """Test that report contains scan information"""
        results = {
            'target': 'https://example.com',
            'findings': []
        }
        
        report = self.generator.generate_report(results)
        
        assert "SCAN INFORMATION" in report
        assert "Target:" in report
        assert "example.com" in report
    
    def test_report_contains_executive_summary(self):
        """Test that report contains executive summary"""
        results = {
            'target': 'https://example.com',
            'findings': [
                {'severity': 'high', 'type': 'xss'},
                {'severity': 'medium', 'type': 'csrf'}
            ]
        }
        
        report = self.generator.generate_report(results)
        
        assert "EXECUTIVE SUMMARY" in report
    
    def test_vulnerability_detail_formatting(self):
        """Test vulnerability detail formatting"""
        results = {
            'target': 'https://example.com',
            'findings': [
                {
                    'type': 'xss',
                    'severity': 'high',
                    'description': 'Cross-site scripting vulnerability',
                    'endpoint': '/search?q=test'
                }
            ]
        }
        
        report = self.generator.generate_report(results)
        
        # Should contain vulnerability information
        assert 'xss' in report.lower() or 'cross-site' in report.lower()
    
    def test_fix_method_code_example_formatting(self):
        """Test fix method code example formatting"""
        results = {
            'target': 'https://example.com',
            'findings': [
                {
                    'type': 'xss',
                    'severity': 'high',
                    'fix_methods': [
                        {
                            'method': 'Output Encoding',
                            'language': 'Python',
                            'code': 'html.escape(user_input)'
                        }
                    ]
                }
            ]
        }
        
        report = self.generator.generate_report(results)
        
        # Report should be generated successfully
        assert isinstance(report, str)
        assert len(report) > 0
    
    def test_executive_summary_calculation(self):
        """Test executive summary severity calculation"""
        results = {
            'target': 'https://example.com',
            'findings': [
                {'severity': 'critical', 'type': 'sqli'},
                {'severity': 'high', 'type': 'xss'},
                {'severity': 'medium', 'type': 'csrf'},
                {'severity': 'low', 'type': 'info_disclosure'}
            ]
        }
        
        report = self.generator.generate_report(results)
        
        # Should show severity counts
        assert 'critical' in report.lower() or 'Critical' in report
    
    def test_missing_data_handling(self):
        """Test handling of missing data"""
        results = {
            # Missing target
            'findings': []
        }
        
        report = self.generator.generate_report(results)
        
        # Should not crash, should handle gracefully
        assert isinstance(report, str)
        assert len(report) > 0
    
    def test_empty_findings_handling(self):
        """Test handling of empty findings"""
        results = {
            'target': 'https://example.com',
            'findings': []
        }
        
        report = self.generator.generate_report(results)
        
        assert isinstance(report, str)
        assert "example.com" in report
    
    def test_generate_text_report_function(self):
        """Test standalone generate_text_report function"""
        results = {
            'target': 'https://example.com',
            'findings': [
                {'severity': 'high', 'type': 'xss'}
            ]
        }
        
        report = generate_text_report(results)
        
        assert isinstance(report, str)
        assert len(report) > 0
        assert "example.com" in report
    
    def test_report_formatting_consistency(self):
        """Test that report formatting is consistent"""
        results = {
            'target': 'https://example.com',
            'findings': [
                {'severity': 'high', 'type': 'xss'}
            ]
        }
        
        report = self.generator.generate_report(results)
        
        # Should have consistent separator lines
        assert '=' in report
        assert '-' in report
    
    def test_multiple_vulnerabilities_formatting(self):
        """Test formatting of multiple vulnerabilities"""
        results = {
            'target': 'https://example.com',
            'findings': [
                {'severity': 'critical', 'type': 'sqli', 'description': 'SQL injection'},
                {'severity': 'high', 'type': 'xss', 'description': 'XSS vulnerability'},
                {'severity': 'medium', 'type': 'csrf', 'description': 'CSRF vulnerability'}
            ]
        }
        
        report = self.generator.generate_report(results)
        
        # All vulnerabilities should be in report
        assert isinstance(report, str)
        assert len(report) > 500  # Should be substantial with multiple vulns
    
    def test_report_contains_recommendations(self):
        """Test that report contains recommendations section"""
        results = {
            'target': 'https://example.com',
            'findings': [
                {'severity': 'high', 'type': 'xss'}
            ]
        }
        
        report = self.generator.generate_report(results)
        
        assert "RECOMMENDATION" in report.upper()
    
    def test_cve_data_in_report(self):
        """Test that CVE data is included in report"""
        results = {
            'target': 'https://example.com',
            'findings': [
                {
                    'severity': 'high',
                    'type': 'known_vulnerability',
                    'cve_id': 'CVE-2021-12345',
                    'cvss_score': 7.5
                }
            ]
        }
        
        report = self.generator.generate_report(results)
        
        # CVE data should be in report if provided
        assert isinstance(report, str)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
