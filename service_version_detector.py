"""
Service Version Detection Module
Advanced service fingerprinting and version detection
"""

import socket
import re
import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class ServiceVersionDetector:
    """
    Advanced service version detection with fingerprinting
    """
    
    def __init__(self):
        """Initialize service version detector"""
        self.service_probes = self._initialize_probes()
        self.version_patterns = self._initialize_patterns()
    
    def _initialize_probes(self) -> Dict:
        """Initialize service probes for different services"""
        return {
            'http': [
                b'GET / HTTP/1.0\r\nHost: {host}\r\n\r\n',
                b'HEAD / HTTP/1.1\r\nHost: {host}\r\n\r\n',
                b'OPTIONS / HTTP/1.0\r\n\r\n'
            ],
            'https': [
                b'GET / HTTP/1.0\r\nHost: {host}\r\n\r\n'
            ],
            'ftp': [
                b'USER anonymous\r\n',
                b'HELP\r\n'
            ],
            'smtp': [
                b'EHLO test\r\n',
                b'HELP\r\n'
            ],
            'ssh': [
                b'SSH-2.0-OpenSSH_Test\r\n'
            ],
            'mysql': [
                b'\x00\x00\x00\x0a'  # MySQL handshake
            ],
            'postgresql': [
                b'\x00\x00\x00\x08\x04\xd2\x16\x2f'  # PostgreSQL startup
            ]
        }
    
    def _initialize_patterns(self) -> Dict:
        """Initialize version extraction patterns"""
        return {
            'nginx': [
                r'nginx[/\s]+(\d+\.\d+\.?\d*)',
                r'Server:\s*nginx[/\s]+(\d+\.\d+\.?\d*)'
            ],
            'apache': [
                r'Apache[/\s]+(\d+\.\d+\.?\d*)',
                r'Server:\s*Apache[/\s]+(\d+\.\d+\.?\d*)'
            ],
            'iis': [
                r'Microsoft-IIS[/\s]+(\d+\.\d+)',
                r'Server:\s*Microsoft-IIS[/\s]+(\d+\.\d+)'
            ],
            'openssh': [
                r'OpenSSH[_\s]+(\d+\.\d+p?\d*)',
                r'SSH-\d+\.\d+-OpenSSH[_\s]+(\d+\.\d+p?\d*)'
            ],
            'mysql': [
                r'(\d+\.\d+\.\d+)-MySQL',
                r'MySQL\s+(\d+\.\d+\.\d+)'
            ],
            'postgresql': [
                r'PostgreSQL\s+(\d+\.\d+\.?\d*)',
                r'postgres\s+\(PostgreSQL\)\s+(\d+\.\d+\.?\d*)'
            ],
            'redis': [
                r'Redis\s+server\s+v=(\d+\.\d+\.\d+)',
                r'redis_version:(\d+\.\d+\.\d+)'
            ],
            'mongodb': [
                r'MongoDB\s+(\d+\.\d+\.\d+)',
                r'version":\s*"(\d+\.\d+\.\d+)"'
            ]
        }
    
    def detect_version(self, host: str, port: int, service: str, banner: str = '') -> Tuple[str, str]:
        """
        Detect service version with advanced fingerprinting
        
        Args:
            host: Target host
            port: Target port
            service: Service name
            banner: Initial banner (if available)
            
        Returns:
            Tuple of (service_name, version)
        """
        # Try to extract version from banner first
        if banner:
            version = self._extract_version_from_banner(service, banner)
            if version != 'Unknown':
                return service, version
        
        # Try active probing
        service_lower = service.lower()
        if service_lower in self.service_probes:
            probed_banner = self._probe_service(host, port, service_lower)
            if probed_banner:
                version = self._extract_version_from_banner(service, probed_banner)
                if version != 'Unknown':
                    return service, version
        
        return service, 'Unknown'
    
    def _probe_service(self, host: str, port: int, service: str) -> str:
        """
        Actively probe service for version information
        
        Args:
            host: Target host
            port: Target port
            service: Service name
            
        Returns:
            Response banner
        """
        probes = self.service_probes.get(service, [])
        
        for probe in probes:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3.0)
                sock.connect((host, port))
                
                # Format probe with host if needed
                if b'{host}' in probe:
                    probe = probe.replace(b'{host}', host.encode())
                
                sock.send(probe)
                response = sock.recv(4096)
                sock.close()
                
                if response:
                    return response.decode('utf-8', errors='ignore')
                    
            except Exception as e:
                logger.debug(f"Probe failed for {service} on {host}:{port}: {e}")
                continue
        
        return ''
    
    def _extract_version_from_banner(self, service: str, banner: str) -> str:
        """
        Extract version from banner using patterns
        
        Args:
            service: Service name
            banner: Banner string
            
        Returns:
            Version string or 'Unknown'
        """
        service_lower = service.lower()
        
        # Try service-specific patterns
        for service_key, patterns in self.version_patterns.items():
            if service_key in service_lower:
                for pattern in patterns:
                    match = re.search(pattern, banner, re.IGNORECASE)
                    if match:
                        return match.group(1)
        
        # Try generic version patterns
        generic_patterns = [
            r'(\d+\.\d+\.\d+)',  # x.y.z
            r'(\d+\.\d+)',        # x.y
            r'[vV]ersion[:\s]+(\S+)',
            r'[sS]erver[:\s]+\S+[/\s]+(\d+\.\d+\.?\d*)'
        ]
        
        for pattern in generic_patterns:
            match = re.search(pattern, banner)
            if match:
                return match.group(1)
        
        return 'Unknown'


# Singleton instance
_detector_instance = None


def get_service_detector() -> ServiceVersionDetector:
    """Get singleton service detector instance"""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = ServiceVersionDetector()
    return _detector_instance
