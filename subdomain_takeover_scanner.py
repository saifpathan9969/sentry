"""
Subdomain Takeover Scanner
===========================

Detects subdomain takeover vulnerabilities

Author: AI Pentest Brain Team
Version: 1.0
"""

import requests
import dns.resolver
import socket
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class SubdomainTakeoverScanner:
    """
    Subdomain takeover vulnerability scanner
    Detects dangling DNS records vulnerable to takeover
    """
    
    def __init__(self, target_domain: str):
        self.target_domain = target_domain
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Fingerprints for various services
        self.service_fingerprints = {
            'github': {
                'cname_patterns': ['github.io'],
                'response_patterns': [
                    'There isn\'t a GitHub Pages site here',
                    'For root URLs (like http://example.com/) you must provide an index.html file'
                ],
                'severity': 'HIGH'
            },
            'heroku': {
                'cname_patterns': ['herokuapp.com'],
                'response_patterns': [
                    'No such app',
                    'There\'s nothing here, yet'
                ],
                'severity': 'HIGH'
            },
            'aws_s3': {
                'cname_patterns': ['s3.amazonaws.com', 's3-website'],
                'response_patterns': [
                    'NoSuchBucket',
                    'The specified bucket does not exist'
                ],
                'severity': 'CRITICAL'
            },
            'azure': {
                'cname_patterns': ['azurewebsites.net', 'cloudapp.net', 'cloudapp.azure.com'],
                'response_patterns': [
                    'Error 404',
                    'Web App - Unavailable'
                ],
                'severity': 'HIGH'
            },
            'aws_eb': {
                'cname_patterns': ['elasticbeanstalk.com'],
                'response_patterns': [
                    'CNAME record pointing to',
                    'Elastic Beanstalk'
                ],
                'severity': 'HIGH'
            },
            'bitbucket': {
                'cname_patterns': ['bitbucket.io'],
                'response_patterns': [
                    'Repository not found'
                ],
                'severity': 'HIGH'
            },
            'shopify': {
                'cname_patterns': ['myshopify.com'],
                'response_patterns': [
                    'Sorry, this shop is currently unavailable',
                    'Only one step left!'
                ],
                'severity': 'HIGH'
            },
            'tumblr': {
                'cname_patterns': ['tumblr.com'],
                'response_patterns': [
                    'Whatever you were looking for doesn\'t currently exist'
                ],
                'severity': 'MEDIUM'
            },
            'wordpress': {
                'cname_patterns': ['wordpress.com'],
                'response_patterns': [
                    'Do you want to register'
                ],
                'severity': 'MEDIUM'
            },
            'ghost': {
                'cname_patterns': ['ghost.io'],
                'response_patterns': [
                    'The thing you were looking for is no longer here'
                ],
                'severity': 'MEDIUM'
            },
            'fastly': {
                'cname_patterns': ['fastly.net'],
                'response_patterns': [
                    'Fastly error: unknown domain'
                ],
                'severity': 'HIGH'
            },
            'netlify': {
                'cname_patterns': ['netlify.com', 'netlify.app'],
                'response_patterns': [
                    'Not Found - Request ID'
                ],
                'severity': 'HIGH'
            },
            'vercel': {
                'cname_patterns': ['vercel.app'],
                'response_patterns': [
                    'The deployment could not be found'
                ],
                'severity': 'HIGH'
            }
        }
    
    def scan_all(self) -> List[Dict]:
        """Run all subdomain takeover checks"""
        logger.info(f"Starting subdomain takeover scan on {self.target_domain}")
        
        vulnerabilities = []
        
        # Get subdomains
        subdomains = self._discover_subdomains()
        logger.info(f"Found {len(subdomains)} subdomains to check")
        
        for subdomain in subdomains:
            vulns = self._check_subdomain_takeover(subdomain)
            vulnerabilities.extend(vulns)
        
        return vulnerabilities
    
    def _discover_subdomains(self) -> List[str]:
        """Discover subdomains (simplified - would normally use comprehensive enumeration)"""
        common_subdomains = [
            'www', 'mail', 'ftp', 'localhost', 'webmail', 'smtp', 'pop', 'ns1', 'webdisk',
            'ns2', 'cpanel', 'whm', 'autodiscover', 'autoconfig', 'm', 'imap', 'test', 'ns',
            'blog', 'pop3', 'dev', 'www2', 'admin', 'forum', 'news', 'vpn', 'ns3', 'mail2',
            'new', 'mysql', 'old', 'lists', 'support', 'mobile', 'mx', 'static', 'docs', 'beta',
            'shop', 'sql', 'secure', 'demo', 'cp', 'calendar', 'wiki', 'web', 'media', 'email',
            'images', 'img', 'www1', 'intranet', 'portal', 'video', 'sip', 'dns2', 'api', 'cdn',
            'stats', 'dns1', 'ns4', 'www3', 'dns', 'search', 'staging', 'server', 'mx1', 'chat',
            'wap', 'my', 'svn', 'mail1', 'sites', 'proxy', 'ads', 'host', 'crm', 'cms', 'backup',
            'mx2', 'lyncdiscover', 'info', 'apps', 'download', 'remote', 'db', 'forums', 'store',
            'relay', 'files', 'newsletter', 'app', 'live', 'owa', 'en', 'start', 'sms', 'office',
            'exchange', 'ipv4'
        ]
        
        found_subdomains = []
        
        for sub in common_subdomains[:20]:  # Limit to first 20 for performance
            subdomain = f"{sub}.{self.target_domain}"
            try:
                # Try DNS resolution
                dns.resolver.resolve(subdomain, 'A')
                found_subdomains.append(subdomain)
            except:
                continue
        
        return found_subdomains
    
    def _check_subdomain_takeover(self, subdomain: str) -> List[Dict]:
        """Check if subdomain is vulnerable to takeover"""
        vulnerabilities = []
        
        try:
            # Get CNAME records
            try:
                answers = dns.resolver.resolve(subdomain, 'CNAME')
                cnames = [str(rdata.target).rstrip('.') for rdata in answers]
            except:
                cnames = []
            
            # If no CNAME, check A record
            if not cnames:
                try:
                    answers = dns.resolver.resolve(subdomain, 'A')
                    # Has A record, probably not vulnerable
                    return vulnerabilities
                except:
                    # No A or CNAME record - potential takeover
                    vulnerabilities.append({
                        'type': 'subdomain_takeover_dangling_dns',
                        'severity': 'HIGH',
                        'subdomain': subdomain,
                        'description': f'Dangling DNS record for {subdomain}',
                        'impact': 'Subdomain can be taken over by registering the service',
                        'evidence': 'No A or CNAME records found',
                        'recommendation': 'Remove DNS record or configure proper destination',
                        'cwe': 'CWE-350: Reliance on Reverse DNS Resolution'
                    })
                    return vulnerabilities
            
            # Check each CNAME against fingerprints
            for cname in cnames:
                for service, fingerprint in self.service_fingerprints.items():
                    # Check if CNAME matches service pattern
                    if any(pattern in cname for pattern in fingerprint['cname_patterns']):
                        # Try to access the subdomain
                        try:
                            response = self.session.get(
                                f"http://{subdomain}",
                                timeout=10,
                                allow_redirects=True
                            )
                            
                            response_text = response.text
                            
                            # Check for takeover indicators
                            if any(pattern in response_text for pattern in fingerprint['response_patterns']):
                                vulnerabilities.append({
                                    'type': 'subdomain_takeover',
                                    'severity': fingerprint['severity'],
                                    'subdomain': subdomain,
                                    'service': service,
                                    'description': f'Subdomain takeover vulnerability via {service}',
                                    'impact': 'Attacker can host malicious content on your subdomain',
                                    'evidence': f'CNAME points to {cname} but service is unclaimed',
                                    'recommendation': f'Remove DNS record or claim {service} account',
                                    'cwe': 'CWE-350: Reliance on Reverse DNS Resolution'
                                })
                        
                        except requests.exceptions.ConnectionError:
                            # Connection failed - likely unclaimed
                            vulnerabilities.append({
                                'type': 'subdomain_takeover_unclaimed',
                                'severity': fingerprint['severity'],
                                'subdomain': subdomain,
                                'service': service,
                                'description': f'Subdomain points to unclaimed {service} service',
                                'impact': 'Attacker can claim service and host malicious content',
                                'evidence': f'CNAME: {cname} - Connection failed',
                                'recommendation': f'Remove DNS record or claim {service} account',
                                'cwe': 'CWE-350: Reliance on Reverse DNS Resolution'
                            })
                        
                        except Exception as e:
                            logger.debug(f"Error checking {subdomain}: {str(e)}")
        
        except Exception as e:
            logger.debug(f"Subdomain check error for {subdomain}: {str(e)}")
        
        return vulnerabilities


# Test function
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    print("="*70)
    print("Subdomain Takeover Scanner - Test")
    print("="*70 + "\n")
    
    # Example usage
    target = "example.com"  # Replace with actual domain
    scanner = SubdomainTakeoverScanner(target)
    
    vulnerabilities = scanner.scan_all()
    
    print(f"\n[+] Found {len(vulnerabilities)} subdomain takeover vulnerabilities\n")
    
    for vuln in vulnerabilities:
        print(f"Type: {vuln['type']}")
        print(f"Severity: {vuln['severity']}")
        print(f"Subdomain: {vuln.get('subdomain', 'N/A')}")
        print(f"Description: {vuln['description']}")
        print("-" * 70)
