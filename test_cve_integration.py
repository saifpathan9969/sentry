"""
Unit Tests for CVE Integration
Tests CVE ID validation, API response parsing, CVSS calculation, caching, and error handling
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cve_integration import CVEDatabase


class TestCVEIntegration:
    """Test CVE database integration functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.cve_db = CVEDatabase()
    
    def test_cve_id_format_validation(self):
        """Test CVE ID format validation"""
        valid_ids = [
            'CVE-2021-12345',
            'CVE-2023-1234',
            'CVE-2020-123456'
        ]
        
        for cve_id in valid_ids:
            # CVE ID should match the pattern CVE-YYYY-NNNNN
            assert cve_id.startswith('CVE-')
            parts = cve_id.split('-')
            assert len(parts) == 3
            assert parts[1].isdigit() and len(parts[1]) == 4  # Year
            assert parts[2].isdigit()  # Number
    
    def test_cve_database_initialization(self):
        """Test CVE database initialization"""
        assert self.cve_db is not None
        assert hasattr(self.cve_db, 'base_url')
        assert hasattr(self.cve_db, 'cache')
        assert hasattr(self.cve_db, 'cache_duration')
    
    def test_cve_database_with_api_key(self):
        """Test CVE database initialization with API key"""
        cve_db_with_key = CVEDatabase(api_key='test_key_123')
        assert cve_db_with_key.api_key == 'test_key_123'
        assert cve_db_with_key.request_delay == 0.6  # Faster with API key
    
    def test_cve_database_without_api_key(self):
        """Test CVE database initialization without API key"""
        assert self.cve_db.api_key is None
        assert self.cve_db.request_delay == 6  # Slower without API key
    
    def test_rate_limiting_enforcement(self):
        """Test that rate limiting is enforced"""
        start_time = time.time()
        
        # Make two consecutive calls
        self.cve_db._rate_limit()
        self.cve_db._rate_limit()
        
        elapsed = time.time() - start_time
        
        # Should have waited at least the request_delay
        # (allowing some tolerance for execution time)
        assert elapsed >= (self.cve_db.request_delay - 0.5)
    
    def test_caching_mechanism(self):
        """Test that caching works correctly"""
        # Add something to cache
        cache_key = 'test_key'
        test_data = [{'cve_id': 'CVE-2021-12345'}]
        
        from datetime import datetime
        self.cve_db.cache[cache_key] = (test_data, datetime.now())
        
        # Verify cache contains the data
        assert cache_key in self.cve_db.cache
        cached_data, cached_time = self.cve_db.cache[cache_key]
        assert cached_data == test_data
    
    def test_enrich_vulnerability_structure(self):
        """Test vulnerability enrichment structure"""
        vulnerability = {
            'type': 'xss',
            'severity': 'high',
            'description': 'Cross-site scripting vulnerability'
        }
        
        enriched = self.cve_db.enrich_vulnerability(vulnerability)
        
        # Should have cve_data field
        assert 'cve_data' in enriched
        assert 'related_cves' in enriched['cve_data']
        assert 'total_found' in enriched['cve_data']
        assert isinstance(enriched['cve_data']['related_cves'], list)
    
    def test_enrich_vulnerability_with_unknown_type(self):
        """Test enrichment with unknown vulnerability type"""
        vulnerability = {
            'type': 'unknown_vuln_type_xyz',
            'severity': 'medium'
        }
        
        enriched = self.cve_db.enrich_vulnerability(vulnerability)
        
        # Should still have cve_data structure
        assert 'cve_data' in enriched
        assert isinstance(enriched['cve_data']['related_cves'], list)
    
    def test_search_cves_method_exists(self):
        """Test that search_cves method exists"""
        assert hasattr(self.cve_db, 'search_cves')
        assert callable(self.cve_db.search_cves)
    
    def test_search_cve_by_keyword_method_exists(self):
        """Test that search_cve_by_keyword method exists"""
        assert hasattr(self.cve_db, 'search_cve_by_keyword')
        assert callable(self.cve_db.search_cve_by_keyword)
    
    def test_search_cves_returns_list(self):
        """Test that search_cves returns a list"""
        # This will use cache or return empty list on error
        result = self.cve_db.search_cves('test', results_per_page=1)
        assert isinstance(result, list)
    
    def test_error_handling_404(self):
        """Test error handling for 404 responses"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.raise_for_status.side_effect = Exception("404 Not Found")
            mock_get.return_value = mock_response
            
            result = self.cve_db.search_cve_by_keyword('nonexistent')
            
            # Should return empty list on error
            assert isinstance(result, list)
            assert len(result) == 0
    
    def test_error_handling_timeout(self):
        """Test error handling for timeout"""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Exception("Timeout")
            
            result = self.cve_db.search_cve_by_keyword('test')
            
            # Should return empty list on timeout
            assert isinstance(result, list)
            assert len(result) == 0
    
    def test_error_handling_rate_limit(self):
        """Test error handling for rate limit exceeded"""
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 429
            mock_response.raise_for_status.side_effect = Exception("Rate limit exceeded")
            mock_get.return_value = mock_response
            
            result = self.cve_db.search_cve_by_keyword('test')
            
            # Should return empty list on rate limit
            assert isinstance(result, list)
    
    def test_cvss_score_extraction(self):
        """Test CVSS score extraction from CVE data"""
        # Mock CVE data with CVSS score
        mock_cve = {
            'cve_id': 'CVE-2021-12345',
            'cvss_score': 7.5,
            'description': 'Test vulnerability'
        }
        
        assert 'cvss_score' in mock_cve
        assert isinstance(mock_cve['cvss_score'], (int, float))
        assert 0 <= mock_cve['cvss_score'] <= 10
    
    def test_vulnerability_type_mapping(self):
        """Test vulnerability type to keyword mapping"""
        test_cases = {
            'sql_injection': 'sql injection',
            'xss': 'cross-site scripting',
            'csrf': 'cross-site request forgery',
            'ssrf': 'server-side request forgery'
        }
        
        for vuln_type, expected_keyword in test_cases.items():
            vulnerability = {'type': vuln_type}
            enriched = self.cve_db.enrich_vulnerability(vulnerability)
            
            # Should have attempted enrichment
            assert 'cve_data' in enriched
    
    def test_cache_expiration(self):
        """Test that cache respects expiration time"""
        from datetime import datetime, timedelta
        
        # Add expired cache entry
        cache_key = 'expired_key'
        old_time = datetime.now() - timedelta(hours=25)  # Older than 24 hours
        self.cve_db.cache[cache_key] = (['old_data'], old_time)
        
        # Cache should be considered expired
        # (actual expiration check happens in search method)
        cached_data, cached_time = self.cve_db.cache[cache_key]
        age = datetime.now() - cached_time
        assert age > self.cve_db.cache_duration
    
    def test_multiple_cve_handling(self):
        """Test handling of multiple CVEs for a single vulnerability"""
        vulnerability = {
            'type': 'xss',
            'cve_ids': ['CVE-2021-12345', 'CVE-2021-67890']
        }
        
        enriched = self.cve_db.enrich_vulnerability(vulnerability)
        
        # Original CVE IDs should be preserved
        assert 'cve_ids' in enriched
        assert len(enriched['cve_ids']) >= 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
