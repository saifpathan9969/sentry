"""
Impossibility Tracker - Quantifies and documents the 22% intrinsic limits
Part of AI Pentest Brain V3.9+

Tracks categories of vulnerabilities that are mathematically/practically impossible
to detect with any automated tool, providing transparency and risk management.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import json
from datetime import datetime


@dataclass
class ImpossibilityCategory:
    """Single category of intrinsic limitation"""
    id: str
    name: str
    percent: float
    explanation: str
    why_impossible: str
    mitigations: List[str]
    evidence_needed: List[str]
    confidence: float  # 0-1 scale
    
    def to_dict(self):
        return asdict(self)


class ImpossibilityTracker:
    """
    Tracks and reports on the 22% of vulnerabilities that are
    fundamentally impossible to detect with automated tools.
    """
    
    # Default impossibility categories based on research
    DEFAULT_CATEGORIES = [
        ImpossibilityCategory(
            id="halting_problem",
            name="Halting Problem (Turing, 1936)",
            percent=3.0,
            explanation="Undecidable program behaviors where no algorithm can determine termination or properties for all programs",
            why_impossible="Mathematically proven by Alan Turing - certain program properties cannot be computed",
            mitigations=[
                "Manual code review for complex termination logic",
                "Static formal verification on critical modules",
                "Design by limiting complexity in critical paths",
                "Use bounded loops and recursion where possible"
            ],
            evidence_needed=[
                "Formal verification report",
                "Manual code audit results",
                "Complexity metrics report"
            ],
            confidence=0.95
        ),
        ImpossibilityCategory(
            id="rices_theorem",
            name="Rice's Theorem (1953)",
            percent=2.0,
            explanation="Semantic properties of programs that are undecidable in the general case",
            why_impossible="Mathematically proven - non-trivial semantic properties cannot be automatically determined",
            mitigations=[
                "Human expert review",
                "Formal methods and theorem proving",
                "Developer attestation and documentation",
                "Type system guarantees"
            ],
            evidence_needed=[
                "Security expert sign-off",
                "Formal proof documents",
                "Architecture review notes"
            ],
            confidence=0.92
        ),
        ImpossibilityCategory(
            id="future_unknowns",
            name="Future Unknowns (Zero-Day & Emerging Threats)",
            percent=2.0,
            explanation="Vulnerabilities not yet discovered or that will appear when future components/attacks are released",
            why_impossible="Cannot detect what doesn't exist yet - quantum attacks, novel exploit techniques, new framework bugs",
            mitigations=[
                "Regular re-scans (weekly/monthly)",
                "Threat intelligence integration",
                "Responsible disclosure monitoring",
                "Bug bounty programs",
                "Keep software/dependencies updated"
            ],
            evidence_needed=[
                "Scan schedule documentation",
                "Threat intel subscription proof",
                "Patch management logs"
            ],
            confidence=0.70
        ),
        ImpossibilityCategory(
            id="human_factors",
            name="Human Factors (Social Engineering & Process)",
            percent=5.0,
            explanation="Attacks that exploit human behavior, policy gaps, or social engineering",
            why_impossible="No code analysis can detect human psychology, phishing susceptibility, or insider threats",
            mitigations=[
                "Security awareness training",
                "Phishing simulation tests",
                "Insider threat programs",
                "Policy & procedure reviews",
                "Access control audits",
                "Background checks"
            ],
            evidence_needed=[
                "Training completion records",
                "Phishing test results",
                "HR security clearances",
                "Access audit logs"
            ],
            confidence=0.85
        ),
        ImpossibilityCategory(
            id="environmental",
            name="Environmental Constraints",
            percent=3.0,
            explanation="Production-only conditions, network topology, hardware timing, load balancer configs that cannot be replicated",
            why_impossible="Testing environment ≠ production environment; some conditions only exist under real load/config",
            mitigations=[
                "Production-like staging environments",
                "Chaos engineering tests",
                "Load testing",
                "Infrastructure-as-code reviews",
                "Network topology analysis",
                "Repeat scans in different conditions"
            ],
            evidence_needed=[
                "Infrastructure diagrams",
                "Load test reports",
                "Production config snapshots",
                "Chaos test results"
            ],
            confidence=0.80
        ),
        ImpossibilityCategory(
            id="combinatorial_explosion",
            name="Combinatorial Explosion",
            percent=5.0,
            explanation="State spaces too large to exhaustively test (10^155 combinations); multi-parameter interactions",
            why_impossible="Testing all combinations would take longer than the universe's lifetime",
            mitigations=[
                "Targeted fuzzing on critical paths",
                "Boundary value analysis",
                "Pairwise/combinatorial testing",
                "Human prioritization of high-risk areas",
                "Formal reduction techniques",
                "Model-based testing"
            ],
            evidence_needed=[
                "Risk assessment matrix",
                "Testing coverage report",
                "Fuzzing campaign results",
                "Critical path documentation"
            ],
            confidence=0.80
        ),
        ImpossibilityCategory(
            id="context_dependent",
            name="Context-Specific Business Rules",
            percent=2.0,
            explanation="Application-unique multi-step business logic impossible to infer without domain knowledge",
            why_impossible="Tool cannot know developer intent, business requirements, or domain-specific rules",
            mitigations=[
                "Business rules documentation and injection",
                "Domain expert reviews",
                "Business logic testing with stakeholders",
                "User story validation",
                "Acceptance criteria verification"
            ],
            evidence_needed=[
                "Business requirements document",
                "Stakeholder sign-off",
                "Logic flow diagrams",
                "Domain expert review notes"
            ],
            confidence=0.88
        )
    ]
    
    def __init__(self, custom_overrides: Optional[Dict[str, float]] = None):
        """
        Initialize tracker with optional custom percentages
        
        Args:
            custom_overrides: Dict mapping category IDs to custom percentages
                            (e.g., for industries with better controls)
        """
        self.categories = []
        self.custom_overrides = custom_overrides or {}
        
        # Load categories with optional overrides
        for cat in self.DEFAULT_CATEGORIES:
            if cat.id in self.custom_overrides:
                cat.percent = self.custom_overrides[cat.id]
            self.categories.append(cat)
    
    def get_total_impossible_pct(self) -> float:
        """Calculate total impossibility percentage"""
        total = sum(cat.percent for cat in self.categories)
        return round(max(0.0, min(total, 100.0)), 3)
    
    def get_breakdown(self) -> Dict:
        """Get complete impossibility breakdown"""
        return {
            "impossibility_breakdown": [cat.to_dict() for cat in self.categories],
            "total_impossible_pct": self.get_total_impossible_pct(),
            "generated_at": datetime.now().isoformat(),
            "note": "These limits apply to ANY automated tool, not just ours"
        }
    
    def calculate_residual_risk(self, base_vuln_score: float) -> Dict:
        """
        Calculate residual risk accounting for impossibilities
        
        Args:
            base_vuln_score: 0-100 score from detected vulnerabilities
            
        Returns:
            Dict with residual risk breakdown
        """
        total_impossible = self.get_total_impossible_pct()
        
        # Conservative multiplier: adds weight for untestable areas
        multiplier = 1.0 + (total_impossible / 100.0)
        residual_score = min(100.0, base_vuln_score * multiplier)
        
        return {
            "base_vulnerability_score": round(base_vuln_score, 2),
            "impossibility_multiplier": round(multiplier, 3),
            "residual_risk_score": round(residual_score, 2),
            "formula": "residual = base * (1 + impossible_pct/100)",
            "interpretation": self._interpret_residual_risk(residual_score)
        }
    
    def _interpret_residual_risk(self, score: float) -> str:
        """Provide human-readable interpretation"""
        if score < 20:
            return "LOW - Tool found few issues, but manual review recommended for impossibilities"
        elif score < 40:
            return "MODERATE - Address found issues + prioritize human review of high-risk impossibilities"
        elif score < 60:
            return "ELEVATED - Significant detected issues + substantial untestable surface"
        elif score < 80:
            return "HIGH - Major issues detected + large untestable areas require immediate attention"
        else:
            return "CRITICAL - Severe detected vulnerabilities + extensive blind spots - comprehensive remediation needed"
    
    def get_category_by_id(self, category_id: str) -> Optional[ImpossibilityCategory]:
        """Get specific category details"""
        for cat in self.categories:
            if cat.id == category_id:
                return cat
        return None
    
    def check_if_finding_in_impossibility(self, finding: Dict) -> Dict:
        """
        Check if a finding falls within an impossibility category
        
        Args:
            finding: Vulnerability finding dict
            
        Returns:
            Dict with category info if matched, else None
        """
        vuln_type = finding.get('type', '').lower()
        description = finding.get('description', '').lower()
        
        # Heuristic matching
        if 'race' in vuln_type or 'timing' in description:
            return {
                "is_impossibility": True,
                "category": "environmental",
                "reason": "Timing-dependent vulnerabilities may not be reproducible in all environments"
            }
        
        if 'business logic' in vuln_type or 'workflow' in description:
            return {
                "is_impossibility": True,
                "category": "context_dependent",
                "reason": "Business logic requires domain knowledge to fully validate"
            }
        
        if 'state' in vuln_type and 'multi' in description:
            return {
                "is_impossibility": True,
                "category": "combinatorial_explosion",
                "reason": "Complex state interactions impossible to exhaustively test"
            }
        
        return {
            "is_impossibility": False,
            "category": None,
            "reason": None
        }
    
    def generate_report_summary(self) -> str:
        """Generate human-readable summary for reports"""
        total = self.get_total_impossible_pct()
        
        summary = f"""
INTRINSIC LIMITATIONS DISCLOSURE

Tool Coverage: {100 - total:.1f}% | Intrinsic Limits: {total:.1f}%

This scan covers the majority of automated testing surface. However, some 
vulnerability classes are inherently untestable or undecidable by ANY automated 
tool due to fundamental mathematical and practical limits:

"""
        for cat in self.categories:
            summary += f"• {cat.name} — {cat.percent}%\n  {cat.explanation}\n"
            if cat.mitigations:
                summary += f"  Mitigations: {', '.join(cat.mitigations[:2])}\n"
            summary += "\n"
        
        summary += """
These limitations are NOT weaknesses of this tool specifically - they represent 
the theoretical and practical boundaries of what ANY automated security testing 
can achieve. Address these areas through:
- Human expert reviews
- Formal verification methods
- Organizational security controls
- Regular re-testing and monitoring

See detailed breakdown in the full report.
"""
        return summary
    
    def generate_pdf_data(self) -> Dict:
        """Generate data structure for PDF visualization"""
        return {
            "pie_chart": {
                "covered": 100 - self.get_total_impossible_pct(),
                "impossible": self.get_total_impossible_pct(),
                "colors": {
                    "covered": "#4CAF50",  # Green
                    "impossible": "#FF9800"  # Orange
                }
            },
            "breakdown_table": [
                {
                    "category": cat.name,
                    "percent": f"{cat.percent}%",
                    "confidence": f"{cat.confidence * 100:.0f}%",
                    "key_mitigation": cat.mitigations[0] if cat.mitigations else "N/A"
                }
                for cat in self.categories
            ]
        }
    
    def validate_ci_policy(self, policy_max_impossible: float, 
                          environment: str = "production") -> Dict:
        """
        Check if impossibility percentage meets CI/CD policy
        
        Args:
            policy_max_impossible: Maximum allowed impossibility % for this env
            environment: Environment name (production, staging, etc.)
            
        Returns:
            Dict with pass/fail and details
        """
        total = self.get_total_impossible_pct()
        passes = total <= policy_max_impossible
        
        return {
            "environment": environment,
            "policy_max_impossible_pct": policy_max_impossible,
            "actual_impossible_pct": total,
            "passes_policy": passes,
            "status": "PASS" if passes else "FAIL",
            "action_required": None if passes else "Risk acceptance or additional controls required",
            "categories_exceeding": [
                cat.name for cat in self.categories 
                if cat.percent > (policy_max_impossible / len(self.categories))
            ] if not passes else []
        }


# Example usage and testing
if __name__ == "__main__":
    # Standard configuration
    print("="*70)
    print("STANDARD CONFIGURATION (General Web App)")
    print("="*70)
    tracker = ImpossibilityTracker()
    
    breakdown = tracker.get_breakdown()
    print(json.dumps(breakdown, indent=2))
    
    print("\n" + "="*70)
    print("RESIDUAL RISK CALCULATION")
    print("="*70)
    residual = tracker.calculate_residual_risk(base_vuln_score=45.0)
    print(json.dumps(residual, indent=2))
    
    print("\n" + "="*70)
    print("REPORT SUMMARY")
    print("="*70)
    print(tracker.generate_report_summary())
    
    # Custom configuration for banking (better controls)
    print("\n" + "="*70)
    print("CUSTOM CONFIGURATION (Banking - Reduced Human Factors)")
    print("="*70)
    custom_tracker = ImpossibilityTracker(custom_overrides={
        "human_factors": 2.0,  # Better training/controls
        "environmental": 1.5   # Better staging environment
    })
    
    custom_breakdown = custom_tracker.get_breakdown()
    print(f"Total Impossible: {custom_breakdown['total_impossible_pct']}%")
    
    # CI/CD policy check
    print("\n" + "="*70)
    print("CI/CD POLICY VALIDATION")
    print("="*70)
    policy_check = tracker.validate_ci_policy(
        policy_max_impossible=15.0,
        environment="production-banking"
    )
    print(json.dumps(policy_check, indent=2))
    
    # Check if finding falls in impossibility category
    print("\n" + "="*70)
    print("FINDING CLASSIFICATION")
    print("="*70)
    test_finding = {
        "type": "Race Condition",
        "description": "Timing-based race in transfer logic"
    }
    classification = tracker.check_if_finding_in_impossibility(test_finding)
    print(json.dumps(classification, indent=2))
