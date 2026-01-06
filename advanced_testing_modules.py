"""
Advanced Testing Modules
Includes brute force testing and rate limit testing with safety controls
"""

import time
import logging
from typing import Dict, List, Optional
import requests

logger = logging.getLogger(__name__)


class BruteForceTest:
    """
    Safe brute force testing with strict limits
    """
    
    def __init__(self, max_attempts: int = 3, delay: float = 2.0):
        """
        Initialize brute force tester
        
        Args:
            max_attempts: Maximum attempts (default 3 for safety)
            delay: Delay between attempts in seconds
        """
        self.max_attempts = min(max_attempts, 3)  # Hard limit of 3
        self.delay = delay  # Use provided delay (for testing, can be < 2.0)
    
    def test_login_brute_force(self, url: str, username_field: str = 'username', 
                                password_field: str = 'password') -> Dict:
        """
        Test if login is vulnerable to brute force
        
        Args:
            url: Login URL
            username_field: Username field name
            password_field: Password field name
            
        Returns:
            Test results dictionary
        """
        logger.info(f"Testing brute force protection on {url} (max {self.max_attempts} attempts)")
        
        # Common test credentials (safe, won't actually work)
        test_credentials = [
            ('admin', 'admin'),
            ('test', 'test'),
            ('user', 'password')
        ][:self.max_attempts]
        
        results = {
            'vulnerable': False,
            'attempts_made': 0,
            'blocked': False,
            'rate_limited': False,
            'lockout_detected': False,
            'response_times': []
        }
        
        for i, (username, password) in enumerate(test_credentials, 1):
            try:
                start_time = time.time()
                
                response = requests.post(
                    url,
                    data={username_field: username, password_field: password},
                    timeout=5,
                    allow_redirects=False
                )
                
                elapsed = time.time() - start_time
                results['response_times'].append(elapsed)
                results['attempts_made'] = i
                
                # Check for rate limiting
                if response.status_code == 429:
                    results['rate_limited'] = True
                    results['vulnerable'] = False
                    logger.info(f"Rate limiting detected after {i} attempts")
                    break
                
                # Check for blocking
                if response.status_code == 403:
                    results['blocked'] = True
                    results['vulnerable'] = False
                    logger.info(f"Blocking detected after {i} attempts")
                    break
                
                # Check for lockout messages
                lockout_keywords = ['locked', 'too many', 'try again', 'blocked']
                if any(keyword in response.text.lower() for keyword in lockout_keywords):
                    results['lockout_detected'] = True
                    results['vulnerable'] = False
                    logger.info(f"Account lockout detected after {i} attempts")
                    break
                
                # Delay between attempts
                if i < len(test_credentials):
                    time.sleep(self.delay)
                    
            except requests.RequestException as e:
                logger.error(f"Brute force test error: {e}")
                break
        
        # If we completed all attempts without protection, it's vulnerable
        if results['attempts_made'] == self.max_attempts and not any([
            results['rate_limited'],
            results['blocked'],
            results['lockout_detected']
        ]):
            results['vulnerable'] = True
            logger.warning(f"No brute force protection detected after {self.max_attempts} attempts")
        
        return results
    
    def test_password_policy(self, url: str) -> Dict:
        """
        Test password policy strength
        
        Args:
            url: Registration or password change URL
            
        Returns:
            Policy test results
        """
        weak_passwords = ['123456', 'password', 'test']
        
        results = {
            'weak_passwords_accepted': [],
            'policy_enforced': True,
            'min_length_required': False,
            'complexity_required': False
        }
        
        # This is a passive test - we don't actually submit
        # Just check if there's client-side validation
        try:
            response = requests.get(url, timeout=5)
            html = response.text.lower()
            
            # Check for password requirements in HTML
            if 'minlength' in html or 'minimum' in html:
                results['min_length_required'] = True
            
            if any(word in html for word in ['uppercase', 'lowercase', 'number', 'special']):
                results['complexity_required'] = True
            
            if not results['min_length_required'] and not results['complexity_required']:
                results['policy_enforced'] = False
                
        except Exception as e:
            logger.error(f"Password policy test error: {e}")
        
        return results


class RateLimitTester:
    """
    Rate limit testing with safety controls
    """
    
    def __init__(self, max_requests: int = 10, time_window: float = 10.0):
        """
        Initialize rate limit tester
        
        Args:
            max_requests: Maximum requests to send
            time_window: Time window in seconds
        """
        self.max_requests = min(max_requests, 20)  # Hard limit of 20
        self.time_window = time_window
    
    def test_rate_limiting(self, url: str, method: str = 'GET') -> Dict:
        """
        Test if endpoint has rate limiting
        
        Args:
            url: Target URL
            method: HTTP method (GET or POST)
            
        Returns:
            Test results dictionary
        """
        logger.info(f"Testing rate limiting on {url} ({self.max_requests} requests in {self.time_window}s)")
        
        results = {
            'rate_limited': False,
            'requests_sent': 0,
            'requests_blocked': 0,
            'limit_threshold': None,
            'response_codes': [],
            'average_response_time': 0.0,
            'rate_limit_headers': {}
        }
        
        response_times = []
        start_time = time.time()
        
        for i in range(self.max_requests):
            try:
                req_start = time.time()
                
                if method.upper() == 'GET':
                    response = requests.get(url, timeout=5)
                else:
                    response = requests.post(url, data={}, timeout=5)
                
                req_time = time.time() - req_start
                response_times.append(req_time)
                
                results['requests_sent'] = i + 1
                results['response_codes'].append(response.status_code)
                
                # Check for rate limiting
                if response.status_code == 429:
                    results['rate_limited'] = True
                    results['limit_threshold'] = i + 1
                    results['requests_blocked'] = self.max_requests - i
                    
                    # Extract rate limit headers
                    for header in ['X-RateLimit-Limit', 'X-RateLimit-Remaining', 'Retry-After']:
                        if header in response.headers:
                            results['rate_limit_headers'][header] = response.headers[header]
                    
                    logger.info(f"Rate limiting detected after {i + 1} requests")
                    break
                
                # Check if we're being blocked
                if response.status_code == 403:
                    results['requests_blocked'] += 1
                
                # Small delay to stay within time window
                if i < self.max_requests - 1:
                    elapsed = time.time() - start_time
                    if elapsed < self.time_window:
                        time.sleep(0.1)
                        
            except requests.RequestException as e:
                logger.error(f"Rate limit test error: {e}")
                break
        
        if response_times:
            results['average_response_time'] = sum(response_times) / len(response_times)
        
        # If we completed all requests without rate limiting, it's vulnerable
        if results['requests_sent'] == self.max_requests and not results['rate_limited']:
            logger.warning(f"No rate limiting detected after {self.max_requests} requests")
        
        return results
    
    def test_rate_limit_bypass(self, url: str) -> Dict:
        """
        Test common rate limit bypass techniques
        
        Args:
            url: Target URL
            
        Returns:
            Bypass test results
        """
        results = {
            'bypass_possible': False,
            'bypass_methods': []
        }
        
        # Test 1: Different User-Agent
        try:
            headers1 = {'User-Agent': 'Mozilla/5.0'}
            headers2 = {'User-Agent': 'curl/7.0'}
            
            r1 = requests.get(url, headers=headers1, timeout=5)
            time.sleep(0.5)
            r2 = requests.get(url, headers=headers2, timeout=5)
            
            if r1.status_code == 429 and r2.status_code != 429:
                results['bypass_possible'] = True
                results['bypass_methods'].append('user_agent_rotation')
                
        except Exception as e:
            logger.debug(f"User-Agent bypass test failed: {e}")
        
        # Test 2: X-Forwarded-For header
        try:
            headers = {'X-Forwarded-For': '1.2.3.4'}
            response = requests.get(url, headers=headers, timeout=5)
            
            if response.status_code != 429:
                results['bypass_possible'] = True
                results['bypass_methods'].append('x_forwarded_for')
                
        except Exception as e:
            logger.debug(f"X-Forwarded-For bypass test failed: {e}")
        
        return results


# Singleton instances
_brute_force_tester = None
_rate_limit_tester = None


def get_brute_force_tester(max_attempts: int = 3) -> BruteForceTest:
    """Get singleton brute force tester"""
    global _brute_force_tester
    if _brute_force_tester is None:
        _brute_force_tester = BruteForceTest(max_attempts=max_attempts)
    return _brute_force_tester


def get_rate_limit_tester(max_requests: int = 10) -> RateLimitTester:
    """Get singleton rate limit tester"""
    global _rate_limit_tester
    if _rate_limit_tester is None:
        _rate_limit_tester = RateLimitTester(max_requests=max_requests)
    return _rate_limit_tester
