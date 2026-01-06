"""
Quick test script to run the penetration testing tool against the test website
"""
import sys
from ai_pentest_brain_complete import AIPentestBrain, RemediationMode

def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    
    print(f"\n{'='*70}")
    print(f"🔍 Testing AI Penetration Testing Brain")
    print(f"{'='*70}")
    print(f"Target: {target}")
    print(f"Mode: REPORT ONLY (safe testing)")
    print(f"{'='*70}\n")
    
    # Initialize the brain
    brain = AIPentestBrain()
    
    # Run autonomous testing in REPORT ONLY mode
    results = brain.autonomous_testing(target, RemediationMode.REPORT_ONLY)
    
    # Print summary
    print(f"\n{'='*70}")
    print(f"📊 TEST RESULTS SUMMARY")
    print(f"{'='*70}")
    
    findings = results.get('findings', [])
    print(f"\n✅ Total Vulnerabilities Found: {len(findings)}")
    
    # Count by severity
    severity_counts = {}
    for finding in findings:
        severity = finding.get('severity', 'unknown')
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    print(f"\n📈 Breakdown by Severity:")
    for severity in ['critical', 'high', 'medium', 'low', 'info']:
        count = severity_counts.get(severity, 0)
        if count > 0:
            print(f"  - {severity.upper()}: {count}")
    
    # List all findings
    print(f"\n🔍 Detailed Findings:")
    for i, finding in enumerate(findings, 1):
        vuln_type = finding.get('type', 'unknown')
        severity = finding.get('severity', 'unknown')
        endpoint = finding.get('endpoint', 'N/A')
        print(f"\n  {i}. [{severity.upper()}] {vuln_type}")
        print(f"     Endpoint: {endpoint}")
        if 'description' in finding:
            desc = finding['description'][:100]
            print(f"     Description: {desc}...")
    
    # Platform detection info
    platform_info = results.get('platform_detection', {})
    print(f"\n🖥️  Platform Detection:")
    print(f"  - Platform: {platform_info.get('platform', 'unknown')}")
    print(f"  - Database: {platform_info.get('database_type', 'unknown')}")
    print(f"  - SQL tests skipped: {platform_info.get('skip_sql_tests', False)}")
    print(f"  - Confidence: {platform_info.get('confidence', 0.0):.2f}")
    
    # Expected vulnerabilities check
    print(f"\n✅ Expected Vulnerabilities Check:")
    expected = {
        'xss': False,
        'missing_headers': False,
        'idor': False,
        'open_redirect': False,
        'sensitive_files': False
    }
    
    for finding in findings:
        vuln_type = finding.get('type', '').lower()
        if 'xss' in vuln_type:
            expected['xss'] = True
        if 'header' in vuln_type or 'hsts' in vuln_type or 'frame' in vuln_type:
            expected['missing_headers'] = True
        if 'idor' in vuln_type:
            expected['idor'] = True
        if 'redirect' in vuln_type:
            expected['open_redirect'] = True
        if 'exposed' in vuln_type or 'sensitive' in vuln_type:
            expected['sensitive_files'] = True
    
    for vuln_type, found in expected.items():
        status = "✅ FOUND" if found else "❌ MISSED"
        print(f"  {status}: {vuln_type.replace('_', ' ').title()}")
    
    print(f"\n{'='*70}")
    print(f"✅ Test Complete!")
    print(f"{'='*70}\n")
    
    # Save detailed report
    import json
    report_file = f"test_report_{target.replace('://', '_').replace('/', '_')}.json"
    with open(report_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"📄 Detailed report saved to: {report_file}\n")

if __name__ == "__main__":
    main()
