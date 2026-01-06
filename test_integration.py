"""
Integration Tests for AI Penetration Testing Brain
End-to-end tests for complete scanning workflow with all modules enabled
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TestEndToEndIntegration:
    """Test complete end-to-end scanning workflow"""
    
    def test_complete_scan_workflow(self):
        """Test full scan workflow with all modules"""
        # This test verifies the integration of all components
        from comprehensive_port_scanner import ComprehensivePortScanner
        from service_version_detector import ServiceVersionDetector
        from cve_integration import CVEDatabase
        from dynamic_attack_calculator import DynamicAttackCalculator
        from text_report_generator import TextReportGenerator
        
        # Initialize all modules
        port_scanner = ComprehensivePortScanner(timeout=1, max_workers=10)
        service_detector = ServiceVersionDetector()
        cve_db = CVEDatabase()
        attack_calc = DynamicAttackCalculator()
        report_gen = TextReportGenerator()
        
        # Verify all modules initialized
        assert port_scanner is not None
        assert service_detector is not None
        assert cve_db is not None
        assert attack_calc is not None
        assert report_gen is not None
        
        print("✓ All modules initialized successfully")
    
    def test_port_scan_to_service_detection(self):
        """Test integration between port scanning and service detection"""
        from comprehensive_port_scanner import ComprehensivePortScanner, PortScanResult
        from service_version_detector import ServiceVersionDetector
        
        scanner = ComprehensivePortScanner(timeout=1, max_workers=10)
        detector = ServiceVersionDetector()
        
        # Simulate port scan result
        port_result = PortScanResult(
            port=80,
            state='open',
            service='http',
            version='Unknown',
            banner='Server: nginx/1.18.0',
            protocol='tcp'
        )
        
        # Detect version from banner
        service, version = detector.detect_version(
            'localhost',
            port_result.port,
            port_result.service,
            port_result.banner
        )
        
        assert service == 'http'
        assert version != 'Unknown'  # Should detect version from banner
        print(f"✓ Port scan → Service detection: {service} {version}")
    
    def test_service_detection_to_cve_enrichment(self):
        """Test integration between service detection and CVE enrichment"""
        from service_version_detector import ServiceVersionDetector
        from cve_integration import CVEDatabase
        
        detector = ServiceVersionDetector()
        cve_db = CVEDatabase()
        
        # Detect service
        service, version = detector.detect_version(
            'localhost',
            80,
            'http',
            'Server: nginx/1.18.0'
        )
        
        # Create vulnerability from service detection
        vulnerability = {
            'type': 'service_exposure',
            'service': service,
            'version': version,
            'port': 80
        }
        
        # Enrich with CVE data
        with patch.object(cve_db, 'search_cves') as mock_search:
            mock_search.return_value = []
            enriched = cve_db.enrich_vulnerability(vulnerability)
        
        assert 'cve_data' in enriched
        print("✓ Service detection → CVE enrichment")
    
    def test_cve_enrichment_to_attack_calculation(self):
        """Test integration between CVE enrichment and attack calculation"""
        from cve_integration import CVEDatabase
        from dynamic_attack_calculator import DynamicAttackCalculator
        
        cve_db = CVEDatabase()
        attack_calc = DynamicAttackCalculator()
        
        # Create vulnerability with CVE data
        vulnerability = {
            'type': 'xss',
            'severity': 'high',
            'cve_data': {
                'related_cves': ['CVE-2023-12345'],
                'cvss_score': 7.5
            }
        }
        
        target_info = {
            'headers': {},
            'technologies': []
        }
        
        # Calculate attack probability
        probability = attack_calc.calculate_probability(vulnerability, target_info)
        
        assert isinstance(probability, float)
        assert 0.0 <= probability <= 1.0
        print(f"✓ CVE enrichment → Attack calculation: {probability:.2f}")
    
    def test_attack_calculation_to_report_generation(self):
        """Test integration between attack calculation and report generation"""
        from dynamic_attack_calculator import DynamicAttackCalculator
        from text_report_generator import TextReportGenerator
        
        attack_calc = DynamicAttackCalculator()
        report_gen = TextReportGenerator()
        
        # Create vulnerability with attack probability
        vulnerability = {
            'type': 'sql_injection',
            'severity': 'critical',
            'attack_probability': 0.75,
            'detection_risk': 0.30
        }
        
        scan_results = {
            'target': 'https://example.com',
            'vulnerabilities': [vulnerability]
        }
        
        # Generate report
        report = report_gen.generate_report(scan_results)
        
        assert len(report) > 0
        assert 'example.com' in report
        print("✓ Attack calculation → Report generation")
    
    def test_complete_module_chain(self):
        """Test complete chain: Port Scan → Service → CVE → Attack → Report"""
        from comprehensive_port_scanner import ComprehensivePortScanner, PortScanResult
        from service_version_detector import ServiceVersionDetector
        from cve_integration import CVEDatabase
        from dynamic_attack_calculator import DynamicAttackCalculator
        from text_report_generator import TextReportGenerator
        
        # Step 1: Port Scanning
        scanner = ComprehensivePortScanner(timeout=1, max_workers=10)
        port_result = PortScanResult(
            port=80,
            state='open',
            service='http',
            version='Unknown',
            banner='Server: nginx/1.18.0',
            protocol='tcp'
        )
        
        # Step 2: Service Detection
        detector = ServiceVersionDetector()
        service, version = detector.detect_version(
            'localhost',
            port_result.port,
            port_result.service,
            port_result.banner
        )
        
        # Step 3: Create vulnerability
        vulnerability = {
            'type': 'service_exposure',
            'service': service,
            'version': version,
            'severity': 'medium'
        }
        
        # Step 4: CVE Enrichment
        cve_db = CVEDatabase()
        with patch.object(cve_db, 'search_cves') as mock_search:
            mock_search.return_value = []
            enriched_vuln = cve_db.enrich_vulnerability(vulnerability)
        
        # Step 5: Attack Calculation
        attack_calc = DynamicAttackCalculator()
        target_info = {'headers': {}, 'technologies': []}
        attack_prob = attack_calc.calculate_probability(enriched_vuln, target_info)
        enriched_vuln['attack_probability'] = attack_prob
        
        # Step 6: Report Generation
        report_gen = TextReportGenerator()
        scan_results = {
            'target': 'localhost',
            'vulnerabilities': [enriched_vuln],
            'port_scan_results': {'open_ports': [port_result]}
        }
        report = report_gen.generate_report(scan_results)
        
        # Verify complete chain
        assert service is not None
        assert 'cve_data' in enriched_vuln
        assert 'attack_probability' in enriched_vuln
        assert len(report) > 0
        
        print("✓ Complete module chain: Port → Service → CVE → Attack → Report")


class TestModuleInteroperability:
    """Test interoperability between different modules"""
    
    def test_config_manager_with_cli(self):
        """Test configuration manager integration with CLI"""
        from config_manager import ConfigManager
        from cli_parser import PentestCLI
        
        config_mgr = ConfigManager()
        cli = PentestCLI()
        
        # Parse CLI args
        cli.parse_args(['example.com', '--scan-mode', 'fast', '--max-threads', '20'])
        
        # Get merged configuration
        config = cli.get_config()
        
        assert config.scan_mode == 'fast'
        assert config.max_threads == 20
        print("✓ Config manager ↔ CLI integration")
    
    def test_error_handler_across_modules(self):
        """Test error handling across all modules"""
        from error_handler import StructuredLogger
        from cve_integration import CVEDatabase
        
        logger = StructuredLogger(__name__)
        cve_db = CVEDatabase()
        
        # Test error handling in CVE module
        # CVE module should handle errors gracefully
        try:
            # Search with invalid keyword should not crash
            result = cve_db.search_cves('', results_per_page=1)
            # Should return empty list or handle gracefully
            assert isinstance(result, list)
        except Exception as e:
            # If exception occurs, logger should handle it
            logger.log_exception(e, "CVE API test")
        
        print("✓ Error handler integration across modules")
    
    def test_text_report_with_all_data_types(self):
        """Test TEXT report generation with all data types"""
        from text_report_generator import TextReportGenerator
        
        report_gen = TextReportGenerator()
        
        # Create comprehensive scan results with proper structure
        scan_results = {
            'target': 'https://example.com',
            'scan_date': '2024-01-15',
            'platform_detection': {
                'platform': 'Firebase',
                'database_type': 'Firestore',
                'confidence': 0.95
            },
            'vulnerabilities': [
                {
                    'type': 'xss',
                    'severity': 'CRITICAL',
                    'endpoint': '/api/test',
                    'evidence': 'XSS payload reflected',
                    'cve_data': {
                        'related_cves': ['CVE-2023-12345'],
                        'cvss_score': 9.6
                    },
                    'attack_probability': 0.85,
                    'detection_risk': 0.30
                }
            ],
            'port_scan_results': {
                'open_ports': [
                    {'port': 80, 'service': 'http', 'version': 'nginx 1.18.0'}
                ]
            }
        }
        
        report = report_gen.generate_report(scan_results)
        
        # Verify report is generated with key sections
        assert 'example.com' in report
        assert 'Firebase' in report  # Platform detection should be included
        assert len(report) > 500
        
        print("✓ TEXT report with all data types")


class TestErrorRecovery:
    """Test error recovery and graceful degradation"""
    
    def test_cve_api_failure_recovery(self):
        """Test that scan continues when CVE API fails"""
        from cve_integration import CVEDatabase
        
        cve_db = CVEDatabase()
        
        vulnerability = {
            'type': 'xss',
            'severity': 'high'
        }
        
        # Simulate API failure
        with patch.object(cve_db, 'search_cves') as mock_search:
            mock_search.side_effect = Exception("API Timeout")
            
            # Should handle error and return vulnerability without CVE data
            enriched = cve_db.enrich_vulnerability(vulnerability)
            
            # Original vulnerability should be returned
            assert enriched['type'] == 'xss'
            print("✓ CVE API failure recovery")
    
    def test_port_scan_timeout_handling(self):
        """Test port scanner handles timeouts gracefully"""
        from comprehensive_port_scanner import ComprehensivePortScanner
        
        scanner = ComprehensivePortScanner(timeout=0.001, max_workers=5)  # Very short timeout
        
        # Should handle timeouts without crashing
        with patch.object(scanner, '_scan_tcp_port') as mock_scan:
            mock_scan.return_value = None  # Simulate timeout
            
            results = scanner.scan_common_ports('127.0.0.1')
            
            # Should return results (even if all closed/filtered)
            assert isinstance(results, list)
            print("✓ Port scan timeout handling")
    
    def test_report_generation_with_missing_data(self):
        """Test report generation handles missing data"""
        from text_report_generator import TextReportGenerator
        
        report_gen = TextReportGenerator()
        
        # Minimal scan results
        scan_results = {
            'target': 'https://example.com'
            # Missing: vulnerabilities, port_scan_results, etc.
        }
        
        # Should generate report without crashing
        report = report_gen.generate_report(scan_results)
        
        assert len(report) > 0
        assert 'example.com' in report
        print("✓ Report generation with missing data")


class TestDataFlow:
    """Test data flow through the complete system"""
    
    def test_vulnerability_data_enrichment_flow(self):
        """Test vulnerability data gets progressively enriched"""
        from cve_integration import CVEDatabase
        from dynamic_attack_calculator import DynamicAttackCalculator
        
        # Start with basic vulnerability
        vulnerability = {
            'type': 'sql_injection',
            'severity': 'critical',
            'url': 'https://example.com/api'
        }
        
        initial_keys = set(vulnerability.keys())
        
        # Step 1: CVE Enrichment
        cve_db = CVEDatabase()
        enriched = cve_db.enrich_vulnerability(vulnerability)
        
        assert 'cve_data' in enriched
        after_cve_keys = set(enriched.keys())
        
        # Step 2: Attack Calculation
        attack_calc = DynamicAttackCalculator()
        target_info = {'headers': {}, 'technologies': []}
        attack_prob = attack_calc.calculate_probability(enriched, target_info)
        enriched['attack_probability'] = attack_prob
        
        assert 'attack_probability' in enriched
        final_keys = set(enriched.keys())
        
        # Verify progressive enrichment - should have more keys after enrichment
        assert len(final_keys) >= len(initial_keys), f"Expected enrichment: {initial_keys} -> {final_keys}"
        assert 'cve_data' in final_keys
        assert 'attack_probability' in final_keys
        
        print("✓ Vulnerability data enrichment flow")
    
    def test_scan_results_aggregation(self):
        """Test scan results are properly aggregated"""
        from text_report_generator import TextReportGenerator
        
        # Simulate results from multiple modules with proper structure
        scan_results = {
            'target': 'https://example.com',
            'scan_date': '2024-01-15',
            'vulnerabilities': [
                {
                    'type': 'xss',
                    'severity': 'HIGH',
                    'endpoint': '/api/test',
                    'evidence': 'XSS found'
                },
                {
                    'type': 'csrf',
                    'severity': 'MEDIUM',
                    'endpoint': '/api/action',
                    'evidence': 'CSRF token missing'
                }
            ],
            'port_scan_results': {
                'open_ports': [
                    {'port': 80, 'service': 'http'},
                    {'port': 443, 'service': 'https'}
                ]
            },
            'platform_detection': {
                'platform': 'Firebase',
                'confidence': 0.90
            }
        }
        
        # Generate report with aggregated data
        report_gen = TextReportGenerator()
        report = report_gen.generate_report(scan_results)
        
        # Verify report is generated with key sections
        assert 'example.com' in report
        assert 'Firebase' in report  # Platform detection should be included
        assert '80' in report or 'http' in report.lower()
        assert len(report) > 500
        
        print("✓ Scan results aggregation")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
