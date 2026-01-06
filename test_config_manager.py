"""
Unit tests for Configuration Management System
Tests environment variables, file loading, validation, and defaults
"""

import pytest
import os
import json
import tempfile
from pathlib import Path
from config_manager import (
    ConfigManager,
    PentestConfig,
    ScanMode,
    ReportFormat,
    create_default_config_file
)


class TestPentestConfig:
    """Test PentestConfig dataclass"""
    
    def test_default_values(self):
        """Test that default configuration values are set correctly"""
        config = PentestConfig()
        
        assert config.scan_mode == "common"
        assert config.enable_udp_scan is False
        assert config.max_threads == 10
        assert config.report_format == "json"
        assert config.safe_mode is True
        assert config.verbose is True
        assert config.nvd_api_key is None
    
    def test_to_dict(self):
        """Test configuration conversion to dictionary"""
        config = PentestConfig(
            scan_mode="fast",
            max_threads=20,
            report_format="text"
        )
        
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert config_dict['scan_mode'] == "fast"
        assert config_dict['max_threads'] == 20
        assert config_dict['report_format'] == "text"
    
    def test_validation_valid_config(self):
        """Test validation passes for valid configuration"""
        config = PentestConfig(
            scan_mode="common",
            report_format="json",
            max_threads=10,
            scan_timeout=5
        )
        
        assert config.validate() is True
    
    def test_validation_invalid_scan_mode(self):
        """Test validation fails for invalid scan mode"""
        config = PentestConfig(scan_mode="invalid_mode")
        
        assert config.validate() is False
    
    def test_validation_invalid_report_format(self):
        """Test validation fails for invalid report format"""
        config = PentestConfig(report_format="invalid_format")
        
        assert config.validate() is False
    
    def test_validation_invalid_max_threads(self):
        """Test validation fails for invalid max_threads"""
        config = PentestConfig(max_threads=0)
        assert config.validate() is False
        
        config = PentestConfig(max_threads=101)
        assert config.validate() is False
    
    def test_validation_invalid_scan_timeout(self):
        """Test validation fails for invalid scan_timeout"""
        config = PentestConfig(scan_timeout=0)
        assert config.validate() is False
        
        config = PentestConfig(scan_timeout=61)
        assert config.validate() is False
    
    def test_validation_slack_config(self):
        """Test validation fails when Slack is enabled without webhook"""
        config = PentestConfig(slack_enabled=True, slack_webhook=None)
        
        assert config.validate() is False
    
    def test_validation_jira_config(self):
        """Test validation fails when Jira is enabled without credentials"""
        config = PentestConfig(jira_enabled=True, jira_url=None)
        assert config.validate() is False
        
        config = PentestConfig(jira_enabled=True, jira_url="http://jira.com", jira_token=None)
        assert config.validate() is False


class TestConfigManager:
    """Test ConfigManager class"""
    
    def test_initialization(self):
        """Test ConfigManager initialization"""
        manager = ConfigManager()
        
        assert manager.config is not None
        assert isinstance(manager.config, PentestConfig)
        assert manager.config_file == ".pentest_config.json"
    
    def test_initialization_custom_file(self):
        """Test ConfigManager initialization with custom file"""
        manager = ConfigManager(config_file="custom_config.json")
        
        assert manager.config_file == "custom_config.json"
    
    def test_load_default_config(self):
        """Test loading configuration with no file or env vars"""
        manager = ConfigManager(config_file="nonexistent.json")
        config = manager.load()
        
        # Should return default configuration
        assert config.scan_mode == "common"
        assert config.max_threads == 10
        assert config.report_format == "json"
    
    def test_load_from_file(self, tmp_path):
        """Test loading configuration from file"""
        # Create temporary config file
        config_file = tmp_path / "test_config.json"
        test_config = {
            "scan_mode": "fast",
            "max_threads": 20,
            "report_format": "text",
            "nvd_api_key": "test_key_123"
        }
        
        with open(config_file, 'w') as f:
            json.dump(test_config, f)
        
        # Load configuration
        manager = ConfigManager(config_file=str(config_file))
        config = manager.load()
        
        assert config.scan_mode == "fast"
        assert config.max_threads == 20
        assert config.report_format == "text"
        assert config.nvd_api_key == "test_key_123"
    
    def test_load_from_env(self, monkeypatch):
        """Test loading configuration from environment variables"""
        # Set environment variables
        monkeypatch.setenv("PENTEST_SCAN_MODE", "full")
        monkeypatch.setenv("PENTEST_MAX_THREADS", "30")
        monkeypatch.setenv("PENTEST_ENABLE_UDP_SCAN", "true")
        monkeypatch.setenv("PENTEST_REPORT_FORMAT", "both")
        monkeypatch.setenv("PENTEST_NVD_API_KEY", "env_key_456")
        
        # Load configuration
        manager = ConfigManager(config_file="nonexistent.json")
        config = manager.load()
        
        assert config.scan_mode == "full"
        assert config.max_threads == 30
        assert config.enable_udp_scan is True
        assert config.report_format == "both"
        assert config.nvd_api_key == "env_key_456"
    
    def test_env_overrides_file(self, tmp_path, monkeypatch):
        """Test that environment variables override file configuration"""
        # Create config file
        config_file = tmp_path / "test_config.json"
        test_config = {
            "scan_mode": "common",
            "max_threads": 10
        }
        
        with open(config_file, 'w') as f:
            json.dump(test_config, f)
        
        # Set environment variable
        monkeypatch.setenv("PENTEST_SCAN_MODE", "full")
        
        # Load configuration
        manager = ConfigManager(config_file=str(config_file))
        config = manager.load()
        
        # Environment variable should override file
        assert config.scan_mode == "full"
        # File value should still be loaded
        assert config.max_threads == 10
    
    def test_boolean_env_conversion(self, monkeypatch):
        """Test boolean environment variable conversion"""
        test_cases = [
            ("true", True),
            ("True", True),
            ("1", True),
            ("yes", True),
            ("on", True),
            ("false", False),
            ("False", False),
            ("0", False),
            ("no", False),
            ("off", False),
        ]
        
        for env_value, expected in test_cases:
            monkeypatch.setenv("PENTEST_ENABLE_UDP_SCAN", env_value)
            
            manager = ConfigManager(config_file="nonexistent.json")
            config = manager.load()
            
            assert config.enable_udp_scan == expected, f"Failed for {env_value}"
    
    def test_integer_env_conversion(self, monkeypatch):
        """Test integer environment variable conversion"""
        monkeypatch.setenv("PENTEST_MAX_THREADS", "25")
        monkeypatch.setenv("PENTEST_SCAN_TIMEOUT", "10")
        
        manager = ConfigManager(config_file="nonexistent.json")
        config = manager.load()
        
        assert config.max_threads == 25
        assert config.scan_timeout == 10
    
    def test_invalid_integer_env(self, monkeypatch):
        """Test handling of invalid integer environment variable"""
        monkeypatch.setenv("PENTEST_MAX_THREADS", "invalid")
        
        manager = ConfigManager(config_file="nonexistent.json")
        config = manager.load()
        
        # Should keep default value
        assert config.max_threads == 10
    
    def test_save_config(self, tmp_path):
        """Test saving configuration to file"""
        config_file = tmp_path / "saved_config.json"
        
        manager = ConfigManager(config_file=str(config_file))
        manager.config.scan_mode = "fast"
        manager.config.max_threads = 25
        manager.config.nvd_api_key = "saved_key"
        
        manager.save()
        
        # Verify file was created
        assert config_file.exists()
        
        # Load and verify content
        with open(config_file, 'r') as f:
            saved_config = json.load(f)
        
        assert saved_config['scan_mode'] == "fast"
        assert saved_config['max_threads'] == 25
        assert saved_config['nvd_api_key'] == "saved_key"
    
    def test_update_config(self):
        """Test updating configuration values"""
        manager = ConfigManager(config_file="nonexistent.json")
        manager.load()
        
        manager.update(
            scan_mode="full",
            max_threads=40,
            report_format="both"
        )
        
        assert manager.config.scan_mode == "full"
        assert manager.config.max_threads == 40
        assert manager.config.report_format == "both"
    
    def test_update_custom_config(self):
        """Test updating custom configuration values"""
        manager = ConfigManager(config_file="nonexistent.json")
        manager.load()
        
        manager.update(custom_key="custom_value")
        
        assert manager.config.custom_config['custom_key'] == "custom_value"
    
    def test_get_config(self):
        """Test getting current configuration"""
        manager = ConfigManager(config_file="nonexistent.json")
        manager.load()
        
        config = manager.get_config()
        
        assert isinstance(config, PentestConfig)
        assert config == manager.config


class TestScanMode:
    """Test ScanMode enum"""
    
    def test_scan_mode_values(self):
        """Test ScanMode enum values"""
        assert ScanMode.COMMON.value == "common"
        assert ScanMode.FAST.value == "fast"
        assert ScanMode.FULL.value == "full"


class TestReportFormat:
    """Test ReportFormat enum"""
    
    def test_report_format_values(self):
        """Test ReportFormat enum values"""
        assert ReportFormat.JSON.value == "json"
        assert ReportFormat.TEXT.value == "text"
        assert ReportFormat.BOTH.value == "both"


class TestCreateDefaultConfigFile:
    """Test create_default_config_file function"""
    
    def test_create_default_config(self, tmp_path):
        """Test creating default configuration file"""
        config_file = tmp_path / "default_config.json"
        
        create_default_config_file(str(config_file))
        
        # Verify file was created
        assert config_file.exists()
        
        # Load and verify content
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        assert config['scan_mode'] == "common"
        assert config['enable_udp_scan'] is False
        assert config['max_threads'] == 10
        assert config['report_format'] == "json"
        assert config['safe_mode'] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
