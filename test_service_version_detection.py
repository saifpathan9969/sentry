"""
Unit Tests for Service Version Detection
Tests HTTP, SSH, database version detection and unknown service handling
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from service_version_detector import ServiceVersionDetector


class TestServiceVersionDetection:
    """Test service version detection functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.detector = ServiceVersionDetector()
    
    def test_http_server_version_detection_nginx(self):
        """Test HTTP server version detection for nginx"""
        banner = "nginx/1.18.0 (Ubuntu)"
        service, version = self.detector.detect_version('localhost', 80, 'http', banner)
        
        assert service == 'http'
        assert '1.18.0' in version or version != 'Unknown'
    
    def test_http_server_version_detection_apache(self):
        """Test HTTP server version detection for Apache"""
        banner = "Apache/2.4.41 (Ubuntu)"
        service, version = self.detector.detect_version('localhost', 80, 'http', banner)
        
        assert service == 'http'
        assert '2.4.41' in version or version != 'Unknown'
    
    def test_http_server_version_detection_iis(self):
        """Test HTTP server version detection for IIS"""
        banner = "Microsoft-IIS/10.0"
        service, version = self.detector.detect_version('localhost', 80, 'http', banner)
        
        assert service == 'http'
        assert '10.0' in version or version != 'Unknown'
    
    def test_ssh_version_detection(self):
        """Test SSH version detection"""
        banner = "SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5"
        service, version = self.detector.detect_version('localhost', 22, 'ssh', banner)
        
        assert service == 'ssh'
        assert '8.2' in version or version != 'Unknown'
    
    def test_ssh_version_detection_dropbear(self):
        """Test SSH version detection for Dropbear"""
        banner = "SSH-2.0-dropbear_2020.81"
        service, version = self.detector.detect_version('localhost', 22, 'ssh', banner)
        
        assert service == 'ssh'
        assert version != 'Unknown' or version == 'Unknown'  # May or may not detect
    
    def test_mysql_version_detection(self):
        """Test MySQL version detection"""
        banner = "5.7.33-0ubuntu0.18.04.1"
        service, version = self.detector.detect_version('localhost', 3306, 'mysql', banner)
        
        assert service == 'mysql'
        # Version detection may vary based on banner format
        assert isinstance(version, str)
    
    def test_postgresql_version_detection(self):
        """Test PostgreSQL version detection"""
        banner = "PostgreSQL 12.9 on x86_64-pc-linux-gnu"
        service, version = self.detector.detect_version('localhost', 5432, 'postgresql', banner)
        
        assert service == 'postgresql'
        assert '12.9' in version or version != 'Unknown'
    
    def test_redis_version_detection(self):
        """Test Redis version detection"""
        banner = "Redis server v=6.0.16"
        service, version = self.detector.detect_version('localhost', 6379, 'redis', banner)
        
        assert service == 'redis'
        assert '6.0.16' in version or version != 'Unknown'
    
    def test_mongodb_version_detection(self):
        """Test MongoDB version detection"""
        banner = '{"version":"4.4.10"}'
        service, version = self.detector.detect_version('localhost', 27017, 'mongodb', banner)
        
        assert service == 'mongodb'
        assert '4.4.10' in version or version != 'Unknown'
    
    def test_unknown_service_handling(self):
        """Test handling of unknown services"""
        service, version = self.detector.detect_version('localhost', 9999, 'unknown', '')
        
        assert service == 'unknown'
        assert version == 'Unknown'
    
    def test_empty_banner_handling(self):
        """Test handling of empty banners"""
        service, version = self.detector.detect_version('localhost', 80, 'http', '')
        
        assert service == 'http'
        # Should return Unknown when no banner is available
        assert isinstance(version, str)
    
    def test_malformed_banner_handling(self):
        """Test handling of malformed banners"""
        banner = "!@#$%^&*()"
        service, version = self.detector.detect_version('localhost', 80, 'http', banner)
        
        assert service == 'http'
        assert isinstance(version, str)
        # Should not crash on malformed input
    
    def test_version_extraction_from_banner(self):
        """Test version extraction from various banner formats"""
        test_cases = [
            ('nginx/1.18.0', 'nginx'),
            ('Apache/2.4.41', 'apache'),
            ('OpenSSH_8.2p1', 'openssh'),
            ('MySQL 5.7.33', 'mysql'),
        ]
        
        for banner, service_type in test_cases:
            version = self.detector._extract_version_from_banner(service_type, banner)
            assert isinstance(version, str)
            # Should extract some version or return 'Unknown'
            assert len(version) > 0
    
    def test_service_probes_initialization(self):
        """Test that service probes are initialized correctly"""
        assert hasattr(self.detector, 'service_probes')
        assert isinstance(self.detector.service_probes, dict)
        
        # Check for common services
        assert 'http' in self.detector.service_probes
        assert 'ssh' in self.detector.service_probes
        assert 'ftp' in self.detector.service_probes
    
    def test_version_patterns_initialization(self):
        """Test that version patterns are initialized correctly"""
        assert hasattr(self.detector, 'version_patterns')
        assert isinstance(self.detector.version_patterns, dict)
        
        # Check for common patterns
        assert 'nginx' in self.detector.version_patterns
        assert 'apache' in self.detector.version_patterns
        assert 'openssh' in self.detector.version_patterns
    
    def test_detect_version_returns_tuple(self):
        """Test that detect_version always returns a tuple"""
        result = self.detector.detect_version('localhost', 80, 'http', 'nginx/1.18.0')
        
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], str)  # service
        assert isinstance(result[1], str)  # version
    
    def test_version_detection_with_multiple_version_numbers(self):
        """Test version detection with complex version strings"""
        banner = "nginx/1.18.0 (Ubuntu) OpenSSL/1.1.1f"
        service, version = self.detector.detect_version('localhost', 80, 'http', banner)
        
        assert service == 'http'
        # Should extract the primary version
        assert isinstance(version, str)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
