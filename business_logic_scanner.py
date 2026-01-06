"""
Advanced Business Logic Vulnerability Scanner
==============================================

Detects complex business logic flaws
Race conditions, workflow exploits, payment issues, etc.

Author: AI Pentest Brain Team
Version: 1.0
"""

import requests
import time
import threading
from typing import Dict, List, Optional, Callable
import logging
import json
from concurrent.futures import ThreadPoolExecutor
import hashlib

logger = logging.getLogger(__name__)


class BusinessLogicScanner:
    """
    Advanced business logic vulnerability scanner
    Tests for application-specific logic flaws
    """
    
    def __init__(self, target_url: str):
        self.target_url = target_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scan_all(self) -> List[Dict]:
        """Run all business logic vulnerability scans"""
        logger.info(f"Starting business logic vulnerability scan on {self.target_url}")
        
        vulnerabilities = []
        
        vulnerabilities.extend(self._check_race_conditions())
        vulnerabilities.extend(self._check_negative_values())
        vulnerabilities.extend(self._check_price_manipulation())
        vulnerabilities.extend(self._check_quantity_manipulation())
        vulnerabilities.extend(self._check_workflow_bypass())
        vulnerabilities.extend(self._check_payment_logic())
        vulnerabilities.extend(self._check_coupon_abuse())
        vulnerabilities.extend(self._check_referral_abuse())
        vulnerabilities.extend(self._check_toctou())
        vulnerabilities.extend(self._check_insufficient_throttling())
        
        return vulnerabilities
    
    def _check_race_conditions(self) -> List[Dict]:
        """Check for race condition vulnerabilities"""
        vulnerabilities = []
        
        # Test endpoints that might have race conditions
        test_endpoints = [
            '/api/purchase',
            '/api/redeem',
            '/api/transfer',
            '/api/withdraw',
            '/api/claim',
            '/api/vote',
            '/cart/checkout'
        ]
        
        for path in test_endpoints:
            url = self.target_url.rstrip('/') + path
            
            try:
                # Send multiple simultaneous requests
                num_requests = 10
                results = []
                
                def make_request():
                    try:
                        resp = self.session.post(
                            url,
                            json={'test': 'race_condition'},
                            timeout=5
                        )
                        return resp.status_code
                    except:
                        return None
                
                # Execute requests in parallel
                with ThreadPoolExecutor(max_workers=num_requests) as executor:
                    futures = [executor.submit(make_request) for _ in range(num_requests)]
                    results = [f.result() for f in futures]
                
                # Check if all requests succeeded
                successful_requests = [r for r in results if r and r == 200]
                
                if len(successful_requests) >= num_requests * 0.8:
                    vulnerabilities.append({
                        'type': 'race_condition',
                        'severity': 'HIGH',
                        'endpoint': url,
                        'description': 'Race condition vulnerability detected',
                        'impact': 'Attacker can exploit timing to perform actions multiple times',
                        'evidence': f'{len(successful_requests)}/{num_requests} concurrent requests succeeded',
                        'recommendation': 'Implement proper locking mechanisms and transaction isolation',
                        'cwe': 'CWE-362: Race Condition'
                    })
                    break
            
            except Exception as e:
                logger.debug(f"Race condition check error for {url}: {str(e)}")
        
        return vulnerabilities
    
    def _check_negative_values(self) -> List[Dict]:
        """Check for negative number vulnerabilities"""
        vulnerabilities = []
        
        # Test endpoints with numeric parameters
        test_params = [
            ('quantity', -1),
            ('amount', -100),
            ('price', -50),
            ('count', -5),
            ('balance', -1000)
        ]
        
        for param_name, negative_value in test_params:
            try:
                response = self.session.post(
                    self.target_url,
                    json={param_name: negative_value},
                    timeout=5
                )
                
                # Check if negative value was accepted
                if response.status_code == 200 and 'error' not in response.text.lower():
                    vulnerabilities.append({
                        'type': 'negative_value_accepted',
                        'severity': 'HIGH',
                        'endpoint': self.target_url,
                        'description': f'Application accepts negative {param_name}',
                        'impact': 'Attacker can manipulate values to gain credit/items',
                        'evidence': f'Negative {param_name} ({negative_value}) accepted',
                        'recommendation': 'Validate that all quantities/prices are positive',
                        'cwe': 'CWE-20: Improper Input Validation'
                    })
                    break
            
            except Exception as e:
                logger.debug(f"Negative value check error: {str(e)}")
        
        return vulnerabilities
    
    def _check_price_manipulation(self) -> List[Dict]:
        """Check for price manipulation vulnerabilities"""
        vulnerabilities = []
        
        try:
            # Try to manipulate price in request
            test_data = {
                'item_id': '123',
                'quantity': 1,
                'price': 0.01  # Try to set low price
            }
            
            response = self.session.post(
                self.target_url + '/api/purchase',
                json=test_data,
                timeout=5
            )
            
            # Check if modified price was accepted
            if response.status_code == 200:
                vulnerabilities.append({
                    'type': 'price_manipulation',
                    'severity': 'CRITICAL',
                    'endpoint': self.target_url,
                    'description': 'Price parameter can be manipulated in purchase request',
                    'impact': 'Attacker can purchase items at arbitrary prices',
                    'evidence': 'Client-provided price accepted',
                    'recommendation': 'Always fetch price from server-side database, never trust client',
                    'cwe': 'CWE-840: Business Logic Errors'
                })
        
        except Exception as e:
            logger.debug(f"Price manipulation check error: {str(e)}")
        
        return vulnerabilities
    
    def _check_quantity_manipulation(self) -> List[Dict]:
        """Check for quantity manipulation"""
        vulnerabilities = []
        
        try:
            # Try extreme quantities
            test_quantities = [0, -1, 9999999, 2147483647]  # Include max int
            
            for qty in test_quantities:
                response = self.session.post(
                    self.target_url + '/api/cart/add',
                    json={'item_id': '123', 'quantity': qty},
                    timeout=5
                )
                
                if response.status_code == 200 and 'error' not in response.text.lower():
                    vulnerabilities.append({
                        'type': 'quantity_manipulation',
                        'severity': 'HIGH',
                        'endpoint': self.target_url,
                        'description': f'Application accepts invalid quantity: {qty}',
                        'impact': 'Attacker can manipulate order quantities to cause issues',
                        'evidence': f'Quantity {qty} accepted',
                        'recommendation': 'Validate quantity is positive and within reasonable limits',
                        'cwe': 'CWE-20: Improper Input Validation'
                    })
                    break
        
        except Exception as e:
            logger.debug(f"Quantity manipulation check error: {str(e)}")
        
        return vulnerabilities
    
    def _check_workflow_bypass(self) -> List[Dict]:
        """Check for workflow bypass vulnerabilities"""
        vulnerabilities = []
        
        # Common workflow endpoints
        workflows = [
            ('/step1', '/step2', '/step3'),  # Multi-step process
            ('/cart', '/checkout', '/confirm'),  # E-commerce
            ('/register', '/verify', '/activate'),  # Registration
        ]
        
        for workflow in workflows:
            try:
                # Try to skip to final step without previous steps
                final_step = self.target_url.rstrip('/') + workflow[-1]
                
                response = self.session.post(final_step, json={'bypass': 'test'}, timeout=5)
                
                # If final step is accessible without prerequisites
                if response.status_code == 200:
                    vulnerabilities.append({
                        'type': 'workflow_bypass',
                        'severity': 'HIGH',
                        'endpoint': final_step,
                        'description': 'Multi-step workflow can be bypassed',
                        'impact': 'Attacker can skip verification/payment steps',
                        'evidence': f'Final step {workflow[-1]} accessible directly',
                        'recommendation': 'Validate all previous steps completed before allowing next step',
                        'cwe': 'CWE-840: Business Logic Errors'
                    })
                    break
            
            except Exception as e:
                logger.debug(f"Workflow bypass check error: {str(e)}")
        
        return vulnerabilities
    
    def _check_payment_logic(self) -> List[Dict]:
        """Check for payment logic vulnerabilities"""
        vulnerabilities = []
        
        try:
            # Test payment bypass scenarios
            payment_tests = [
                {'total': 0},  # Zero payment
                {'total': -100},  # Negative payment
                {'currency': 'XXX'},  # Invalid currency
                {'paid': True, 'amount': 0},  # Boolean bypass
            ]
            
            for test_data in payment_tests:
                response = self.session.post(
                    self.target_url + '/api/payment/process',
                    json=test_data,
                    timeout=5
                )
                
                if response.status_code == 200 and 'success' in response.text.lower():
                    vulnerabilities.append({
                        'type': 'payment_bypass',
                        'severity': 'CRITICAL',
                        'endpoint': self.target_url,
                        'description': 'Payment validation can be bypassed',
                        'impact': 'Attacker can obtain goods/services without payment',
                        'evidence': f'Payment bypass successful with: {test_data}',
                        'recommendation': 'Implement robust server-side payment validation',
                        'cwe': 'CWE-840: Business Logic Errors'
                    })
                    break
        
        except Exception as e:
            logger.debug(f"Payment logic check error: {str(e)}")
        
        return vulnerabilities
    
    def _check_coupon_abuse(self) -> List[Dict]:
        """Check for coupon/promo code abuse"""
        vulnerabilities = []
        
        try:
            # Test if same coupon can be used multiple times
            test_coupon = 'TEST2024'
            
            response1 = self.session.post(
                self.target_url + '/api/coupon/apply',
                json={'code': test_coupon},
                timeout=5
            )
            
            # Try applying same coupon again
            response2 = self.session.post(
                self.target_url + '/api/coupon/apply',
                json={'code': test_coupon},
                timeout=5
            )
            
            # If both succeed, coupon can be reused
            if response1.status_code == 200 and response2.status_code == 200:
                vulnerabilities.append({
                    'type': 'coupon_reuse',
                    'severity': 'MEDIUM',
                    'endpoint': self.target_url,
                    'description': 'Coupon codes can be reused multiple times',
                    'impact': 'Attacker can abuse single-use coupons',
                    'evidence': 'Same coupon applied successfully twice',
                    'recommendation': 'Track coupon usage per user/session and limit reuse',
                    'cwe': 'CWE-840: Business Logic Errors'
                })
        
        except Exception as e:
            logger.debug(f"Coupon abuse check error: {str(e)}")
        
        return vulnerabilities
    
    def _check_referral_abuse(self) -> List[Dict]:
        """Check for referral system abuse"""
        vulnerabilities = []
        
        try:
            # Test self-referral
            test_data = {
                'user_id': '123',
                'referrer_id': '123'  # Self-referral
            }
            
            response = self.session.post(
                self.target_url + '/api/referral/claim',
                json=test_data,
                timeout=5
            )
            
            if response.status_code == 200:
                vulnerabilities.append({
                    'type': 'referral_self_abuse',
                    'severity': 'MEDIUM',
                    'endpoint': self.target_url,
                    'description': 'Users can refer themselves',
                    'impact': 'Attacker can farm referral bonuses',
                    'evidence': 'Self-referral accepted',
                    'recommendation': 'Prevent users from referring themselves',
                    'cwe': 'CWE-840: Business Logic Errors'
                })
        
        except Exception as e:
            logger.debug(f"Referral abuse check error: {str(e)}")
        
        return vulnerabilities
    
    def _check_toctou(self) -> List[Dict]:
        """Check for Time-of-Check to Time-of-Use vulnerabilities"""
        vulnerabilities = []
        
        try:
            # Test TOCTOU in balance check
            # First check balance
            balance_response = self.session.get(
                self.target_url + '/api/balance',
                timeout=5
            )
            
            if balance_response.status_code == 200:
                # Try to spend immediately after check
                spend_response = self.session.post(
                    self.target_url + '/api/transfer',
                    json={'amount': 1000000},  # Large amount
                    timeout=5
                )
                
                # If spend succeeds despite insufficient balance
                if spend_response.status_code == 200:
                    vulnerabilities.append({
                        'type': 'toctou_vulnerability',
                        'severity': 'HIGH',
                        'endpoint': self.target_url,
                        'description': 'TOCTOU vulnerability in balance checking',
                        'impact': 'Attacker can spend more than available balance',
                        'evidence': 'Balance check and spend not atomic',
                        'recommendation': 'Use database transactions with proper isolation',
                        'cwe': 'CWE-367: Time-of-check Time-of-use Race Condition'
                    })
        
        except Exception as e:
            logger.debug(f"TOCTOU check error: {str(e)}")
        
        return vulnerabilities
    
    def _check_insufficient_throttling(self) -> List[Dict]:
        """Check for insufficient throttling on business operations"""
        vulnerabilities = []
        
        # Operations that should be throttled
        throttled_operations = [
            '/api/vote',
            '/api/like',
            '/api/download',
            '/api/password/reset',
            '/api/verification/send'
        ]
        
        for path in throttled_operations:
            try:
                url = self.target_url.rstrip('/') + path
                
                # Send multiple requests quickly
                request_count = 20
                successful_requests = 0
                
                for i in range(request_count):
                    response = self.session.post(url, json={'test': i}, timeout=2)
                    if response.status_code == 200:
                        successful_requests += 1
                
                # If most requests succeeded, throttling is insufficient
                if successful_requests >= request_count * 0.9:
                    vulnerabilities.append({
                        'type': 'insufficient_throttling',
                        'severity': 'MEDIUM',
                        'endpoint': url,
                        'description': 'Business operation lacks proper throttling',
                        'impact': 'Attacker can abuse operation through automation',
                        'evidence': f'{successful_requests}/{request_count} requests succeeded',
                        'recommendation': 'Implement rate limiting on sensitive operations',
                        'cwe': 'CWE-770: Allocation of Resources Without Limits'
                    })
                    break
            
            except Exception as e:
                logger.debug(f"Throttling check error for {path}: {str(e)}")
        
        return vulnerabilities


# Test function
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    print("="*70)
    print("Advanced Business Logic Scanner - Test")
    print("="*70 + "\n")
    
    target = "http://localhost:8080"
    scanner = BusinessLogicScanner(target)
    
    vulnerabilities = scanner.scan_all()
    
    print(f"\n[+] Found {len(vulnerabilities)} business logic vulnerabilities\n")
    
    for vuln in vulnerabilities:
        print(f"Type: {vuln['type']}")
        print(f"Severity: {vuln['severity']}")
        print(f"Description: {vuln['description']}")
        print("-" * 70)
