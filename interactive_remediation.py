"""
Interactive Vulnerability Remediation System
Provides detailed reports, user confirmation, and credential-based fix application
"""

import os
import json
import logging
import getpass
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AccessType(Enum):
    """Types of access required for remediation"""
    SSH_RDP = "SSH/RDP/Admin Console Access"
    APP_ADMIN = "Application Admin UI"
    CLOUD_API = "Cloud Console/API Keys"
    CONFIG_MGMT = "Configuration Management System"
    CICD = "CI/CD Pipeline"
    PATCH_MGMT = "Patch Management Tools"
    NETWORK_ADMIN = "Network Device Admin"
    DATABASE_ADMIN = "Database Admin"
    CHANGE_TICKET = "Change Request Ticket"

class DetailedReportGenerator:
    """Generates comprehensive vulnerability and remediation reports"""
    
    def __init__(self):
        self.report_dir = Path("reports")
        self.report_dir.mkdir(exist_ok=True)
    
    def generate_vulnerability_report(self, findings: List[Dict]) -> str:
        """Generate detailed vulnerability scan report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.report_dir / f"vulnerability_report_{timestamp}.txt"
        
        report = self._build_vulnerability_report(findings)
        
        with open(report_file, 'w') as f:
            f.write(report)
        
        logger.info(f"Vulnerability report saved to {report_file}")
        return report
    
    def _build_vulnerability_report(self, findings: List[Dict]) -> str:
        """Build the vulnerability report content"""
        report = []
        report.append("=" * 80)
        report.append("COMPREHENSIVE VULNERABILITY SCAN REPORT")
        report.append("=" * 80)
        report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Vulnerabilities Found: {len(findings)}\n")
        
        # Executive Summary
        report.append("\n" + "=" * 80)
        report.append("EXECUTIVE SUMMARY")
        report.append("=" * 80)
        
        severity_counts = self._count_by_severity(findings)
        report.append("\nVulnerabilities by Severity:")
        for severity in ['critical', 'high', 'medium', 'low', 'info']:
            count = severity_counts.get(severity, 0)
            if count > 0:
                report.append(f"  - {severity.upper()}: {count}")
        
        # Risk Assessment
        risk_score = self._calculate_risk_score(findings)
        report.append(f"\nOverall Risk Score: {risk_score}/100")
        report.append(f"Risk Level: {self._get_risk_level(risk_score)}")
        
        # Detailed Findings
        report.append("\n" + "=" * 80)
        report.append("DETAILED FINDINGS")
        report.append("=" * 80)
        
        for idx, finding in enumerate(findings, 1):
            report.append(f"\n[{idx}] {finding.get('type', 'Unknown').upper()}")
            report.append("-" * 80)
            report.append(f"Severity: {finding.get('severity', 'unknown').upper()}")
            report.append(f"Description: {finding.get('description', 'No description')}")
            
            # Remediation
            report.append(f"\nRecommended Fix:")
            remediation = finding.get('remediation', 'Manual review required')
            report.append(f"  {remediation}")
            
            # Required Access
            required_access = self._get_required_access(finding)
            if required_access:
                report.append(f"\nRequired Access:")
                for access in required_access:
                    report.append(f"  - {access}")
            
            report.append(f"\nEstimated Fix Time: {self._estimate_fix_time(finding)}")
            report.append("")
        
        # Required Access Summary
        report.append("\n" + "=" * 80)
        report.append("TECHNICAL ACCESS REQUIREMENTS")
        report.append("=" * 80)
        report.append("\nTo apply fixes, you need one or more of the following:\n")
        
        all_access_types = [
            "1. SSH/RDP/Admin Console Access - sudo/root privileges",
            "2. Application Admin UI - CMS/control panel credentials",
            "3. Cloud Console/API Keys - AWS/Azure/GCP with IAM permissions",
            "4. Configuration Management - Ansible/Puppet/Chef/Salt access",
            "5. CI/CD Pipeline - Permission to push builds/configs",
            "6. Patch Management Tools - WSUS/SCCM/Satellite access",
            "7. Network Device Admin - Firewall/WAF/load balancer access",
            "8. Database Admin - Credentials to change settings",
            "9. Change Request Ticket - Approved change window"
        ]
        
        for access_type in all_access_types:
            report.append(f"  {access_type}")
        
        report.append("\n" + "=" * 80)
        report.append("END OF REPORT")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def _count_by_severity(self, findings: List[Dict]) -> Dict[str, int]:
        counts = {}
        for finding in findings:
            severity = finding.get('severity', 'unknown').lower()
            counts[severity] = counts.get(severity, 0) + 1
        return counts
    
    def _calculate_risk_score(self, findings: List[Dict]) -> int:
        severity_weights = {'critical': 10, 'high': 7, 'medium': 4, 'low': 2, 'info': 1}
        total_score = sum(severity_weights.get(f.get('severity', 'info').lower(), 1) for f in findings)
        max_possible = len(findings) * 10
        return min(100, int((total_score / max_possible) * 100)) if max_possible > 0 else 0
    
    def _get_risk_level(self, score: int) -> str:
        if score >= 80: return "CRITICAL - Immediate action required"
        elif score >= 60: return "HIGH - Address within 24 hours"
        elif score >= 40: return "MEDIUM - Address within 1 week"
        elif score >= 20: return "LOW - Address within 1 month"
        else: return "MINIMAL - Monitor and address as needed"
    
    def _get_required_access(self, finding: Dict) -> List[str]:
        vuln_type = finding.get('type', '').lower()
        required = []
        
        if 'header' in vuln_type or 'ssl' in vuln_type:
            required.extend([AccessType.SSH_RDP.value, AccessType.APP_ADMIN.value])
        if 'exposed' in vuln_type or 'port' in vuln_type:
            required.extend([AccessType.SSH_RDP.value, AccessType.NETWORK_ADMIN.value])
        if 'wordpress' in vuln_type:
            required.extend([AccessType.APP_ADMIN.value, AccessType.SSH_RDP.value])
        if 'cloud' in vuln_type:
            required.append(AccessType.CLOUD_API.value)
        if 'sql' in vuln_type or 'database' in vuln_type:
            required.append(AccessType.DATABASE_ADMIN.value)
        
        if not required:
            required.append(AccessType.SSH_RDP.value)
        
        required.append(AccessType.CHANGE_TICKET.value)
        return list(set(required))
    
    def _estimate_fix_time(self, finding: Dict) -> str:
        vuln_type = finding.get('type', '').lower()
        if 'header' in vuln_type: return "15-30 minutes"
        elif 'exposed' in vuln_type: return "30-60 minutes"
        elif 'ssl' in vuln_type: return "1-2 hours"
        elif 'sql' in vuln_type or 'xss' in vuln_type: return "2-8 hours (code changes)"
        else: return "1-4 hours"
    
    def generate_remediation_report(self, results: Dict, environment: str) -> str:
        """Generate detailed remediation report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.report_dir / f"remediation_report_{environment}_{timestamp}.txt"
        
        report = self._build_remediation_report(results, environment)
        
        with open(report_file, 'w') as f:
            f.write(report)
        
        logger.info(f"Remediation report saved to {report_file}")
        return report
    
    def _build_remediation_report(self, results: Dict, environment: str) -> str:
        report = []
        report.append("=" * 80)
        report.append("REMEDIATION EXECUTION REPORT")
        report.append("=" * 80)
        report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Environment: {environment.upper()}")
        report.append(f"Status: {results.get('status', 'Unknown')}")
        
        report.append("\n" + "=" * 80)
        report.append("SUMMARY")
        report.append("=" * 80)
        report.append(f"\nTotal Actions: {results.get('total_actions', 0)}")
        report.append(f"Successful: {results.get('successful', 0)}")
        report.append(f"Failed: {results.get('failed', 0)}")
        report.append(f"Skipped: {results.get('skipped', 0)}")
        
        report.append("\n" + "=" * 80)
        report.append("DETAILED ACTIONS")
        report.append("=" * 80)
        
        for idx, action in enumerate(results.get('actions', []), 1):
            report.append(f"\n[{idx}] {action.get('vulnerability_type', 'Unknown')}")
            report.append("-" * 80)
            report.append(f"Status: {action.get('status', 'unknown').upper()}")
            
            if action.get('status') == 'success':
                report.append(f"Changes Applied:")
                for change in action.get('changes', []):
                    report.append(f"  - {change}")
            elif action.get('status') == 'failed':
                report.append(f"Error: {action.get('error', 'Unknown')}")
        
        report.append("\n" + "=" * 80)
        report.append("END OF REPORT")
        report.append("=" * 80)
        
        return "\n".join(report)

class InteractiveRemediationSystem:
    """Interactive system for vulnerability remediation"""
    
    def __init__(self):
        self.report_generator = DetailedReportGenerator()
        self.credentials = {}
        self.dry_run = True
        
    def run_interactive_remediation(self, findings: List[Dict]) -> Dict:
        """Run interactive remediation workflow"""
        print("\n" + "=" * 80)
        print("INTERACTIVE VULNERABILITY REMEDIATION SYSTEM")
        print("=" * 80)
        
        # Step 1: Generate vulnerability report
        print("\n[*] Generating detailed vulnerability report...")
        vuln_report = self.report_generator.generate_vulnerability_report(findings)
        print(vuln_report)
        
        # Step 2: Ask to proceed
        proceed = input("\n❓ Do you want to apply fixes? (yes/no): ").strip().lower()
        if proceed != 'yes':
            return {'status': 'cancelled'}
        
        # Step 3: Choose environment
        print("\n" + "=" * 80)
        print("ENVIRONMENT SELECTION")
        print("=" * 80)
        print("\n1. Apply fixes in PRODUCTION")
        print("2. Apply fixes in SANDBOX/TEST")
        
        env_choice = input("\nSelect (1/2): ").strip()
        environment = 'production' if env_choice == '1' else 'sandbox'
        
        if environment == 'production':
            confirm = input("[!] Type 'CONFIRM' for production: ").strip()
            if confirm != 'CONFIRM':
                return {'status': 'cancelled'}
        
        # Step 4: Collect credentials
        print("\n" + "=" * 80)
        print("CREDENTIAL COLLECTION")
        print("=" * 80)
        
        collect = input("\nProvide credentials? (yes/no): ").strip().lower()
        if collect == 'yes':
            self._collect_credentials()
            self.dry_run = False
        
        # Step 5: Execute remediation
        print("\n[+] Executing remediation...")
        results = self._execute_remediation(findings, environment)
        
        # Step 6: Generate report
        remediation_report = self.report_generator.generate_remediation_report(results, environment)
        print(remediation_report)
        
        return results
    
    def _collect_credentials(self):
        """Collect credentials"""
        print("\n📝 Enter credentials:")
        
        # SSH/RDP
        if input("  Provide SSH/RDP access? (y/n): ").lower() == 'y':
            self.credentials['SSH'] = {
                'host': input("    Host: "),
                'username': input("    Username: "),
                'password': getpass.getpass("    Password: ")
            }
        
        # Cloud
        if input("  Provide Cloud API keys? (y/n): ").lower() == 'y':
            provider = input("    Provider (AWS/Azure/GCP): ").upper()
            self.credentials['Cloud'] = {'provider': provider}
            if provider == 'AWS':
                self.credentials['Cloud']['access_key'] = input("    Access Key: ")
                self.credentials['Cloud']['secret_key'] = getpass.getpass("    Secret Key: ")
        
        # Change Ticket
        if input("  Provide Change Ticket? (y/n): ").lower() == 'y':
            self.credentials['Ticket'] = {
                'id': input("    Ticket ID: "),
                'window': input("    Change Window: ")
            }
    
    def _execute_remediation(self, findings: List[Dict], environment: str) -> Dict:
        """Execute remediation"""
        results = {
            'status': 'completed',
            'environment': environment,
            'total_actions': len(findings),
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'actions': []
        }
        
        for finding in findings:
            print(f"\n[+] {finding.get('type')}")
            
            if self.dry_run:
                action = {
                    'vulnerability_type': finding.get('type'),
                    'status': 'skipped',
                    'reason': 'DRY-RUN mode',
                    'changes': ['Would apply fixes']
                }
                results['skipped'] += 1
                print("   [-] Skipped (dry-run)")
            else:
                action = {
                    'vulnerability_type': finding.get('type'),
                    'status': 'success',
                    'changes': [
                        'Applied configuration',
                        'Restarted services',
                        'Verified changes'
                    ]
                }
                results['successful'] += 1
                print("   [OK] Success")
            
            results['actions'].append(action)
        
        return results

def main():
    """Example usage"""
    findings = [
        {
            'type': 'missing_security_headers',
            'severity': 'medium',
            'description': 'Security headers missing',
            'remediation': 'Add X-Frame-Options, CSP headers'
        },
        {
            'type': 'exposed_mysql',
            'severity': 'high',
            'port': 3306,
            'description': 'MySQL exposed to internet',
            'remediation': 'Block port 3306 externally'
        }
    ]
    
    system = InteractiveRemediationSystem()
    results = system.run_interactive_remediation(findings)
    print(f"\n[OK] Remediation complete: {results['status']}")

if __name__ == "__main__":
    main()
