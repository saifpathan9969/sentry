"""
Unit tests for CLI Parser
Tests argument parsing, configuration integration, and validation
"""

import pytest
import sys
from cli_parser import PentestCLI, create_cli
from config_manager import PentestConfig


class TestPentestCLI:
    """Test PentestCLI class"""
    
    def test_initialization(self):
        """Test CLI initialization"""
        cli = PentestCLI()
        
        assert cli.parser is not None
        assert cli.config_manager is not None
        assert cli.args is None
    
    def test_parse_target_only(self):
        """Test parsing with target only"""
        cli = PentestCLI()
        args = cli.parse_args(['example.com'])
        
        assert args.target == 'example.com'
        assert args.scan_mode is None
        assert args.report_format is None
    
    def test_parse_scan_mode(self):
        """Test parsing scan mode options"""
        cli = PentestCLI()
        
        # Test common mode
        args = cli.parse_args(['example.com', '--scan-mode', 'common'])
        assert args.scan_mode == 'common'
        
        # Test fast mode
        args = cli.parse_args(['example.com', '--scan-mode', 'fast'])
        assert args.scan_mode == 'fast'
        
        # Test full mode
        args = cli.parse_args(['example.com', '--scan-mode', 'full'])
        assert args.scan_mode == 'full'
    
    def test_parse_report_format(self):
        """Test parsing report format options"""
        cli = PentestCLI()
        
        # Test json format
        args = cli.parse_args(['example.com', '--report-format', 'json'])
        assert args.report_format == 'json'
        
        # Test text format
        args = cli.parse_args(['example.com', '--report-format', 'text'])
        assert args.report_format == 'text'
        
        # Test both format
        args = cli.parse_args(['example.com', '--report-format', 'both'])
        assert args.report_format == 'both'
    
    def test_parse_enable_udp_scan(self):
        """Test parsing UDP scan flag"""
        cli = PentestCLI()
        
        # Without flag
        args = cli.parse_args(['example.com'])
        assert args.enable_udp_scan is False
        
        # With flag
        args = cli.parse_args(['example.com', '--enable-udp-scan'])
        assert args.enable_udp_scan is True
    
    def test_parse_max_threads(self):
        """Test parsing max threads option"""
        cli = PentestCLI()
        args = cli.parse_args(['example.com', '--max-threads', '20'])
        
        assert args.max_threads == 20
    
    def test_parse_scan_timeout(self):
        """Test parsing scan timeout option"""
        cli = PentestCLI()
        args = cli.parse_args(['example.com', '--scan-timeout', '10'])
        
        assert args.scan_timeout == 10
    
    def test_parse_nvd_api_key(self):
        """Test parsing NVD API key"""
        cli = PentestCLI()
        args = cli.parse_args(['example.com', '--nvd-api-key', 'test_key_123'])
        
        assert args.nvd_api_key == 'test_key_123'
    
    def test_parse_request_timeout(self):
        """Test parsing request timeout"""
        cli = PentestCLI()
        args = cli.parse_args(['example.com', '--request-timeout', '15'])
        
        assert args.request_timeout == 15
    
    def test_parse_max_retries(self):
        """Test parsing max retries"""
        cli = PentestCLI()
        args = cli.parse_args(['example.com', '--max-retries', '5'])
        
        assert args.max_retries == 5
    
    def test_parse_no_safe_mode(self):
        """Test parsing no-safe-mode flag"""
        cli = PentestCLI()
        
        # Without flag
        args = cli.parse_args(['example.com'])
        assert args.no_safe_mode is False
        
        # With flag
        args = cli.parse_args(['example.com', '--no-safe-mode'])
        assert args.no_safe_mode is True
    
    def test_parse_quiet(self):
        """Test parsing quiet flag"""
        cli = PentestCLI()
        
        # Without flag
        args = cli.parse_args(['example.com'])
        assert args.quiet is False
        
        # With flag
        args = cli.parse_args(['example.com', '--quiet'])
        assert args.quiet is True
    
    def test_parse_jwt_token(self):
        """Test parsing JWT token"""
        cli = PentestCLI()
        args = cli.parse_args(['example.com', '--jwt-token', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'])
        
        assert args.jwt_token == 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
    
    def test_parse_slack_webhook(self):
        """Test parsing Slack webhook"""
        cli = PentestCLI()
        args = cli.parse_args(['example.com', '--slack-webhook', 'https://hooks.slack.com/test'])
        
        assert args.slack_webhook == 'https://hooks.slack.com/test'
    
    def test_parse_jira_credentials(self):
        """Test parsing Jira credentials"""
        cli = PentestCLI()
        args = cli.parse_args([
            'example.com',
            '--jira-url', 'https://jira.company.com',
            '--jira-token', 'test_token'
        ])
        
        assert args.jira_url == 'https://jira.company.com'
        assert args.jira_token == 'test_token'
    
    def test_parse_disable_features(self):
        """Test parsing feature disable flags"""
        cli = PentestCLI()
        args = cli.parse_args([
            'example.com',
            '--disable-behavioral-analysis',
            '--disable-federated-learning',
            '--disable-adaptive-intelligence'
        ])
        
        assert args.disable_behavioral_analysis is True
        assert args.disable_federated_learning is True
        assert args.disable_adaptive_intelligence is True
    
    def test_parse_multiple_options(self):
        """Test parsing multiple options together"""
        cli = PentestCLI()
        args = cli.parse_args([
            'example.com',
            '--scan-mode', 'fast',
            '--report-format', 'both',
            '--max-threads', '25',
            '--enable-udp-scan',
            '--nvd-api-key', 'my_key'
        ])
        
        assert args.target == 'example.com'
        assert args.scan_mode == 'fast'
        assert args.report_format == 'both'
        assert args.max_threads == 25
        assert args.enable_udp_scan is True
        assert args.nvd_api_key == 'my_key'
    
    def test_get_config_default(self):
        """Test getting configuration with defaults"""
        cli = PentestCLI()
        cli.parse_args(['example.com'])
        config = cli.get_config()
        
        assert isinstance(config, PentestConfig)
        assert config.scan_mode == 'common'
        assert config.report_format == 'json'
        assert config.max_threads == 10
    
    def test_get_config_with_cli_args(self):
        """Test getting configuration with CLI arguments"""
        cli = PentestCLI()
        cli.parse_args([
            'example.com',
            '--scan-mode', 'full',
            '--report-format', 'text',
            '--max-threads', '30'
        ])
        config = cli.get_config()
        
        assert config.scan_mode == 'full'
        assert config.report_format == 'text'
        assert config.max_threads == 30
    
    def test_cli_overrides_defaults(self):
        """Test that CLI arguments override default configuration"""
        cli = PentestCLI()
        cli.parse_args([
            'example.com',
            '--scan-mode', 'fast',
            '--enable-udp-scan'
        ])
        config = cli.get_config()
        
        # CLI args should override defaults
        assert config.scan_mode == 'fast'
        assert config.enable_udp_scan is True
        
        # Defaults should still be present for non-overridden values
        assert config.max_threads == 10
        assert config.report_format == 'json'
    
    def test_apply_cli_args_scanning(self):
        """Test applying CLI args for scanning options"""
        cli = PentestCLI()
        cli.parse_args([
            'example.com',
            '--scan-mode', 'full',
            '--enable-udp-scan',
            '--max-threads', '40',
            '--scan-timeout', '15',
            '--scan-db-ports'
        ])
        config = cli.get_config()
        
        assert config.scan_mode == 'full'
        assert config.enable_udp_scan is True
        assert config.max_threads == 40
        assert config.scan_timeout == 15
        assert config.scan_db_ports is True
    
    def test_apply_cli_args_safety(self):
        """Test applying CLI args for safety options"""
        cli = PentestCLI()
        cli.parse_args([
            'example.com',
            '--no-safe-mode',
            '--quiet',
            '--max-brute-force-attempts', '5'
        ])
        config = cli.get_config()
        
        assert config.safe_mode is False
        assert config.verbose is False
        assert config.max_brute_force_attempts == 5
    
    def test_apply_cli_args_soar(self):
        """Test applying CLI args for SOAR integration"""
        cli = PentestCLI()
        cli.parse_args([
            'example.com',
            '--slack-webhook', 'https://hooks.slack.com/test',
            '--jira-url', 'https://jira.test.com',
            '--jira-token', 'token123'
        ])
        config = cli.get_config()
        
        assert config.slack_enabled is True
        assert config.slack_webhook == 'https://hooks.slack.com/test'
        assert config.jira_enabled is True
        assert config.jira_url == 'https://jira.test.com'
        assert config.jira_token == 'token123'
    
    def test_get_target_from_args(self):
        """Test getting target from parsed arguments"""
        cli = PentestCLI()
        cli.parse_args(['example.com'])
        
        target = cli.get_target()
        assert target == 'example.com'
    
    def test_validate_and_get_config_valid(self):
        """Test validation with valid configuration"""
        cli = PentestCLI()
        cli.parse_args([
            'example.com',
            '--scan-mode', 'common',
            '--max-threads', '10'
        ])
        
        config = cli.validate_and_get_config()
        assert config is not None
        assert isinstance(config, PentestConfig)
    
    def test_validate_and_get_config_invalid(self):
        """Test validation with invalid configuration"""
        cli = PentestCLI()
        cli.parse_args([
            'example.com',
            '--max-threads', '200'  # Invalid: > 100
        ])
        
        config = cli.validate_and_get_config()
        assert config is None
    
    def test_invalid_scan_mode(self):
        """Test that invalid scan mode raises error"""
        cli = PentestCLI()
        
        with pytest.raises(SystemExit):
            cli.parse_args(['example.com', '--scan-mode', 'invalid'])
    
    def test_invalid_report_format(self):
        """Test that invalid report format raises error"""
        cli = PentestCLI()
        
        with pytest.raises(SystemExit):
            cli.parse_args(['example.com', '--report-format', 'invalid'])
    
    def test_invalid_integer_value(self):
        """Test that invalid integer value raises error"""
        cli = PentestCLI()
        
        with pytest.raises(SystemExit):
            cli.parse_args(['example.com', '--max-threads', 'not_a_number'])


class TestCreateCLI:
    """Test create_cli function"""
    
    def test_create_cli(self):
        """Test creating CLI instance"""
        cli = create_cli()
        
        assert isinstance(cli, PentestCLI)
        assert cli.parser is not None
        assert cli.config_manager is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
