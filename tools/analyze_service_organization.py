#!/usr/bin/env python3
"""
Analyze Service Organization Strategy

Analyzes a system's functional architecture to recommend the optimal
service organization strategy: plugin-based modular, domain-based, workflow-based, or hybrid.

Analysis Factors:
1. Coordination Complexity - How much cross-service coordination is required?
2. Workflow Span - Do workflows span multiple domains?
3. Operation Types - CRUD-heavy vs workflow-heavy?
4. State Management - Distributed state requirements?
5. Extensibility Requirements - Does the system need runtime extensibility? (NEW v3.21.0)

Recommendations:
- Plugin-Based Modular: High extensibility, protocol-based interfaces, modular components (PREFERRED for modern systems)
- Domain-Based: Clear domains, low coordination, CRUD-heavy
- Workflow-Based: High coordination, cross-domain workflows, workflow-heavy
- Hybrid: Mix of patterns based on specific service needs

Usage:
    python3 analyze_service_organization.py /path/to/system_root/

Inputs:
    - specs/functional/functional_architecture.json (required)
    - specs/machine/service_arch/ (optional - for brownfield analysis)

Outputs:
    - Console output with analysis and recommendation
    - specs/machine/service_organization_strategy.json (choice recording)

Version: 4.1.1

Changelog v4.1.1:
- FIX: KeyError 'span_type' when no functional flows defined
- NEW: REAL_TIME operation type for games/emulators/simulations
- NEW: Real-time system detection via keywords
- FIX: Graceful handling of missing span data in presentation
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

    # Keywords indicating extensibility/plugin requirements (NEW v3.21.0)
    EXTENSIBILITY_KEYWORDS = {
        'plugin', 'extension', 'module', 'adapter', 'provider', 'handler',
        'strategy', 'factory', 'registry', 'loader', 'hook', 'callback',
        'injectable', 'configurable', 'customizable', 'extensible', 'pluggable',
        'interface', 'protocol', 'contract', 'abstraction', 'dynamic',
        'runtime', 'discover', 'register', 'unregister', 'swap', 'replace'
    }

    # Keywords indicating modular architecture needs
    MODULARITY_KEYWORDS = {
        'component', 'module', 'package', 'layer', 'boundary', 'isolation',
        'decouple', 'independent', 'standalone', 'reusable', 'composable',
        'interchangeable', 'hot-swap', 'lazy-load', 'on-demand'
    }

    # Keywords indicating real-time/frame-based systems (NEW v4.1.1)
    REAL_TIME_KEYWORDS = {
        'game_loop', 'main_loop', 'frame', 'render', 'update', 'tick',
        '60fps', 'fps', 'frame_rate', 'framerate', 'vsync', 'refresh',
        'emulator', 'emulation', 'simulation', 'real_time', 'realtime',
        'ppu', 'apu', 'cpu', 'gpu', 'controller', 'input_poll',
        'audio_callback', 'video_buffer', 'pixel', 'sprite', 'tile',
        'scanline', 'vblank', 'hblank', 'interrupt', 'cycle'
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
            span_type: "SINGLE_DOMAIN" | "CROSS_DOMAIN" | "NONE"
        """
        print("\n🌐 Analyzing workflow span...")

        # Extract flows from functional architecture
        flows = self.functional_arch.get('functional_flows', [])
        if not flows:
            # FIX v4.1.1: Return complete details dict to avoid KeyError
            print("  ⚠️  No functional flows defined - checking for real-time system indicators")
            is_realtime = self._detect_real_time_system()
            details = {
                'span_type': 'NONE',
                'total_flows': 0,
                'cross_domain_flows': 0,
                'ratio': 0.0,
                'examples': [],
                'is_real_time': is_realtime,
                'note': 'No workflow flows defined - system may be frame-based/real-time rather than workflow-based'
            }
            if is_realtime:
                print("  🎮 Real-time/frame-based system detected")
            return "NONE", details

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

    def _detect_real_time_system(self) -> bool:
        """
        Detect if this is a real-time/frame-based system (NEW v4.1.1)

        Returns:
            True if system appears to be real-time/frame-based
        """
        realtime_score = 0
        total_functions = 0

        for func in self.functional_arch.get('functions', []):
            total_functions += 1
            func_name = func.get('function_name', func.get('name', '')).lower()
            func_desc = func.get('description', '').lower()

            # Check for real-time keywords
            for keyword in self.REAL_TIME_KEYWORDS:
                if keyword in func_name or keyword in func_desc:
                    realtime_score += 1
                    break

        # Also check cluster names
        for cluster in self.functional_arch.get('functional_clusters', []):
            cluster_name = cluster.get('name', '').lower()
            cluster_desc = cluster.get('description', '').lower()

            for keyword in self.REAL_TIME_KEYWORDS:
                if keyword in cluster_name or keyword in cluster_desc:
                    realtime_score += 2
                    break

        # If significant portion of functions are real-time related
        ratio = realtime_score / max(total_functions, 1)
        return ratio > 0.15 or realtime_score >= 5

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
        Analyze operation types: CRUD vs Workflow vs Real-Time (NEW v4.1.1)

        Returns:
            Tuple of (operation_type, analysis_details)
            operation_type: "CRUD_HEAVY" | "WORKFLOW_HEAVY" | "REAL_TIME" | "BALANCED"
        """
        print("\n⚙️  Analyzing operation types...")

        crud_operations = []
        workflow_operations = []
        realtime_operations = []  # NEW v4.1.1
        other_operations = []

        for func in self.functional_arch.get('functions', []):
            func_name = func.get('function_name', func.get('name', '')).lower()
            func_desc = func.get('description', '').lower()

            # Check for CRUD keywords
            crud_found = any(keyword in func_name or keyword in func_desc
                           for keyword in self.CRUD_KEYWORDS)

            # Check for workflow keywords
            workflow_found = any(keyword in func_name or keyword in func_desc
                               for keyword in self.WORKFLOW_KEYWORDS)

            # Check for real-time keywords (NEW v4.1.1)
            realtime_found = any(keyword in func_name or keyword in func_desc
                               for keyword in self.REAL_TIME_KEYWORDS)

            if realtime_found:
                realtime_operations.append(func.get('function_name', func.get('name', '')))
            elif crud_found and not workflow_found:
                crud_operations.append(func.get('function_name', func.get('name', '')))
            elif workflow_found:
                workflow_operations.append(func.get('function_name', func.get('name', '')))
            else:
                other_operations.append(func.get('function_name', func.get('name', '')))

        total = len(crud_operations) + len(workflow_operations) + len(realtime_operations) + len(other_operations)
        crud_ratio = len(crud_operations) / max(total, 1)
        workflow_ratio = len(workflow_operations) / max(total, 1)
        realtime_ratio = len(realtime_operations) / max(total, 1)

        # Determine operation type (NEW v4.1.1: added REAL_TIME)
        if realtime_ratio > 0.3:
            op_type = "REAL_TIME"
        elif crud_ratio > 0.6:
            op_type = "CRUD_HEAVY"
        elif workflow_ratio > 0.6:
            op_type = "WORKFLOW_HEAVY"
        else:
            op_type = "BALANCED"

        details = {
            'type': op_type,
            'crud_operations': len(crud_operations),
            'workflow_operations': len(workflow_operations),
            'realtime_operations': len(realtime_operations),  # NEW v4.1.1
            'other_operations': len(other_operations),
            'crud_ratio': crud_ratio,
            'workflow_ratio': workflow_ratio,
            'realtime_ratio': realtime_ratio  # NEW v4.1.1
        }

        print(f"  📊 CRUD operations: {len(crud_operations)}/{total} ({crud_ratio:.1%})")
        print(f"  📊 Workflow operations: {len(workflow_operations)}/{total} ({workflow_ratio:.1%})")
        print(f"  📊 Real-time operations: {len(realtime_operations)}/{total} ({realtime_ratio:.1%})")
        print(f"  🎯 Operation type: {op_type}")

        return op_type, details

    def analyze_extensibility_requirements(self) -> Tuple[str, Dict[str, Any]]:
        """
        Analyze extensibility and modularity requirements (NEW v3.21.0)

        Returns:
            Tuple of (extensibility_level, analysis_details)
            extensibility_level: "LOW" | "MEDIUM" | "HIGH"
        """
        print("\n🔌 Analyzing extensibility requirements...")

        extensible_functions = []
        modular_functions = []
        total_functions = 0

        for func in self.functional_arch.get('functions', []):
            total_functions += 1
            func_name = func.get('name', '').lower()
            func_desc = func.get('description', '').lower()

            # Check for extensibility keywords
            ext_keywords_found = []
            for keyword in self.EXTENSIBILITY_KEYWORDS:
                if keyword in func_name or keyword in func_desc:
                    ext_keywords_found.append(keyword)

            if ext_keywords_found:
                extensible_functions.append({
                    'name': func.get('name', ''),
                    'keywords': ext_keywords_found,
                    'description': func.get('description', '')
                })

            # Check for modularity keywords
            mod_keywords_found = []
            for keyword in self.MODULARITY_KEYWORDS:
                if keyword in func_name or keyword in func_desc:
                    mod_keywords_found.append(keyword)

            if mod_keywords_found:
                modular_functions.append({
                    'name': func.get('name', ''),
                    'keywords': mod_keywords_found,
                    'description': func.get('description', '')
                })

        extensibility_count = len(extensible_functions)
        modularity_count = len(modular_functions)
        combined_count = len(set([f['name'] for f in extensible_functions] +
                                  [f['name'] for f in modular_functions]))
        combined_ratio = combined_count / max(total_functions, 1)

        # Determine extensibility level
        if combined_count >= 5 or combined_ratio > 0.15:
            level = "HIGH"
        elif combined_count >= 2 or combined_ratio > 0.05:
            level = "MEDIUM"
        else:
            level = "LOW"

        details = {
            'level': level,
            'extensible_functions': extensibility_count,
            'modular_functions': modularity_count,
            'combined_unique': combined_count,
            'total_functions': total_functions,
            'ratio': combined_ratio,
            'extensibility_examples': extensible_functions[:5],
            'modularity_examples': modular_functions[:5]
        }

        print(f"  📊 Extensibility indicators: {extensibility_count}/{total_functions}")
        print(f"  📊 Modularity indicators: {modularity_count}/{total_functions}")
        print(f"  📊 Combined unique: {combined_count}/{total_functions} ({combined_ratio:.1%})")
        print(f"  🎯 Extensibility level: {level}")
        if extensible_functions:
            print(f"  📋 Extensibility examples:")
            for func in extensible_functions[:3]:
                print(f"     - {func['name']}: {', '.join(func['keywords'][:3])}")
        if modular_functions:
            print(f"  📋 Modularity examples:")
            for func in modular_functions[:3]:
                print(f"     - {func['name']}: {', '.join(func['keywords'][:3])}")

        return level, details

    def generate_recommendation(
        self,
        coordination_level: str,
        span_type: str,
        operation_type: str,
        extensibility_level: str = "LOW"
    ) -> Tuple[str, str]:
        """
        Generate service organization recommendation

        Args:
            coordination_level: "LOW" | "MEDIUM" | "HIGH"
            span_type: "SINGLE_DOMAIN" | "CROSS_DOMAIN"
            operation_type: "CRUD_HEAVY" | "WORKFLOW_HEAVY" | "BALANCED"
            extensibility_level: "LOW" | "MEDIUM" | "HIGH"

        Returns:
            Tuple of (recommendation, rationale)
            recommendation: "PLUGIN_BASED" | "DOMAIN_BASED" | "WORKFLOW_BASED" | "HYBRID"
        """
        print("\n💡 Generating recommendation...")

        # Decision matrix - scores for each strategy
        score_plugin = 0
        score_workflow = 0
        score_domain = 0
        score_hybrid = 0

        # Factor 1: Extensibility requirements (NEW - most important for plugin-based)
        if extensibility_level == "HIGH":
            score_plugin += 4  # Strong signal for plugin-based
            score_hybrid += 1  # Hybrid can also support extensibility
        elif extensibility_level == "MEDIUM":
            score_plugin += 2
            score_hybrid += 1
        # LOW extensibility doesn't add to plugin score

        # Factor 2: Coordination complexity
        if coordination_level == "HIGH":
            score_workflow += 2
            score_plugin += 1  # Plugin-based also handles coordination well
        elif coordination_level == "MEDIUM":
            score_workflow += 1
            score_domain += 1
            score_plugin += 1
        else:  # LOW
            score_domain += 2

        # Factor 3: Workflow span
        if span_type == "CROSS_DOMAIN":
            score_workflow += 2
            score_plugin += 1  # Plugins can span domains via protocols
        else:  # SINGLE_DOMAIN
            score_domain += 2

        # Factor 4: Operation types (NEW v4.1.1: added REAL_TIME)
        if operation_type == "REAL_TIME":
            score_plugin += 3  # Real-time systems benefit greatly from swappable backends
            score_hybrid += 2  # Hybrid also works well
            # Workflow-based is NOT recommended for real-time (tight coupling needed)
            score_workflow -= 1
        elif operation_type == "WORKFLOW_HEAVY":
            score_workflow += 2
        elif operation_type == "CRUD_HEAVY":
            score_domain += 2
        else:  # BALANCED
            score_workflow += 1
            score_domain += 1
            score_plugin += 1  # Balanced systems benefit from modularity
            score_hybrid += 1

        # Bonus for plugin-based: modern systems benefit from Protocol-based interfaces
        # Plugin-based is generally the most flexible architecture
        score_plugin += 1  # Small baseline bonus for modern architecture

        # Calculate hybrid score as a blend
        score_hybrid += (score_workflow + score_domain) // 3

        # Determine recommendation based on highest score
        scores = {
            'PLUGIN_BASED': score_plugin,
            'WORKFLOW_BASED': score_workflow,
            'DOMAIN_BASED': score_domain,
            'HYBRID': score_hybrid
        }

        # Get top two scores
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_strategy, top_score = sorted_scores[0]
        second_strategy, second_score = sorted_scores[1]

        # If top two are very close, recommend the more flexible option
        if top_score - second_score <= 1:
            # Prefer plugin-based when scores are close (more flexible)
            if 'PLUGIN_BASED' in [top_strategy, second_strategy]:
                recommendation = 'PLUGIN_BASED'
            elif 'HYBRID' in [top_strategy, second_strategy]:
                recommendation = 'HYBRID'
            else:
                recommendation = top_strategy
        else:
            recommendation = top_strategy

        # Generate rationale based on recommendation
        if recommendation == "PLUGIN_BASED":
            rationale = "Plugin-Based Modular Architecture recommended due to:"
            reasons = []
            if extensibility_level == "HIGH":
                reasons.append(f"HIGH extensibility requirements - system needs runtime plugin loading/swapping")
            elif extensibility_level == "MEDIUM":
                reasons.append("MEDIUM extensibility requirements - system benefits from modular, replaceable components")
            # NEW v4.1.1: Real-time specific reasoning
            if operation_type == "REAL_TIME":
                reasons.append("REAL_TIME system benefits from swappable backends (headless, SDL, pygame)")
                reasons.append("Plugin architecture enables AI training mode without display/audio")
            reasons.append("Protocol-based interfaces enable loose coupling and easy testing")
            reasons.append("Dependency injection provides flexibility for different environments")
            if coordination_level in ["HIGH", "MEDIUM"]:
                reasons.append("Coordination can be handled via injected orchestrators")
            if operation_type == "BALANCED":
                reasons.append("Balanced operations work well with modular plugin structure")
            rationale += "\n" + "\n".join(f"  - {r}" for r in reasons)

        elif recommendation == "WORKFLOW_BASED":
            rationale = "Workflow-based organization recommended due to:"
            reasons = []
            if coordination_level == "HIGH":
                reasons.append(f"HIGH coordination complexity ({coordination_level})")
            if span_type == "CROSS_DOMAIN":
                reasons.append("workflows span multiple domains")
            if operation_type == "WORKFLOW_HEAVY":
                reasons.append("system is workflow-heavy, not CRUD-heavy")
            rationale += "\n" + "\n".join(f"  - {r}" for r in reasons)

        elif recommendation == "DOMAIN_BASED":
            rationale = "Domain-based organization recommended due to:"
            reasons = []
            if coordination_level == "LOW":
                reasons.append(f"LOW coordination complexity ({coordination_level})")
            if span_type == "SINGLE_DOMAIN":
                reasons.append("workflows stay within single domains")
            if operation_type == "CRUD_HEAVY":
                reasons.append("system is CRUD-heavy with simple operations")
            rationale += "\n" + "\n".join(f"  - {r}" for r in reasons)

        else:  # HYBRID
            rationale = "Hybrid organization recommended due to mixed characteristics:\n"
            rationale += f"  - Coordination: {coordination_level}\n"
            rationale += f"  - Workflow span: {span_type}\n"
            rationale += f"  - Operation type: {operation_type}\n"
            rationale += f"  - Extensibility: {extensibility_level}\n"
            rationale += "Consider combining patterns: plugin-based for extensible components, workflow services for coordination, domain services for shared capabilities."

        # Print scoring breakdown for transparency
        print(f"\n  📊 Strategy Scores:")
        print(f"     Plugin-Based: {score_plugin}")
        print(f"     Workflow-Based: {score_workflow}")
        print(f"     Domain-Based: {score_domain}")
        print(f"     Hybrid: {score_hybrid}")
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

        # FIX v4.1.1: Handle missing span fields gracefully
        span_data = self.analysis_results.get('span', {})
        span_type = span_data.get('span_type', 'UNKNOWN')
        cross_domain = span_data.get('cross_domain_flows', 0)
        total_flows = span_data.get('total_flows', 0)
        print(f"\n2. Workflow Span: {span_type}")
        if total_flows > 0:
            print(f"   {cross_domain} of {total_flows} flows span multiple domains")
        elif span_data.get('is_real_time'):
            print(f"   No workflow flows - system is frame-based/real-time")
        else:
            print(f"   No workflow flows defined")

        op_data = self.analysis_results.get('operations', {})
        print(f"\n3. Operation Types: {op_data.get('type', 'UNKNOWN')}")
        realtime_ratio = op_data.get('realtime_ratio', 0)
        if realtime_ratio > 0:
            print(f"   CRUD: {op_data.get('crud_ratio', 0):.0%}, Workflows: {op_data.get('workflow_ratio', 0):.0%}, Real-time: {realtime_ratio:.0%}")
        else:
            print(f"   CRUD: {op_data.get('crud_ratio', 0):.0%}, Workflows: {op_data.get('workflow_ratio', 0):.0%}")

        # NEW: Extensibility analysis (v3.21.0)
        if 'extensibility' in self.analysis_results:
            print(f"\n4. Extensibility Requirements: {self.analysis_results['extensibility']['level']}")
            print(f"   {self.analysis_results['extensibility']['combined_unique']} functions indicate extensibility/modularity needs")

        print(f"\n💡 RECOMMENDATION: {recommendation}")
        print(f"\n{rationale}")

        print("\n" + "=" * 70)
        print("ORGANIZATION STRATEGY OPTIONS")
        print("=" * 70)

        print(f"\n1. Plugin-Based Modular Architecture {'⭐ RECOMMENDED' if recommendation == 'PLUGIN_BASED' else ''}")
        print(f"   Services: Modular components with Protocol-based interfaces")
        print(f"   Example: PluginRegistry, ExtensionLoader, AdapterFactory, ProviderManager")
        print(f"   Best for: High extensibility, runtime plugin loading, multi-environment deployment")
        print(f"   Pros: Maximum flexibility, loose coupling, easy testing, runtime swappable components")
        print(f"   Cons: Requires Protocol + DI patterns, more initial design effort")
        print(f"   Key patterns: Protocol interfaces, Dependency Injection, Plugin discovery")

        print(f"\n2. Domain-Based Organization {'⭐ RECOMMENDED' if recommendation == 'DOMAIN_BASED' else ''}")
        print(f"   Services: Organized by business domain/capability")
        print(f"   Example: UserService, ProductService, OrderService")
        print(f"   Best for: Clear domains, low coordination, CRUD operations")
        print(f"   Pros: Aligns with business domains, clear ownership")
        print(f"   Cons: Cross-domain coordination becomes distributed state")

        print(f"\n3. Workflow-Based Organization {'⭐ RECOMMENDED' if recommendation == 'WORKFLOW_BASED' else ''}")
        print(f"   Services: Organized by user workflows/operations")
        print(f"   Example: CheckoutWorkflowService, InventoryManagementService")
        print(f"   Best for: High coordination, cross-domain workflows")
        print(f"   Pros: Coordination is local, workflows self-contained")
        print(f"   Cons: May duplicate some domain logic")

        print(f"\n4. Hybrid (Mix of Patterns) {'⭐ RECOMMENDED' if recommendation == 'HYBRID' else ''}")
        print(f"   Combines patterns based on specific service needs:")
        print(f"   - Plugin services: Extensible, swappable components")
        print(f"   - Workflow services: Complex coordination operations")
        print(f"   - Domain services: Shared capabilities")
        print(f"   Best for: Large, complex systems with varied requirements")
        print(f"   Pros: Best of all strategies, tailored per component")
        print(f"   Cons: Most complex to design, requires clear architectural guidelines")

        print("\n" + "=" * 70)
        print("LLM AGENT: Make an EDUCATED recommendation based on:")
        print("  1. The analysis scores above")
        print("  2. User's stated requirements and preferences")
        print("  3. System complexity and future extensibility needs")
        print("  4. Team experience with patterns (Protocol/DI vs traditional)")
        print("DO NOT just echo 'tool recommends X' - synthesize the analysis!")
        print("=" * 70)

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
            extensibility_level, ext_details = self.analyze_extensibility_requirements()  # NEW v3.21.0

            # Store results
            self.analysis_results = {
                'coordination': coord_details,
                'span': span_details,
                'operations': op_details,
                'extensibility': ext_details  # NEW v3.21.0
            }

            # Generate recommendation
            recommendation, rationale = self.generate_recommendation(
                coordination_level,
                span_type,
                operation_type,
                extensibility_level  # NEW v3.21.0
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
