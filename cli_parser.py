"""
Enhanced Command-Line Interface for AI Pentest Brain
Provides comprehensive argument parsing with integration to ConfigManager
"""

import argparse
import sys
from typing import Optional
from config_manager import ConfigManager, PentestConfig, ScanMode, ReportFormat


class PentestCLI:
    """Command-line interface parser for AI Pentest Brain"""
    
    def __init__(self):
        self.parser = self._create_parser()
        self.args = None
        self.config_manager = ConfigManager()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser with all options"""
        parser = argparse.ArgumentParser(
            prog='ai_pentest_brain',
            description='AI-Powered Penetration Testing Brain - Autonomous Security Testing',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Basic scan with default settings
  python ai_pentest_brain_complete.py example.com
  
  # Full port scan with TEXT report
  python ai_pentest_brain_complete.py example.com --scan-mode full --report-format text
  
  # Fast scan with UDP enabled
  python ai_pentest_brain_complete.py example.com --scan-mode fast --enable-udp-scan
  
  # Scan with NVD API key for CVE enrichment
  python ai_pentest_brain_complete.py example.com --nvd-api-key YOUR_KEY
  
  # Custom thread count and timeout
  python ai_pentest_brain_complete.py example.com --max-threads 20 --scan-timeout 10
  
  # Generate both JSON and TEXT reports
  python ai_pentest_brain_complete.py example.com --report-format both
  
  # Use configuration file
  python ai_pentest_brain_complete.py example.com --config my_config.json

Configuration Priority:
  1. Command-line arguments (highest priority)
  2. Environment variables (PENTEST_*)
  3. Configuration file (.pentest_config.json)
  4. Default values (lowest priority)

Environment Variables:
  All options can be set via environment variables with PENTEST_ prefix:
    PENTEST_SCAN_MODE=full
    PENTEST_ENABLE_UDP_SCAN=true
    PENTEST_MAX_THREADS=20
    PENTEST_NVD_API_KEY=your_key
    ... and more (see config_manager.py for full list)
            """
        )
        
        # Positional argument
        parser.add_argument(
            'target',
            nargs='?',
            help='Target domain or IP address (e.g., example.com, 192.168.1.1)'
        )
        
        # Scanning options
        scan_group = parser.add_argument_group('Scanning Options')
        scan_group.add_argument(
            '--scan-mode',
            choices=['common', 'fast', 'full'],
            help='Port scanning mode: common (top 1000), fast (top 100), full (all 65535)'
        )
        scan_group.add_argument(
            '--enable-udp-scan',
            action='store_true',
            help='Enable UDP port scanning (slower but more comprehensive)'
        )
        scan_group.add_argument(
            '--max-threads',
            type=int,
            metavar='N',
            help='Maximum number of scanning threads (1-100, default: 10)'
        )
        scan_group.add_argument(
            '--scan-timeout',
            type=int,
            metavar='SECONDS',
            help='Timeout for port scanning in seconds (1-60, default: 5)'
        )
        scan_group.add_argument(
            '--scan-db-ports',
            action='store_true',
            help='Include database ports in scanning (MySQL, PostgreSQL, MongoDB, Redis)'
        )
        
        # Report options
        report_group = parser.add_argument_group('Report Options')
        report_group.add_argument(
            '--report-format',
            choices=['json', 'text', 'both'],
            help='Report output format (default: json)'
        )
        report_group.add_argument(
            '--report-directory',
            metavar='DIR',
            help='Directory to save reports (default: reports/)'
        )
        
        # CVE integration
        cve_group = parser.add_argument_group('CVE Integration')
        cve_group.add_argument(
            '--nvd-api-key',
            metavar='KEY',
            help='NIST NVD API key for CVE enrichment (get from https://nvd.nist.gov/developers/request-an-api-key)'
        )
        cve_group.add_argument(
            '--cve-cache-ttl',
            type=int,
            metavar='SECONDS',
            help='CVE cache time-to-live in seconds (default: 86400 = 24 hours)'
        )
        
        # Network options
        network_group = parser.add_argument_group('Network Options')
        network_group.add_argument(
            '--request-timeout',
            type=int,
            metavar='SECONDS',
            help='HTTP request timeout in seconds (1-120, default: 10)'
        )
        network_group.add_argument(
            '--max-retries',
            type=int,
            metavar='N',
            help='Maximum number of request retries (0-10, default: 3)'
        )
        network_group.add_argument(
            '--user-agent',
            metavar='STRING',
            help='Custom User-Agent string for HTTP requests'
        )
        
        # Safety options
        safety_group = parser.add_argument_group('Safety Options')
        safety_group.add_argument(
            '--no-safe-mode',
            action='store_true',
            help='Disable safe mode (allows more aggressive testing)'
        )
        safety_group.add_argument(
            '--quiet',
            action='store_true',
            help='Reduce verbosity (opposite of --verbose)'
        )
        safety_group.add_argument(
            '--max-brute-force-attempts',
            type=int,
            metavar='N',
            help='Maximum brute force attempts (1-10, default: 3)'
        )
        safety_group.add_argument(
            '--max-rate-limit-requests',
            type=int,
            metavar='N',
            help='Maximum rate limit test requests (1-100, default: 20)'
        )
        
        # Authentication
        auth_group = parser.add_argument_group('Authentication')
        auth_group.add_argument(
            '--jwt-token',
            metavar='TOKEN',
            help='JWT token for authenticated scanning'
        )
        
        # Advanced features
        advanced_group = parser.add_argument_group('Advanced Features')
        advanced_group.add_argument(
            '--disable-behavioral-analysis',
            action='store_true',
            help='Disable behavioral intelligence analysis'
        )
        advanced_group.add_argument(
            '--disable-federated-learning',
            action='store_true',
            help='Disable federated learning'
        )
        advanced_group.add_argument(
            '--disable-adaptive-intelligence',
            action='store_true',
            help='Disable adaptive intelligence engine'
        )
        
        # SOAR integration
        soar_group = parser.add_argument_group('SOAR Integration')
        soar_group.add_argument(
            '--slack-webhook',
            metavar='URL',
            help='Slack webhook URL for notifications'
        )
        soar_group.add_argument(
            '--jira-url',
            metavar='URL',
            help='Jira instance URL'
        )
        soar_group.add_argument(
            '--jira-token',
            metavar='TOKEN',
            help='Jira API token'
        )
        
        # Configuration file
        config_group = parser.add_argument_group('Configuration')
        config_group.add_argument(
            '--config',
            metavar='FILE',
            help='Path to configuration file (default: .pentest_config.json)'
        )
        config_group.add_argument(
            '--save-config',
            metavar='FILE',
            help='Save current configuration to file and exit'
        )
        config_group.add_argument(
            '--show-config',
            action='store_true',
            help='Show current configuration and exit'
        )
        
        # Version and help
        parser.add_argument(
            '--version',
            action='version',
            version='AI Pentest Brain v4.0 (Phase 2 Enhanced)'
        )
        
        return parser
    
    def parse_args(self, args: Optional[list] = None) -> argparse.Namespace:
        """
        Parse command-line arguments
        
        Args:
            args: Optional list of arguments (uses sys.argv if None)
        
        Returns:
            Parsed arguments namespace
        """
        self.args = self.parser.parse_args(args)
        return self.args
    
    def get_config(self) -> PentestConfig:
        """
        Get complete configuration by merging CLI args with ConfigManager
        
        Priority: CLI args > Environment vars > Config file > Defaults
        
        Returns:
            Complete PentestConfig object
        """
        # Load base configuration from file and environment
        if self.args and self.args.config:
            self.config_manager = ConfigManager(config_file=self.args.config)
        
        config = self.config_manager.load()
        
        # Override with command-line arguments (highest priority)
        if self.args:
            self._apply_cli_args(config)
        
        return config
    
    def _apply_cli_args(self, config: PentestConfig):
        """Apply command-line arguments to configuration"""
        # Scanning options
        if self.args.scan_mode:
            config.scan_mode = self.args.scan_mode
        
        if self.args.enable_udp_scan:
            config.enable_udp_scan = True
        
        if self.args.max_threads:
            config.max_threads = self.args.max_threads
        
        if self.args.scan_timeout:
            config.scan_timeout = self.args.scan_timeout
        
        if self.args.scan_db_ports:
            config.scan_db_ports = True
        
        # Report options
        if self.args.report_format:
            config.report_format = self.args.report_format
        
        if self.args.report_directory:
            config.report_directory = self.args.report_directory
        
        # CVE integration
        if self.args.nvd_api_key:
            config.nvd_api_key = self.args.nvd_api_key
        
        if self.args.cve_cache_ttl:
            config.cve_cache_ttl = self.args.cve_cache_ttl
        
        # Network options
        if self.args.request_timeout:
            config.request_timeout = self.args.request_timeout
        
        if self.args.max_retries:
            config.max_retries = self.args.max_retries
        
        if self.args.user_agent:
            config.user_agent = self.args.user_agent
        
        # Safety options
        if self.args.no_safe_mode:
            config.safe_mode = False
        
        if self.args.quiet:
            config.verbose = False
        
        if self.args.max_brute_force_attempts:
            config.max_brute_force_attempts = self.args.max_brute_force_attempts
        
        if self.args.max_rate_limit_requests:
            config.max_rate_limit_requests = self.args.max_rate_limit_requests
        
        # Authentication
        if self.args.jwt_token:
            config.jwt_token = self.args.jwt_token
        
        # Advanced features
        if self.args.disable_behavioral_analysis:
            config.enable_behavioral_analysis = False
        
        if self.args.disable_federated_learning:
            config.enable_federated_learning = False
        
        if self.args.disable_adaptive_intelligence:
            config.enable_adaptive_intelligence = False
        
        # SOAR integration
        if self.args.slack_webhook:
            config.slack_enabled = True
            config.slack_webhook = self.args.slack_webhook
        
        if self.args.jira_url:
            config.jira_enabled = True
            config.jira_url = self.args.jira_url
        
        if self.args.jira_token:
            config.jira_token = self.args.jira_token
    
    def handle_special_commands(self) -> bool:
        """
        Handle special commands that exit immediately
        
        Returns:
            True if a special command was handled (should exit), False otherwise
        """
        if not self.args:
            return False
        
        # Show configuration
        if self.args.show_config:
            config = self.get_config()
            print("\n" + "="*60)
            print("Current Configuration")
            print("="*60 + "\n")
            
            for key, value in config.to_dict().items():
                if not key.startswith('custom_'):
                    print(f"{key:30s} = {value}")
            
            print("\n" + "="*60)
            return True
        
        # Save configuration
        if self.args.save_config:
            config = self.get_config()
            self.config_manager.config = config
            self.config_manager.save(config)
            
            # Also save to specified file if different
            if self.args.save_config != self.config_manager.config_file:
                import json
                from pathlib import Path
                
                save_path = Path(self.args.save_config)
                save_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(save_path, 'w') as f:
                    json.dump(config.to_dict(), f, indent=2)
                
                print(f"✓ Configuration saved to: {self.args.save_config}")
            else:
                print(f"✓ Configuration saved to: {self.config_manager.config_file}")
            
            return True
        
        return False
    
    def get_target(self) -> Optional[str]:
        """
        Get target from CLI args or prompt user
        
        Returns:
            Target URL/IP or None if not provided
        """
        if self.args and self.args.target:
            return self.args.target
        
        # Prompt user if not provided
        target = input("Enter target domain or IP (e.g., example.com): ").strip()
        return target if target else None
    
    def validate_and_get_config(self) -> Optional[PentestConfig]:
        """
        Validate configuration and return it, or None if invalid
        
        Returns:
            Valid PentestConfig or None
        """
        config = self.get_config()
        
        if not config.validate():
            print("\n✗ Configuration validation failed!")
            print("  Please check your configuration and try again.")
            print("  Use --show-config to see current configuration.")
            return None
        
        return config


def create_cli() -> PentestCLI:
    """
    Create and initialize CLI parser
    
    Returns:
        Initialized PentestCLI instance
    """
    return PentestCLI()


if __name__ == "__main__":
    # Demo: Show help
    cli = create_cli()
    cli.parser.print_help()
    
    print("\n" + "="*60)
    print("CLI Parser Demo")
    print("="*60)
    
    # Parse example arguments
    test_args = [
        'example.com',
        '--scan-mode', 'fast',
        '--report-format', 'both',
        '--max-threads', '20'
    ]
    
    cli.parse_args(test_args)
    config = cli.get_config()
    
    print("\nParsed Configuration:")
    print("-" * 60)
    print(f"Target: {cli.args.target}")
    print(f"Scan Mode: {config.scan_mode}")
    print(f"Report Format: {config.report_format}")
    print(f"Max Threads: {config.max_threads}")
    
    print("\n✓ CLI parser ready")
