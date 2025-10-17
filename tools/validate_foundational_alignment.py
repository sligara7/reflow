#!/usr/bin/env python3
"""
Foundational Alignment Validation Tool

Ensures that any new features, services, or changes align with the system's 
foundational documents and architectural principles before allowing workflow progression.

This tool enforces the "black box" architecture principle where:
1. Each service encapsulates internal functions 
2. Services interact only through well-defined interfaces
3. Changes maintain consistency with foundational mission and constraints
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple
import re


class FoundationalValidator:
    def __init__(self, system_path: str):
        self.system_path = Path(system_path)
        self.validation_results = {
            "timestamp": "",
            "system": self.system_path.name,
            "foundational_alignment": {
                "mission_alignment": {"status": "not_checked", "issues": []},
                "user_scenario_coverage": {"status": "not_checked", "issues": []},
                "success_criteria_impact": {"status": "not_checked", "issues": []},
                "architectural_consistency": {"status": "not_checked", "issues": []},
                "black_box_integrity": {"status": "not_checked", "issues": []},
            },
            "overall_status": "pending",
            "blocking_issues": [],
            "recommendations": [],
        }

    def validate_mission_alignment(self, change_proposal: Dict[str, Any]) -> bool:
        """Validate that proposed changes align with system mission."""
        mission_file = self.system_path / "SYSTEM_MISSION_STATEMENT.md"

        if not mission_file.exists():
            self.validation_results["foundational_alignment"]["mission_alignment"][
                "issues"
            ].append(
                {
                    "type": "missing_foundational_document",
                    "severity": "critical",
                    "description": "SYSTEM_MISSION_STATEMENT.md not found",
                    "recommendation": "Create mission statement before proceeding with changes",
                }
            )
            return False

        # Parse mission statement to extract key mission elements
        mission_content = mission_file.read_text()
        mission_keywords = self._extract_mission_keywords(mission_content)

        # Check if change proposal aligns with mission keywords
        proposal_text = str(change_proposal)
        alignment_score = self._calculate_alignment_score(
            mission_keywords, proposal_text
        )

        if alignment_score < 0.3:  # Threshold for mission alignment
            self.validation_results["foundational_alignment"]["mission_alignment"][
                "issues"
            ].append(
                {
                    "type": "mission_misalignment",
                    "severity": "high",
                    "description": f"Proposed changes show low alignment with system mission (score: {alignment_score:.2f})",
                    "recommendation": "Revise proposal to better align with system mission or update mission statement if scope has legitimately expanded",
                }
            )
            return False

        self.validation_results["foundational_alignment"]["mission_alignment"][
            "status"
        ] = "pass"
        return True

    def validate_black_box_integrity(self, affected_services: List[str]) -> bool:
        """Validate that changes maintain black box architecture principles."""
        integrity_violations = []

        for service_id in affected_services:
            service_arch_file = (
                self.system_path
                / "specs"
                / "machine"
                / "service_arch"
                / service_id
                / "service_architecture.json"
            )

            if not service_arch_file.exists():
                integrity_violations.append(
                    {
                        "service": service_id,
                        "type": "missing_service_architecture",
                        "severity": "critical",
                        "description": f"Service {service_id} lacks service_architecture.json",
                        "recommendation": f"Create service_architecture.json for {service_id} using template",
                    }
                )
                continue

            # Load service architecture
            with open(service_arch_file) as f:
                service_arch = json.load(f)

            # Check black box principles
            self._validate_interface_encapsulation(
                service_arch, service_id, integrity_violations
            )
            self._validate_internal_function_privacy(
                service_arch, service_id, integrity_violations
            )
            self._validate_dependency_clarity(
                service_arch, service_id, integrity_violations
            )

        if integrity_violations:
            self.validation_results["foundational_alignment"]["black_box_integrity"][
                "issues"
            ] = integrity_violations
            self.validation_results["foundational_alignment"]["black_box_integrity"][
                "status"
            ] = "fail"
            return False

        self.validation_results["foundational_alignment"]["black_box_integrity"][
            "status"
        ] = "pass"
        return True

    def validate_architectural_consistency(self) -> bool:
        """Validate consistency with architectural_definitions.json."""
        arch_def_file = (
            self.system_path.parent.parent
            / "definitions"
            / "architectural_definitions.json"
        )

        if not arch_def_file.exists():
            self.validation_results["foundational_alignment"][
                "architectural_consistency"
            ]["issues"].append(
                {
                    "type": "missing_architectural_definitions",
                    "severity": "critical",
                    "description": "architectural_definitions.json not found",
                    "recommendation": "Ensure architectural_definitions.json exists before validation",
                }
            )
            return False

        # Load architectural definitions
        with open(arch_def_file) as f:
            arch_defs = json.load(f)

        # Validate UAF compliance
        uaf_compliance = self._check_uaf_compliance(arch_defs)
        if not uaf_compliance:
            return False

        self.validation_results["foundational_alignment"]["architectural_consistency"][
            "status"
        ] = "pass"
        return True

    def generate_validation_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report."""
        # Determine overall status
        all_checks = self.validation_results["foundational_alignment"]
        critical_failures = []

        for check_name, check_result in all_checks.items():
            if check_result["status"] == "fail":
                critical_issues = [
                    issue
                    for issue in check_result["issues"]
                    if issue.get("severity") == "critical"
                ]
                critical_failures.extend(critical_issues)

        if critical_failures:
            self.validation_results["overall_status"] = "blocked"
            self.validation_results["blocking_issues"] = critical_failures
        elif any(check["status"] == "fail" for check in all_checks.values()):
            self.validation_results["overall_status"] = "conditional"
        else:
            self.validation_results["overall_status"] = "pass"

        # Generate recommendations
        self._generate_recommendations()

        return self.validation_results

    def _extract_mission_keywords(self, mission_text: str) -> List[str]:
        """Extract key terms from mission statement."""
        # Remove markdown formatting and extract meaningful terms
        clean_text = re.sub(r"[#*\-_]", "", mission_text)
        words = re.findall(r"\b[a-zA-Z]{4,}\b", clean_text.lower())

        # Filter out common words and focus on domain-specific terms
        common_words = {
            "this",
            "that",
            "with",
            "from",
            "they",
            "have",
            "will",
            "been",
            "were",
            "said",
            "each",
            "which",
            "their",
            "time",
            "would",
            "there",
            "could",
            "other",
        }
        meaningful_words = [
            word for word in words if word not in common_words and len(word) > 3
        ]

        return list(set(meaningful_words))  # Remove duplicates

    def _calculate_alignment_score(
        self, mission_keywords: List[str], proposal_text: str
    ) -> float:
        """Calculate alignment score between mission and proposal."""
        if not mission_keywords:
            return 1.0  # Assume alignment if no mission keywords found

        proposal_lower = proposal_text.lower()
        matches = sum(1 for keyword in mission_keywords if keyword in proposal_lower)

        return matches / len(mission_keywords)

    def _validate_interface_encapsulation(
        self, service_arch: Dict, service_id: str, violations: List
    ):
        """Validate that service properly encapsulates through interfaces."""
        interfaces = service_arch.get("interfaces", [])

        # Check that all external communication goes through declared interfaces
        for interface in interfaces:
            if interface.get("dependency_type") == "external":
                if not interface.get("path") and not interface.get("description"):
                    violations.append(
                        {
                            "service": service_id,
                            "type": "incomplete_interface_specification",
                            "severity": "high",
                            "description": f"External interface '{interface.get('name')}' lacks proper specification",
                            "recommendation": "Add complete path and description for external interfaces",
                        }
                    )

    def _validate_internal_function_privacy(
        self, service_arch: Dict, service_id: str, violations: List
    ):
        """Validate that internal functions are not exposed externally."""
        # This would require more sophisticated analysis of actual implementation
        # For now, we check that component_classification is correct
        component_type = service_arch.get("component_classification")

        if component_type == "function" and service_arch.get("interfaces"):
            # Functions should not have external interfaces
            external_interfaces = [
                iface
                for iface in service_arch["interfaces"]
                if iface.get("dependency_type") == "external"
            ]
            if external_interfaces:
                violations.append(
                    {
                        "service": service_id,
                        "type": "function_exposure_violation",
                        "severity": "high",
                        "description": f"Internal function {service_id} has external interfaces",
                        "recommendation": "Functions should not expose external interfaces; wrap in service layer",
                    }
                )

    def _validate_dependency_clarity(
        self, service_arch: Dict, service_id: str, violations: List
    ):
        """Validate that dependencies are clearly defined."""
        dependencies = service_arch.get("dependencies", [])
        interfaces = service_arch.get("interfaces", [])

        # Check that all dependencies have corresponding interface definitions
        dependency_interfaces = [
            iface
            for iface in interfaces
            if iface.get("dependency_type") in ["direct", "indirect"]
        ]

        if len(dependencies) != len(dependency_interfaces):
            violations.append(
                {
                    "service": service_id,
                    "type": "dependency_interface_mismatch",
                    "severity": "medium",
                    "description": f"Service has {len(dependencies)} dependencies but {len(dependency_interfaces)} dependency interfaces",
                    "recommendation": "Ensure each dependency has corresponding interface definition",
                }
            )

    def _check_uaf_compliance(self, arch_defs: Dict) -> bool:
        """Check compliance with UAF definitions."""
        required_sections = [
            "core_concepts",
            "hierarchy_levels",
            "implementation_status",
        ]

        for section in required_sections:
            if section not in arch_defs:
                self.validation_results["foundational_alignment"][
                    "architectural_consistency"
                ]["issues"].append(
                    {
                        "type": "uaf_compliance_failure",
                        "severity": "high",
                        "description": f"Missing {section} in architectural_definitions.json",
                        "recommendation": f"Add {section} section to architectural_definitions.json",
                    }
                )
                return False

        return True

    def _generate_recommendations(self):
        """Generate actionable recommendations based on validation results."""
        recommendations = []

        # Check for critical blocking issues
        if self.validation_results["overall_status"] == "blocked":
            recommendations.append(
                "CRITICAL: Address all blocking issues before proceeding with any workflow steps"
            )

        # Specific recommendations based on failure types
        all_issues = []
        for check_result in self.validation_results["foundational_alignment"].values():
            all_issues.extend(check_result.get("issues", []))

        issue_types = set(issue["type"] for issue in all_issues)

        if "missing_foundational_document" in issue_types:
            recommendations.append(
                "1. Create all missing foundational documents (SYSTEM_MISSION_STATEMENT.md, USER_SCENARIOS.md, SUCCESS_CRITERIA.md)"
            )
            recommendations.append(
                "2. Run full architecture workflow (Arch-01 through Arch-06) to establish proper foundation"
            )

        if "mission_misalignment" in issue_types:
            recommendations.append(
                "3. Either revise change proposal to align with mission OR update mission statement if legitimate scope expansion"
            )

        if any("black_box" in issue_type for issue_type in issue_types):
            recommendations.append(
                "4. Review and correct service architecture to maintain black box principles"
            )
            recommendations.append(
                "5. Ensure all external communication goes through well-defined interfaces"
            )

        self.validation_results["recommendations"] = recommendations


def main():
    if len(sys.argv) < 2:
        print(
            "Usage: python3 validate_foundational_alignment.py <system_path> [--change-proposal <path>]"
        )
        sys.exit(1)

    system_path = sys.argv[1]
    change_proposal_path = None

    # Parse optional change proposal argument
    if "--change-proposal" in sys.argv:
        idx = sys.argv.index("--change-proposal")
        if idx + 1 < len(sys.argv):
            change_proposal_path = sys.argv[idx + 1]

    validator = FoundationalValidator(system_path)

    # Load change proposal if provided
    change_proposal = {}
    if change_proposal_path and os.path.exists(change_proposal_path):
        with open(change_proposal_path) as f:
            if change_proposal_path.endswith(".json"):
                change_proposal = json.load(f)
            else:
                change_proposal = {"content": f.read()}

    # Run validation checks
    validator.validate_mission_alignment(change_proposal)
    validator.validate_architectural_consistency()

    # If change affects services, validate black box integrity
    affected_services = change_proposal.get("affected_services", [])
    if affected_services:
        validator.validate_black_box_integrity(affected_services)

    # Generate report
    report = validator.generate_validation_report()

    # Output results
    print(json.dumps(report, indent=2))

    # Exit with appropriate code
    if report["overall_status"] == "blocked":
        sys.exit(1)
    elif report["overall_status"] == "conditional":
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
