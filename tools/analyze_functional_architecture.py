#!/usr/bin/env python3
"""
Functional Architecture Analyzer v2.0.0

Framework-agnostic functional architecture analysis tool.

Analyzes functional architectures to identify:
- Functional gaps (missing functions, unreachable functions, orphaned functions)
- Flow efficiency (cycles, high fan-out/fan-in)
- Context bottlenecks (optional - for architectures with context consumption tracking)
- Critical path analysis
- Redundant functions

Version 2.0.0 Changes (2025-11-08):
- Framework-agnostic: Works with ANY functional architecture (microservices, AI agents, etc.)
- Flexible field support:
  - execution_time: Accepts both numeric (execution_time_seconds) and string formats ("0.01 seconds")
  - context_consumption: Optional field (skipped for traditional systems without resource tracking)
  - dependencies: Handles both 'function_dependencies' and 'dependencies' keys
  - Field names: Supports both 'source'/'target' and 'source_function'/'target_function'
- Context analysis runs ONLY if context consumption data is present
- No assumptions about system type (AI agent vs traditional)
"""

import json
import networkx as nx
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional
import sys
import re

def parse_execution_time(time_value) -> float:
    """
    Parse execution time from various formats.

    Handles:
    - Numeric values (1, 2.5, 60)
    - String with units ("0.01 seconds", "1-5 seconds", "Continuous")

    Returns execution time in seconds (float), or 0.0 if unparseable.
    """
    if isinstance(time_value, (int, float)):
        return float(time_value)

    if isinstance(time_value, str):
        # Handle ranges like "1-5 seconds" - take average
        range_match = re.match(r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s*seconds?', time_value, re.IGNORECASE)
        if range_match:
            low = float(range_match.group(1))
            high = float(range_match.group(2))
            return (low + high) / 2.0

        # Handle single value like "0.01 seconds"
        single_match = re.match(r'(\d+(?:\.\d+)?)\s*seconds?', time_value, re.IGNORECASE)
        if single_match:
            return float(single_match.group(1))

        # Handle special cases like "Continuous (event-driven)"
        if 'continuous' in time_value.lower():
            return 0.0  # Continuous processes don't have discrete execution time

    # Default to 0 if unparseable
    return 0.0

def has_context_data(arch: Dict) -> bool:
    """
    Check if the functional architecture contains context consumption data.

    Returns True if context_consumption field exists and has non-zero values.
    This is framework-agnostic - any architecture can optionally track context.
    """
    if 'functions' in arch and len(arch['functions']) > 0:
        # Check if any function has context_consumption field with non-zero value
        for func in arch['functions']:
            if func.get('context_consumption', 0) > 0:
                return True

    return False

def load_functional_architecture(filepath: Path) -> Dict:
    """Load functional architecture JSON."""
    with open(filepath, 'r') as f:
        return json.load(f)

def build_functional_graph(arch: Dict) -> nx.DiGraph:
    """Build NetworkX directed graph from functional architecture."""
    G = nx.DiGraph()

    # Add nodes (functions)
    for func in arch['functions']:
        # Handle context_consumption (optional for traditional systems)
        context_consumption = func.get('context_consumption', 0)

        # Handle execution_time (flexible field names and formats)
        execution_time = 0.0
        if 'execution_time_seconds' in func:
            execution_time = parse_execution_time(func['execution_time_seconds'])
        elif 'execution_time' in func:
            execution_time = parse_execution_time(func['execution_time'])

        G.add_node(
            func['function_id'],
            label=func['function_name'],
            type=func['function_type'],
            context_consumption=context_consumption,
            execution_time=execution_time,
            description=func['description']
        )

    # Add edges (dependencies) - handle both schema variations
    # Some schemas use 'function_dependencies', others use 'dependencies'
    dependencies = arch.get('function_dependencies', arch.get('dependencies', []))

    for dep in dependencies:
        # Normalize field names (handle schema variations)
        source = dep.get('source', dep.get('source_function', ''))
        target = dep.get('target', dep.get('target_function', ''))
        dep_type = dep.get('type', dep.get('dependency_type', 'dependency'))

        # Skip if source or target is missing
        if not source or not target:
            continue

        # Weight might be context_consumption (AI workflows) or execution_probability (traditional)
        weight = dep.get('weight', 0)

        G.add_edge(
            source,
            target,
            type=dep_type,
            weight=weight,
            probability=dep.get('probability', 1.0),
            condition=dep.get('condition', '')
        )

    return G

def analyze_context_paths(G: nx.DiGraph, arch: Dict, context_threshold: int = 160000) -> Optional[Dict]:
    """
    Analyze all paths for cumulative context consumption.

    Returns None if system has no context consumption data (traditional systems).
    """
    # Check if any function has context consumption > 0
    has_context_data = any(G.nodes[n].get('context_consumption', 0) > 0 for n in G.nodes())

    if not has_context_data:
        return None  # Skip context analysis for traditional systems

    results = {
        'bottleneck_paths': [],
        'warning_paths': [],
        'safe_paths': [],
        'critical_functions': [],
        'summary': {}
    }

    # Extract explicit entry and exit points from functional flows
    sources = []
    sinks = []
    if 'functional_flows' in arch:
        for flow in arch['functional_flows']:
            if 'entry_point' in flow:
                sources.append(flow['entry_point'])
            if 'exit_points' in flow:
                sinks.extend(flow['exit_points'])

    # Fallback to topological approach if no explicit entry points
    if not sources:
        sources = [n for n in G.nodes() if G.in_degree(n) == 0]
    if not sinks:
        sinks = [n for n in G.nodes() if G.out_degree(n) == 0]

    all_paths = []
    max_path_length = 15  # Limit to avoid exponential explosion

    for source in sources:
        for sink in sinks:
            try:
                paths = nx.all_simple_paths(G, source, sink, cutoff=max_path_length)
                for path in paths:
                    # Calculate cumulative context
                    context_sum = 0
                    for i, node in enumerate(path):
                        # Add node's own context consumption
                        context_sum += G.nodes[node].get('context_consumption', 0)
                        # Add edge weight if there's a next node
                        if i < len(path) - 1:
                            edge_data = G[path[i]][path[i+1]]
                            # Edge weight might be different from node consumption
                            # Use edge weight as the context cost of the transition
                            context_sum += edge_data.get('weight', 0)

                    path_info = {
                        'path': path,
                        'context_consumption': context_sum,
                        'length': len(path),
                        'source': source,
                        'sink': sink
                    }

                    all_paths.append(path_info)

                    # Categorize by context consumption
                    if context_sum > context_threshold:
                        results['bottleneck_paths'].append(path_info)
                    elif context_sum > context_threshold * 0.875:  # 140k for 160k threshold
                        results['warning_paths'].append(path_info)
                    else:
                        results['safe_paths'].append(path_info)
            except nx.NetworkXNoPath:
                continue

    # Find high-context functions
    context_by_function = [(n, G.nodes[n].get('context_consumption', 0)) for n in G.nodes()]
    context_by_function.sort(key=lambda x: x[1], reverse=True)
    results['critical_functions'] = context_by_function[:10]

    # Summary statistics
    if all_paths:
        context_values = [p['context_consumption'] for p in all_paths]
        results['summary'] = {
            'total_paths_analyzed': len(all_paths),
            'bottleneck_paths': len(results['bottleneck_paths']),
            'warning_paths': len(results['warning_paths']),
            'safe_paths': len(results['safe_paths']),
            'max_context_path': max(context_values) if context_values else 0,
            'avg_context_path': sum(context_values) / len(context_values) if context_values else 0,
            'context_threshold': context_threshold,
            'bottleneck_percentage': (len(results['bottleneck_paths']) / len(all_paths)) * 100 if all_paths else 0
        }
    else:
        # No simple paths found (likely due to cycles or disconnected graph)
        results['summary'] = {
            'total_paths_analyzed': 0,
            'bottleneck_paths': 0,
            'warning_paths': 0,
            'safe_paths': 0,
            'max_context_path': 0,
            'avg_context_path': 0,
            'context_threshold': context_threshold,
            'bottleneck_percentage': 0,
            'note': 'No simple paths found - graph may contain cycles or be disconnected. Use cycle detection for analysis.'
        }

    return results

def detect_cycles(G: nx.DiGraph) -> List[List[str]]:
    """Detect cycles in functional graph."""
    try:
        cycles = list(nx.simple_cycles(G))
        return cycles
    except:
        return []

def detect_gaps(G: nx.DiGraph, arch: Dict) -> Dict:
    """Detect potential functional gaps."""
    gaps = {
        'orphaned_functions': [],
        'unreachable_functions': [],
        'dead_end_functions': [],
        'missing_error_handlers': []
    }

    # Orphaned functions (no connections)
    for node in G.nodes():
        if G.degree(node) == 0:
            gaps['orphaned_functions'].append({
                'function_id': node,
                'function_name': G.nodes[node].get('label', '')
            })

    # Unreachable functions (no path from any entry point)
    # Extract explicit entry points from functional flows
    sources = []
    if 'functional_flows' in arch:
        for flow in arch['functional_flows']:
            if 'entry_point' in flow:
                sources.append(flow['entry_point'])

    # Fallback to topological approach if no explicit entry points
    if not sources:
        sources = [n for n in G.nodes() if G.in_degree(n) == 0]

    reachable = set()
    for source in sources:
        reachable.update(nx.descendants(G, source))
        reachable.add(source)

    for node in G.nodes():
        if node not in reachable and G.degree(node) > 0:
            gaps['unreachable_functions'].append({
                'function_id': node,
                'function_name': G.nodes[node].get('label', '')
            })

    # Dead-end functions (no outgoing edges, not intentional sinks)
    for node in G.nodes():
        if G.out_degree(node) == 0 and G.in_degree(node) > 0:
            # Check if it's an intentional exit point
            func_name = G.nodes[node].get('label', '')
            if 'Write' not in func_name and 'Save' not in func_name and 'Complete' not in func_name:
                gaps['dead_end_functions'].append({
                    'function_id': node,
                    'function_name': func_name
                })

    # Check for error handling
    for func in arch['functions']:
        if 'error_handling' not in func or not func['error_handling']:
            gaps['missing_error_handlers'].append({
                'function_id': func['function_id'],
                'function_name': func['function_name']
            })

    return gaps

def detect_redundancy(G: nx.DiGraph) -> List[Dict]:
    """Detect potentially redundant functions based on similarity."""
    redundancy_candidates = []

    # Simple heuristic: functions with very similar names or purposes
    functions = [(n, G.nodes[n]) for n in G.nodes()]

    for i, (id1, data1) in enumerate(functions):
        for id2, data2 in functions[i+1:]:
            name1 = data1.get('label', '').lower()
            name2 = data2.get('label', '').lower()

            # Check for very similar names
            if name1 in name2 or name2 in name1:
                redundancy_candidates.append({
                    'function_1': id1,
                    'function_1_name': data1.get('label', ''),
                    'function_2': id2,
                    'function_2_name': data2.get('label', ''),
                    'reason': 'Similar names suggest potential redundancy'
                })

    return redundancy_candidates

def analyze_flow_efficiency(G: nx.DiGraph) -> Dict:
    """Analyze flow efficiency (cycles, handoffs, complexity)."""
    analysis = {
        'cycles': [],
        'excessive_handoffs': [],
        'high_fan_out': [],
        'high_fan_in': []
    }

    # Detect cycles
    cycles = detect_cycles(G)
    for cycle in cycles:
        analysis['cycles'].append({
            'cycle': cycle,
            'length': len(cycle),
            'note': 'Cycles may indicate iterative refinement (expected) or circular dependency (problematic)'
        })

    # High fan-out (function calls too many others)
    for node in G.nodes():
        out_degree = G.out_degree(node)
        if out_degree > 5:
            analysis['high_fan_out'].append({
                'function_id': node,
                'function_name': G.nodes[node].get('label', ''),
                'fan_out': out_degree,
                'note': 'High fan-out may indicate god function'
            })

    # High fan-in (function called by too many others)
    for node in G.nodes():
        in_degree = G.in_degree(node)
        if in_degree > 5:
            analysis['high_fan_in'].append({
                'function_id': node,
                'function_name': G.nodes[node].get('label', ''),
                'fan_in': in_degree,
                'note': 'High fan-in indicates critical function'
            })

    return analysis

def generate_recommendations(context_analysis: Optional[Dict], gaps: Dict, efficiency: Dict) -> List[str]:
    """Generate actionable recommendations based on analysis."""
    recommendations = []

    # Context recommendations (only for AI agent workflows)
    if context_analysis is not None:
        if context_analysis['summary']['bottleneck_paths'] > 0:
            recommendations.append(
                f"CRITICAL: {context_analysis['summary']['bottleneck_paths']} paths exceed context threshold "
                f"({context_analysis['summary']['context_threshold']} tokens). Consider: "
                "(1) Breaking long flows into separate sessions with context refresh, "
                "(2) Implementing lazy loading for high-context functions, "
                "(3) Summarizing outputs instead of full details."
            )

        if context_analysis['summary']['warning_paths'] > 0:
            recommendations.append(
                f"WARNING: {context_analysis['summary']['warning_paths']} paths approaching context limits. "
                "Monitor these flows and optimize high-context functions."
            )

        # Top context consumers
        if context_analysis['critical_functions']:
            top_func = context_analysis['critical_functions'][0]
            recommendations.append(
                f"Highest context consumer: {top_func[0]} ({top_func[1]} tokens). "
                f"Consider refactoring to reduce context consumption."
            )

    # Gap recommendations
    if gaps['orphaned_functions']:
        recommendations.append(
            f"Found {len(gaps['orphaned_functions'])} orphaned functions with no connections. "
            "These functions may be incomplete or unnecessary."
        )

    if gaps['unreachable_functions']:
        recommendations.append(
            f"Found {len(gaps['unreachable_functions'])} unreachable functions. "
            "These functions cannot be executed in any workflow path."
        )

    # Efficiency recommendations
    if efficiency['cycles']:
        recommendations.append(
            f"Found {len(efficiency['cycles'])} cycles. Review to determine if these are "
            "intentional iterative refinement loops or problematic circular dependencies."
        )

    if efficiency['high_fan_out']:
        for item in efficiency['high_fan_out']:
            recommendations.append(
                f"Function {item['function_id']} has high fan-out ({item['fan_out']}). "
                "Consider decomposing into smaller functions."
            )

    return recommendations

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 analyze_functional_architecture.py <functional_architecture.json>")
        sys.exit(1)

    arch_path = Path(sys.argv[1])
    if not arch_path.exists():
        print(f"Error: File not found: {arch_path}")
        sys.exit(1)

    print(f"Loading functional architecture from: {arch_path}")
    arch = load_functional_architecture(arch_path)

    print("\nBuilding functional graph...")
    G = build_functional_graph(arch)
    print(f"Graph built: {G.number_of_nodes()} functions, {G.number_of_edges()} dependencies")

    # Context analysis (runs only if context consumption data is present)
    context_analysis = None
    has_context = has_context_data(arch)

    print("\n" + "="*80)
    print("CONTEXT PATH ANALYSIS")
    print("="*80)

    if has_context:
        print("Context consumption data detected - analyzing paths...")
        context_analysis = analyze_context_paths(G, arch)

        if context_analysis is not None:
            print(f"\nAnalyzed {context_analysis['summary']['total_paths_analyzed']} paths")
            print(f"Context threshold: {context_analysis['summary']['context_threshold']} tokens")
            print(f"Bottleneck paths (CRITICAL): {context_analysis['summary']['bottleneck_paths']}")
            print(f"Warning paths: {context_analysis['summary']['warning_paths']}")
            print(f"Safe paths: {context_analysis['summary']['safe_paths']}")
            print(f"Max context path: {context_analysis['summary']['max_context_path']:.0f} tokens")
            print(f"Avg context path: {context_analysis['summary']['avg_context_path']:.0f} tokens")

            if context_analysis['bottleneck_paths']:
                print("\nCRITICAL BOTTLENECK PATHS:")
                for i, path_info in enumerate(context_analysis['bottleneck_paths'][:5], 1):
                    print(f"  {i}. {' → '.join(path_info['path'])}")
                    print(f"     Context: {path_info['context_consumption']} tokens")

            print("\nTOP 5 CONTEXT-CONSUMING FUNCTIONS:")
            for func_id, context in context_analysis['critical_functions'][:5]:
                func_name = G.nodes[func_id].get('label', '')
                print(f"  {func_id} ({func_name}): {context} tokens")
    else:
        print("No context consumption data found - skipping context analysis.")
        print("(This is normal for architectures that don't track resource consumption)")

    print("\n" + "="*80)
    print("GAP DETECTION")
    print("="*80)
    gaps = detect_gaps(G, arch)
    print(f"Orphaned functions: {len(gaps['orphaned_functions'])}")
    print(f"Unreachable functions: {len(gaps['unreachable_functions'])}")
    print(f"Dead-end functions: {len(gaps['dead_end_functions'])}")
    print(f"Functions missing error handlers: {len(gaps['missing_error_handlers'])}")

    if gaps['orphaned_functions']:
        print("\nORPHANED FUNCTIONS:")
        for item in gaps['orphaned_functions']:
            print(f"  {item['function_id']}: {item['function_name']}")

    if gaps['unreachable_functions']:
        print("\nUNREACHABLE FUNCTIONS:")
        for item in gaps['unreachable_functions']:
            print(f"  {item['function_id']}: {item['function_name']}")

    print("\n" + "="*80)
    print("FLOW EFFICIENCY ANALYSIS")
    print("="*80)
    efficiency = analyze_flow_efficiency(G)
    print(f"Cycles detected: {len(efficiency['cycles'])}")
    print(f"High fan-out functions: {len(efficiency['high_fan_out'])}")
    print(f"High fan-in functions: {len(efficiency['high_fan_in'])}")

    if efficiency['cycles']:
        print("\nCYCLES (may be intentional iterative refinement):")
        for cycle_info in efficiency['cycles'][:5]:
            print(f"  {' → '.join(cycle_info['cycle'])} → {cycle_info['cycle'][0]}")

    print("\n" + "="*80)
    print("RECOMMENDATIONS")
    print("="*80)
    recommendations = generate_recommendations(context_analysis, gaps, efficiency)
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")

    # Save detailed results
    output_path = arch_path.parent / "functional_architecture_analysis.json"
    results = {
        'metadata': {
            'input_file': str(arch_path),
            'timestamp': '2025-11-08',
            'analyzer_version': '2.0.0',
            'context_analysis_performed': has_context,
            'note': 'v2.0.0: Framework-agnostic analysis with flexible field support'
        },
        'graph_summary': {
            'total_functions': G.number_of_nodes(),
            'total_dependencies': G.number_of_edges()
        },
        'context_analysis': context_analysis,
        'gap_analysis': gaps,
        'efficiency_analysis': efficiency,
        'recommendations': recommendations
    }

    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nDetailed results saved to: {output_path}")

if __name__ == '__main__':
    main()
