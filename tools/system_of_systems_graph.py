#!/usr/bin/env python3
"""
System-of-Systems Graph Generator

Creates machine-readable JSON representation of system architecture using NetworkX.
This tool builds a directed graph where:
- Nodes represent services/systems/components  
- Edges represent interfaces/dependencies between components
- Output is NetworkX node_link_data format for LLM architectural analysis

Replaces visual graph generation with JSON-only output for automated analysis.
"""

import os
import json
import networkx as nx
import sys
import argparse
from typing import Dict, List, Tuple
from pathlib import Path
from datetime import datetime

# Adjust paths for reflow directory structure
REFLOW_ROOT = Path(__file__).parent.parent
TEMPLATES_PATH = REFLOW_ROOT / "templates"
DEFINITIONS_PATH = REFLOW_ROOT / "definitions"


# --- STEP 1: Load the robust index file ---
def load_service_architecture_index(index_path: str) -> Dict[str, str]:
    """Load the mapping of service_id to file path from the index file.

    Handles both flat dictionaries and structured index files with 'components' key.
    Returns a flat mapping of service_id to file_path.
    """
    with open(index_path, "r") as f:
        index_data = json.load(f)

    # Handle structured index format with metadata and components
    if isinstance(index_data, dict) and "components" in index_data:
        return index_data["components"]

    # Handle legacy flat format (service_id: file_path mapping)
    elif isinstance(index_data, dict):
        # Filter out non-component metadata keys
        metadata_keys = {
            "system_name",
            "description",
            "last_updated",
            "version",
            "metadata",
        }
        return {
            k: v
            for k, v in index_data.items()
            if k not in metadata_keys and isinstance(v, str)
        }

    else:
        raise ValueError(
            f"Invalid index format: expected dict with 'components' key or flat service mapping"
        )


# --- STEP 2: Build the system-of-systems graph ---
def classify_node(service_id: str, data: dict) -> Tuple[str, str]:
    """Return (level, display_name) based on UAF hierarchical classification and service data."""

    # Use UAF hierarchical_tier if available
    tier = data.get("hierarchical_tier")
    if tier == "tier_0_system_of_systems":
        level = "system_of_systems"
    elif tier == "tier_1_systems":
        level = "system"
    elif tier == "tier_2_components":
        level = "package"  # Map to existing 'package' level for compatibility
    elif tier == "tier_3_internal_modules":
        level = "module"  # New level for internal modules
    else:
        # Fallback heuristics for non-UAF formatted data
        if service_id.endswith("_service") and "package_name" not in data:
            level = "service"
        elif "package_name" in data:
            level = "package"
        else:
            level = "package"  # Default to package level

    # Get display name, preferring service_name
    display_name = (
        data.get("service_name")
        or data.get("package_name")
        or service_id.replace("_", "-")  # Convert underscores to hyphens for display
    )

    return (level, display_name)


def build_system_graph(
    index: Dict[str, str], include_levels: List[str], index_dir: str
) -> nx.DiGraph:
    """Build a directed graph from all service_architecture.json files filtering by include_levels (e.g., ['package']).

    Args:
        index: Dictionary mapping service_id to file paths
        include_levels: List of levels to include in the graph
        index_dir: Directory containing the index.json file, used for resolving relative paths
    """
    G = nx.DiGraph()
    service_info = {}
    node_levels = {}

    # Pass 1: load and classify
    for service_id, file_path in index.items():
        # Handle relative paths by making them relative to index directory
        if not os.path.isabs(file_path):
            file_path = os.path.join(index_dir, file_path)

        try:
            with open(file_path, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Warning: Could not find file {file_path} for service {service_id}")
            continue
        except json.JSONDecodeError:
            print(f"Warning: Invalid JSON in {file_path} for service {service_id}")
            continue

        level, display = classify_node(service_id, data)
        node_levels[service_id] = level
        if level in include_levels:
            G.add_node(service_id, label=display, level=level, raw=data)
        service_info[service_id] = data
    # Pass 2: add edges only if both endpoints are kept (to avoid partial hierarchy clutter)
    for service_id, data in service_info.items():
        if service_id not in G:  # Skip nodes filtered out
            continue
        # Dependencies
        dependencies = []
        if "dependencies" in data:
            dependencies = data["dependencies"]
        elif "srd" in data and "dependencies" in data["srd"]:
            dependencies = data["srd"]["dependencies"]
        for dep in dependencies:
            dep_id = None
            for sid, info in service_info.items():
                name_candidates = [
                    sid,
                    info.get("service_name", "").lower().replace(" ", "_"),
                    info.get("package_name", "").lower().replace(" ", "_"),
                ]
                if dep.lower().replace(" ", "_") in name_candidates:
                    dep_id = sid
                    break
            if dep_id and dep_id in G:
                G.add_edge(service_id, dep_id, type="dependency")
        # Interfaces
        icd = data.get("icd", data)
        interfaces = icd.get("interfaces", [])
        for iface in interfaces:
            if isinstance(iface, dict):
                for dep in iface.get("dependencies", []):
                    dep_id = None
                    for sid, info in service_info.items():
                        name_candidates = [
                            sid,
                            info.get("service_name", "").lower().replace(" ", "_"),
                            info.get("package_name", "").lower().replace(" ", "_"),
                        ]
                        if dep.lower().replace(" ", "_") in name_candidates:
                            dep_id = sid
                            break
                    if dep_id and dep_id in G:
                        G.add_edge(service_id, dep_id, type="interface")
    return G


# --- STEP 4: Export machine-readable graph object for LLM analysis ---
def export_graph_json(G: nx.DiGraph, out_path: str):
    """Export NetworkX graph as machine-readable JSON for LLM architectural analysis.

    Uses NetworkX's node_link_data format which includes:
    - nodes: List of all nodes with their attributes (services/systems/components)
    - links: List of all edges with their attributes (interfaces/dependencies)
    - directed: True (indicates this is a directed graph)
    - multigraph: False

    Example output structure:
    {
      "directed": true,
      "multigraph": false,
      "graph": {},
      "nodes": [
        {
          "id": "auth_service",
          "label": "Authentication Service",
          "level": "service",
          "raw": {...service_architecture_data...}
        }
      ],
      "links": [
        {
          "source": "web_frontend",
          "target": "auth_service",
          "type": "dependency"
        }
      ],
      "metadata": {
        "export_timestamp": "2025-10-14T...",
        "node_count": 5,
        "edge_count": 8,
        "purpose": "system_of_systems_architectural_analysis"
      }
    }
    """
    data = nx.node_link_data(G)

    # Add metadata for LLM analysis
    data["metadata"] = {
        "export_timestamp": datetime.now().isoformat(),
        "node_count": len(G.nodes()),
        "edge_count": len(G.edges()),
        "purpose": "system_of_systems_architectural_analysis",
        "format": "networkx_node_link_data",
        "usage_instructions": [
            "Parse nodes array to understand all services/systems in architecture",
            "Parse links array to understand dependencies and interfaces between services",
            "Check raw data in nodes for detailed service specifications",
            "Cross-reference with architectural issues report for problems to fix",
        ],
    }

    with open(out_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"System-of-systems graph exported to {out_path}")
    print(
        f"Format: NetworkX JSON with {len(G.nodes())} nodes and {len(G.edges())} edges"
    )
    print(
        f"LLM agents can parse this JSON to understand system topology and dependencies"
    )


# --- STEP 5: Architectural Issue Detection ---
def detect_architectural_issues(G: nx.DiGraph) -> Dict[str, List[Dict]]:
    """Detect common architectural issues in the system graph"""
    issues = {
        "circular_dependencies": [],
        "orphaned_nodes": [],
        "missing_interfaces": [],
        "inconsistent_protocols": [],
        "security_gaps": [],
        "performance_bottlenecks": [],
    }

    # 1. Detect circular dependencies
    try:
        cycles = list(nx.simple_cycles(G))
        for cycle in cycles:
            issues["circular_dependencies"].append(
                {
                    "cycle": cycle,
                    "description": f"Circular dependency detected: {' -> '.join(cycle + [cycle[0]])}",
                    "severity": "critical",
                    "recommendation": "Consider introducing async communication or refactoring service responsibilities",
                }
            )
    except:
        pass

    # 2. Find orphaned nodes (no incoming or outgoing edges)
    for node in G.nodes():
        in_degree = G.in_degree(node)
        out_degree = G.out_degree(node)
        if in_degree == 0 and out_degree == 0:
            issues["orphaned_nodes"].append(
                {
                    "node": node,
                    "description": f"Orphaned node '{node}' has no connections",
                    "severity": "warning",
                    "recommendation": "Verify if this component is needed or add appropriate interfaces",
                }
            )

    # 3. Check for nodes with high connectivity (potential bottlenecks)
    avg_degree = (
        sum(dict(G.degree()).values()) / len(G.nodes()) if len(G.nodes()) > 0 else 0
    )
    for node in G.nodes():
        total_degree = G.in_degree(node) + G.out_degree(node)
        if total_degree > max(
            avg_degree * 2, 5
        ):  # Significantly above average or >5 connections
            issues["performance_bottlenecks"].append(
                {
                    "node": node,
                    "connections": total_degree,
                    "description": f"Node '{node}' has {total_degree} connections, potential bottleneck",
                    "severity": "warning",
                    "recommendation": "Consider load balancing or splitting responsibilities",
                }
            )

    # 4. Check for missing authentication/security interfaces
    for node in G.nodes():
        node_data = G.nodes[node].get("raw", {})
        interfaces = node_data.get("interfaces", [])

        has_auth = False
        for interface in interfaces:
            if isinstance(interface, dict):
                if (
                    interface.get("auth_required", False)
                    or "auth" in interface.get("name", "").lower()
                ):
                    has_auth = True
                    break

        # If node has incoming connections but no auth, flag as potential security gap
        if G.in_degree(node) > 0 and not has_auth:
            issues["security_gaps"].append(
                {
                    "node": node,
                    "description": f"Node '{node}' receives connections but lacks authentication interface",
                    "severity": "medium",
                    "recommendation": "Add authentication/authorization interface",
                }
            )

    # 5. Check for inconsistent interface protocols
    protocol_map = {}
    for u, v, data in G.edges(data=True):
        edge_type = data.get("type", "unknown")
        if edge_type not in protocol_map:
            protocol_map[edge_type] = []
        protocol_map[edge_type].append((u, v))

    # Look for nodes that mix protocols inconsistently
    for node in G.nodes():
        incoming_protocols = set()
        outgoing_protocols = set()

        for u, v, data in G.edges(data=True):
            protocol = data.get("type", "unknown")
            if v == node:
                incoming_protocols.add(protocol)
            if u == node:
                outgoing_protocols.add(protocol)

        if len(incoming_protocols) > 2 or len(outgoing_protocols) > 2:
            issues["inconsistent_protocols"].append(
                {
                    "node": node,
                    "incoming_protocols": list(incoming_protocols),
                    "outgoing_protocols": list(outgoing_protocols),
                    "description": f"Node '{node}' uses multiple communication protocols",
                    "severity": "info",
                    "recommendation": "Consider standardizing on fewer protocols for consistency",
                }
            )

    return issues


def export_issues_report(issues: Dict, out_path: str):
    """Export architectural issues to a machine-readable JSON report for LLM analysis"""

    # Count issues by severity
    severity_counts = {"critical": 0, "warning": 0, "medium": 0, "info": 0}
    total_issues = 0

    for category, issue_list in issues.items():
        for issue in issue_list:
            severity = issue.get("severity", "info")
            severity_counts[severity] += 1
            total_issues += 1

    report = {
        "analysis_timestamp": datetime.now().isoformat(),
        "summary": {
            "total_issues": total_issues,
            "critical_issues": severity_counts["critical"],
            "warning_issues": severity_counts["warning"],
            "medium_issues": severity_counts["medium"],
            "info_issues": severity_counts["info"],
            "action_required": severity_counts["critical"] > 0
            or severity_counts["warning"] > 0,
        },
        "architectural_issues": issues,
        "recommendations": {
            "immediate_action_required": severity_counts["critical"] > 0,
            "review_recommended": severity_counts["warning"] + severity_counts["medium"]
            > 0,
            "overall_status": "needs_attention" if total_issues > 0 else "healthy",
        },
        "llm_agent_instructions": {
            "priority_order": ["critical", "warning", "medium", "info"],
            "fix_workflow": [
                "1. Address all critical issues first - these can break the system",
                "2. Review and fix warning issues - these indicate architectural problems",
                "3. Consider medium issues - these may affect maintainability",
                "4. Info issues are suggestions for improvement",
                "5. Update service_architecture.json files to resolve issues",
                "6. Re-run system_of_systems_graph.py to verify fixes",
            ],
            "common_fixes": {
                "circular_dependencies": "Break cycles by introducing async communication, event-driven architecture, or refactoring service boundaries",
                "orphaned_nodes": "Either remove unused services or add missing interface connections",
                "performance_bottlenecks": "Split high-connectivity services or add load balancing/caching layers",
                "security_gaps": "Add authentication/authorization interfaces for services that handle user data",
                "inconsistent_protocols": "Standardize on fewer communication protocols (e.g., REST, gRPC, message queues)",
            },
        },
    }

    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"Architectural issues report exported to {out_path}")
    print(
        f"Found {total_issues} issues: {severity_counts['critical']} critical, {severity_counts['warning']} warnings"
    )
    if severity_counts["critical"] > 0:
        print("⚠️  CRITICAL ISSUES DETECTED - Immediate LLM agent attention required")
    elif severity_counts["warning"] > 0:
        print("⚠️  WARNING ISSUES DETECTED - LLM agent should review and fix")
    else:
        print("✅ No critical issues detected - Architecture appears healthy")

    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Build and export a machine-readable system-of-systems graph from an index.json for LLM architectural analysis. Uses NetworkX to model nodes (services/systems) and edges (interfaces) with JSON output."
    )
    parser.add_argument("index", help="Path to index.json (absolute path recommended)")
    parser.add_argument(
        "--mode",
        choices=["all", "systems", "packages", "components", "modules", "multi"],
        default="packages",
        help="Which hierarchy level(s) to include: modules (tier 3), packages/components (tier 2), systems (tier 1), all (all levels), or multi (generate multiple viewpoints)",
    )
    parser.add_argument(
        "--json",
        default="system_of_systems_graph.json",
        help="Output graph JSON filename (NetworkX node_link_data format)",
    )
    parser.add_argument(
        "--issues",
        default="architecture_issues.json",
        help="Output architectural issues report filename",
    )
    parser.add_argument(
        "--analyze-issues",
        action="store_true",
        help="Perform automated architectural issue analysis",
    )
    args = parser.parse_args()

    # Resolve absolute path to index file and its containing directory
    index_path = os.path.abspath(args.index)
    index_dir = os.path.dirname(index_path)

    index = load_service_architecture_index(index_path)
    print(f"Loaded {len(index)} components from index")

    # Define viewpoints for multi-mode
    viewpoints = [
        {"mode": "systems", "levels": ["system", "service"]},
        {"mode": "packages", "levels": ["package"]},
        {"mode": "modules", "levels": ["module", "package"]},
        {
            "mode": "all",
            "levels": ["system_of_systems", "system", "service", "package", "module"],
        },
    ]

    if args.mode == "multi":
        # Generate multiple viewpoints
        for viewpoint in viewpoints:
            include_levels = viewpoint["levels"]
            G = build_system_graph(
                index, include_levels=include_levels, index_dir=index_dir
            )

            if len(G.nodes()) == 0:
                print(
                    f"Skipping {viewpoint['mode']} view - no nodes at specified levels"
                )
                continue

            # Create output filename
            out_json = os.path.join(index_dir, f"graph_{viewpoint['mode']}.json")

            export_graph_json(G, out_json)
            print(
                f"Generated {viewpoint['mode']} view: {len(G.nodes())} nodes, {len(G.edges())} edges"
            )

            # Perform issue analysis if requested
            if args.analyze_issues:
                issues = detect_architectural_issues(G)
                issues_file = os.path.join(
                    index_dir, f"issues_{viewpoint['mode']}.json"
                )
                export_issues_report(issues, issues_file)

    else:
        # Single mode operation
        if args.mode == "all":
            include_levels = [
                "system_of_systems",
                "system",
                "service",
                "package",
                "module",
            ]
        elif args.mode == "systems":
            include_levels = ["system", "service"]
        elif args.mode == "components":
            include_levels = ["package"]
        elif args.mode == "modules":
            include_levels = [
                "module",
                "package",
            ]  # Include parent packages for context
        else:  # packages (default)
            include_levels = ["package"]

        G = build_system_graph(
            index, include_levels=include_levels, index_dir=index_dir
        )

        # Write output files in the same directory as the index
        out_json = os.path.join(index_dir, args.json)
        export_graph_json(G, out_json)
        print(f"Nodes kept ({args.mode}): {len(G.nodes())}; Edges: {len(G.edges())}")

        # Perform issue analysis if requested
        if args.analyze_issues:
            issues = detect_architectural_issues(G)
            issues_file = os.path.join(index_dir, args.issues)
            export_issues_report(issues, issues_file)

    print("System-of-systems graph generation complete!")
    print("Output: NetworkX JSON format optimized for LLM architectural analysis")
