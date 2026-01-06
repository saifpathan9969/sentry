"""
Cache Poisoning Vulnerability Scanner
======================================

Detects web cache poisoning and cache deception vulnerabilities

Author: AI Pentest Brain Team
Version: 1.0
"""

import requests
import hashlib
import time
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class CachePoisoningScanner:
    """
    Cache poisoning and deception vulnerability scanner
    Tests for cache manipulation vulnerabilities
    """
    
    def __init__(self, target_url: str):
        self.target_url = target_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Headers that might be used as cache keys
        self.unkeyed_headers = [
            'X-Forwarded-Host',
            'X-Forwarded-Scheme',
            'X-Original-URL',
            'X-Rewrite-URL',
            'X-Forwarded-Server',
            'X-Host',
            'X-Forwarded-Proto',
            'Forwarded',
            'True-Client-IP',
            'X-Custom-IP-Authorization'
        ]
    
    def scan_all(self) -> List[Dict]:
        """Run all cache poisoning checks"""
        logger.info(f"Starting cache poisoning scan on {self.target_url}")
        
        vulnerabilities = []
        
        vulnerabilities.extend(self._check_unkeyed_header_poisoning())
        vulnerabilities.extend(self._check_host_header_poisoning())
        vulnerabilities.extend(self._check_cache_deception())
        vulnerabilities.extend(self._check_dos_via_cache())
        vulnerabilities.extend(self._check_cache_key_injection())
        
        return vulnerabilities
    
    def _check_unkeyed_header_poisoning(self) -> List[Dict]:
        """Check for unkeyed header cache poisoning"""
        vulnerabilities = []
        
        for header_name in self.unkeyed_headers:
            try:
                # Send request with malicious header
                malicious_value = f"evil.com"
                headers = {header_name: malicious_value}
                
                # First request to poison cache
                cache_buster = hashlib.md5(str(time.time()).encode()).hexdigest()
                url = f"{self.target_url}?cb={cache_buster}"
                
                response1 = self.session.get(url, headers=headers, timeout=10)
                
                # Second request without malicious header to check if cached
                time.sleep(1)
                response2 = self.session.get(url, timeout=10)
                
                # Check if malicious value appears in second response
                if malicious_value in response2.text and response2.text == response1.text:
                    vulnerabilities.append({
                        'type': 'cache_poisoning_unkeyed_header',
                        'severity': 'HIGH',
                        'endpoint': self.target_url,
                        'description': f'Cache poisoning via unkeyed {header_name} header',
                        'impact': 'Attacker can poison cache and affect all users',
                        'evidence': f'{header_name}: {malicious_value} reflected in cached response',
                        'recommendation': f'Include {header_name} in cache key or validate its value',
                        'cwe': 'CWE-444: HTTP Request/Response Smuggling'
                    })
                    
            except Exception as e:
                logger.debug(f"Unkeyed header check error for {header_name}: {str(e)}")
        
        return vulnerabilities
    
    def _check_host_header_poisoning(self) -> List[Dict]:
        """Check for Host header cache poisoning"""
        vulnerabilities = []
        
        try:
            # Try poisoning with Host header
            cache_buster = hashlib.md5(str(time.time()).encode()).hexdigest()
            url = f"{self.target_url}?cb={cache_buster}"
            
            # First request with malicious host
            headers = {'Host': 'evil.com'}
            response1 = self.session.get(url, headers=headers, timeout=10)
            
            # Check if evil.com appears in response
            if 'evil.com' in response1.text:
                # Try to retrieve from cache
                time.sleep(1)
                response2 = self.session.get(url, timeout=10)
                
                if 'evil.com' in response2.text:
                    vulnerabilities.append({
                        'type': 'cache_poisoning_host_header',
                        'severity': 'CRITICAL',
                        'endpoint': self.target_url,
                        'description': 'Host header cache poisoning vulnerability',
                        'impact': 'Attacker can redirect all users to malicious site',
                        'evidence': 'Malicious host reflected in cached response',
                        'recommendation': 'Include Host header in cache key and validate against whitelist',
                        'cwe': 'CWE-644: Improper Neutralization of HTTP Headers'
                    })
                    
        except Exception as e:
            logger.debug(f"Host header poisoning check error: {str(e)}")
        
        return vulnerabilities
    
    def _check_cache_deception(self) -> List[Dict]:
        """Check for cache deception vulnerability"""
        vulnerabilities = []
        
        try:
            # Try accessing sensitive page with static extension
            deception_paths = [
                '/account.css',
                '/profile.js',
                '/user/info.jpg',
                '/admin.png',
                '/api/user.css'
            ]
            
            for path in deception_paths:
                url = self.target_url.rstrip('/') + path
                
                # First request
                response1 = self.session.get(url, timeout=10)
                
                # Check if we got sensitive data
                if response1.status_code == 200:
                    # Check for indicators of sensitive data
                    sensitive_indicators = ['email', 'password', 'ssn', 'credit', 'token', 'session']
                    
                    if any(indicator in response1.text.lower() for indicator in sensitive_indicators):
                        # Try to retrieve from cache (simulated - normally would be from shared cache)
                        time.sleep(1)
                        response2 = self.session.get(url, timeout=10)
                        
                        if response2.text == response1.text:
                            vulnerabilities.append({
                                'type': 'web_cache_deception',
                                'severity': 'HIGH',
                                'endpoint': url,
                                'description': 'Web cache deception - sensitive data cached',
                                'impact': 'Attacker can trick users into caching sensitive data publicly',
                                'evidence': f'Sensitive data cached at: {path}',
                                'recommendation': 'Only cache static resources, validate file extensions server-side',
                                'cwe': 'CWE-524: Use of Cache Containing Sensitive Information'
                            })
                            break
                            
        except Exception as e:
            logger.debug(f"Cache deception check error: {str(e)}")
        
        return vulnerabilities
    
    def _check_dos_via_cache(self) -> List[Dict]:
        """Check for DoS via cache poisoning"""
        vulnerabilities = []
        
        try:
            # Try to cache error pages
            cache_buster = hashlib.md5(str(time.time()).encode()).hexdigest()
            
            # Send request that causes error
            headers = {'X-Forwarded-Host': 'invalid-domain-that-does-not-exist.com'}
            url = f"{self.target_url}?cb={cache_buster}"
            
            response1 = self.session.get(url, headers=headers, timeout=10)
            
            # Check if error was cached
            if response1.status_code >= 400:
                time.sleep(1)
                response2 = self.session.get(url, timeout=10)
                
                if response2.status_code == response1.status_code:
                    vulnerabilities.append({
                        'type': 'cache_poisoning_dos',
                        'severity': 'MEDIUM',
                        'endpoint': self.target_url,
                        'description': 'Error pages can be cached causing DoS',
                        'impact': 'Attacker can cause DoS by poisoning cache with errors',
                        'evidence': f'Error {response1.status_code} was cached',
                        'recommendation': 'Do not cache error responses',
                        'cwe': 'CWE-400: Uncontrolled Resource Consumption'
                    })
                    
        except Exception as e:
            logger.debug(f"DoS via cache check error: {str(e)}")
        
        return vulnerabilities
    
    def _check_cache_key_injection(self) -> List[Dict]:
        """Check for cache key injection"""
        vulnerabilities = []
        
        try:
            # Try injecting into cache key via URL
            injection_payloads = [
                '?utm_source=<script>alert(1)</script>',
                '?callback=evil.com',
                '?locale=../../../etc/passwd'
            ]
            
            for payload in injection_payloads:
                cache_buster = hashlib.md5(str(time.time()).encode()).hexdigest()
                url = f"{self.target_url}{payload}&cb={cache_buster}"
                
                response1 = self.session.get(url, timeout=10)
                
                # Check if payload is reflected
                if any(p in response1.text for p in ['<script>', 'evil.com', 'passwd']):
                    # Try to get from cache
                    time.sleep(1)
                    response2 = self.session.get(url, timeout=10)
                    
                    if response2.text == response1.text:
                        vulnerabilities.append({
                            'type': 'cache_key_injection',
                            'severity': 'HIGH',
                            'endpoint': self.target_url,
                            'description': 'Cache key injection - malicious payload cached',
                            'impact': 'XSS or other injection attacks via cached responses',
                            'evidence': f'Payload cached: {payload}',
                            'recommendation': 'Sanitize all cache key parameters',
                            'cwe': 'CWE-74: Injection'
                        })
                        break
                        
        except Exception as e:
            logger.debug(f"Cache key injection check error: {str(e)}")
        
        return vulnerabilities


# Test function
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    print("="*70)
    print("Cache Poisoning Scanner - Test")
    print("="*70 + "\n")
    
    target = "http://localhost:8080"
    scanner = CachePoisoningScanner(target)
    
    vulnerabilities = scanner.scan_all()
    
    print(f"\n[+] Found {len(vulnerabilities)} cache poisoning vulnerabilities\n")
    
    for vuln in vulnerabilities:
        print(f"Type: {vuln['type']}")
        print(f"Severity: {vuln['severity']}")
        print(f"Description: {vuln['description']}")
        print("-" * 70)
