#!/usr/bin/env python3
"""
Reflow Test Validator - Compares actual vs expected outputs

Purpose: Validate workflow outputs by comparing actual generated artifacts
         against pre-defined expected outputs (ground truth).

Usage:
    python3 test_validator.py --test-case microservices_basic --strict
    python3 test_validator.py --test-case all --output validation_report.json

Created: 2025-11-18 (v3.16.0 - Reflow Testing Framework)
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any
import argparse
import difflib


class ReflowTestValidator:
    """Validates Reflow workflow outputs against expected results."""

    def __init__(self, tests_root: str):
        self.tests_root = Path(tests_root)
        self.test_systems_dir = self.tests_root / "test_systems"

    def load_json(self, file_path: Path) -> Dict:
        """Load JSON file."""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            raise ValueError(f"Failed to load {file_path}: {e}")

    def compare_json_files(
        self,
        expected_path: Path,
        actual_path: Path,
        strict: bool = False
    ) -> Dict:
        """
        Compare two JSON files.

        Args:
            expected_path: Path to expected output
            actual_path: Path to actual output
            strict: If True, require exact match. If False, allow minor differences.

        Returns:
            Dict with comparison results
        """
        result = {
            "file": expected_path.name,
            "match": False,
            "differences": [],
            "similarity_score": 0.0,
            "error": None
        }

        # Check if both files exist
        if not expected_path.exists():
            result["error"] = f"Expected file not found: {expected_path}"
            return result

        if not actual_path.exists():
            result["error"] = f"Actual file not found: {actual_path}"
            return result

        try:
            expected_data = self.load_json(expected_path)
            actual_data = self.load_json(actual_path)

            # Deep comparison
            differences = self._deep_compare(expected_data, actual_data, path="root")

            if not differences:
                result["match"] = True
                result["similarity_score"] = 1.0
            else:
                result["differences"] = differences
                result["similarity_score"] = self._calculate_similarity(
                    expected_data,
                    actual_data,
                    differences
                )
                result["match"] = not strict and result["similarity_score"] >= 0.95

        except Exception as e:
            result["error"] = str(e)

        return result

    def _deep_compare(
        self,
        expected: Any,
        actual: Any,
        path: str = "root"
    ) -> List[str]:
        """
        Recursively compare two data structures.

        Returns:
            List of difference descriptions
        """
        differences = []

        # Type mismatch
        if type(expected) != type(actual):
            differences.append(
                f"{path}: Type mismatch (expected {type(expected).__name__}, "
                f"got {type(actual).__name__})"
            )
            return differences

        # Dict comparison
        if isinstance(expected, dict):
            all_keys = set(expected.keys()) | set(actual.keys())

            for key in all_keys:
                key_path = f"{path}.{key}"

                if key not in expected:
                    differences.append(f"{key_path}: Extra key in actual")
                elif key not in actual:
                    differences.append(f"{key_path}: Missing key in actual")
                else:
                    differences.extend(
                        self._deep_compare(expected[key], actual[key], key_path)
                    )

        # List comparison
        elif isinstance(expected, list):
            if len(expected) != len(actual):
                differences.append(
                    f"{path}: Length mismatch (expected {len(expected)}, "
                    f"got {len(actual)})"
                )

            # Compare elements
            for i in range(min(len(expected), len(actual))):
                differences.extend(
                    self._deep_compare(
                        expected[i],
                        actual[i],
                        f"{path}[{i}]"
                    )
                )

        # Primitive comparison
        else:
            if expected != actual:
                differences.append(
                    f"{path}: Value mismatch (expected '{expected}', got '{actual}')"
                )

        return differences

    def _calculate_similarity(
        self,
        expected: Any,
        actual: Any,
        differences: List[str]
    ) -> float:
        """
        Calculate similarity score between expected and actual.

        Returns:
            Float between 0.0 (completely different) and 1.0 (identical)
        """
        # Convert to JSON strings for sequence matching
        expected_str = json.dumps(expected, sort_keys=True, indent=2)
        actual_str = json.dumps(actual, sort_keys=True, indent=2)

        # Use difflib sequence matcher
        matcher = difflib.SequenceMatcher(None, expected_str, actual_str)
        return matcher.ratio()

    def validate_test_case(
        self,
        test_case: str,
        strict: bool = False
    ) -> Dict:
        """
        Validate all outputs for a test case.

        Args:
            test_case: Test case name
            strict: Require exact matches

        Returns:
            Validation results for test case
        """
        test_path = self.test_systems_dir / test_case
        expected_dir = test_path / "expected_outputs"
        actual_dir = test_path / "actual_outputs"

        result = {
            "test_case": test_case,
            "timestamp": datetime.utcnow().isoformat(),
            "strict_mode": strict,
            "file_comparisons": [],
            "overall_pass": False,
            "errors": []
        }

        if not expected_dir.exists():
            result["errors"].append(f"Expected outputs directory not found: {expected_dir}")
            return result

        if not actual_dir.exists():
            result["errors"].append(f"Actual outputs directory not found: {actual_dir}")
            return result

        # Get all expected output files
        expected_files = list(expected_dir.glob("*.json"))

        if not expected_files:
            result["errors"].append("No expected output files found")
            return result

        # Compare each expected file with actual
        all_passed = True
        for expected_file in expected_files:
            actual_file = actual_dir / expected_file.name

            comparison = self.compare_json_files(expected_file, actual_file, strict)
            result["file_comparisons"].append(comparison)

            if not comparison["match"]:
                all_passed = False

        result["overall_pass"] = all_passed and not result["errors"]

        return result

    def validate_test_suite(
        self,
        test_cases: List[str],
        strict: bool = False
    ) -> Dict:
        """
        Validate multiple test cases.

        Args:
            test_cases: List of test case names
            strict: Require exact matches

        Returns:
            Validation results for entire suite
        """
        if test_cases == ["all"]:
            test_cases = [
                d.name for d in self.test_systems_dir.iterdir()
                if d.is_dir() and not d.name.startswith('.')
            ]

        suite_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "strict_mode": strict,
            "test_cases": test_cases,
            "results": [],
            "summary": {
                "total": len(test_cases),
                "passed": 0,
                "failed": 0
            }
        }

        for test_case in test_cases:
            print(f"\nValidating test case: {test_case}")
            result = self.validate_test_case(test_case, strict)
            suite_results["results"].append(result)

            if result["overall_pass"]:
                suite_results["summary"]["passed"] += 1
                print(f"  ✅ PASS")
            else:
                suite_results["summary"]["failed"] += 1
                print(f"  ❌ FAIL")

        return suite_results

    def save_validation_report(self, results: Dict, output_file: str):
        """Save validation report to JSON file."""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\nValidation report saved to: {output_path}")

    def print_validation_summary(self, results: Dict):
        """Print human-readable validation summary."""
        print("\n" + "=" * 70)
        print("VALIDATION SUMMARY")
        print("=" * 70)

        summary = results["summary"]
        print(f"Total Test Cases: {summary['total']}")
        print(f"Passed: {summary['passed']} ✅")
        print(f"Failed: {summary['failed']} ❌")
        print(f"Success Rate: {summary['passed'] / summary['total'] * 100:.1f}%")

        print("\nDetailed Results:")
        print("-" * 70)

        for test_result in results["results"]:
            test_case = test_result["test_case"]
            status = "✅ PASS" if test_result["overall_pass"] else "❌ FAIL"
            print(f"\n{test_case}: {status}")

            if test_result["errors"]:
                for error in test_result["errors"]:
                    print(f"  ERROR: {error}")

            for comparison in test_result["file_comparisons"]:
                file_name = comparison["file"]
                if comparison["error"]:
                    print(f"  {file_name}: ERROR - {comparison['error']}")
                elif comparison["match"]:
                    print(f"  {file_name}: ✅ MATCH (100%)")
                else:
                    score = comparison["similarity_score"] * 100
                    print(f"  {file_name}: ⚠️  MISMATCH ({score:.1f}% similar)")

                    if comparison["differences"] and len(comparison["differences"]) <= 10:
                        for diff in comparison["differences"][:5]:
                            print(f"    - {diff}")
                        if len(comparison["differences"]) > 5:
                            remaining = len(comparison["differences"]) - 5
                            print(f"    ... and {remaining} more differences")

        print("\n" + "=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Reflow Test Validator - Compare actual vs expected outputs"
    )
    parser.add_argument(
        "--test-case",
        type=str,
        required=True,
        help="Test case name or 'all' for all test cases"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Require exact matches (no tolerance for minor differences)"
    )
    parser.add_argument(
        "--tests-root",
        type=str,
        default="/home/user/reflow/tests",
        help="Path to tests directory"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="tests/validation_report.json",
        help="Output file for validation report"
    )

    args = parser.parse_args()

    # Initialize validator
    validator = ReflowTestValidator(args.tests_root)

    # Validate
    test_cases = [args.test_case] if args.test_case != "all" else ["all"]
    results = validator.validate_test_suite(test_cases, args.strict)

    # Save report
    validator.save_validation_report(results, args.output)

    # Print summary
    validator.print_validation_summary(results)

    # Exit with error code if any tests failed
    if results["summary"]["failed"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
