"""
Interactive Fix Application Module
Provides interactive system for applying vulnerability fixes with user approval
"""

import os
import sys
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass

@dataclass
class FixResult:
    """Result of a fix application"""
    success: bool
    message: str
    applied: bool
    skipped: bool
    details: Dict[str, Any]

class InteractiveFixApplication:
    """Interactive system for applying vulnerability fixes"""
    
    def __init__(self):
        self.applied_fixes: List[Dict] = []
        self.skipped_fixes: List[Dict] = []
        self.session_start = datetime.now()
        self.session_log: List[str] = []
    
    def show_pending_fixes(self, pending_fixes: List[Dict]) -> None:
        """Display pending fixes that require user approval"""
        print("\n" + "="*80)
        print("PENDING FIXES REQUIRING APPROVAL")
        print("="*80)
        
        if not pending_fixes:
            print("\nNo pending fixes require approval.")
            return
        
        print(f"\nTotal fixes pending: {len(pending_fixes)}\n")
        
        # Group by severity
        severity_groups = {}
        for fix in pending_fixes:
            severity = fix.get('severity', 'unknown').upper()
            if severity not in severity_groups:
                severity_groups[severity] = []
            severity_groups[severity].append(fix)
        
        # Display by severity (Critical first)
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO', 'UNKNOWN']:
            if severity in severity_groups:
                fixes = severity_groups[severity]
                print(f"\n[{severity}] - {len(fixes)} fix(es)")
                print("-" * 40)
                for idx, fix in enumerate(fixes, 1):
                    vuln_type = fix.get('type', fix.get('vulnerability_type', 'Unknown'))
                    endpoint = fix.get('endpoint', fix.get('url', 'N/A'))
                    print(f"  {idx}. {vuln_type}")
                    print(f"     Endpoint: {endpoint}")
                    if fix.get('description'):
                        desc = fix['description'][:80] + '...' if len(fix.get('description', '')) > 80 else fix.get('description', '')
                        print(f"     Description: {desc}")
    
    def ask_to_proceed(self) -> bool:
        """Ask user if they want to proceed with interactive fix application"""
        print("\n" + "="*80)
        print("INTERACTIVE FIX APPLICATION")
        print("="*80)
        print("\nThis will guide you through each fix one by one.")
        print("You can approve, skip, or stop at any point.")
        print("\nOptions during fix application:")
        print("  [Y/yes]  - Apply this fix")
        print("  [N/no]   - Skip this fix")
        print("  [S/stop] - Stop all fix application")
        print("  [V/view] - View more details about this fix")
        
        response = input("\nProceed with interactive fix application? (yes/no): ").strip().lower()
        return response in ['yes', 'y']
    
    def apply_fix_interactive(self, fix: Dict, current_idx: int, total: int) -> str:
        """
        Apply a single fix interactively with user approval
        
        Returns:
            'APPLIED' - Fix was applied
            'SKIPPED' - Fix was skipped
            'STOP' - User requested to stop
        """
        print("\n" + "-"*80)
        print(f"FIX {current_idx}/{total}")
        print("-"*80)
        
        # Display fix details
        vuln_type = fix.get('type', fix.get('vulnerability_type', 'Unknown'))
        severity = fix.get('severity', 'UNKNOWN').upper()
        endpoint = fix.get('endpoint', fix.get('url', 'N/A'))
        description = fix.get('description', 'No description available')
        remediation = fix.get('remediation', fix.get('fix', 'Manual remediation required'))
        
        print(f"\n  Vulnerability: {vuln_type}")
        print(f"  Severity: {severity}")
        print(f"  Endpoint: {endpoint}")
        print(f"\n  Description:")
        print(f"    {description}")
        print(f"\n  Recommended Fix:")
        print(f"    {remediation}")
        
        # Show evidence if available
        evidence = fix.get('evidence', {})
        if evidence:
            print(f"\n  Evidence:")
            for key, value in evidence.items():
                if isinstance(value, str) and len(value) > 100:
                    value = value[:100] + '...'
                print(f"    {key}: {value}")
        
        # Get user decision
        while True:
            response = input(f"\n  Apply this fix? [Y]es/[N]o/[S]top/[V]iew more: ").strip().lower()
            
            if response in ['y', 'yes']:
                # Apply the fix
                result = self._apply_single_fix(fix)
                if result.success:
                    print(f"\n  ✓ Fix applied successfully: {result.message}")
                    self.applied_fixes.append({
                        'fix': fix,
                        'result': result,
                        'timestamp': datetime.now().isoformat()
                    })
                    self._log(f"Applied: {vuln_type} at {endpoint}")
                else:
                    print(f"\n  ✗ Fix failed: {result.message}")
                    self._log(f"Failed: {vuln_type} at {endpoint} - {result.message}")
                return 'APPLIED'
            
            elif response in ['n', 'no']:
                print(f"\n  → Fix skipped")
                self.skipped_fixes.append({
                    'fix': fix,
                    'reason': 'User skipped',
                    'timestamp': datetime.now().isoformat()
                })
                self._log(f"Skipped: {vuln_type} at {endpoint}")
                return 'SKIPPED'
            
            elif response in ['s', 'stop']:
                print(f"\n  ■ Stopping fix application")
                self._log("User stopped fix application")
                return 'STOP'
            
            elif response in ['v', 'view']:
                self._show_detailed_view(fix)
            
            else:
                print("  Invalid input. Please enter Y, N, S, or V.")
    
    def _apply_single_fix(self, fix: Dict) -> FixResult:
        """Apply a single fix (simulation in safe mode)"""
        vuln_type = fix.get('type', fix.get('vulnerability_type', 'Unknown')).lower()
        
        try:
            # Determine fix type and apply appropriate action
            if 'sql' in vuln_type:
                return self._fix_sql_injection(fix)
            elif 'xss' in vuln_type or 'cross_site' in vuln_type:
                return self._fix_xss(fix)
            elif 'header' in vuln_type or 'missing' in vuln_type:
                return self._fix_missing_header(fix)
            elif 'path' in vuln_type or 'traversal' in vuln_type:
                return self._fix_path_traversal(fix)
            elif 'command' in vuln_type or 'injection' in vuln_type:
                return self._fix_command_injection(fix)
            elif 'csrf' in vuln_type:
                return self._fix_csrf(fix)
            elif 'idor' in vuln_type:
                return self._fix_idor(fix)
            else:
                return self._fix_generic(fix)
                
        except Exception as e:
            return FixResult(
                success=False,
                message=f"Error applying fix: {str(e)}",
                applied=False,
                skipped=False,
                details={'error': str(e)}
            )
    
    def _fix_sql_injection(self, fix: Dict) -> FixResult:
        """Fix SQL injection vulnerability"""
        return FixResult(
            success=True,
            message="SQL injection fix simulated - Use parameterized queries",
            applied=True,
            skipped=False,
            details={
                'fix_type': 'sql_injection',
                'action': 'Recommend implementing parameterized queries',
                'code_change': 'Replace string concatenation with prepared statements'
            }
        )
    
    def _fix_xss(self, fix: Dict) -> FixResult:
        """Fix XSS vulnerability"""
        return FixResult(
            success=True,
            message="XSS fix simulated - Implement output encoding",
            applied=True,
            skipped=False,
            details={
                'fix_type': 'xss',
                'action': 'Add output encoding and CSP headers',
                'code_change': 'HTML encode all user output'
            }
        )
    
    def _fix_missing_header(self, fix: Dict) -> FixResult:
        """Fix missing security header"""
        return FixResult(
            success=True,
            message="Security header fix simulated - Add recommended headers",
            applied=True,
            skipped=False,
            details={
                'fix_type': 'missing_header',
                'action': 'Add security headers to web server configuration',
                'headers_to_add': ['X-Frame-Options', 'X-Content-Type-Options', 'Strict-Transport-Security']
            }
        )
    
    def _fix_path_traversal(self, fix: Dict) -> FixResult:
        """Fix path traversal vulnerability"""
        return FixResult(
            success=True,
            message="Path traversal fix simulated - Validate file paths",
            applied=True,
            skipped=False,
            details={
                'fix_type': 'path_traversal',
                'action': 'Implement path validation and whitelist approach',
                'code_change': 'Use realpath() and validate against allowed directories'
            }
        )
    
    def _fix_command_injection(self, fix: Dict) -> FixResult:
        """Fix command injection vulnerability"""
        return FixResult(
            success=True,
            message="Command injection fix simulated - Use safe APIs",
            applied=True,
            skipped=False,
            details={
                'fix_type': 'command_injection',
                'action': 'Replace system commands with safe library functions',
                'code_change': 'Avoid shell=True, use subprocess with argument lists'
            }
        )
    
    def _fix_csrf(self, fix: Dict) -> FixResult:
        """Fix CSRF vulnerability"""
        return FixResult(
            success=True,
            message="CSRF fix simulated - Implement CSRF tokens",
            applied=True,
            skipped=False,
            details={
                'fix_type': 'csrf',
                'action': 'Add CSRF token validation',
                'code_change': 'Generate and validate CSRF tokens for state-changing requests'
            }
        )
    
    def _fix_idor(self, fix: Dict) -> FixResult:
        """Fix IDOR vulnerability"""
        return FixResult(
            success=True,
            message="IDOR fix simulated - Implement authorization checks",
            applied=True,
            skipped=False,
            details={
                'fix_type': 'idor',
                'action': 'Add authorization verification',
                'code_change': 'Verify user has permission to access requested resource'
            }
        )
    
    def _fix_generic(self, fix: Dict) -> FixResult:
        """Generic fix for other vulnerability types"""
        return FixResult(
            success=True,
            message=f"Generic fix simulated for {fix.get('type', 'unknown')}",
            applied=True,
            skipped=False,
            details={
                'fix_type': 'generic',
                'action': fix.get('remediation', 'Manual review recommended'),
                'code_change': 'Review and apply recommended remediation steps'
            }
        )
    
    def _show_detailed_view(self, fix: Dict) -> None:
        """Show detailed view of a fix"""
        print("\n  " + "="*60)
        print("  DETAILED FIX INFORMATION")
        print("  " + "="*60)
        
        for key, value in fix.items():
            if key == 'evidence':
                print(f"\n  {key}:")
                if isinstance(value, dict):
                    for k, v in value.items():
                        print(f"    {k}: {v}")
                else:
                    print(f"    {value}")
            else:
                print(f"\n  {key}: {value}")
        
        print("\n  " + "="*60)
    
    def _log(self, message: str) -> None:
        """Add message to session log"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.session_log.append(f"[{timestamp}] {message}")
    
    def generate_session_report(self, auto_fixed_count: int = 0) -> Dict:
        """Generate comprehensive session report"""
        session_end = datetime.now()
        session_duration = session_end - self.session_start
        
        report = {
            'session_info': {
                'start_time': self.session_start.isoformat(),
                'end_time': session_end.isoformat(),
                'duration_seconds': session_duration.total_seconds()
            },
            'summary': {
                'auto_fixed': auto_fixed_count,
                'interactive_applied': len(self.applied_fixes),
                'interactive_skipped': len(self.skipped_fixes),
                'total_processed': len(self.applied_fixes) + len(self.skipped_fixes)
            },
            'applied_fixes': self.applied_fixes,
            'skipped_fixes': self.skipped_fixes,
            'session_log': self.session_log
        }
        
        # Print summary
        print("\n" + "="*80)
        print("SESSION SUMMARY")
        print("="*80)
        print(f"\nSession Duration: {session_duration}")
        print(f"\nFixes Summary:")
        print(f"  Auto-fixed (Phase 1): {auto_fixed_count}")
        print(f"  Interactive Applied: {len(self.applied_fixes)}")
        print(f"  Interactive Skipped: {len(self.skipped_fixes)}")
        print(f"  Total Processed: {report['summary']['total_processed']}")
        
        # Save report to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"session_report_{timestamp}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"\nSession report saved to: {report_file}")
        
        return report


# Module-level function for backward compatibility
def create_interactive_system():
    """Create and return an InteractiveFixApplication instance"""
    return InteractiveFixApplication()


