#!/usr/bin/env python3
"""
Analyze Service Organization Strategy

Analyzes a system's functional architecture to recommend the optimal
service organization strategy: domain-based, workflow-based, or hybrid.

Analysis Factors:
1. Coordination Complexity - How much cross-service coordination is required?
2. Workflow Span - Do workflows span multiple domains?
3. Operation Types - CRUD-heavy vs workflow-heavy?
4. State Management - Distributed state requirements?

Recommendations:
- Domain-Based: Clear domains, low coordination, CRUD-heavy
- Workflow-Based: High coordination, cross-domain workflows, workflow-heavy
- Hybrid: Mix of both patterns

Usage:
    python3 analyze_service_organization.py /path/to/system_root/

Inputs:
    - specs/functional/functional_architecture.json (required)
    - specs/machine/service_arch/ (optional - for brownfield analysis)

Outputs:
    - Console output with analysis and recommendation
    - specs/machine/service_organization_strategy.json (choice recording)

Version: 3.18.0
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict, Counter
from datetime import datetime
import re

# Import secure path handling
from path_utils import sanitize_path, validate_system_root, PathSecurityError
from json_utils import safe_load_json, JSONValidationError


class ServiceOrganizationAnalyzer:
    """Analyze system and recommend service organization strategy"""

    # Keywords indicating coordination requirements
    COORDINATION_KEYWORDS = {
        'lock', 'coordinate', 'synchronize', 'queue', 'schedule',
        'orchestrate', 'coordinate', 'transaction', 'reserve', 'allocate',
        'claim', 'acquire', 'release', 'checkout', 'checkin'
    }

    # Keywords indicating CRUD operations
    CRUD_KEYWORDS = {
        'create', 'read', 'get', 'list', 'update', 'edit', 'modify',
        'delete', 'remove', 'find', 'search', 'query', 'fetch'
    }

    # Keywords indicating workflow operations
    WORKFLOW_KEYWORDS = {
        'submit', 'execute', 'process', 'run', 'start', 'complete',
        'workflow', 'pipeline', 'orchestrate', 'batch', 'job',
        'task', 'operation', 'procedure', 'sequence'
    }

    def __init__(self, system_root: str):
        """
        Initialize analyzer

        Args:
            system_root: Path to system root directory

        Raises:
            PathSecurityError: If system_root is invalid
        """
        self.system_root = validate_system_root(system_root)
        self.functional_arch: Optional[Dict] = None
        self.service_arch: Optional[Dict] = None
        self.analysis_results: Dict[str, Any] = {}

    def load_inputs(self):
        """Load functional architecture and optional service architecture"""
        print("Loading functional architecture...")

        # Load functional architecture (required)
        func_arch_path = self.system_root / "specs" / "functional" / "functional_architecture.json"
        if not func_arch_path.exists():
            func_arch_path = self.system_root / "specs" / "machine" / "functional_architecture.json"

        if not func_arch_path.exists():
            print(f"❌ Functional architecture not found")
            print(f"   Expected: {func_arch_path}")
            print(f"   Run functional analysis workflow first (01d-functional_analysis.json)")
            sys.exit(1)

        self.functional_arch = safe_load_json(func_arch_path)
        print(f"✅ Loaded functional architecture with {len(self.functional_arch.get('functions', []))} functions")

        # Load service architecture (optional - for brownfield)
        service_arch_path = self.system_root / "specs" / "machine" / "service_architecture.json"
        if service_arch_path.exists():
            self.service_arch = safe_load_json(service_arch_path)
            print(f"✅ Found existing service architecture (brownfield analysis)")

    def analyze_coordination_complexity(self) -> Tuple[str, Dict[str, Any]]:
        """
        Analyze coordination complexity based on function descriptions

        Returns:
            Tuple of (complexity_level, analysis_details)
            complexity_level: "LOW" | "MEDIUM" | "HIGH"
        """
        print("\n🔄 Analyzing coordination complexity...")

        coordination_functions = []
        total_functions = 0

        for func in self.functional_arch.get('functions', []):
            total_functions += 1
            func_name = func.get('name', '')
            func_desc = func.get('description', '').lower()

            # Check for coordination keywords
            coord_keywords_found = []
            for keyword in self.COORDINATION_KEYWORDS:
                if keyword in func_name.lower() or keyword in func_desc:
                    coord_keywords_found.append(keyword)

            if coord_keywords_found:
                coordination_functions.append({
                    'name': func_name,
                    'keywords': coord_keywords_found,
                    'description': func.get('description', '')
                })

        coordination_count = len(coordination_functions)
        coordination_ratio = coordination_count / max(total_functions, 1)

        # Determine complexity level
        if coordination_count < 2:
            level = "LOW"
        elif coordination_count < 5:
            level = "MEDIUM"
        else:
            level = "HIGH"

        details = {
            'level': level,
            'coordination_functions': coordination_count,
            'total_functions': total_functions,
            'ratio': coordination_ratio,
            'examples': coordination_functions[:5]  # Top 5 examples
        }

        print(f"  📊 Coordination functions: {coordination_count}/{total_functions} ({coordination_ratio:.1%})")
        print(f"  🎯 Complexity level: {level}")
        if coordination_functions:
            print(f"  📋 Examples:")
            for func in coordination_functions[:3]:
                print(f"     - {func['name']}: {', '.join(func['keywords'])}")

        return level, details

    def analyze_workflow_span(self) -> Tuple[str, Dict[str, Any]]:
        """
        Analyze whether workflows span multiple domains

        Returns:
            Tuple of (span_type, analysis_details)
            span_type: "SINGLE_DOMAIN" | "CROSS_DOMAIN"
        """
        print("\n🌐 Analyzing workflow span...")

        # Extract flows from functional architecture
        flows = self.functional_arch.get('functional_flows', [])
        if not flows:
            print("  ⚠️  No functional flows defined - assuming SINGLE_DOMAIN")
            return "SINGLE_DOMAIN", {'flows': 0, 'cross_domain': 0}

        # Map functions to domains (if we can infer from naming/grouping)
        function_domains = self._infer_function_domains()

        cross_domain_flows = []
        for flow in flows:
            flow_name = flow.get('name', 'unknown')
            sequence = flow.get('sequence', [])

            if len(sequence) < 2:
                continue

            # Check if flow crosses domain boundaries
            domains_in_flow = set()
            for step in sequence:
                func_name = step if isinstance(step, str) else step.get('function', '')
                domain = function_domains.get(func_name, 'unknown')
                domains_in_flow.add(domain)

            if len(domains_in_flow) > 1:
                cross_domain_flows.append({
                    'name': flow_name,
                    'domains': list(domains_in_flow),
                    'steps': len(sequence)
                })

        cross_domain_ratio = len(cross_domain_flows) / max(len(flows), 1)

        # Determine span type
        if cross_domain_ratio < 0.3:
            span_type = "SINGLE_DOMAIN"
        else:
            span_type = "CROSS_DOMAIN"

        details = {
            'span_type': span_type,
            'total_flows': len(flows),
            'cross_domain_flows': len(cross_domain_flows),
            'ratio': cross_domain_ratio,
            'examples': cross_domain_flows[:5]
        }

        print(f"  📊 Cross-domain flows: {len(cross_domain_flows)}/{len(flows)} ({cross_domain_ratio:.1%})")
        print(f"  🎯 Span type: {span_type}")
        if cross_domain_flows:
            print(f"  📋 Examples:")
            for flow in cross_domain_flows[:3]:
                print(f"     - {flow['name']}: spans {len(flow['domains'])} domains")

        return span_type, details

    def _infer_function_domains(self) -> Dict[str, str]:
        """
        Infer domain for each function based on naming patterns

        Returns:
            Dict mapping function_name -> domain_name
        """
        function_domains = {}

        for func in self.functional_arch.get('functions', []):
            func_name = func.get('name', '')

            # Try to infer domain from function name
            # Common patterns: UserManagement.CreateUser, Device.CommandDevice
            if '.' in func_name:
                domain = func_name.split('.')[0]
            # Or from prefixes: CreateUser -> User, ProcessPayment -> Payment
            else:
                # Extract likely domain name from function name
                # Look for capitalized words
                words = re.findall(r'[A-Z][a-z]*', func_name)
                if len(words) >= 2:
                    # Last word is often the domain: CreateUser -> User
                    domain = words[-1]
                else:
                    domain = 'General'

            function_domains[func_name] = domain

        # Print domain distribution
        domain_counts = Counter(function_domains.values())
        print(f"  📂 Identified {len(domain_counts)} potential domains:")
        for domain, count in domain_counts.most_common(5):
            print(f"     - {domain}: {count} functions")

        return function_domains

    def analyze_operation_types(self) -> Tuple[str, Dict[str, Any]]:
        """
        Analyze operation types: CRUD vs Workflow

        Returns:
            Tuple of (operation_type, analysis_details)
            operation_type: "CRUD_HEAVY" | "WORKFLOW_HEAVY" | "BALANCED"
        """
        print("\n⚙️  Analyzing operation types...")

        crud_operations = []
        workflow_operations = []
        other_operations = []

        for func in self.functional_arch.get('functions', []):
            func_name = func.get('name', '').lower()
            func_desc = func.get('description', '').lower()

            # Check for CRUD keywords
            crud_found = any(keyword in func_name or keyword in func_desc
                           for keyword in self.CRUD_KEYWORDS)

            # Check for workflow keywords
            workflow_found = any(keyword in func_name or keyword in func_desc
                               for keyword in self.WORKFLOW_KEYWORDS)

            if crud_found and not workflow_found:
                crud_operations.append(func.get('name', ''))
            elif workflow_found:
                workflow_operations.append(func.get('name', ''))
            else:
                other_operations.append(func.get('name', ''))

        total = len(crud_operations) + len(workflow_operations) + len(other_operations)
        crud_ratio = len(crud_operations) / max(total, 1)
        workflow_ratio = len(workflow_operations) / max(total, 1)

        # Determine operation type
        if crud_ratio > 0.6:
            op_type = "CRUD_HEAVY"
        elif workflow_ratio > 0.6:
            op_type = "WORKFLOW_HEAVY"
        else:
            op_type = "BALANCED"

        details = {
            'type': op_type,
            'crud_operations': len(crud_operations),
            'workflow_operations': len(workflow_operations),
            'other_operations': len(other_operations),
            'crud_ratio': crud_ratio,
            'workflow_ratio': workflow_ratio
        }

        print(f"  📊 CRUD operations: {len(crud_operations)}/{total} ({crud_ratio:.1%})")
        print(f"  📊 Workflow operations: {len(workflow_operations)}/{total} ({workflow_ratio:.1%})")
        print(f"  🎯 Operation type: {op_type}")

        return op_type, details

    def generate_recommendation(
        self,
        coordination_level: str,
        span_type: str,
        operation_type: str
    ) -> Tuple[str, str]:
        """
        Generate service organization recommendation

        Args:
            coordination_level: "LOW" | "MEDIUM" | "HIGH"
            span_type: "SINGLE_DOMAIN" | "CROSS_DOMAIN"
            operation_type: "CRUD_HEAVY" | "WORKFLOW_HEAVY" | "BALANCED"

        Returns:
            Tuple of (recommendation, rationale)
            recommendation: "DOMAIN_BASED" | "WORKFLOW_BASED" | "HYBRID"
        """
        print("\n💡 Generating recommendation...")

        # Decision matrix
        score_workflow = 0
        score_domain = 0

        # Factor 1: Coordination complexity
        if coordination_level == "HIGH":
            score_workflow += 2
        elif coordination_level == "MEDIUM":
            score_workflow += 1
            score_domain += 1
        else:  # LOW
            score_domain += 2

        # Factor 2: Workflow span
        if span_type == "CROSS_DOMAIN":
            score_workflow += 2
        else:  # SINGLE_DOMAIN
            score_domain += 2

        # Factor 3: Operation types
        if operation_type == "WORKFLOW_HEAVY":
            score_workflow += 2
        elif operation_type == "CRUD_HEAVY":
            score_domain += 2
        else:  # BALANCED
            score_workflow += 1
            score_domain += 1

        # Determine recommendation
        if score_workflow > score_domain + 1:
            recommendation = "WORKFLOW_BASED"
            rationale = f"Workflow-based organization recommended due to:"
            reasons = []
            if coordination_level == "HIGH":
                reasons.append(f"HIGH coordination complexity ({coordination_level})")
            if span_type == "CROSS_DOMAIN":
                reasons.append("workflows span multiple domains")
            if operation_type == "WORKFLOW_HEAVY":
                reasons.append("system is workflow-heavy, not CRUD-heavy")
            rationale += "\n" + "\n".join(f"  - {r}" for r in reasons)

        elif score_domain > score_workflow + 1:
            recommendation = "DOMAIN_BASED"
            rationale = f"Domain-based organization recommended due to:"
            reasons = []
            if coordination_level == "LOW":
                reasons.append(f"LOW coordination complexity ({coordination_level})")
            if span_type == "SINGLE_DOMAIN":
                reasons.append("workflows stay within single domains")
            if operation_type == "CRUD_HEAVY":
                reasons.append("system is CRUD-heavy with simple operations")
            rationale += "\n" + "\n".join(f"  - {r}" for r in reasons)

        else:
            recommendation = "HYBRID"
            rationale = f"Hybrid organization recommended due to mixed characteristics:\n"
            rationale += f"  - Coordination: {coordination_level}\n"
            rationale += f"  - Workflow span: {span_type}\n"
            rationale += f"  - Operation type: {operation_type}\n"
            rationale += "Consider workflow services for complex coordination and domain services for shared capabilities."

        print(f"  🎯 Recommendation: {recommendation}")
        print(f"  📝 Rationale:\n{rationale}")

        return recommendation, rationale

    def present_choice_to_user(self, recommendation: str, rationale: str):
        """
        Present choice to user (this would integrate with LLM workflow)

        Args:
            recommendation: Recommended strategy
            rationale: Reasoning for recommendation
        """
        print("\n" + "=" * 70)
        print("SERVICE ORGANIZATION STRATEGY CHOICE")
        print("=" * 70)

        print(f"\n📊 ANALYSIS SUMMARY:")
        print(f"\n1. Coordination Complexity: {self.analysis_results['coordination']['level']}")
        print(f"   {self.analysis_results['coordination']['coordination_functions']} functions require coordination")

        print(f"\n2. Workflow Span: {self.analysis_results['span']['span_type']}")
        print(f"   {self.analysis_results['span']['cross_domain_flows']} of {self.analysis_results['span']['total_flows']} flows span multiple domains")

        print(f"\n3. Operation Types: {self.analysis_results['operations']['type']}")
        print(f"   CRUD: {self.analysis_results['operations']['crud_ratio']:.0%}, Workflows: {self.analysis_results['operations']['workflow_ratio']:.0%}")

        print(f"\n💡 RECOMMENDATION: {recommendation}")
        print(f"\n{rationale}")

        print("\n" + "=" * 70)
        print("ORGANIZATION STRATEGY OPTIONS")
        print("=" * 70)

        print(f"\n1. Domain-Based Organization")
        print(f"   Services: Organized by business domain/capability")
        print(f"   Example: UserService, ProductService, OrderService")
        print(f"   Best for: Clear domains, low coordination, CRUD operations")
        print(f"   Pros: Aligns with business domains, clear ownership")
        print(f"   Cons: Cross-domain coordination becomes distributed state")

        print(f"\n2. Workflow-Based Organization {'⭐ RECOMMENDED' if recommendation == 'WORKFLOW_BASED' else ''}")
        print(f"   Services: Organized by user workflows/operations")
        print(f"   Example: CheckoutWorkflowService, InventoryManagementService")
        print(f"   Best for: High coordination, cross-domain workflows")
        print(f"   Pros: Coordination is local, workflows self-contained")
        print(f"   Cons: May duplicate some domain logic")

        print(f"\n3. Hybrid (Domain + Workflow) {'⭐ RECOMMENDED' if recommendation == 'HYBRID' else ''}")
        print(f"   Workflow Services: Complex coordination operations")
        print(f"   Domain Services: Shared capabilities")
        print(f"   Best for: Large systems with both workflows and domains")
        print(f"   Pros: Best of both strategies")
        print(f"   Cons: More complex to design initially")

        print("\n" + "=" * 70)

    def save_analysis_results(self, recommendation: str, rationale: str):
        """Save analysis results to JSON file"""
        output_path = self.system_root / "specs" / "machine" / "service_organization_analysis.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        output_data = {
            "analysis_date": datetime.now().isoformat(),
            "recommendation": recommendation,
            "rationale": rationale,
            "analysis_results": self.analysis_results,
            "user_choice": None,  # Filled in by workflow after user selects
            "user_choice_rationale": None
        }

        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)

        print(f"\n✅ Analysis saved to: {output_path}")

    def run(self):
        """Run the analysis process"""
        try:
            self.load_inputs()

            # Run analyses
            coordination_level, coord_details = self.analyze_coordination_complexity()
            span_type, span_details = self.analyze_workflow_span()
            operation_type, op_details = self.analyze_operation_types()

            # Store results
            self.analysis_results = {
                'coordination': coord_details,
                'span': span_details,
                'operations': op_details
            }

            # Generate recommendation
            recommendation, rationale = self.generate_recommendation(
                coordination_level,
                span_type,
                operation_type
            )

            # Present choice
            self.present_choice_to_user(recommendation, rationale)

            # Save results
            self.save_analysis_results(recommendation, rationale)

            print("\n✅ Service organization analysis complete!")
            print("\n⚠️  NEXT STEP: LLM should present these options to the user and record choice in service_organization_strategy.json")

        except Exception as e:
            print(f"\n❌ Error during analysis: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


def main():
    """Main entry point"""
    if len(sys.argv) != 2:
        print("Usage: python3 analyze_service_organization.py /path/to/system_root/")
        sys.exit(1)

    system_root = sys.argv[1]
    analyzer = ServiceOrganizationAnalyzer(system_root)
    analyzer.run()


if __name__ == "__main__":
    main()
