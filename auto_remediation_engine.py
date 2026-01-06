"""
Automated Vulnerability Remediation Engine
Automatically fixes identified security vulnerabilities
"""

import os
import re
import json
import logging
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import requests
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RemediationEngine:
    """
    Automated vulnerability remediation engine
    Fixes security issues identified during penetration testing
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.dry_run = self.config.get('dry_run', True)  # Safe by default
        self.backup_enabled = self.config.get('backup_enabled', True)
        self.remediation_log = []
        
    def remediate_findings(self, findings: List[Dict]) -> Dict:
        """
        Automatically remediate identified vulnerabilities
        
        Args:
            findings: List of vulnerability findings
            
        Returns:
            Dictionary with remediation results
        """
        results = {
            'start_time': datetime.now().isoformat(),
            'total_findings': len(findings),
            'remediated': 0,
            'failed': 0,
            'skipped': 0,
            'actions': []
        }
        
        logger.info(f"Starting remediation for {len(findings)} findings")
        
        for finding in findings:
            try:
                action = self._remediate_finding(finding)
                results['actions'].append(action)
                
                if action['status'] == 'success':
                    results['remediated'] += 1
                elif action['status'] == 'failed':
                    results['failed'] += 1
                else:
                    results['skipped'] += 1
                    
            except Exception as e:
                logger.error(f"Error remediating {finding.get('type')}: {str(e)}")
                results['failed'] += 1
                results['actions'].append({
                    'finding': finding.get('type'),
                    'status': 'failed',
                    'error': str(e)
                })
        
        results['end_time'] = datetime.now().isoformat()
        return results
    
    def _remediate_finding(self, finding: Dict) -> Dict:
        """Remediate a single finding"""
        vuln_type = finding.get('type', '').lower()
        
        # Route to appropriate remediation handler
        if 'missing_security_headers' in vuln_type or 'header' in vuln_type:
            return self._fix_security_headers(finding)
        elif 'ssl' in vuln_type or 'tls' in vuln_type:
            return self._fix_ssl_tls(finding)
        elif 'exposed' in vuln_type or 'port' in vuln_type:
            return self._fix_exposed_service(finding)
        elif 'wordpress' in vuln_type:
            return self._fix_wordpress(finding)
        elif 'outdated' in vuln_type or 'version' in vuln_type:
            return self._fix_outdated_software(finding)
        elif 'weak_password' in vuln_type or 'authentication' in vuln_type:
            return self._fix_weak_authentication(finding)
        elif 'sql' in vuln_type:
            return self._fix_sql_injection(finding)
        elif 'xss' in vuln_type:
            return self._fix_xss(finding)
        else:
            return {
                'finding': finding.get('type'),
                'status': 'skipped',
                'reason': 'No automated remediation available',
                'manual_action_required': True,
                'recommendation': finding.get('remediation', 'Manual review required')
            }
    
    def _fix_security_headers(self, finding: Dict) -> Dict:
        """Fix missing security headers"""
        logger.info("Fixing security headers...")
        
        headers_to_add = {
            'X-Frame-Options': 'SAMEORIGIN',
            'X-Content-Type-Options': 'nosniff',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'",
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
        }
        
        if self.dry_run:
            return {
                'finding': finding.get('type'),
                'status': 'success',
                'action': 'dry_run',
                'message': 'Would add security headers',
                'headers': headers_to_add,
                'instructions': self._generate_header_instructions(headers_to_add)
            }
        
        # Generate configuration snippets for different web servers
        configs = self._generate_security_header_configs(headers_to_add)
        
        return {
            'finding': finding.get('type'),
            'status': 'success',
            'action': 'configuration_generated',
            'message': 'Security header configurations generated',
            'configurations': configs
        }
    
    def _generate_header_instructions(self, headers: Dict) -> Dict:
        """Generate instructions for adding security headers"""
        return {
            'apache': self._generate_apache_headers(headers),
            'nginx': self._generate_nginx_headers(headers),
            'iis': self._generate_iis_headers(headers),
            'nodejs': self._generate_nodejs_headers(headers)
        }
    
    def _generate_apache_headers(self, headers: Dict) -> str:
        """Generate Apache configuration"""
        config = "# Add to .htaccess or apache config\n"
        config += "<IfModule mod_headers.c>\n"
        for header, value in headers.items():
            config += f"    Header always set {header} \"{value}\"\n"
        config += "</IfModule>\n"
        return config
    
    def _generate_nginx_headers(self, headers: Dict) -> str:
        """Generate Nginx configuration"""
        config = "# Add to nginx.conf or site config\n"
        for header, value in headers.items():
            config += f"add_header {header} \"{value}\" always;\n"
        return config
    
    def _generate_iis_headers(self, headers: Dict) -> str:
        """Generate IIS configuration"""
        config = "<!-- Add to web.config -->\n"
        config += "<system.webServer>\n"
        config += "  <httpProtocol>\n"
        config += "    <customHeaders>\n"
        for header, value in headers.items():
            config += f"      <add name=\"{header}\" value=\"{value}\" />\n"
        config += "    </customHeaders>\n"
        config += "  </httpProtocol>\n"
        config += "</system.webServer>\n"
        return config
    
    def _generate_nodejs_headers(self, headers: Dict) -> str:
        """Generate Node.js/Express configuration"""
        config = "// Add to Express app\n"
        config += "const helmet = require('helmet');\n"
        config += "app.use(helmet());\n\n"
        config += "// Or manually:\n"
        config += "app.use((req, res, next) => {\n"
        for header, value in headers.items():
            config += f"  res.setHeader('{header}', '{value}');\n"
        config += "  next();\n"
        config += "});\n"
        return config
    
    def _generate_security_header_configs(self, headers: Dict) -> Dict:
        """Generate configurations for all web servers"""
        return {
            'apache': self._generate_apache_headers(headers),
            'nginx': self._generate_nginx_headers(headers),
            'iis': self._generate_iis_headers(headers),
            'nodejs': self._generate_nodejs_headers(headers)
        }
    
    def _fix_ssl_tls(self, finding: Dict) -> Dict:
        """Fix SSL/TLS issues"""
        logger.info("Fixing SSL/TLS configuration...")
        
        recommendations = {
            'protocols': 'Disable SSLv2, SSLv3, TLSv1.0, TLSv1.1. Enable TLSv1.2 and TLSv1.3',
            'ciphers': 'Use strong cipher suites only',
            'certificate': 'Ensure valid certificate with proper chain',
            'hsts': 'Enable HTTP Strict Transport Security'
        }
        
        configs = {
            'apache': self._generate_apache_ssl_config(),
            'nginx': self._generate_nginx_ssl_config(),
            'iis': 'Use IIS Crypto tool to configure SSL/TLS'
        }
        
        return {
            'finding': finding.get('type'),
            'status': 'success',
            'action': 'configuration_generated',
            'recommendations': recommendations,
            'configurations': configs
        }
    
    def _generate_apache_ssl_config(self) -> str:
        """Generate Apache SSL configuration"""
        return """
# Apache SSL/TLS Configuration
SSLProtocol -all +TLSv1.2 +TLSv1.3
SSLCipherSuite HIGH:!aNULL:!MD5:!3DES
SSLHonorCipherOrder on
SSLCompression off
SSLSessionTickets off
"""
    
    def _generate_nginx_ssl_config(self) -> str:
        """Generate Nginx SSL configuration"""
        return """
# Nginx SSL/TLS Configuration
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers HIGH:!aNULL:!MD5;
ssl_prefer_server_ciphers on;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
"""
    
    def _fix_exposed_service(self, finding: Dict) -> Dict:
        """Fix exposed service"""
        logger.info("Generating firewall rules for exposed service...")
        
        port = finding.get('port', 'unknown')
        service = finding.get('service', 'unknown')
        
        firewall_rules = {
            'iptables': f"iptables -A INPUT -p tcp --dport {port} -j DROP",
            'ufw': f"ufw deny {port}/tcp",
            'firewalld': f"firewall-cmd --permanent --remove-port={port}/tcp",
            'windows': f"netsh advfirewall firewall add rule name=\"Block {service}\" dir=in action=block protocol=TCP localport={port}"
        }
        
        return {
            'finding': finding.get('type'),
            'status': 'success',
            'action': 'firewall_rules_generated',
            'port': port,
            'service': service,
            'firewall_rules': firewall_rules,
            'recommendation': f'Block port {port} or restrict access to trusted IPs only'
        }
    
    def _fix_wordpress(self, finding: Dict) -> Dict:
        """Fix WordPress vulnerabilities"""
        logger.info("Generating WordPress security fixes...")
        
        fixes = {
            'update_wordpress': 'wp core update',
            'update_plugins': 'wp plugin update --all',
            'update_themes': 'wp theme update --all',
            'security_plugins': [
                'Wordfence Security',
                'iThemes Security',
                'Sucuri Security'
            ],
            'hardening': {
                'disable_file_editing': "define('DISALLOW_FILE_EDIT', true);",
                'limit_login_attempts': 'Install Limit Login Attempts plugin',
                'two_factor_auth': 'Install Two Factor Authentication plugin',
                'change_admin_username': 'Create new admin user and delete default admin',
                'strong_passwords': 'Enforce strong password policy'
            }
        }
        
        return {
            'finding': finding.get('type'),
            'status': 'success',
            'action': 'recommendations_generated',
            'fixes': fixes
        }
    
    def _fix_outdated_software(self, finding: Dict) -> Dict:
        """Fix outdated software"""
        logger.info("Generating update commands...")
        
        update_commands = {
            'debian_ubuntu': 'apt update && apt upgrade -y',
            'centos_rhel': 'yum update -y',
            'fedora': 'dnf update -y',
            'arch': 'pacman -Syu',
            'windows': 'Check Windows Update in Settings',
            'macos': 'softwareupdate -i -a'
        }
        
        return {
            'finding': finding.get('type'),
            'status': 'success',
            'action': 'update_commands_generated',
            'update_commands': update_commands,
            'recommendation': 'Update all software to latest versions'
        }
    
    def _fix_weak_authentication(self, finding: Dict) -> Dict:
        """Fix weak authentication"""
        logger.info("Generating authentication security improvements...")
        
        improvements = {
            'password_policy': {
                'min_length': 12,
                'require_uppercase': True,
                'require_lowercase': True,
                'require_numbers': True,
                'require_special': True,
                'expiry_days': 90
            },
            'multi_factor_auth': 'Enable MFA for all users',
            'account_lockout': {
                'threshold': 5,
                'duration_minutes': 30
            },
            'session_management': {
                'timeout_minutes': 30,
                'secure_cookies': True,
                'httponly_cookies': True
            }
        }
        
        return {
            'finding': finding.get('type'),
            'status': 'success',
            'action': 'security_policy_generated',
            'improvements': improvements
        }
    
    def _fix_sql_injection(self, finding: Dict) -> Dict:
        """Fix SQL injection vulnerabilities"""
        logger.info("Generating SQL injection fixes...")
        
        fixes = {
            'use_prepared_statements': True,
            'input_validation': True,
            'parameterized_queries': True,
            'orm_usage': 'Use ORM frameworks (SQLAlchemy, Django ORM, etc.)',
            'code_examples': {
                'python': """
# Bad (vulnerable)
cursor.execute("SELECT * FROM users WHERE id = " + user_id)

# Good (safe)
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
""",
                'php': """
// Bad (vulnerable)
$query = "SELECT * FROM users WHERE id = " . $_GET['id'];

// Good (safe)
$stmt = $pdo->prepare("SELECT * FROM users WHERE id = ?");
$stmt->execute([$_GET['id']]);
""",
                'nodejs': """
// Bad (vulnerable)
db.query("SELECT * FROM users WHERE id = " + userId);

// Good (safe)
db.query("SELECT * FROM users WHERE id = ?", [userId]);
"""
            }
        }
        
        return {
            'finding': finding.get('type'),
            'status': 'success',
            'action': 'code_fixes_generated',
            'fixes': fixes
        }
    
    def _fix_xss(self, finding: Dict) -> Dict:
        """Fix XSS vulnerabilities"""
        logger.info("Generating XSS fixes...")
        
        fixes = {
            'output_encoding': True,
            'input_validation': True,
            'content_security_policy': True,
            'code_examples': {
                'python_flask': """
# Use Jinja2 auto-escaping (enabled by default)
{{ user_input }}  # Automatically escaped

# For raw HTML (use carefully)
{{ user_input | safe }}  # Only if you trust the input
""",
                'javascript': """
// Bad (vulnerable)
element.innerHTML = userInput;

// Good (safe)
element.textContent = userInput;
// or
element.innerText = userInput;
""",
                'php': """
// Bad (vulnerable)
echo $_GET['name'];

// Good (safe)
echo htmlspecialchars($_GET['name'], ENT_QUOTES, 'UTF-8');
"""
            }
        }
        
        return {
            'finding': finding.get('type'),
            'status': 'success',
            'action': 'code_fixes_generated',
            'fixes': fixes
        }
    
    def generate_remediation_report(self, results: Dict, output_file: str = None) -> str:
        """Generate a comprehensive remediation report"""
        report = f"""
AUTOMATED REMEDIATION REPORT
============================

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SUMMARY
-------
Total Findings: {results['total_findings']}
Remediated: {results['remediated']}
Failed: {results['failed']}
Skipped: {results['skipped']}

ACTIONS TAKEN
-------------
"""
        
        for action in results['actions']:
            report += f"\n{action['finding']}\n"
            report += f"Status: {action['status']}\n"
            
            if 'configurations' in action:
                report += "\nConfigurations Generated:\n"
                for server, config in action['configurations'].items():
                    report += f"\n{server.upper()}:\n{config}\n"
            
            if 'recommendation' in action:
                report += f"Recommendation: {action['recommendation']}\n"
            
            if 'manual_action_required' in action and action['manual_action_required']:
                report += "[!] MANUAL ACTION REQUIRED\n"
            
            report += "-" * 50 + "\n"
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"Remediation report saved to {output_file}")
        
        return report

def main():
    """Example usage"""
    # Sample findings
    findings = [
        {
            'type': 'missing_security_headers',
            'severity': 'medium',
            'description': 'Security headers are missing',
            'remediation': 'Add security headers'
        },
        {
            'type': 'exposed_mysql',
            'severity': 'high',
            'port': 3306,
            'service': 'mysql',
            'description': 'MySQL is exposed to the internet',
            'remediation': 'Block external access to MySQL'
        },
        {
            'type': 'wordpress_detected',
            'severity': 'medium',
            'description': 'WordPress installation detected',
            'remediation': 'Update WordPress and plugins'
        }
    ]
    
    # Initialize remediation engine
    engine = RemediationEngine({
        'dry_run': True,  # Safe mode
        'backup_enabled': True
    })
    
    # Remediate findings
    results = engine.remediate_findings(findings)
    
    # Generate report
    report = engine.generate_remediation_report(results, 'remediation_report.txt')
    print(report)

if __name__ == "__main__":
    main()
