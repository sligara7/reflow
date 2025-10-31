#!/usr/bin/env python3
"""
Reflow Knowledge Gap Detection Validation Suite

Runs system_of_systems_graph_v2.py on purposefully flawed architectures
and validates that expected knowledge gaps are detected.

Usage:
    python3 tests/validate_knowledge_gap_detection.py
    python3 tests/validate_knowledge_gap_detection.py --test 01_orphaned_interface
    python3 tests/validate_knowledge_gap_detection.py --baseline
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

class bcolors:
    """Terminal colors for output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


class KnowledgeGapValidator:
    def __init__(self, reflow_root: Path):
        self.reflow_root = reflow_root
        self.tests_dir = reflow_root / "tests/fixtures/knowledge_gaps"
        self.tool_path = reflow_root / "tools/system_of_systems_graph_v2.py"
        self.results = []

    def discover_tests(self) -> List[Path]:
        """Discover all test cases"""
        test_dirs = sorted([d for d in self.tests_dir.iterdir() if d.is_dir()])
        return test_dirs

    def load_expected_gaps(self, test_dir: Path) -> Dict:
        """Load expected_gaps.json for a test case"""
        expected_file = test_dir / "expected_gaps.json"
        if not expected_file.exists():
            return None

        with open(expected_file, 'r') as f:
            return json.load(f)

    def run_analysis(self, test_dir: Path) -> Tuple[bool, Dict]:
        """Run system_of_systems_graph_v2.py on a test case"""
        index_file = test_dir / "specs/machine/service_arch_index.json"
        output_file = test_dir / "detected_gaps.json"

        if not index_file.exists():
            return False, {"error": f"Index file not found: {index_file}"}

        # Run tool
        cmd = [
            "python3",
            str(self.tool_path),
            str(index_file),
            "--detect-gaps",
            "--output",
            str(output_file)
        ]

        try:
            result = subprocess.run(
                cmd,
                cwd=str(test_dir),
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                return False, {"error": f"Tool failed: {result.stderr}"}

            # Load detected gaps
            if not output_file.exists():
                return False, {"error": "Output file not created"}

            with open(output_file, 'r') as f:
                detected = json.load(f)

            return True, detected

        except subprocess.TimeoutExpired:
            return False, {"error": "Tool execution timed out"}
        except Exception as e:
            return False, {"error": str(e)}

    def compare_gaps(self, expected: Dict, detected: Dict) -> Tuple[bool, List[str]]:
        """Compare expected vs detected gaps"""
        issues = []

        # Extract gaps from detected output
        detected_gaps = detected.get("knowledge_gaps", {})
        detected_summary = detected.get("knowledge_gaps_summary", {})

        expected_gaps = expected.get("expected_knowledge_gaps", {})
        expected_totals = expected.get("expected_totals", {})

        # Check total count
        expected_total = expected_totals.get("total_gaps", 0)
        detected_total = detected_summary.get("total_gaps", 0)

        if expected_total != detected_total:
            issues.append(f"Total gaps mismatch: expected {expected_total}, detected {detected_total}")

        # Check each gap type
        for gap_type in ["orphaned_interfaces", "unmet_dependencies", "implied_mediators",
                         "structural_holes", "unexplained_outputs", "missing_bidirectional"]:
            expected_count = len(expected_gaps.get(gap_type, []))
            detected_count = len(detected_gaps.get(gap_type, []))

            if expected_count != detected_count:
                issues.append(f"{gap_type}: expected {expected_count}, detected {detected_count}")

            # Check specific gaps
            expected_items = expected_gaps.get(gap_type, [])
            detected_items = detected_gaps.get(gap_type, [])

            for exp_item in expected_items:
                # Check if this specific gap was detected
                if gap_type == "orphaned_interfaces":
                    key = "interface_id"
                elif gap_type == "unmet_dependencies":
                    key = "interface_id"
                else:
                    key = "component"  # Generic fallback

                exp_id = exp_item.get(key)
                detected_ids = [d.get(key) for d in detected_items]

                if exp_id not in detected_ids:
                    issues.append(f"Missing expected {gap_type}: {exp_id}")

        passed = len(issues) == 0
        return passed, issues

    def run_test(self, test_dir: Path) -> Dict:
        """Run a single test case"""
        test_name = test_dir.name

        print(f"\n{bcolors.HEADER}{'='*70}{bcolors.ENDC}")
        print(f"{bcolors.HEADER}Running Test: {test_name}{bcolors.ENDC}")
        print(f"{bcolors.HEADER}{'='*70}{bcolors.ENDC}")

        # Load expected gaps
        expected = self.load_expected_gaps(test_dir)
        if expected is None:
            print(f"{bcolors.WARNING}⚠ No expected_gaps.json found - SKIPPED{bcolors.ENDC}")
            return {
                "test": test_name,
                "status": "skipped",
                "reason": "No expected_gaps.json"
            }

        print(f"\n{bcolors.OKBLUE}📋 Expected gaps:{bcolors.ENDC}")
        print(f"   Description: {expected.get('description', 'N/A')}")
        totals = expected.get('expected_totals', {}).get('by_type', {})
        for gap_type, count in totals.items():
            if count > 0:
                print(f"   - {gap_type}: {count}")

        # Run analysis
        print(f"\n{bcolors.OKBLUE}🔍 Running system_of_systems_graph_v2.py...{bcolors.ENDC}")
        success, detected = self.run_analysis(test_dir)

        if not success:
            print(f"{bcolors.FAIL}✗ FAILED: {detected.get('error', 'Unknown error')}{bcolors.ENDC}")
            return {
                "test": test_name,
                "status": "failed",
                "reason": detected.get('error', 'Unknown error')
            }

        # Compare results
        print(f"\n{bcolors.OKBLUE}⚖ Comparing expected vs detected gaps...{bcolors.ENDC}")
        passed, issues = self.compare_gaps(expected, detected)

        if passed:
            print(f"{bcolors.OKGREEN}✓ PASSED: All expected gaps detected correctly!{bcolors.ENDC}")
            return {
                "test": test_name,
                "status": "passed",
                "expected": expected,
                "detected": detected
            }
        else:
            print(f"{bcolors.FAIL}✗ FAILED: Gaps mismatch{bcolors.ENDC}")
            for issue in issues:
                print(f"   - {issue}")
            return {
                "test": test_name,
                "status": "failed",
                "issues": issues,
                "expected": expected,
                "detected": detected
            }

    def run_all_tests(self, filter_test: str = None) -> None:
        """Run all discovered tests"""
        tests = self.discover_tests()

        if filter_test:
            tests = [t for t in tests if t.name == filter_test]
            if not tests:
                print(f"{bcolors.FAIL}Test '{filter_test}' not found{bcolors.ENDC}")
                return

        print(f"\n{bcolors.BOLD}{bcolors.OKCYAN}")
        print("╔════════════════════════════════════════════════════════════════════╗")
        print("║    Reflow Knowledge Gap Detection Validation Suite                ║")
        print("╚════════════════════════════════════════════════════════════════════╝")
        print(f"{bcolors.ENDC}")

        print(f"\n{bcolors.OKBLUE}Discovered {len(tests)} test case(s):{bcolors.ENDC}")
        for test in tests:
            print(f"   - {test.name}")

        # Run tests
        for test_dir in tests:
            result = self.run_test(test_dir)
            self.results.append(result)

        # Summary
        self.print_summary()

    def print_summary(self) -> None:
        """Print test summary"""
        print(f"\n{bcolors.BOLD}{bcolors.OKCYAN}")
        print("╔════════════════════════════════════════════════════════════════════╗")
        print("║                       Test Summary                                 ║")
        print("╚════════════════════════════════════════════════════════════════════╝")
        print(f"{bcolors.ENDC}")

        passed = sum(1 for r in self.results if r['status'] == 'passed')
        failed = sum(1 for r in self.results if r['status'] == 'failed')
        skipped = sum(1 for r in self.results if r['status'] == 'skipped')
        total = len(self.results)

        print(f"\n{bcolors.OKBLUE}Results:{bcolors.ENDC}")
        print(f"   Total:   {total}")
        print(f"   {bcolors.OKGREEN}Passed:  {passed}{bcolors.ENDC}")
        print(f"   {bcolors.FAIL}Failed:  {failed}{bcolors.ENDC}")
        print(f"   {bcolors.WARNING}Skipped: {skipped}{bcolors.ENDC}")

        if total > 0:
            pass_rate = (passed / total) * 100
            print(f"\n   {bcolors.BOLD}Pass Rate: {pass_rate:.1f}%{bcolors.ENDC}")

        # Detailed results
        print(f"\n{bcolors.OKBLUE}Detailed Results:{bcolors.ENDC}")
        for result in self.results:
            status = result['status']
            test_name = result['test']

            if status == 'passed':
                print(f"   {bcolors.OKGREEN}✓{bcolors.ENDC} {test_name}")
            elif status == 'failed':
                print(f"   {bcolors.FAIL}✗{bcolors.ENDC} {test_name}")
                if 'issues' in result:
                    for issue in result['issues'][:3]:  # Show first 3 issues
                        print(f"      - {issue}")
            else:
                print(f"   {bcolors.WARNING}⊘{bcolors.ENDC} {test_name} (skipped)")

    def generate_baseline_report(self) -> None:
        """Generate baseline performance report"""
        report_file = self.tests_dir.parent / "baseline_report.json"

        baseline = {
            "generated": datetime.now().isoformat(),
            "reflow_version": "3.7.0",
            "total_tests": len(self.results),
            "passed": sum(1 for r in self.results if r['status'] == 'passed'),
            "failed": sum(1 for r in self.results if r['status'] == 'failed'),
            "skipped": sum(1 for r in self.results if r['status'] == 'skipped'),
            "pass_rate": (sum(1 for r in self.results if r['status'] == 'passed') / len(self.results) * 100) if self.results else 0,
            "results": self.results
        }

        with open(report_file, 'w') as f:
            json.dump(baseline, f, indent=2)

        print(f"\n{bcolors.OKGREEN}✓ Baseline report saved: {report_file}{bcolors.ENDC}")

        # Also create human-readable markdown
        md_file = self.tests_dir.parent / "BASELINE_REPORT.md"
        with open(md_file, 'w') as f:
            f.write(f"# Reflow Knowledge Gap Detection - Baseline Report\n\n")
            f.write(f"**Generated**: {baseline['generated']}\n")
            f.write(f"**Reflow Version**: {baseline['reflow_version']}\n\n")
            f.write(f"## Summary\n\n")
            f.write(f"- **Total Tests**: {baseline['total_tests']}\n")
            f.write(f"- **Passed**: {baseline['passed']}\n")
            f.write(f"- **Failed**: {baseline['failed']}\n")
            f.write(f"- **Skipped**: {baseline['skipped']}\n")
            f.write(f"- **Pass Rate**: {baseline['pass_rate']:.1f}%\n\n")
            f.write(f"## Test Results\n\n")

            for result in self.results:
                status_icon = "✓" if result['status'] == 'passed' else "✗" if result['status'] == 'failed' else "⊘"
                f.write(f"### {status_icon} {result['test']}\n\n")
                f.write(f"**Status**: {result['status'].upper()}\n\n")

                if result['status'] == 'passed' and 'expected' in result:
                    f.write(f"**Description**: {result['expected'].get('description', 'N/A')}\n\n")
                    totals = result['expected'].get('expected_totals', {}).get('by_type', {})
                    f.write(f"**Expected Gaps**:\n")
                    for gap_type, count in totals.items():
                        if count > 0:
                            f.write(f"- {gap_type}: {count}\n")
                    f.write(f"\n**Result**: All expected gaps detected correctly ✓\n\n")
                elif result['status'] == 'failed':
                    if 'issues' in result:
                        f.write(f"**Issues**:\n")
                        for issue in result['issues']:
                            f.write(f"- {issue}\n")
                    else:
                        f.write(f"**Error**: {result.get('reason', 'Unknown')}\n")
                    f.write(f"\n")
                else:
                    f.write(f"**Reason**: {result.get('reason', 'N/A')}\n\n")

        print(f"{bcolors.OKGREEN}✓ Markdown report saved: {md_file}{bcolors.ENDC}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Validate Reflow knowledge gap detection")
    parser.add_argument("--test", help="Run specific test case", default=None)
    parser.add_argument("--baseline", help="Generate baseline report", action="store_true")
    args = parser.parse_args()

    # Find reflow root
    reflow_root = Path(__file__).parent.parent

    validator = KnowledgeGapValidator(reflow_root)
    validator.run_all_tests(filter_test=args.test)

    if args.baseline:
        validator.generate_baseline_report()

    # Exit with appropriate code
    failed = sum(1 for r in validator.results if r['status'] == 'failed')
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
