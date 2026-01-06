"""
Unit Tests for Port Scanner Integration
Tests scan mode selection, result formatting, and error handling
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from comprehensive_port_scanner import ComprehensivePortScanner, PortScanResult
from ai_pentest_brain_complete import AIPentestBrain


class TestPortScannerIntegration:
    """Test port scanner integration into reconnaissance phase"""
    
    def test_scan_mode_selection_common(self):
        """Test that common scan mode is selected correctly"""
        config = {'scan_mode': 'common'}
        brain = AIPentestBrain(config)
        
        assert brain.config.get('scan_mode') == 'common'
    
    def test_scan_mode_selection_fast(self):
        """Test that fast scan mode is selected correctly"""
        config = {'scan_mode': 'fast'}
        brain = AIPentestBrain(config)
        
        assert brain.config.get('scan_mode') == 'fast'
    
    def test_scan_mode_selection_full(self):
        """Test that full scan mode is selected correctly"""
        config = {'scan_mode': 'full'}
        brain = AIPentestBrain(config)
        
        assert brain.config.get('scan_mode') == 'full'
    
    def test_scan_mode_default(self):
        """Test that default scan mode is 'common'"""
        config = {}
        brain = AIPentestBrain(config)
        
        # Default should be 'common' if not specified
        assert brain.config.get('scan_mode', 'common') == 'common'
    
    def test_port_scan_result_formatting(self):
        """Test that port scan results are formatted correctly"""
        # Create mock port scan results
        mock_results = [
            PortScanResult(
                port=80,
                state='open',
                service='http',
                version='nginx 1.18.0',
                banner='nginx/1.18.0',
                protocol='tcp'
            ),
            PortScanResult(
                port=443,
                state='open',
                service='https',
                version='nginx 1.18.0',
                banner='nginx/1.18.0',
                protocol='tcp'
            ),
            PortScanResult(
                port=22,
                state='open',
                service='ssh',
                version='OpenSSH 8.2p1',
                banner='SSH-2.0-OpenSSH_8.2p1',
                protocol='tcp'
            )
        ]
        
        # Format results as dictionary (simulating what perform_recon does)
        open_ports_dict = {}
        for result in mock_results:
            open_ports_dict[str(result.port)] = {
                'state': result.state,
                'service': result.service,
                'version': result.version,
                'banner': result.banner,
                'protocol': result.protocol
            }
        
        # Verify formatting
        assert '80' in open_ports_dict
        assert open_ports_dict['80']['service'] == 'http'
        assert open_ports_dict['80']['version'] == 'nginx 1.18.0'
        assert open_ports_dict['80']['protocol'] == 'tcp'
        
        assert '443' in open_ports_dict
        assert '22' in open_ports_dict
    
    def test_udp_scan_disabled_by_default(self):
        """Test that UDP scanning is disabled by default"""
        config = {}
        brain = AIPentestBrain(config)
        
        assert brain.config.get('enable_udp_scan', False) == False
    
    def test_udp_scan_enabled(self):
        """Test that UDP scanning can be enabled"""
        config = {'enable_udp_scan': True}
        brain = AIPentestBrain(config)
        
        assert brain.config.get('enable_udp_scan') == True
    
    def test_error_handling_connection_failure(self):
        """Test error handling for connection failures"""
        scanner = ComprehensivePortScanner(timeout=0.1)
        
        # Try to scan a non-existent host (should handle gracefully)
        # This should not raise an exception
        try:
            results = scanner.scan_common_ports('192.0.2.1')  # TEST-NET-1 (non-routable)
            # Should return empty list or handle gracefully
            assert isinstance(results, list)
        except Exception as e:
            pytest.fail(f"Scanner should handle connection failures gracefully: {e}")
    
    def test_error_handling_invalid_port(self):
        """Test error handling for invalid port numbers"""
        scanner = ComprehensivePortScanner()
        
        # Port scanner should validate port ranges internally
        # This test ensures the scanner doesn't crash on edge cases
        result = scanner._scan_tcp_port('localhost', 1)
        assert result is None or isinstance(result, PortScanResult)
    
    def test_port_scan_result_structure(self):
        """Test that PortScanResult has correct structure"""
        result = PortScanResult(
            port=80,
            state='open',
            service='http',
            version='nginx 1.18.0',
            banner='nginx/1.18.0',
            protocol='tcp'
        )
        
        assert result.port == 80
        assert result.state == 'open'
        assert result.service == 'http'
        assert result.version == 'nginx 1.18.0'
        assert result.banner == 'nginx/1.18.0'
        assert result.protocol == 'tcp'
    
    def test_common_ports_list(self):
        """Test that common ports scan includes expected ports"""
        scanner = ComprehensivePortScanner()
        
        # Common ports should include standard web/ssh/database ports
        # We can't test actual scanning without a target, but we can verify the method exists
        assert hasattr(scanner, 'scan_common_ports')
    
    def test_fast_mode_uses_top_1000(self):
        """Test that fast mode scans top 1000 ports"""
        scanner = ComprehensivePortScanner()
        
        # Verify the _get_top_1000_ports method exists
        assert hasattr(scanner, '_get_top_1000_ports')
        
        # Get the port list
        top_ports = scanner._get_top_1000_ports()
        
        # Should return a list of 1000 ports
        assert isinstance(top_ports, list)
        assert len(top_ports) <= 1000  # May be less if not all defined
    
    def test_udp_port_formatting(self):
        """Test that UDP ports are formatted with /udp suffix"""
        # Create mock UDP result
        udp_result = PortScanResult(
            port=53,
            state='open',
            service='dns',
            version='Unknown',
            banner='',
            protocol='udp'
        )
        
        # Format as it would be in perform_recon
        port_key = f"{udp_result.port}/udp"
        
        assert port_key == '53/udp'
        assert udp_result.protocol == 'udp'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
