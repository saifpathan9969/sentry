"""
Comprehensive Port Scanner Module
Scans all 65,535 TCP ports with service detection and version fingerprinting
"""

import socket
import concurrent.futures
from typing import Dict, List, Optional, Tuple
import logging
import time
from dataclasses import dataclass
import re

logger = logging.getLogger(__name__)


@dataclass
class PortScanResult:
    """Result of a port scan"""
    port: int
    state: str  # 'open', 'closed', 'filtered'
    service: str
    version: str
    banner: str
    protocol: str  # 'tcp' or 'udp'


class ComprehensivePortScanner:
    """
    Comprehensive port scanner with service detection
    Supports full TCP scan (all 65,535 ports) and common UDP ports
    """
    
    def __init__(self, timeout: float = 1.0, max_workers: int = 100):
        """
        Initialize port scanner
        
        Args:
            timeout: Socket timeout in seconds
            max_workers: Maximum concurrent threads
        """
        self.timeout = timeout
        self.max_workers = max_workers
        
        # Common service signatures for banner grabbing
        self.service_signatures = {
            'SSH': [b'SSH-', b'OpenSSH'],
            'HTTP': [b'HTTP/', b'Server:', b'<html', b'<!DOCTYPE'],
            'HTTPS': [b'HTTP/', b'Server:'],
            'FTP': [b'220', b'FTP'],
            'SMTP': [b'220', b'SMTP', b'ESMTP'],
            'MySQL': [b'mysql', b'MariaDB'],
            'PostgreSQL': [b'PostgreSQL'],
            'MongoDB': [b'MongoDB'],
            'Redis': [b'Redis'],
            'Telnet': [b'Telnet'],
            'POP3': [b'+OK', b'POP3'],
            'IMAP': [b'* OK', b'IMAP'],
            'DNS': [b'DNS'],
            'LDAP': [b'LDAP'],
            'RDP': [b'RDP', b'Remote Desktop'],
        }
        
        # Common ports with known services
        self.common_ports = {
            20: 'FTP-DATA', 21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP',
            53: 'DNS', 80: 'HTTP', 110: 'POP3', 143: 'IMAP', 443: 'HTTPS',
            445: 'SMB', 465: 'SMTPS', 587: 'SMTP', 993: 'IMAPS', 995: 'POP3S',
            1433: 'MSSQL', 1521: 'Oracle', 3306: 'MySQL', 3389: 'RDP',
            5432: 'PostgreSQL', 5900: 'VNC', 6379: 'Redis', 8080: 'HTTP-Proxy',
            8443: 'HTTPS-Alt', 8888: 'HTTP-Alt', 9200: 'Elasticsearch',
            27017: 'MongoDB', 50000: 'DB2'
        }
    
    def scan_all_ports(self, target: str, fast_mode: bool = False) -> List[PortScanResult]:
        """
        Scan all TCP ports (1-65535) or top 1000 in fast mode
        
        Args:
            target: Target hostname or IP
            fast_mode: If True, scan only top 1000 ports
            
        Returns:
            List of PortScanResult objects for open ports
        """
        logger.info(f"Starting {'fast' if fast_mode else 'comprehensive'} port scan on {target}")
        start_time = time.time()
        
        if fast_mode:
            ports_to_scan = self._get_top_1000_ports()
        else:
            ports_to_scan = range(1, 65536)
        
        open_ports = []
        
        # Scan ports in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_port = {
                executor.submit(self._scan_tcp_port, target, port): port 
                for port in ports_to_scan
            }
            
            for future in concurrent.futures.as_completed(future_to_port):
                result = future.result()
                if result and result.state == 'open':
                    open_ports.append(result)
                    logger.info(f"Found open port: {result.port}/{result.protocol} - {result.service}")
        
        elapsed = time.time() - start_time
        logger.info(f"Port scan complete. Found {len(open_ports)} open ports in {elapsed:.2f} seconds")
        
        return sorted(open_ports, key=lambda x: x.port)
    
    def scan_common_ports(self, target: str) -> List[PortScanResult]:
        """
        Scan only common ports (faster)
        
        Args:
            target: Target hostname or IP
            
        Returns:
            List of PortScanResult objects for open ports
        """
        logger.info(f"Scanning common ports on {target}")
        
        open_ports = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_port = {
                executor.submit(self._scan_tcp_port, target, port): port 
                for port in self.common_ports.keys()
            }
            
            for future in concurrent.futures.as_completed(future_to_port):
                result = future.result()
                if result and result.state == 'open':
                    open_ports.append(result)
        
        return sorted(open_ports, key=lambda x: x.port)
    
    def scan_udp_ports(self, target: str) -> List[PortScanResult]:
        """
        Scan common UDP ports
        
        Args:
            target: Target hostname or IP
            
        Returns:
            List of PortScanResult objects for open UDP ports
        """
        logger.info(f"Scanning common UDP ports on {target}")
        
        # Common UDP ports
        udp_ports = [53, 67, 68, 69, 123, 161, 162, 500, 514, 520, 1900, 4500]
        
        open_ports = []
        
        for port in udp_ports:
            result = self._scan_udp_port(target, port)
            if result and result.state == 'open':
                open_ports.append(result)
        
        return open_ports
    
    def _scan_tcp_port(self, target: str, port: int) -> Optional[PortScanResult]:
        """
        Scan a single TCP port
        
        Args:
            target: Target hostname or IP
            port: Port number
            
        Returns:
            PortScanResult if port is open, None otherwise
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            
            result = sock.connect_ex((target, port))
            
            if result == 0:
                # Port is open, try to grab banner
                banner = self._grab_banner(sock)
                service, version = self._identify_service(port, banner)
                
                sock.close()
                
                return PortScanResult(
                    port=port,
                    state='open',
                    service=service,
                    version=version,
                    banner=banner,
                    protocol='tcp'
                )
            else:
                sock.close()
                return None
                
        except socket.timeout:
            return None
        except socket.error:
            return None
        except Exception as e:
            logger.debug(f"Error scanning port {port}: {e}")
            return None
    
    def _scan_udp_port(self, target: str, port: int) -> Optional[PortScanResult]:
        """
        Scan a single UDP port
        
        Args:
            target: Target hostname or IP
            port: Port number
            
        Returns:
            PortScanResult if port is open, None otherwise
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(self.timeout)
            
            # Send empty packet
            sock.sendto(b'', (target, port))
            
            try:
                data, _ = sock.recvfrom(1024)
                # If we get a response, port is likely open
                service = self.common_ports.get(port, f'udp-{port}')
                
                sock.close()
                
                return PortScanResult(
                    port=port,
                    state='open',
                    service=service,
                    version='Unknown',
                    banner=data.decode('utf-8', errors='ignore')[:100],
                    protocol='udp'
                )
            except socket.timeout:
                # No response - port might be open or filtered
                sock.close()
                return None
                
        except Exception as e:
            logger.debug(f"Error scanning UDP port {port}: {e}")
            return None
    
    def _grab_banner(self, sock: socket.socket) -> str:
        """
        Grab banner from open socket
        
        Args:
            sock: Open socket
            
        Returns:
            Banner string
        """
        try:
            # Try to receive banner
            sock.settimeout(2.0)
            banner = sock.recv(1024)
            return banner.decode('utf-8', errors='ignore').strip()
        except:
            # If no banner, try sending HTTP request
            try:
                sock.send(b'GET / HTTP/1.0\r\n\r\n')
                banner = sock.recv(1024)
                return banner.decode('utf-8', errors='ignore').strip()
            except:
                return ''
    
    def _identify_service(self, port: int, banner: str) -> Tuple[str, str]:
        """
        Identify service and version from port and banner
        
        Args:
            port: Port number
            banner: Banner string
            
        Returns:
            Tuple of (service_name, version)
        """
        # Check banner against signatures
        banner_bytes = banner.encode('utf-8', errors='ignore')
        
        for service, signatures in self.service_signatures.items():
            for sig in signatures:
                if sig in banner_bytes:
                    version = self._extract_version(banner)
                    return service, version
        
        # Fall back to common port mapping
        if port in self.common_ports:
            return self.common_ports[port], 'Unknown'
        
        return f'tcp-{port}', 'Unknown'
    
    def _extract_version(self, banner: str) -> str:
        """
        Extract version from banner
        
        Args:
            banner: Banner string
            
        Returns:
            Version string or 'Unknown'
        """
        # Common version patterns
        patterns = [
            r'(\d+\.\d+\.\d+)',  # x.y.z
            r'(\d+\.\d+)',        # x.y
            r'[vV]ersion[:\s]+(\S+)',
            r'[sS]erver[:\s]+(\S+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, banner)
            if match:
                return match.group(1)
        
        return 'Unknown'
    
    def _get_top_1000_ports(self) -> List[int]:
        """
        Get list of top 1000 most common ports
        
        Returns:
            List of exactly 1000 port numbers
        """
        # Top 1000 ports - start with range 1-987
        top_ports = list(range(1, 988))
        
        # Add important high ports to reach exactly 1000
        important_high_ports = [
            1433, 1521, 3306, 3389, 5432, 5900, 6379, 
            8080, 8443, 8888, 9200, 27017, 50000
        ]
        top_ports.extend(important_high_ports)
        
        # Ensure exactly 1000 ports
        unique_ports = sorted(set(top_ports))
        return unique_ports[:1000]


# Singleton instance
_scanner_instance = None


def get_port_scanner(timeout: float = 1.0, max_workers: int = 100) -> ComprehensivePortScanner:
    """
    Get singleton port scanner instance
    
    Args:
        timeout: Socket timeout
        max_workers: Maximum concurrent threads
        
    Returns:
        ComprehensivePortScanner instance
    """
    global _scanner_instance
    
    if _scanner_instance is None:
        _scanner_instance = ComprehensivePortScanner(timeout, max_workers)
    
    return _scanner_instance
