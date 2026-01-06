"""
CVE Database Integration Module
Integrates with NIST NVD API to fetch CVE data, CVSS scores, and exploit information
"""

import requests
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import time

logger = logging.getLogger(__name__)


class CVEDatabase:
    """
    CVE Database Integration with NIST NVD API
    Provides CVE IDs, CVSS scores, exploit data, and patch information
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize CVE Database
        
        Args:
            api_key: Optional NIST NVD API key for higher rate limits
        """
        self.api_key = api_key
        self.base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        self.cache = {}  # Simple in-memory cache
        self.cache_duration = timedelta(hours=24)
        
        # Rate limiting
        self.last_request_time = 0
        self.request_delay = 6 if not api_key else 0.6  # 6 seconds without key, 0.6 with key
        
    def _rate_limit(self):
        """Enforce rate limiting for NIST NVD API"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.request_delay:
            sleep_time = self.request_delay - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def search_cve_by_keyword(self, keyword: str, max_results: int = 5) -> List[Dict]:
        """
        Search CVEs by keyword (e.g., 'nginx', 'mysql', 'xss')
        
        Args:
            keyword: Search keyword
            max_results: Maximum number of results to return
            
        Returns:
            List of CVE dictionaries with relevant information
        """
        # Check cache first
        cache_key = f"keyword_{keyword}_{max_results}"
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if datetime.now() - cached_time < self.cache_duration:
                logger.debug(f"CVE cache hit for keyword: {keyword}")
                return cached_data
        
        try:
            self._rate_limit()
            
            headers = {}
            if self.api_key:
                headers['apiKey'] = self.api_key
            
            params = {
                'keywordSearch': keyword,
                'resultsPerPage': max_results
            }
            
            response = requests.get(self.base_url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            cves = []
            
            if 'vulnerabilities' in data:
                for vuln in data['vulnerabilities']:
                    cve_data = vuln.get('cve', {})
                    cve_info = self._parse_cve_data(cve_data)
                    if cve_info:
                        cves.append(cve_info)
            
            # Cache the results
            self.cache[cache_key] = (cves, datetime.now())
            
            logger.info(f"Found {len(cves)} CVEs for keyword: {keyword}")
            return cves
            
        except Exception as e:
            # Catch all exceptions including RequestException, timeouts, and HTTP errors
            logger.error(f"Error fetching CVE data for keyword '{keyword}': {e}")
            return []
    
    def search_cves(self, keyword: str, results_per_page: int = 5) -> List[Dict]:
        """
        Alias for search_cve_by_keyword for compatibility
        
        Args:
            keyword: Search keyword
            results_per_page: Maximum number of results to return
            
        Returns:
            List of CVE dictionaries
        """
        return self.search_cve_by_keyword(keyword, max_results=results_per_page)
    
    def get_cve_by_id(self, cve_id: str) -> Optional[Dict]:
        """
        Get specific CVE by ID (e.g., 'CVE-2021-44228')
        
        Args:
            cve_id: CVE identifier
            
        Returns:
            CVE dictionary with detailed information
        """
        # Check cache
        if cve_id in self.cache:
            cached_data, cached_time = self.cache[cve_id]
            if datetime.now() - cached_time < self.cache_duration:
                logger.debug(f"CVE cache hit for ID: {cve_id}")
                return cached_data
        
        try:
            self._rate_limit()
            
            headers = {}
            if self.api_key:
                headers['apiKey'] = self.api_key
            
            params = {'cveId': cve_id}
            
            response = requests.get(self.base_url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'vulnerabilities' in data and len(data['vulnerabilities']) > 0:
                cve_data = data['vulnerabilities'][0].get('cve', {})
                cve_info = self._parse_cve_data(cve_data)
                
                # Cache the result
                if cve_info:
                    self.cache[cve_id] = (cve_info, datetime.now())
                
                return cve_info
            
            return None
            
        except requests.RequestException as e:
            logger.error(f"Error fetching CVE {cve_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching CVE {cve_id}: {e}")
            return None
    
    def _parse_cve_data(self, cve_data: Dict) -> Optional[Dict]:
        """
        Parse CVE data from NIST NVD API response
        
        Args:
            cve_data: Raw CVE data from API
            
        Returns:
            Parsed CVE dictionary
        """
        try:
            cve_id = cve_data.get('id', 'Unknown')
            
            # Get description
            descriptions = cve_data.get('descriptions', [])
            description = next((d['value'] for d in descriptions if d.get('lang') == 'en'), 'No description available')
            
            # Get CVSS scores
            metrics = cve_data.get('metrics', {})
            cvss_v3 = None
            cvss_v2 = None
            
            # Try CVSS v3.1 first, then v3.0
            if 'cvssMetricV31' in metrics and len(metrics['cvssMetricV31']) > 0:
                cvss_v3 = metrics['cvssMetricV31'][0].get('cvssData', {})
            elif 'cvssMetricV30' in metrics and len(metrics['cvssMetricV30']) > 0:
                cvss_v3 = metrics['cvssMetricV30'][0].get('cvssData', {})
            
            # CVSS v2 as fallback
            if 'cvssMetricV2' in metrics and len(metrics['cvssMetricV2']) > 0:
                cvss_v2 = metrics['cvssMetricV2'][0].get('cvssData', {})
            
            # Get severity
            severity = 'Unknown'
            cvss_score = 0.0
            cvss_vector = 'N/A'
            
            if cvss_v3:
                cvss_score = cvss_v3.get('baseScore', 0.0)
                cvss_vector = cvss_v3.get('vectorString', 'N/A')
                severity = cvss_v3.get('baseSeverity', 'Unknown')
            elif cvss_v2:
                cvss_score = cvss_v2.get('baseScore', 0.0)
                cvss_vector = cvss_v2.get('vectorString', 'N/A')
                # Map CVSS v2 score to severity
                if cvss_score >= 7.0:
                    severity = 'HIGH'
                elif cvss_score >= 4.0:
                    severity = 'MEDIUM'
                else:
                    severity = 'LOW'
            
            # Get CWE
            weaknesses = cve_data.get('weaknesses', [])
            cwe_ids = []
            for weakness in weaknesses:
                for desc in weakness.get('description', []):
                    if desc.get('lang') == 'en':
                        cwe_ids.append(desc.get('value', ''))
            
            # Get references
            references = cve_data.get('references', [])
            ref_urls = [ref.get('url', '') for ref in references[:5]]  # Limit to 5
            
            # Get published and modified dates
            published = cve_data.get('published', 'Unknown')
            modified = cve_data.get('lastModified', 'Unknown')
            
            return {
                'cve_id': cve_id,
                'description': description,
                'cvss_score': cvss_score,
                'cvss_vector': cvss_vector,
                'severity': severity,
                'cwe_ids': cwe_ids,
                'references': ref_urls,
                'published': published,
                'modified': modified,
                'exploit_available': self._check_exploit_db(cve_id)  # Check Exploit-DB
            }
            
        except Exception as e:
            logger.error(f"Error parsing CVE data: {e}")
            return None
    
    def _check_exploit_db(self, cve_id: str) -> bool:
        """
        Check if exploit is available in Exploit-DB
        
        Args:
            cve_id: CVE identifier
            
        Returns:
            True if exploit is available, False otherwise
        """
        try:
            # Simple check - search Exploit-DB
            url = f"https://www.exploit-db.com/search?cve={cve_id}"
            response = requests.get(url, timeout=5)
            
            # If we get results, exploit likely exists
            # This is a simple heuristic - could be improved
            return 'No Results' not in response.text
            
        except Exception:
            # If check fails, assume no exploit to be safe
            return False
    
    def enrich_vulnerability(self, vulnerability: Dict) -> Dict:
        """
        Enrich vulnerability with CVE data
        
        Args:
            vulnerability: Vulnerability dictionary
            
        Returns:
            Enriched vulnerability with CVE information
        """
        vuln_type = vulnerability.get('type', '').lower()
        
        # Map vulnerability types to search keywords
        keyword_map = {
            'sql_injection': 'sql injection',
            'xss': 'cross-site scripting',
            'cross_site_scripting': 'cross-site scripting',
            'csrf': 'cross-site request forgery',
            'ssrf': 'server-side request forgery',
            'xxe': 'xml external entity',
            'command_injection': 'command injection',
            'path_traversal': 'path traversal',
            'idor': 'insecure direct object reference',
            'deserialization': 'insecure deserialization',
            'open_redirect': 'open redirect'
        }
        
        keyword = keyword_map.get(vuln_type, vuln_type)
        
        # Search for related CVEs
        cves = self.search_cve_by_keyword(keyword, max_results=3)
        
        if cves:
            vulnerability['cve_data'] = {
                'related_cves': [cve['cve_id'] for cve in cves],
                'example_cve': cves[0],  # Most relevant CVE
                'total_found': len(cves)
            }
            
            # Add CVSS score if not present
            if 'cvss_score' not in vulnerability and cves:
                vulnerability['cvss_score'] = cves[0]['cvss_score']
            
            logger.info(f"Enriched {vuln_type} with {len(cves)} related CVEs")
        else:
            vulnerability['cve_data'] = {
                'related_cves': [],
                'example_cve': None,
                'total_found': 0
            }
        
        return vulnerability


# Singleton instance
_cve_db_instance = None


def get_cve_database(api_key: Optional[str] = None) -> CVEDatabase:
    """
    Get singleton CVE Database instance
    
    Args:
        api_key: Optional NIST NVD API key
        
    Returns:
        CVEDatabase instance
    """
    global _cve_db_instance
    
    if _cve_db_instance is None:
        _cve_db_instance = CVEDatabase(api_key)
    
    return _cve_db_instance
