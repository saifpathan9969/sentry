"""
Property-Based Test Data Generators for AI Pentest Brain
Uses Hypothesis to generate realistic test data for all components
"""

from hypothesis import strategies as st
from hypothesis.strategies import composite
from typing import Dict, List, Any
from datetime import datetime, date
import string


# ============================================================================
# Basic Data Generators
# ============================================================================

@composite
def url_strategy(draw):
    """Generate valid URLs"""
    protocol = draw(st.sampled_from(['http', 'https']))
    domain = draw(st.text(
        alphabet=string.ascii_lowercase + string.digits + '-',
        min_size=3,
        max_size=20
    ).filter(lambda x: not x.startswith('-') and not x.endswith('-')))
    tld = draw(st.sampled_from(['com', 'org', 'net', 'io', 'dev', 'co']))
    path = draw(st.one_of(
        st.just(''),
        st.text(alphabet=string.ascii_lowercase + string.digits + '/-_', min_size=1, max_size=50)
    ))
    
    url = f"{protocol}://{domain}.{tld}"
    if path and not path.startswith('/'):
        path = '/' + path
    return url + path


@composite
def ip_address_strategy(draw):
    """Generate valid IPv4 addresses"""
    octets = [draw(st.integers(min_value=0, max_value=255)) for _ in range(4)]
    return '.'.join(map(str, octets))


@composite
def port_strategy(draw):
    """Generate valid port numbers"""
    return draw(st.integers(min_value=1, max_value=65535))


@composite
def cve_id_strategy(draw):
    """Generate valid CVE IDs"""
    year = draw(st.integers(min_value=1999, max_value=2025))
    number = draw(st.integers(min_value=1, max_value=99999))
    return f"CVE-{year}-{number:04d}"


@composite
def severity_strategy(draw):
    """Generate vulnerability severity levels"""
    return draw(st.sampled_from(['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']))


@composite
def cvss_score_strategy(draw):
    """Generate CVSS scores (0.0 - 10.0)"""
    return draw(st.floats(min_value=0.0, max_value=10.0, allow_nan=False, allow_infinity=False))


# ============================================================================
# Port Scan Result Generators
# ============================================================================

@composite
def service_name_strategy(draw):
    """Generate common service names"""
    services = [
        'http', 'https', 'ssh', 'ftp', 'smtp', 'pop3', 'imap',
        'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
        'dns', 'ldap', 'smb', 'rdp', 'vnc', 'telnet'
    ]
    return draw(st.sampled_from(services))


@composite
def service_version_strategy(draw):
    """Generate service version strings"""
    major = draw(st.integers(min_value=1, max_value=10))
    minor = draw(st.integers(min_value=0, max_value=20))
    patch = draw(st.integers(min_value=0, max_value=50))
    
    version_format = draw(st.sampled_from([
        f"{major}.{minor}.{patch}",
        f"{major}.{minor}",
        f"v{major}.{minor}.{patch}",
        f"{major}.{minor}.{patch}-stable"
    ]))
    
    return version_format


@composite
def open_port_strategy(draw):
    """Generate open port information"""
    port = draw(port_strategy())
    service = draw(service_name_strategy())
    version = draw(st.one_of(st.none(), service_version_strategy()))
    state = draw(st.sampled_from(['open', 'filtered', 'closed']))
    
    return {
        'port': port,
        'service': service,
        'version': version,
        'state': state,
        'protocol': draw(st.sampled_from(['tcp', 'udp']))
    }


@composite
def port_scan_result_strategy(draw):
    """Generate complete port scan results"""
    target = draw(st.one_of(url_strategy(), ip_address_strategy()))
    num_ports = draw(st.integers(min_value=0, max_value=20))
    open_ports = [draw(open_port_strategy()) for _ in range(num_ports)]
    
    return {
        'target': target,
        'scan_time': draw(st.floats(min_value=0.1, max_value=300.0)),
        'open_ports': open_ports,
        'total_ports_scanned': draw(st.integers(min_value=num_ports, max_value=65535)),
        'scan_mode': draw(st.sampled_from(['common', 'fast', 'full'])),
        'udp_enabled': draw(st.booleans())
    }


# ============================================================================
# Service Detection Generators
# ============================================================================

@composite
def http_server_banner_strategy(draw):
    """Generate HTTP server banners"""
    servers = ['nginx', 'Apache', 'IIS', 'lighttpd', 'Caddy']
    server = draw(st.sampled_from(servers))
    version = draw(service_version_strategy())
    
    return f"{server}/{version}"


@composite
def ssh_banner_strategy(draw):
    """Generate SSH banners"""
    implementations = ['OpenSSH', 'Dropbear', 'libssh']
    impl = draw(st.sampled_from(implementations))
    version = draw(service_version_strategy())
    
    return f"SSH-2.0-{impl}_{version}"


@composite
def service_detection_result_strategy(draw):
    """Generate service detection results"""
    port = draw(port_strategy())
    service = draw(service_name_strategy())
    
    if service in ['http', 'https']:
        banner = draw(http_server_banner_strategy())
    elif service == 'ssh':
        banner = draw(ssh_banner_strategy())
    else:
        banner = draw(st.text(min_size=5, max_size=50))
    
    return {
        'port': port,
        'service': service,
        'banner': banner,
        'version': draw(st.one_of(st.none(), service_version_strategy())),
        'confidence': draw(st.floats(min_value=0.0, max_value=1.0))
    }


# ============================================================================
# CVE Data Generators
# ============================================================================

@composite
def cwe_id_strategy(draw):
    """Generate CWE IDs"""
    number = draw(st.integers(min_value=1, max_value=1000))
    return f"CWE-{number}"


@composite
def cve_data_strategy(draw):
    """Generate CVE data"""
    cve_id = draw(cve_id_strategy())
    
    return {
        'cve_id': cve_id,
        'description': draw(st.text(min_size=20, max_size=200)),
        'cvss_score': draw(cvss_score_strategy()),
        'severity': draw(severity_strategy()),
        'cwe_id': draw(st.one_of(st.none(), cwe_id_strategy())),
        'published_date': draw(st.dates(min_value=date(2000, 1, 1), max_value=date(2025, 12, 31)).map(str)),
        'last_modified': draw(st.dates(min_value=date(2000, 1, 1), max_value=date(2025, 12, 31)).map(str)),
        'references': draw(st.lists(url_strategy(), min_size=0, max_size=5)),
        'exploit_available': draw(st.booleans())
    }


@composite
def vulnerability_with_cve_strategy(draw):
    """Generate vulnerability with CVE data"""
    vuln_type = draw(st.sampled_from([
        'SQL Injection', 'XSS', 'CSRF', 'Command Injection',
        'Path Traversal', 'SSRF', 'XXE', 'Deserialization',
        'Authentication Bypass', 'Privilege Escalation'
    ]))
    
    num_cves = draw(st.integers(min_value=0, max_value=5))
    cves = [draw(cve_data_strategy()) for _ in range(num_cves)]
    
    return {
        'type': vuln_type,
        'severity': draw(severity_strategy()),
        'url': draw(url_strategy()),
        'parameter': draw(st.one_of(st.none(), st.text(min_size=1, max_size=20))),
        'payload': draw(st.text(min_size=5, max_size=100)),
        'cves': cves,
        'confidence': draw(st.floats(min_value=0.0, max_value=1.0)),
        'verified': draw(st.booleans())
    }


# ============================================================================
# Scan Result Generators
# ============================================================================

@composite
def vulnerability_strategy(draw):
    """Generate vulnerability findings"""
    vuln_type = draw(st.sampled_from([
        'SQL Injection', 'XSS', 'CSRF', 'Command Injection',
        'Path Traversal', 'SSRF', 'XXE', 'Deserialization',
        'Authentication Bypass', 'Privilege Escalation',
        'Weak Cryptography', 'Security Misconfiguration'
    ]))
    
    return {
        'type': vuln_type,
        'severity': draw(severity_strategy()),
        'url': draw(url_strategy()),
        'parameter': draw(st.one_of(st.none(), st.text(min_size=1, max_size=20))),
        'payload': draw(st.text(min_size=5, max_size=100)),
        'evidence': draw(st.text(min_size=10, max_size=200)),
        'confidence': draw(st.floats(min_value=0.0, max_value=1.0)),
        'remediation': draw(st.text(min_size=20, max_size=150))
    }


@composite
def scan_result_strategy(draw):
    """Generate complete scan results"""
    target = draw(url_strategy())
    num_vulns = draw(st.integers(min_value=0, max_value=20))
    vulnerabilities = [draw(vulnerability_strategy()) for _ in range(num_vulns)]
    
    return {
        'target': target,
        'scan_start': draw(st.datetimes(min_value=datetime(2024, 1, 1), max_value=datetime(2025, 12, 31)).map(str)),
        'scan_end': draw(st.datetimes(min_value=datetime(2024, 1, 1), max_value=datetime(2025, 12, 31)).map(str)),
        'vulnerabilities': vulnerabilities,
        'total_requests': draw(st.integers(min_value=num_vulns, max_value=1000)),
        'scan_duration': draw(st.floats(min_value=1.0, max_value=3600.0)),
        'scan_mode': draw(st.sampled_from(['quick', 'normal', 'deep'])),
        'status': draw(st.sampled_from(['completed', 'partial', 'failed']))
    }


# ============================================================================
# Fix Recommendation Generators
# ============================================================================

@composite
def code_language_strategy(draw):
    """Generate programming language names"""
    return draw(st.sampled_from([
        'python', 'javascript', 'java', 'php', 'ruby',
        'go', 'rust', 'csharp', 'typescript', 'sql'
    ]))


@composite
def code_example_strategy(draw):
    """Generate code examples"""
    language = draw(code_language_strategy())
    
    # Simple code snippets
    snippets = {
        'python': 'import hashlib\npassword_hash = hashlib.sha256(password.encode()).hexdigest()',
        'javascript': 'const hash = crypto.createHash("sha256").update(password).digest("hex");',
        'java': 'MessageDigest md = MessageDigest.getInstance("SHA-256");',
        'php': '$hash = hash("sha256", $password);',
        'sql': 'SELECT * FROM users WHERE id = ?'
    }
    
    return {
        'language': language,
        'code': snippets.get(language, draw(st.text(min_size=20, max_size=100)))
    }


@composite
def fix_recommendation_strategy(draw):
    """Generate fix recommendations"""
    vuln_type = draw(st.sampled_from([
        'SQL Injection', 'XSS', 'CSRF', 'Command Injection'
    ]))
    
    num_examples = draw(st.integers(min_value=1, max_value=3))
    code_examples = [draw(code_example_strategy()) for _ in range(num_examples)]
    
    return {
        'vulnerability_type': vuln_type,
        'severity': draw(severity_strategy()),
        'description': draw(st.text(min_size=50, max_size=200)),
        'fix_methods': draw(st.lists(st.text(min_size=20, max_size=100), min_size=1, max_size=5)),
        'code_examples': code_examples,
        'references': draw(st.lists(url_strategy(), min_size=1, max_size=3)),
        'estimated_effort': draw(st.sampled_from(['low', 'medium', 'high'])),
        'priority': draw(st.integers(min_value=1, max_value=5))
    }


# ============================================================================
# Attack Probability Generators
# ============================================================================

@composite
def security_headers_strategy(draw):
    """Generate security headers"""
    headers = {}
    
    if draw(st.booleans()):
        headers['X-Frame-Options'] = draw(st.sampled_from(['DENY', 'SAMEORIGIN']))
    if draw(st.booleans()):
        headers['X-Content-Type-Options'] = 'nosniff'
    if draw(st.booleans()):
        headers['Strict-Transport-Security'] = 'max-age=31536000'
    if draw(st.booleans()):
        headers['Content-Security-Policy'] = "default-src 'self'"
    
    return headers


@composite
def attack_probability_data_strategy(draw):
    """Generate attack probability calculation data"""
    return {
        'vulnerability_type': draw(st.sampled_from([
            'SQL Injection', 'XSS', 'CSRF', 'Command Injection'
        ])),
        'base_probability': draw(st.floats(min_value=0.0, max_value=1.0)),
        'waf_detected': draw(st.booleans()),
        'ids_ips_detected': draw(st.booleans()),
        'security_headers': draw(security_headers_strategy()),
        'patch_level': draw(st.sampled_from(['outdated', 'current', 'latest'])),
        'authentication_required': draw(st.booleans()),
        'rate_limiting': draw(st.booleans())
    }


# ============================================================================
# Report Data Generators
# ============================================================================

@composite
def report_data_strategy(draw):
    """Generate complete report data"""
    num_vulns = draw(st.integers(min_value=0, max_value=15))
    vulnerabilities = [draw(vulnerability_with_cve_strategy()) for _ in range(num_vulns)]
    
    # Count by severity
    severity_counts = {
        'CRITICAL': sum(1 for v in vulnerabilities if v['severity'] == 'CRITICAL'),
        'HIGH': sum(1 for v in vulnerabilities if v['severity'] == 'HIGH'),
        'MEDIUM': sum(1 for v in vulnerabilities if v['severity'] == 'MEDIUM'),
        'LOW': sum(1 for v in vulnerabilities if v['severity'] == 'LOW'),
        'INFO': sum(1 for v in vulnerabilities if v['severity'] == 'INFO')
    }
    
    return {
        'target': draw(url_strategy()),
        'scan_date': draw(st.datetimes(min_value=datetime(2024, 1, 1), max_value=datetime(2025, 12, 31)).map(str)),
        'vulnerabilities': vulnerabilities,
        'severity_counts': severity_counts,
        'total_vulnerabilities': num_vulns,
        'scan_duration': draw(st.floats(min_value=1.0, max_value=3600.0)),
        'port_scan_results': draw(st.one_of(st.none(), port_scan_result_strategy())),
        'recommendations': draw(st.lists(fix_recommendation_strategy(), min_size=0, max_size=5))
    }


# ============================================================================
# Configuration Data Generators
# ============================================================================

@composite
def config_data_strategy(draw):
    """Generate configuration data"""
    return {
        'scan_mode': draw(st.sampled_from(['common', 'fast', 'full'])),
        'enable_udp_scan': draw(st.booleans()),
        'max_threads': draw(st.integers(min_value=1, max_value=100)),
        'scan_timeout': draw(st.integers(min_value=1, max_value=60)),
        'report_format': draw(st.sampled_from(['json', 'text', 'both'])),
        'nvd_api_key': draw(st.one_of(st.none(), st.text(min_size=32, max_size=64))),
        'safe_mode': draw(st.booleans()),
        'verbose': draw(st.booleans()),
        'max_retries': draw(st.integers(min_value=0, max_value=10))
    }


# Export all strategies
__all__ = [
    'url_strategy',
    'ip_address_strategy',
    'port_strategy',
    'cve_id_strategy',
    'severity_strategy',
    'cvss_score_strategy',
    'service_name_strategy',
    'service_version_strategy',
    'open_port_strategy',
    'port_scan_result_strategy',
    'service_detection_result_strategy',
    'cve_data_strategy',
    'vulnerability_with_cve_strategy',
    'vulnerability_strategy',
    'scan_result_strategy',
    'code_example_strategy',
    'fix_recommendation_strategy',
    'attack_probability_data_strategy',
    'security_headers_strategy',
    'report_data_strategy',
    'config_data_strategy'
]


# Example usage and testing
if __name__ == "__main__":
    from hypothesis import given, settings
    
    print("Testing data generators...")
    
    @given(url_strategy())
    @settings(max_examples=5)
    def test_url_generation(url):
        print(f"URL: {url}")
        assert url.startswith('http')
    
    @given(port_scan_result_strategy())
    @settings(max_examples=3)
    def test_port_scan_generation(result):
        print(f"\nPort Scan Result:")
        print(f"  Target: {result['target']}")
        print(f"  Open Ports: {len(result['open_ports'])}")
        print(f"  Scan Mode: {result['scan_mode']}")
    
    @given(vulnerability_with_cve_strategy())
    @settings(max_examples=3)
    def test_vulnerability_generation(vuln):
        print(f"\nVulnerability:")
        print(f"  Type: {vuln['type']}")
        print(f"  Severity: {vuln['severity']}")
        print(f"  CVEs: {len(vuln['cves'])}")
    
    test_url_generation()
    test_port_scan_generation()
    test_vulnerability_generation()
    
    print("\n✓ All generators working correctly!")
