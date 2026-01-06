"""
Configuration Management System for AI Pentest Brain
Supports environment variables, configuration files, and validation
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass, field, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class ScanMode(Enum):
    """Port scanning modes"""
    COMMON = "common"  # Top 1000 ports
    FAST = "fast"      # Top 100 ports
    FULL = "full"      # All 65,535 ports


class ReportFormat(Enum):
    """Report output formats"""
    JSON = "json"
    TEXT = "text"
    BOTH = "both"


@dataclass
class PentestConfig:
    """Complete configuration for AI Pentest Brain"""
    
    # Scanning Configuration
    scan_mode: str = "common"
    enable_udp_scan: bool = False
    max_threads: int = 10
    scan_timeout: int = 5
    
    # Report Configuration
    report_format: str = "json"
    report_directory: str = "reports"
    
    # CVE Integration
    nvd_api_key: Optional[str] = None
    cve_cache_ttl: int = 86400  # 24 hours
    
    # Safety Configuration
    safe_mode: bool = True
    verbose: bool = True
    max_brute_force_attempts: int = 3
    max_rate_limit_requests: int = 20
    
    # Network Configuration
    request_timeout: int = 10
    max_retries: int = 3
    user_agent: str = "AI-Pentest-Brain/4.0"
    
    # SOAR Integration (Optional)
    slack_enabled: bool = False
    slack_webhook: Optional[str] = None
    jira_enabled: bool = False
    jira_url: Optional[str] = None
    jira_token: Optional[str] = None
    siem_enabled: bool = False
    siem_type: Optional[str] = None
    waf_enabled: bool = False
    waf_api_url: Optional[str] = None
    
    # Advanced Features
    enable_behavioral_analysis: bool = True
    enable_federated_learning: bool = True
    enable_adaptive_intelligence: bool = True
    
    # Database ports scanning (disabled by default to reduce noise)
    scan_db_ports: bool = False
    
    # JWT/OAuth token for authenticated scanning
    jwt_token: Optional[str] = None
    
    # Additional custom configuration
    custom_config: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        config_dict = asdict(self)
        # Remove None values for cleaner output
        return {k: v for k, v in config_dict.items() if v is not None}
    
    def validate(self) -> bool:
        """Validate configuration values"""
        errors = []
        
        # Validate scan_mode
        valid_scan_modes = [mode.value for mode in ScanMode]
        if self.scan_mode not in valid_scan_modes:
            errors.append(f"Invalid scan_mode: {self.scan_mode}. Must be one of: {valid_scan_modes}")
        
        # Validate report_format
        valid_report_formats = [fmt.value for fmt in ReportFormat]
        if self.report_format not in valid_report_formats:
            errors.append(f"Invalid report_format: {self.report_format}. Must be one of: {valid_report_formats}")
        
        # Validate numeric ranges
        if self.max_threads < 1 or self.max_threads > 100:
            errors.append(f"Invalid max_threads: {self.max_threads}. Must be between 1 and 100")
        
        if self.scan_timeout < 1 or self.scan_timeout > 60:
            errors.append(f"Invalid scan_timeout: {self.scan_timeout}. Must be between 1 and 60 seconds")
        
        if self.request_timeout < 1 or self.request_timeout > 120:
            errors.append(f"Invalid request_timeout: {self.request_timeout}. Must be between 1 and 120 seconds")
        
        if self.max_retries < 0 or self.max_retries > 10:
            errors.append(f"Invalid max_retries: {self.max_retries}. Must be between 0 and 10")
        
        if self.max_brute_force_attempts < 1 or self.max_brute_force_attempts > 10:
            errors.append(f"Invalid max_brute_force_attempts: {self.max_brute_force_attempts}. Must be between 1 and 10")
        
        if self.max_rate_limit_requests < 1 or self.max_rate_limit_requests > 100:
            errors.append(f"Invalid max_rate_limit_requests: {self.max_rate_limit_requests}. Must be between 1 and 100")
        
        # Validate SOAR configuration
        if self.slack_enabled and not self.slack_webhook:
            errors.append("slack_enabled is True but slack_webhook is not provided")
        
        if self.jira_enabled and (not self.jira_url or not self.jira_token):
            errors.append("jira_enabled is True but jira_url or jira_token is missing")
        
        if self.waf_enabled and not self.waf_api_url:
            errors.append("waf_enabled is True but waf_api_url is not provided")
        
        # Log errors
        if errors:
            for error in errors:
                logger.error(f"Configuration validation error: {error}")
            return False
        
        return True


class ConfigManager:
    """Manages configuration loading from multiple sources with priority"""
    
    CONFIG_FILE_NAME = ".pentest_config.json"
    ENV_PREFIX = "PENTEST_"
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration manager
        
        Args:
            config_file: Optional path to configuration file
        """
        self.config_file = config_file or self.CONFIG_FILE_NAME
        self.config = PentestConfig()
    
    def load(self) -> PentestConfig:
        """
        Load configuration from multiple sources with priority:
        1. Default values (lowest priority)
        2. Configuration file
        3. Environment variables (highest priority)
        
        Returns:
            PentestConfig: Loaded and validated configuration
        """
        # Start with defaults (already set in PentestConfig)
        logger.info("Loading configuration...")
        
        # Load from configuration file if it exists
        self._load_from_file()
        
        # Override with environment variables
        self._load_from_env()
        
        # Validate configuration
        if not self.config.validate():
            logger.warning("Configuration validation failed, using defaults where possible")
        
        logger.info("Configuration loaded successfully")
        return self.config
    
    def _load_from_file(self):
        """Load configuration from JSON file"""
        config_path = Path(self.config_file)
        
        if not config_path.exists():
            logger.info(f"Configuration file not found: {self.config_file}")
            return
        
        try:
            with open(config_path, 'r') as f:
                file_config = json.load(f)
            
            logger.info(f"Loading configuration from: {self.config_file}")
            
            # Update configuration with file values
            for key, value in file_config.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
                    logger.debug(f"Set {key} = {value} from config file")
                else:
                    # Store unknown keys in custom_config
                    self.config.custom_config[key] = value
                    logger.debug(f"Set custom config {key} = {value}")
            
            logger.info(f"Loaded {len(file_config)} configuration values from file")
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse configuration file: {e}")
        except Exception as e:
            logger.error(f"Failed to load configuration file: {e}")
    
    def _load_from_env(self):
        """Load configuration from environment variables"""
        env_vars_found = 0
        
        # Map environment variable names to config attributes
        env_mappings = {
            'SCAN_MODE': 'scan_mode',
            'ENABLE_UDP_SCAN': 'enable_udp_scan',
            'MAX_THREADS': 'max_threads',
            'SCAN_TIMEOUT': 'scan_timeout',
            'REPORT_FORMAT': 'report_format',
            'REPORT_DIRECTORY': 'report_directory',
            'NVD_API_KEY': 'nvd_api_key',
            'CVE_CACHE_TTL': 'cve_cache_ttl',
            'SAFE_MODE': 'safe_mode',
            'VERBOSE': 'verbose',
            'MAX_BRUTE_FORCE_ATTEMPTS': 'max_brute_force_attempts',
            'MAX_RATE_LIMIT_REQUESTS': 'max_rate_limit_requests',
            'REQUEST_TIMEOUT': 'request_timeout',
            'MAX_RETRIES': 'max_retries',
            'USER_AGENT': 'user_agent',
            'SLACK_ENABLED': 'slack_enabled',
            'SLACK_WEBHOOK': 'slack_webhook',
            'JIRA_ENABLED': 'jira_enabled',
            'JIRA_URL': 'jira_url',
            'JIRA_TOKEN': 'jira_token',
            'SIEM_ENABLED': 'siem_enabled',
            'SIEM_TYPE': 'siem_type',
            'WAF_ENABLED': 'waf_enabled',
            'WAF_API_URL': 'waf_api_url',
            'ENABLE_BEHAVIORAL_ANALYSIS': 'enable_behavioral_analysis',
            'ENABLE_FEDERATED_LEARNING': 'enable_federated_learning',
            'ENABLE_ADAPTIVE_INTELLIGENCE': 'enable_adaptive_intelligence',
            'SCAN_DB_PORTS': 'scan_db_ports',
            'JWT_TOKEN': 'jwt_token',
        }
        
        for env_name, config_attr in env_mappings.items():
            env_var = f"{self.ENV_PREFIX}{env_name}"
            value = os.getenv(env_var)
            
            if value is not None:
                # Convert value to appropriate type
                current_value = getattr(self.config, config_attr)
                
                if isinstance(current_value, bool):
                    # Convert string to boolean
                    value = value.lower() in ('true', '1', 'yes', 'on')
                elif isinstance(current_value, int):
                    # Convert string to integer
                    try:
                        value = int(value)
                    except ValueError:
                        logger.warning(f"Invalid integer value for {env_var}: {value}")
                        continue
                
                setattr(self.config, config_attr, value)
                logger.debug(f"Set {config_attr} = {value} from environment variable {env_var}")
                env_vars_found += 1
        
        if env_vars_found > 0:
            logger.info(f"Loaded {env_vars_found} configuration values from environment variables")
    
    def save(self, config: Optional[PentestConfig] = None):
        """
        Save configuration to file
        
        Args:
            config: Configuration to save (uses current config if not provided)
        """
        if config:
            self.config = config
        
        config_path = Path(self.config_file)
        
        try:
            # Create directory if it doesn't exist
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert config to dictionary and save
            config_dict = self.config.to_dict()
            
            with open(config_path, 'w') as f:
                json.dump(config_dict, f, indent=2)
            
            logger.info(f"Configuration saved to: {self.config_file}")
        
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
    
    def get_config(self) -> PentestConfig:
        """Get current configuration"""
        return self.config
    
    def update(self, **kwargs):
        """
        Update configuration values
        
        Args:
            **kwargs: Configuration key-value pairs to update
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
                logger.debug(f"Updated {key} = {value}")
            else:
                self.config.custom_config[key] = value
                logger.debug(f"Updated custom config {key} = {value}")
        
        # Validate after update
        if not self.config.validate():
            logger.warning("Configuration validation failed after update")


def create_default_config_file(path: str = ".pentest_config.json"):
    """
    Create a default configuration file with all options documented
    
    Args:
        path: Path where to create the configuration file
    """
    default_config = {
        "# Scanning Configuration": None,
        "scan_mode": "common",
        "enable_udp_scan": False,
        "max_threads": 10,
        "scan_timeout": 5,
        "scan_db_ports": False,
        
        "# Report Configuration": None,
        "report_format": "json",
        "report_directory": "reports",
        
        "# CVE Integration": None,
        "nvd_api_key": None,
        "cve_cache_ttl": 86400,
        
        "# Safety Configuration": None,
        "safe_mode": True,
        "verbose": True,
        "max_brute_force_attempts": 3,
        "max_rate_limit_requests": 20,
        
        "# Network Configuration": None,
        "request_timeout": 10,
        "max_retries": 3,
        "user_agent": "AI-Pentest-Brain/4.0",
        
        "# SOAR Integration (Optional)": None,
        "slack_enabled": False,
        "slack_webhook": None,
        "jira_enabled": False,
        "jira_url": None,
        "jira_token": None,
        
        "# Advanced Features": None,
        "enable_behavioral_analysis": True,
        "enable_federated_learning": True,
        "enable_adaptive_intelligence": True,
    }
    
    # Remove comment keys (they're just for documentation)
    config_to_save = {k: v for k, v in default_config.items() if not k.startswith("#")}
    
    try:
        with open(path, 'w') as f:
            json.dump(config_to_save, f, indent=2)
        print(f"✓ Default configuration file created: {path}")
        print(f"  Edit this file to customize your pentest configuration")
    except Exception as e:
        print(f"✗ Failed to create configuration file: {e}")


if __name__ == "__main__":
    # Demo: Create default config file
    print("Configuration Manager Demo")
    print("=" * 60)
    
    # Create default config file
    create_default_config_file()
    
    # Load configuration
    config_manager = ConfigManager()
    config = config_manager.load()
    
    print("\nLoaded Configuration:")
    print("-" * 60)
    for key, value in config.to_dict().items():
        if not key.startswith('custom_'):
            print(f"{key:30s} = {value}")
    
    print("\n✓ Configuration management system ready")
