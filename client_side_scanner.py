"""
Client-Side Vulnerability Scanner
==================================

Detects client-side security vulnerabilities
PostMessage, DOM issues, WebWorkers, LocalStorage, etc.

Author: AI Pentest Brain Team
Version: 1.0
"""

import requests
import re
import json
from typing import Dict, List, Optional
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class ClientSideScanner:
    """
    Client-side vulnerability scanner
    Tests for browser-side security issues
    """
    
    def __init__(self, target_url: str):
        self.target_url = target_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scan_all(self) -> List[Dict]:
        """Run all client-side vulnerability scans"""
        logger.info(f"Starting client-side vulnerability scan on {self.target_url}")
        
        vulnerabilities = []
        
        # Get page content
        try:
            response = self.session.get(self.target_url, timeout=10)
            html_content = response.text
            headers = response.headers
        except Exception as e:
            logger.error(f"Failed to fetch target: {str(e)}")
            return vulnerabilities
        
        vulnerabilities.extend(self._check_postmessage(html_content))
        vulnerabilities.extend(self._check_dom_clobbering(html_content))
        vulnerabilities.extend(self._check_localstorage_issues(html_content))
        vulnerabilities.extend(self._check_webstorage_xss(html_content))
        vulnerabilities.extend(self._check_webworker_vulnerabilities(html_content))
        vulnerabilities.extend(self._check_service_worker_issues(html_content))
        vulnerabilities.extend(self._check_cors_misconfiguration(headers))
        vulnerabilities.extend(self._check_client_side_validation_bypass(html_content))
        vulnerabilities.extend(self._check_prototype_pollution(html_content))
        vulnerabilities.extend(self._check_dangling_markup(html_content))
        
        return vulnerabilities
    
    def _check_postmessage(self, html: str) -> List[Dict]:
        """Check for insecure postMessage usage"""
        vulnerabilities = []
        
        # Pattern for postMessage listeners
        postmessage_patterns = [
            r'window\.addEventListener\s*\(\s*["\']message["\']',
            r'window\.onmessage\s*=',
            r'\.postMessage\s*\(',
        ]
        
        for pattern in postmessage_patterns:
            if re.search(pattern, html, re.IGNORECASE):
                # Check if origin validation is present
                if not re.search(r'event\.origin\s*[!=]=', html):
                    vulnerabilities.append({
                        'type': 'postmessage_missing_origin_validation',
                        'severity': 'HIGH',
                        'endpoint': self.target_url,
                        'description': 'postMessage listener without origin validation',
                        'impact': 'Attacker can send malicious messages from any origin',
                        'evidence': 'postMessage listener found without origin check',
                        'recommendation': 'Always validate event.origin before processing messages',
                        'cwe': 'CWE-346: Origin Validation Error'
                    })
                    break
                
                # Check for wildcard origin
                if re.search(r'\.postMessage\s*\([^)]*\*[^)]*\)', html):
                    vulnerabilities.append({
                        'type': 'postmessage_wildcard_origin',
                        'severity': 'HIGH',
                        'endpoint': self.target_url,
                        'description': 'postMessage using wildcard (*) origin',
                        'impact': 'Messages can be read by any origin',
                        'evidence': 'postMessage with wildcard origin found',
                        'recommendation': 'Specify exact target origin instead of wildcard',
                        'cwe': 'CWE-346: Origin Validation Error'
                    })
                    break
        
        return vulnerabilities
    
    def _check_dom_clobbering(self, html: str) -> List[Dict]:
        """Check for DOM clobbering vulnerabilities"""
        vulnerabilities = []
        
        # Check for dangerous ID/name attributes
        dangerous_patterns = [
            (r'<[^>]+id\s*=\s*["\'](?:window|document|location|navigator)["\']', 'Dangerous ID clobbering global objects'),
            (r'<form[^>]+name\s*=\s*["\'][^"\']+["\']', 'Form name clobbering'),
            (r'<img[^>]+name\s*=\s*["\'][^"\']+["\']', 'Image name clobbering'),
        ]
        
        for pattern, desc in dangerous_patterns:
            if re.search(pattern, html, re.IGNORECASE):
                # Check if these are accessed in JavaScript
                if re.search(r'window\.\w+|document\.\w+', html):
                    vulnerabilities.append({
                        'type': 'dom_clobbering',
                        'severity': 'MEDIUM',
                        'endpoint': self.target_url,
                        'description': f'Potential DOM clobbering: {desc}',
                        'impact': 'Attacker can override JavaScript globals via HTML attributes',
                        'evidence': f'Pattern found: {desc}',
                        'recommendation': 'Avoid using ID/name attributes that match global objects',
                        'cwe': 'CWE-79: Cross-site Scripting'
                    })
                    break
        
        return vulnerabilities
    
    def _check_localstorage_issues(self, html: str) -> List[Dict]:
        """Check for localStorage security issues"""
        vulnerabilities = []
        
        # Check if sensitive data is stored in localStorage
        if re.search(r'localStorage\.setItem', html, re.IGNORECASE):
            # Check for sensitive keywords
            sensitive_keywords = ['password', 'token', 'secret', 'apikey', 'api_key', 'auth']
            
            for keyword in sensitive_keywords:
                if re.search(rf'localStorage\.setItem\s*\([^)]*{keyword}[^)]*\)', html, re.IGNORECASE):
                    vulnerabilities.append({
                        'type': 'localstorage_sensitive_data',
                        'severity': 'HIGH',
                        'endpoint': self.target_url,
                        'description': 'Sensitive data stored in localStorage',
                        'impact': 'XSS can steal sensitive data from localStorage',
                        'evidence': f'localStorage usage with keyword: {keyword}',
                        'recommendation': 'Use httpOnly cookies for sensitive data, not localStorage',
                        'cwe': 'CWE-922: Insecure Storage of Sensitive Information'
                    })
                    break
        
        return vulnerabilities
    
    def _check_webstorage_xss(self, html: str) -> List[Dict]:
        """Check for XSS via Web Storage"""
        vulnerabilities = []
        
        # Check if localStorage/sessionStorage values are used in innerHTML or eval
        dangerous_sinks = [
            r'\.innerHTML\s*=\s*localStorage',
            r'\.innerHTML\s*=\s*sessionStorage',
            r'eval\s*\(\s*localStorage',
            r'eval\s*\(\s*sessionStorage',
            r'document\.write\s*\(\s*localStorage',
            r'\.outerHTML\s*=\s*localStorage'
        ]
        
        for pattern in dangerous_sinks:
            if re.search(pattern, html, re.IGNORECASE):
                vulnerabilities.append({
                    'type': 'webstorage_xss',
                    'severity': 'HIGH',
                    'endpoint': self.target_url,
                    'description': 'Web Storage data used in dangerous sink',
                    'impact': 'XSS via localStorage/sessionStorage manipulation',
                    'evidence': 'Storage data flows into dangerous sink (innerHTML/eval)',
                    'recommendation': 'Sanitize all Web Storage data before inserting into DOM',
                    'cwe': 'CWE-79: Cross-site Scripting'
                })
                break
        
        return vulnerabilities
    
    def _check_webworker_vulnerabilities(self, html: str) -> List[Dict]:
        """Check for Web Worker security issues"""
        vulnerabilities = []
        
        # Check for Web Worker creation
        if re.search(r'new\s+Worker\s*\(', html, re.IGNORECASE):
            # Check if worker URL is user-controllable
            if re.search(r'new\s+Worker\s*\(\s*[^)]*location\.|new\s+Worker\s*\(\s*[^)]*window\.', html, re.IGNORECASE):
                vulnerabilities.append({
                    'type': 'webworker_injection',
                    'severity': 'HIGH',
                    'endpoint': self.target_url,
                    'description': 'Web Worker URL potentially user-controllable',
                    'impact': 'Attacker can execute arbitrary JavaScript in worker context',
                    'evidence': 'Worker created with user-controllable URL',
                    'recommendation': 'Use static worker URLs, validate all inputs',
                    'cwe': 'CWE-94: Code Injection'
                })
            
            # Check for importScripts with user input
            if re.search(r'importScripts\s*\([^)]*location\.|importScripts\s*\([^)]*window\.', html, re.IGNORECASE):
                vulnerabilities.append({
                    'type': 'webworker_importscripts_injection',
                    'severity': 'HIGH',
                    'endpoint': self.target_url,
                    'description': 'importScripts with user-controllable URL',
                    'impact': 'Attacker can load malicious scripts into worker',
                    'evidence': 'importScripts uses user-controllable input',
                    'recommendation': 'Use static script URLs, whitelist allowed origins',
                    'cwe': 'CWE-94: Code Injection'
                })
        
        return vulnerabilities
    
    def _check_service_worker_issues(self, html: str) -> List[Dict]:
        """Check for Service Worker vulnerabilities"""
        vulnerabilities = []
        
        # Check for Service Worker registration
        if re.search(r'navigator\.serviceWorker\.register', html, re.IGNORECASE):
            # Check if SW path is user-controllable
            if re.search(r'serviceWorker\.register\s*\([^)]*location\.|serviceWorker\.register\s*\([^)]*window\.', html, re.IGNORECASE):
                vulnerabilities.append({
                    'type': 'service_worker_injection',
                    'severity': 'CRITICAL',
                    'endpoint': self.target_url,
                    'description': 'Service Worker path user-controllable',
                    'impact': 'Attacker can register malicious SW and intercept all requests',
                    'evidence': 'SW registration with user-controllable path',
                    'recommendation': 'Use static SW paths only',
                    'cwe': 'CWE-94: Code Injection'
                })
            
            # Check if Service Worker scope is too broad
            if re.search(r'serviceWorker\.register\s*\([^)]*scope\s*:\s*["\']\/["\']', html, re.IGNORECASE):
                vulnerabilities.append({
                    'type': 'service_worker_broad_scope',
                    'severity': 'MEDIUM',
                    'endpoint': self.target_url,
                    'description': 'Service Worker registered with root scope',
                    'impact': 'SW can intercept all site requests',
                    'evidence': 'SW scope set to root (/)',
                    'recommendation': 'Use minimal necessary scope for Service Workers',
                    'cwe': 'CWE-269: Improper Privilege Management'
                })
        
        return vulnerabilities
    
    def _check_cors_misconfiguration(self, headers: dict) -> List[Dict]:
        """Check for CORS misconfigurations"""
        vulnerabilities = []
        
        acao = headers.get('Access-Control-Allow-Origin', '')
        acac = headers.get('Access-Control-Allow-Credentials', '')
        
        # Check for wildcard with credentials
        if acao == '*' and acac.lower() == 'true':
            vulnerabilities.append({
                'type': 'cors_wildcard_with_credentials',
                'severity': 'HIGH',
                'endpoint': self.target_url,
                'description': 'CORS wildcard origin with credentials',
                'impact': 'Any origin can read responses with credentials',
                'evidence': 'Access-Control-Allow-Origin: * with Allow-Credentials: true',
                'recommendation': 'Use specific origins, not wildcard with credentials',
                'cwe': 'CWE-346: Origin Validation Error'
            })
        
        # Check for null origin
        if acao == 'null':
            vulnerabilities.append({
                'type': 'cors_null_origin',
                'severity': 'HIGH',
                'endpoint': self.target_url,
                'description': 'CORS allows null origin',
                'impact': 'Local files can access the resource',
                'evidence': 'Access-Control-Allow-Origin: null',
                'recommendation': 'Do not allow null origin',
                'cwe': 'CWE-346: Origin Validation Error'
            })
        
        return vulnerabilities
    
    def _check_client_side_validation_bypass(self, html: str) -> List[Dict]:
        """Check for client-side validation that can be bypassed"""
        vulnerabilities = []
        
        # Check for validation only in JavaScript
        validation_patterns = [
            r'<input[^>]+required[^>]*>',
            r'<input[^>]+pattern\s*=',
            r'<input[^>]+maxlength\s*=',
        ]
        
        has_client_validation = any(re.search(p, html, re.IGNORECASE) for p in validation_patterns)
        
        if has_client_validation:
            # Check if there's server-side validation indication
            if not re.search(r'<form[^>]+method\s*=\s*["\']post["\']', html, re.IGNORECASE):
                vulnerabilities.append({
                    'type': 'client_side_validation_only',
                    'severity': 'MEDIUM',
                    'endpoint': self.target_url,
                    'description': 'Relies on client-side validation only',
                    'impact': 'Attacker can bypass validation by disabling JavaScript',
                    'evidence': 'Client-side validation found without server-side backup',
                    'recommendation': 'Always validate on server-side, never trust client',
                    'cwe': 'CWE-602: Client-Side Enforcement of Server-Side Security'
                })
        
        return vulnerabilities
    
    def _check_prototype_pollution(self, html: str) -> List[Dict]:
        """Check for prototype pollution vulnerabilities"""
        vulnerabilities = []
        
        # Check for dangerous object operations
        dangerous_patterns = [
            r'Object\.assign\s*\([^)]*location\.|Object\.assign\s*\([^)]*window\.',
            r'\.hasOwnProperty\s*\(',
            r'for\s*\(\s*\w+\s+in\s+',
            r'JSON\.parse\s*\([^)]*location\.',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, html, re.IGNORECASE):
                # Check if __proto__ is checked
                if '__proto__' not in html and 'constructor' not in html:
                    vulnerabilities.append({
                        'type': 'prototype_pollution',
                        'severity': 'HIGH',
                        'endpoint': self.target_url,
                        'description': 'Potential prototype pollution vulnerability',
                        'impact': 'Attacker can inject properties into Object.prototype',
                        'evidence': 'Unsafe object operations without prototype checks',
                        'recommendation': 'Validate object keys, use Object.create(null), check for __proto__',
                        'cwe': 'CWE-1321: Prototype Pollution'
                    })
                    break
        
        return vulnerabilities
    
    def _check_dangling_markup(self, html: str) -> List[Dict]:
        """Check for dangling markup injection"""
        vulnerabilities = []
        
        # Check for user input in attributes without proper encoding
        dangerous_contexts = [
            r'<[^>]+\s+\w+\s*=\s*["\'][^"\']*\{\{[^}]*\}\}',  # Template injection in attrs
            r'<[^>]+\s+href\s*=\s*["\'][^"\']*\$',  # Variable in href
            r'<[^>]+\s+src\s*=\s*["\'][^"\']*\$',   # Variable in src
        ]
        
        for pattern in dangerous_contexts:
            if re.search(pattern, html):
                vulnerabilities.append({
                    'type': 'dangling_markup_injection',
                    'severity': 'MEDIUM',
                    'endpoint': self.target_url,
                    'description': 'Potential dangling markup injection',
                    'impact': 'Attacker can inject markup to capture sensitive data',
                    'evidence': 'User-controlled data in HTML attributes',
                    'recommendation': 'Properly encode all user input in HTML contexts',
                    'cwe': 'CWE-79: Cross-site Scripting'
                })
                break
        
        return vulnerabilities


# Test function
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    print("="*70)
    print("Client-Side Vulnerability Scanner - Test")
    print("="*70 + "\n")
    
    target = "http://localhost:8080"
    scanner = ClientSideScanner(target)
    
    vulnerabilities = scanner.scan_all()
    
    print(f"\n[+] Found {len(vulnerabilities)} client-side vulnerabilities\n")
    
    for vuln in vulnerabilities:
        print(f"Type: {vuln['type']}")
        print(f"Severity: {vuln['severity']}")
        print(f"Description: {vuln['description']}")
        print("-" * 70)
