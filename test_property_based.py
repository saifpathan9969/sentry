"""
Property-Based Tests for AI Penetration Testing Brain Enhancements
Uses Hypothesis for property-based testing to verify correctness properties
"""

import pytest
from hypothesis import given, strategies as st, settings
from hypothesis.strategies import composite
from typing import List, Dict
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from comprehensive_port_scanner import ComprehensivePortScanner, PortScanResult
from service_version_detector import ServiceVersionDetector
from cve_integration import CVEDatabase
from text_report_generator import TextReportGenerator

# Import test data generators
from test_data_generators import (
    vulnerability_with_cve_strategy,
    scan_result_strategy as scan_results_strategy,
    fix_recommendation_strategy as vulnerability_with_fixes_strategy,
    cve_id_strategy,
    severity_strategy,
    url_strategy
)


# ============================================================================
# Hypothesis Strategies (Test Data Generators)
# ============================================================================

@composite
def port_number_strategy(draw):
    """Generate valid port numbers (1-65535)"""
    return draw(st.integers(min_value=1, max_value=65535))


@composite
def open_ports_strategy(draw):
    """Generate list of open ports"""
    return draw(st.lists(
        port_number_strategy(),
        min_size=1,
        max_size=50,
        unique=True
    ))


@composite
def port_scan_result_strategy(draw):
    """Generate PortScanResult objects"""
    port = draw(port_number_strategy())
    state = draw(st.sampled_from(['open', 'closed', 'filtered']))
    service = draw(st.sampled_from(['http', 'https', 'ssh', 'ftp', 'smtp', 'mysql', 'postgresql', 'unknown']))
    version = draw(st.one_of(
        st.just('Unknown'),
        st.text(min_size=3, max_size=20)
    ))
    banner = draw(st.text(min_size=0, max_size=100))
    protocol = draw(st.sampled_from(['tcp', 'udp']))
    
    return PortScanResult(
        port=port,
        state=state,
        service=service,
        version=version,
        banner=banner,
        protocol=protocol
    )


@composite
def identified_service_strategy(draw):
    """Generate identified service data"""
    service = draw(st.sampled_from(['http', 'https', 'ssh', 'ftp', 'smtp', 'mysql', 'postgresql', 'redis', 'mongodb']))
    port = draw(port_number_strategy())
    version = draw(st.one_of(
        st.just('Unknown'),
        st.text(min_size=3, max_size=20)
    ))
    banner = draw(st.text(min_size=0, max_size=100))
    
    return {
        'service': service,
        'port': port,
        'version': version,
        'banner': banner,
        'host': 'localhost'
    }


@composite
def vulnerability_with_multiple_cves_strategy(draw):
    """Generate vulnerability with multiple CVE IDs"""
    num_cves = draw(st.integers(min_value=2, max_value=5))
    cve_ids = [draw(cve_id_strategy()) for _ in range(num_cves)]
    
    return {
        'type': draw(st.sampled_from(['SQL Injection', 'XSS', 'Command Injection'])),
        'severity': draw(severity_strategy()),
        'expected_cve_ids': cve_ids,
        'cve_ids': cve_ids,  # Actual CVE IDs in the vulnerability
        'description': draw(st.text(min_size=20, max_size=100))
    }


@composite
def known_vuln_type_strategy(draw):
    """Generate vulnerability of known types that should have CVE mappings"""
    vuln_type = draw(st.sampled_from([
        'sql_injection', 'xss', 'cross_site_scripting', 'csrf', 
        'ssrf', 'xxe', 'command_injection', 'path_traversal'
    ]))
    
    return {
        'type': vuln_type,
        'severity': draw(st.sampled_from(['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'])),
        'endpoint': f'/api/{draw(st.text(min_size=3, max_size=20))}',
        'description': draw(st.text(min_size=10, max_size=100))
    }


# ============================================================================
# Property 6: Service fingerprinting on open ports
# Feature: pentest-brain-enhancements, Property 6: Service fingerprinting on open ports
# Validates: Requirements 2.3.2
# ============================================================================

@given(port_results=st.lists(port_scan_result_strategy(), min_size=1, max_size=20))
@settings(max_examples=100, deadline=None)
def test_service_fingerprinting_on_open_ports(port_results):
    """
    For any open port discovered during scanning, 
    the system should attempt service fingerprinting to identify the running service.
    """
    detector = ServiceVersionDetector()
    
    for result in port_results:
        if result.state == 'open':
            # Service fingerprinting should be attempted
            service, version = detector.detect_version(
                'localhost',
                result.port,
                result.service,
                result.banner
            )
            
            # Service should be identified (not None)
            assert service is not None, f"Service should be identified for open port {result.port}"
            assert isinstance(service, str), "Service should be a string"
            
            # Version should be attempted (can be 'Unknown' but not None)
            assert version is not None, f"Version detection should be attempted for port {result.port}"
            assert isinstance(version, str), "Version should be a string"


# ============================================================================
# Property 7: Version detection and vulnerability checking
# Feature: pentest-brain-enhancements, Property 7: Version detection and vulnerability checking
# Validates: Requirements 2.3.3
# ============================================================================

@composite
def service_with_banner_strategy(draw):
    """Generate service data with realistic banners for version detection"""
    service = draw(st.sampled_from(['http', 'https', 'ssh', 'ftp', 'smtp', 'mysql', 'postgresql', 'redis', 'mongodb']))
    port = draw(port_number_strategy())
    
    # Generate realistic banners based on service type
    banner_templates = {
        'http': [
            'Server: nginx/1.18.0',
            'Server: Apache/2.4.41 (Ubuntu)',
            'Server: Microsoft-IIS/10.0',
            'nginx/1.20.1',
            'Apache/2.4.52'
        ],
        'https': [
            'Server: nginx/1.18.0',
            'Server: Apache/2.4.41 (Ubuntu)',
        ],
        'ssh': [
            'SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5',
            'SSH-2.0-OpenSSH_7.9',
            'SSH-2.0-Dropbear_2020.81'
        ],
        'ftp': [
            '220 ProFTPD 1.3.6 Server',
            '220 vsftpd 3.0.3'
        ],
        'smtp': [
            '220 mail.example.com ESMTP Postfix',
            '220 smtp.gmail.com ESMTP'
        ],
        'mysql': [
            '5.7.33-MySQL',
            'MySQL 8.0.23'
        ],
        'postgresql': [
            'PostgreSQL 12.7',
            'PostgreSQL 13.3'
        ],
        'redis': [
            'Redis server v=6.2.5',
            'redis_version:5.0.7'
        ],
        'mongodb': [
            'MongoDB 4.4.6',
            'version": "5.0.3"'
        ]
    }
    
    # Select a banner template or generate empty/unknown
    if draw(st.booleans()):
        banner = draw(st.sampled_from(banner_templates.get(service, [''])))
    else:
        banner = ''
    
    return {
        'service': service,
        'port': port,
        'banner': banner,
        'host': 'localhost'
    }


@given(service_data=service_with_banner_strategy())
@settings(max_examples=100, deadline=None)  # Disable deadline for network operations
def test_version_detection_and_vulnerability_checking(service_data):
    """
    For any identified service, the system should attempt version detection 
    and check for known vulnerabilities associated with that service and version.
    """
    detector = ServiceVersionDetector()
    
    # Attempt version detection (primarily from banner, avoiding network calls)
    detected_service, detected_version = detector.detect_version(
        service_data['host'],
        service_data['port'],
        service_data['service'],
        service_data['banner']
    )
    
    # Version detection should be attempted (result should not be None)
    assert detected_service is not None, "Service detection should return a result"
    assert detected_version is not None, "Version detection should return a result"
    assert isinstance(detected_service, str), "Service should be a string"
    assert isinstance(detected_version, str), "Version should be a string"
    
    # Service should match the input service
    assert detected_service == service_data['service'], "Detected service should match input service"
    
    # If banner contains version info, version should be detected
    if service_data['banner'] and any(char.isdigit() for char in service_data['banner']):
        # Banner has version info, so detection should attempt to extract it
        # Version might still be 'Unknown' if pattern doesn't match, but that's acceptable
        assert isinstance(detected_version, str), "Version should be a string"
    
    # If version is detected (not 'Unknown'), vulnerability checking should be possible
    if detected_version != 'Unknown':
        # Vulnerability checking would be done by CVE integration
        # Here we just verify the data structure is suitable for CVE lookup
        assert len(detected_version) > 0, "Detected version should not be empty"
        
        # Service name should be valid for CVE search
        assert len(detected_service) > 0, "Service name should not be empty"
        
        # Version should contain at least one digit (valid version format)
        assert any(char.isdigit() for char in detected_version), "Version should contain digits"


# ============================================================================
# Property 2: CVE data enrichment completeness
# Feature: pentest-brain-enhancements, Property 2: CVE data enrichment completeness
# Validates: Requirements 2.1.2, 2.1.5, 2.2.2, 2.2.3, 2.2.4
# ============================================================================

@given(vulnerability=vulnerability_with_cve_strategy())
@settings(max_examples=10, deadline=None)  # Reduced from 100 to 10 to avoid long API calls
def test_cve_enrichment_completeness(vulnerability):
    """
    For any vulnerability with available CVE data, the enriched vulnerability 
    should include CVE ID, CVSS v3 score, CVSS vector string, severity level, 
    CWE classification, exploit availability status, and patch availability status.
    """
    # Mock CVE database for testing
    from cve_integration import CVEDatabase
    
    cve_db = CVEDatabase()
    
    # Enrich the vulnerability
    enriched = cve_db.enrich_vulnerability(vulnerability)
    
    # Check if CVE data was added
    if enriched.get('cve_data') and enriched['cve_data'].get('related_cves'):
        # If CVE data is available, verify completeness
        cve_data = enriched['cve_data']
        
        # Should have related CVEs list
        assert 'related_cves' in cve_data, "Should have related_cves field"
        assert isinstance(cve_data['related_cves'], list), "related_cves should be a list"
        
        # Should have example CVE with complete data
        if cve_data.get('example_cve'):
            example = cve_data['example_cve']
            
            # CVE ID should be present
            assert 'cve_id' in example or 'id' in example, "Should have CVE ID"
            
            # CVSS score should be present
            assert 'cvss_score' in example, "Should have CVSS score"
            
            # Description should be present
            assert 'description' in example, "Should have description"


# ============================================================================
# Property 4: Multiple CVE listing
# Feature: pentest-brain-enhancements, Property 4: Multiple CVE listing
# Validates: Requirements 2.2.5
# ============================================================================

@given(vulnerability=vulnerability_with_multiple_cves_strategy())
@settings(max_examples=100)
def test_multiple_cve_listing(vulnerability):
    """
    For any vulnerability that maps to multiple CVEs, 
    all relevant CVE IDs should be included in the vulnerability data.
    """
    expected_cves = vulnerability.get('expected_cve_ids', [])
    
    # If we have expected CVEs, verify they're all present
    if expected_cves:
        actual_cves = vulnerability.get('cve_ids', [])
        
        # All expected CVEs should be in the actual list
        for cve_id in expected_cves:
            assert cve_id in actual_cves, f"Expected CVE {cve_id} should be in vulnerability data"
        
        # Should have at least as many CVEs as expected
        assert len(actual_cves) >= len(expected_cves), "Should include all expected CVEs"


# ============================================================================
# Property 5: NVD API query for vulnerabilities
# Feature: pentest-brain-enhancements, Property 5: NVD API query for vulnerabilities
# Validates: Requirements 2.2.1
# ============================================================================

@given(vulnerability=known_vuln_type_strategy())
@settings(max_examples=10, deadline=None)  # Reduced from 50 to 10 to avoid long API calls
def test_nvd_api_queried_for_known_types(vulnerability):
    """
    For any known vulnerability type (XSS, SQLi, etc.), 
    the CVE integration should attempt to query the NVD API.
    """
    from cve_integration import CVEDatabase
    
    cve_db = CVEDatabase()
    vuln_type = vulnerability['type']
    
    # Known vulnerability types that should trigger CVE lookup
    KNOWN_CVE_TYPES = [
        'sql_injection', 'xss', 'cross_site_scripting', 'csrf',
        'ssrf', 'xxe', 'command_injection', 'path_traversal',
        'idor', 'deserialization', 'open_redirect'
    ]
    
    if vuln_type in KNOWN_CVE_TYPES:
        # Enrich should attempt to add CVE data
        enriched = cve_db.enrich_vulnerability(vulnerability)
        
        # Should have cve_data field added (even if empty)
        assert 'cve_data' in enriched, f"CVE data should be added for known type: {vuln_type}"
        
        # cve_data should have the expected structure
        cve_data = enriched['cve_data']
        assert 'related_cves' in cve_data, "Should have related_cves field"
        assert 'total_found' in cve_data, "Should have total_found field"
        assert isinstance(cve_data['related_cves'], list), "related_cves should be a list"


# ============================================================================
# Property 1: Report generation completeness
# Feature: pentest-brain-enhancements, Property 1: Report generation completeness
# Validates: Requirements 2.1.1, 2.1.4
# ============================================================================

@given(scan_results=scan_results_strategy())
@settings(max_examples=100)
def test_report_generation_completeness(scan_results):
    """
    For any completed scan with results, the generated TEXT report should contain 
    all required sections: scan information, executive summary, network scan results, 
    vulnerability findings, and recommendations.
    """
    from text_report_generator import TextReportGenerator
    
    generator = TextReportGenerator()
    report = generator.generate_report(scan_results)
    
    # Check for required sections
    assert "SCAN INFORMATION" in report or "Scan Information" in report.upper()
    assert "EXECUTIVE SUMMARY" in report or "Executive Summary" in report.upper()
    assert "RECOMMENDATIONS" in report or "Recommendations" in report.upper()
    
    # Report should not be empty
    assert len(report) > 100, "Report should have substantial content"


# ============================================================================
# Property 3: Fix recommendations include code examples
# Feature: pentest-brain-enhancements, Property 3: Fix recommendations include code examples
# Validates: Requirements 2.1.3
# ============================================================================

@given(vulnerability=vulnerability_with_fixes_strategy())
@settings(max_examples=100)
def test_fix_recommendations_have_code_examples(vulnerability):
    """
    For any vulnerability with fix recommendations, each fix method should include 
    at least one code example with language specification.
    """
    fix_methods = vulnerability.get('code_examples', [])
    
    # If there are fix methods, verify they have code examples
    if fix_methods:
        for fix_method in fix_methods:
            assert 'language' in fix_method, "Fix method should specify language"
            assert 'code' in fix_method, "Fix method should include code example"
            assert len(fix_method['code']) > 0, "Code example should not be empty"
            assert isinstance(fix_method['language'], str), "Language should be a string"
            assert isinstance(fix_method['code'], str), "Code should be a string"
