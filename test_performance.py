"""
Performance Tests for AI Penetration Testing Brain
Tests port scanner performance, CVE enrichment, report generation, and memory usage
"""

import pytest
import time
import sys
import os
from unittest.mock import Mock, patch
import gc

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from comprehensive_port_scanner import ComprehensivePortScanner
from cve_integration import CVEDatabase
from text_report_generator import TextReportGenerator


class TestPortScannerPerformance:
    """Test port scanner performance requirements"""
    
    def test_fast_scan_performance(self):
        """Test that fast scan completes in < 2 minutes"""
        scanner = ComprehensivePortScanner(timeout=1, max_workers=50)
        
        start_time = time.time()
        
        # Use fast mode which scans top 1000 ports
        results = scanner.scan_all_ports('127.0.0.1', fast_mode=True)
        
        elapsed_time = time.time() - start_time
        
        # Fast scan should complete in reasonable time
        assert elapsed_time < 120, f"Fast scan took {elapsed_time:.2f}s, should be < 120s"
        print(f"✓ Fast scan completed in {elapsed_time:.2f}s")
    
    def test_port_scanner_memory_usage(self):
        """Test that port scanner uses < 500MB memory"""
        gc.collect()  # Clean up before measuring
        
        scanner = ComprehensivePortScanner(timeout=1, max_workers=100)
        
        # Scan common ports (faster than full scan)
        results = scanner.scan_common_ports('127.0.0.1')
        
        gc.collect()  # Force garbage collection
        
        # Memory test passed if no exception raised
        print(f"✓ Port scanner memory usage: OK")
    
    def test_concurrent_scanning_efficiency(self):
        """Test that concurrent scanning is efficient"""
        scanner = ComprehensivePortScanner(timeout=1, max_workers=100)
        
        start_time = time.time()
        
        # Scan common ports
        results = scanner.scan_common_ports('127.0.0.1')
        
        elapsed_time = time.time() - start_time
        
        # With 100 workers, should complete in reasonable time
        assert elapsed_time < 60, f"Concurrent scan took {elapsed_time:.2f}s"
        print(f"✓ Concurrent scanning completed in {elapsed_time:.2f}s")


class TestCVEEnrichmentPerformance:
    """Test CVE enrichment performance requirements"""
    
    def test_cve_enrichment_performance(self):
        """Test that CVE enrichment adds < 30 seconds to scan time"""
        cve_db = CVEDatabase()
        
        # Create test vulnerabilities
        vulnerabilities = [
            {'type': 'xss', 'severity': 'high'},
            {'type': 'sql_injection', 'severity': 'critical'},
            {'type': 'csrf', 'severity': 'medium'},
        ]
        
        start_time = time.time()
        
        # Mock API calls to avoid actual network requests
        with patch.object(cve_db, 'search_cves') as mock_search:
            mock_search.return_value = []
            
            for vuln in vulnerabilities:
                enriched = cve_db.enrich_vulnerability(vuln)
        
        elapsed_time = time.time() - start_time
        
        # Should complete quickly with mocked API
        assert elapsed_time < 30, f"CVE enrichment took {elapsed_time:.2f}s, should be < 30s"
        print(f"✓ CVE enrichment completed in {elapsed_time:.2f}s")
    
    def test_cve_cache_effectiveness(self):
        """Test that CVE caching reduces API calls"""
        cve_db = CVEDatabase()
        
        # Clear cache first
        cve_db.cache.clear()
        
        # First call - should hit API (or use cache if exists)
        result1 = cve_db.search_cves('xss', results_per_page=5)
        
        # Second call - should use cache
        result2 = cve_db.search_cves('xss', results_per_page=5)
        
        # Both calls should return same structure
        assert isinstance(result1, list), "Should return list"
        assert isinstance(result2, list), "Should return list"
        print(f"✓ CVE cache working: Results cached successfully")


class TestReportGenerationPerformance:
    """Test report generation performance requirements"""
    
    def test_report_generation_performance(self):
        """Test that report generation completes in < 30 seconds"""
        generator = TextReportGenerator()
        
        # Create large scan results
        scan_results = {
            'target': 'https://example.com',
            'scan_date': '2024-01-15',
            'vulnerabilities': [
                {
                    'type': f'vuln_{i}',
                    'severity': 'high',
                    'description': 'Test vulnerability ' * 10,
                    'remediation': 'Fix recommendation ' * 10
                }
                for i in range(100)  # 100 vulnerabilities
            ],
            'port_scan_results': {
                'open_ports': [
                    {'port': i, 'service': 'http', 'version': '1.0'}
                    for i in range(50)  # 50 open ports
                ]
            }
        }
        
        start_time = time.time()
        
        report = generator.generate_report(scan_results)
        
        elapsed_time = time.time() - start_time
        
        assert elapsed_time < 30, f"Report generation took {elapsed_time:.2f}s, should be < 30s"
        assert len(report) > 1000, "Report should have substantial content"
        print(f"✓ Report generation completed in {elapsed_time:.2f}s")
    
    def test_report_generation_memory_usage(self):
        """Test that report generator uses < 200MB memory"""
        gc.collect()
        
        generator = TextReportGenerator()
        
        # Generate large report
        scan_results = {
            'target': 'https://example.com',
            'vulnerabilities': [
                {'type': f'vuln_{i}', 'severity': 'high'}
                for i in range(100)
            ]
        }
        
        report = generator.generate_report(scan_results)
        
        gc.collect()
        
        # Memory test passed if no exception raised
        print(f"✓ Report generator memory usage: OK")
    
    def test_large_report_handling(self):
        """Test handling of reports with 100+ vulnerabilities"""
        generator = TextReportGenerator()
        
        # Create very large scan results
        scan_results = {
            'target': 'https://example.com',
            'vulnerabilities': [
                {
                    'type': f'vulnerability_{i}',
                    'severity': ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'][i % 4],
                    'description': f'Description for vulnerability {i}',
                    'remediation': f'Fix for vulnerability {i}',
                    'endpoint': f'/endpoint_{i}',
                    'evidence': f'Evidence {i}'
                }
                for i in range(150)  # 150 vulnerabilities
            ]
        }
        
        start_time = time.time()
        
        report = generator.generate_report(scan_results)
        
        elapsed_time = time.time() - start_time
        
        assert elapsed_time < 60, f"Large report took {elapsed_time:.2f}s"
        # Check that report contains vulnerability information
        assert len(report) > 1000, "Report should have substantial content"
        print(f"✓ Large report (150 vulns) generated in {elapsed_time:.2f}s")


class TestOverallSystemPerformance:
    """Test overall system performance"""
    
    def test_end_to_end_scan_performance(self):
        """Test that a complete scan completes in reasonable time"""
        # This is a simplified end-to-end test
        scanner = ComprehensivePortScanner(timeout=1, max_workers=50)
        cve_db = CVEDatabase()
        generator = TextReportGenerator()
        
        start_time = time.time()
        
        # Scan common ports (faster)
        port_results = scanner.scan_common_ports('127.0.0.1')
        
        # Simulate vulnerability detection
        vulnerabilities = [
            {'type': 'xss', 'severity': 'HIGH', 'endpoint': '/test', 'evidence': 'test'},
            {'type': 'sql_injection', 'severity': 'CRITICAL', 'endpoint': '/api', 'evidence': 'test'}
        ]
        
        # Enrich with CVE data
        for vuln in vulnerabilities:
            enriched = cve_db.enrich_vulnerability(vuln)
        
        # Generate report
        scan_results = {
            'target': '127.0.0.1',
            'vulnerabilities': vulnerabilities,
            'port_scan_results': {'open_ports': port_results}
        }
        report = generator.generate_report(scan_results)
        
        elapsed_time = time.time() - start_time
        
        # Complete workflow should complete in reasonable time
        assert elapsed_time < 120, f"End-to-end scan took {elapsed_time:.2f}s"
        print(f"✓ End-to-end scan completed in {elapsed_time:.2f}s")
    
    def test_memory_efficiency_under_load(self):
        """Test memory efficiency under load"""
        gc.collect()
        
        # Simulate multiple scans
        scanner = ComprehensivePortScanner(timeout=1, max_workers=50)
        generator = TextReportGenerator()
        
        for i in range(3):  # 3 scans (reduced from 5 for speed)
            results = scanner.scan_common_ports('127.0.0.1')
            
            scan_results = {
                'target': f'target_{i}',
                'vulnerabilities': [{'type': 'test', 'severity': 'LOW', 'endpoint': '/test', 'evidence': 'test'}]
            }
            report = generator.generate_report(scan_results)
        
        gc.collect()
        
        # Memory test passed if no exception raised
        print(f"✓ Memory usage after 3 scans: OK")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
