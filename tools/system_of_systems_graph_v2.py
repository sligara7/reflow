#!/usr/bin/env python3
"""
System-of-Systems Graph Generator v2.0 - Framework-Agnostic Edition

Creates machine-readable JSON representation of system architecture using NetworkX.
Supports multiple architectural frameworks (UAF, Systems Biology, Social Networks, etc.)

Key Features:
- Framework-agnostic parsing via framework adapters
- Universal node/edge schema (all frameworks → same graph structure)
- Knowledge gap detection (missing nodes, edges, mediators)
- Comprehensive NetworkX analysis (centrality, paths, connectivity, clustering)
- Backward compatible with UAF-based systems

This tool builds a directed graph where:
- Nodes represent components (services, agents, genes, species, etc.)
- Edges represent connections (interfaces, relationships, interactions, etc.)
- Output is NetworkX node_link_data format + analysis results
"""

import os
import json
import networkx as nx
import sys
import argparse
from typing import Dict, List, Tuple, Any, Optional, Set
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Adjust paths for reflow directory structure
REFLOW_ROOT = Path(__file__).parent.parent
TEMPLATES_PATH = REFLOW_ROOT / "templates"
DEFINITIONS_PATH = REFLOW_ROOT / "definitions"

# =============================================================================
# FRAMEWORK ADAPTER - Load and adapt framework-specific files to universal schema
# =============================================================================

def load_framework_config(system_root: str) -> Dict[str, Any]:
    """Load framework configuration from working_memory.json.

    Returns framework metadata including field mappings for node/edge schemas.
    Falls back to UAF if no framework specified (backward compatibility).
    """
    working_memory_path = os.path.join(system_root, "context", "working_memory.json")

    # Default to UAF for backward compatibility
    default_framework = {
        "framework_id": "uaf",
        "framework_name": "UAF 1.2",
        "component_term": "service",
        "connection_term": "interface"
    }

    if not os.path.exists(working_memory_path):
        print(f"Warning: No working_memory.json found, defaulting to UAF framework")
        return default_framework

    try:
        with open(working_memory_path, 'r') as f:
            working_memory = json.load(f)

        framework_id = working_memory.get('architectural_framework', 'uaf')

        return {
            "framework_id": framework_id,
            "framework_name": working_memory.get('framework_name', 'UAF 1.2'),
            "component_term": working_memory.get('component_term', 'service'),
            "connection_term": working_memory.get('connection_term', 'interface'),
            "definitions_path": working_memory.get('definitions_path')
        }
    except Exception as e:
        print(f"Warning: Error loading working_memory.json: {e}, defaulting to UAF")
        return default_framework


def load_framework_registry(framework_id: str) -> Dict[str, Any]:
    """Load framework schema mappings from framework_registry.json."""
    registry_path = DEFINITIONS_PATH / "framework_registry.json"

    if not registry_path.exists():
        # Fallback for UAF when registry doesn't exist (backward compatibility)
        if framework_id == 'uaf':
            return {
                "node_schema": {
                    "id_field": "service_id",
                    "name_field": "service_name",
                    "type_field": "classification",
                    "functions_field": "functions",
                    "interfaces_field": "interfaces",
                    "dependencies_field": "dependencies"
                },
                "edge_schema": {
                    "id_field": "name",
                    "type_field": "interface_type",
                    "direction_field": "direction",
                    "protocol_field": "protocol"
                }
            }
        else:
            raise FileNotFoundError(f"framework_registry.json not found at {registry_path}")

    with open(registry_path, 'r') as f:
        registry = json.load(f)

    if framework_id not in registry.get('frameworks', {}):
        raise ValueError(f"Framework '{framework_id}' not found in registry. Available: {list(registry['frameworks'].keys())}")

    return registry['frameworks'][framework_id]


def adapt_component_to_universal(component_data: Dict, framework_schema: Dict) -> Dict:
    """Convert framework-specific component file to universal schema.

    All frameworks must provide:
    - node_id: unique identifier
    - node_name: human-readable name
    - node_type: classification within framework
    - functions: list of capabilities
    - interfaces: list of connections to other nodes

    Framework-specific data is preserved in 'raw' field.
    """
    node_schema = framework_schema['node_schema']

    # Extract universal properties using framework-specific field names
    universal = {
        'node_id': component_data.get(node_schema['id_field']),
        'node_name': component_data.get(node_schema['name_field']),
        'node_type': component_data.get(node_schema['type_field']),
        'functions': component_data.get(node_schema['functions_field'], []),
        'interfaces': component_data.get(node_schema['interfaces_field'], []),
        'dependencies': component_data.get(node_schema.get('dependencies_field', 'dependencies'), []),
        'raw': component_data  # Preserve full framework-specific data
    }

    # Handle missing required fields
    if not universal['node_id']:
        raise ValueError(f"Missing required field '{node_schema['id_field']}' in component data")
    if not universal['node_name']:
        universal['node_name'] = universal['node_id']  # Fallback to ID

    return universal


# =============================================================================
# INDEX LOADING
# =============================================================================

def load_component_index(index_path: str) -> Dict[str, str]:
    """Load the mapping of component_id to file path from the index file.

    Handles multiple index formats:
    - Structured index with 'components' key
    - Legacy flat format (UAF compatibility)
    - Framework-agnostic component registry

    Returns a flat mapping of component_id to file_path.
    """
    with open(index_path, 'r') as f:
        index_data = json.load(f)

    # Handle structured index format with metadata and components
    if isinstance(index_data, dict) and 'components' in index_data:
        return index_data['components']

    # Handle legacy flat format (service_id: file_path mapping)
    elif isinstance(index_data, dict):
        # Filter out non-component metadata keys
        metadata_keys = {'system_name', 'description', 'last_updated', 'version', 'metadata',
                        'framework', 'architectural_framework'}
        return {k: v for k, v in index_data.items() if k not in metadata_keys and isinstance(v, str)}

    else:
        raise ValueError(f"Invalid index format: expected dict with 'components' key or flat component mapping")


# =============================================================================
# GRAPH BUILDING - Framework-Agnostic
# =============================================================================

def build_universal_graph(index: Dict[str, str], framework_schema: Dict, system_root: str) -> nx.DiGraph:
    """Build a directed graph from component architecture files using universal schema.

    All frameworks map to the same structure:
    - Nodes: components with id, name, type, functions, interfaces
    - Edges: connections between components with type and direction

    Args:
        index: Dictionary mapping component_id to file paths
        framework_schema: Schema from framework_registry.json
        system_root: System root directory for resolving relative paths

    Returns:
        NetworkX DiGraph with universal node/edge attributes
    """
    G = nx.DiGraph()
    component_data_cache = {}

    # Pass 1: Load all components and add as nodes
    print(f"Loading {len(index)} components...")
    for component_id, file_path in index.items():
        # Handle relative paths
        if not os.path.isabs(file_path):
            file_path = os.path.join(system_root, file_path)

        try:
            with open(file_path, 'r') as f:
                raw_data = json.load(f)
        except FileNotFoundError:
            print(f"Warning: Could not find file {file_path} for component {component_id}")
            continue
        except json.JSONDecodeError:
            print(f"Warning: Invalid JSON in {file_path} for component {component_id}")
            continue

        try:
            # Convert to universal schema
            universal_node = adapt_component_to_universal(raw_data, framework_schema)
            component_data_cache[component_id] = universal_node

            # Add node to graph with universal attributes
            G.add_node(
                component_id,
                name=universal_node['node_name'],
                type=universal_node['node_type'],
                functions=universal_node['functions'],
                interfaces=universal_node['interfaces'],
                dependencies=universal_node['dependencies'],
                raw=universal_node['raw']
            )

        except Exception as e:
            print(f"Warning: Error processing {component_id}: {e}")
            continue

    print(f"Added {G.number_of_nodes()} nodes to graph")

    # Pass 2: Add edges based on dependencies and interfaces
    print("Building edges from dependencies and interfaces...")
    for component_id, universal_node in component_data_cache.items():
        if component_id not in G:
            continue

        # Add edges from dependencies
        for dep in universal_node['dependencies']:
            # Try to match dependency to component_id
            dep_id = match_dependency_to_component(dep, component_data_cache)
            if dep_id and dep_id in G:
                G.add_edge(component_id, dep_id, type='dependency', interaction_type='requires')

        # Add edges from interfaces
        for interface in universal_node['interfaces']:
            if not isinstance(interface, dict):
                continue

            # Check for explicit connections in interface
            connected_to = interface.get('connects_to', interface.get('connected_services',
                                        interface.get('target_components', [])))

            if isinstance(connected_to, str):
                connected_to = [connected_to]

            for target in connected_to:
                target_id = match_dependency_to_component(target, component_data_cache)
                if target_id and target_id in G:
                    edge_type = interface.get('type', interface.get('interface_type',
                                             interface.get('interaction_type', 'connection')))
                    direction = interface.get('direction', 'directed')

                    G.add_edge(component_id, target_id,
                              type='interface',
                              interaction_type=edge_type,
                              direction=direction)

    print(f"Added {G.number_of_edges()} edges to graph")

    return G


def match_dependency_to_component(dependency_name: str, components: Dict[str, Dict]) -> Optional[str]:
    """Match a dependency string to a component_id.

    Tries multiple matching strategies:
    - Exact match on component_id
    - Match on node_name (case-insensitive, underscore/space normalized)
    - Partial match on node_name
    """
    if not dependency_name:
        return None

    dep_normalized = dependency_name.lower().replace(' ', '_').replace('-', '_')

    # Exact match on component_id
    if dependency_name in components:
        return dependency_name

    # Try normalized matching
    for comp_id, comp_data in components.items():
        # Match on component_id normalized
        if comp_id.lower().replace(' ', '_').replace('-', '_') == dep_normalized:
            return comp_id

        # Match on node_name normalized
        node_name = comp_data.get('node_name', '').lower().replace(' ', '_').replace('-', '_')
        if node_name == dep_normalized:
            return comp_id

    # Partial match (for cases like "rules_service" matching "game_rules_service")
    for comp_id, comp_data in components.items():
        if dep_normalized in comp_id.lower():
            return comp_id
        node_name = comp_data.get('node_name', '').lower().replace(' ', '_')
        if dep_normalized in node_name:
            return comp_id

    return None


# =============================================================================
# KNOWLEDGE GAP DETECTION
# =============================================================================

def detect_knowledge_gaps(G: nx.DiGraph, component_data: Dict[str, Dict]) -> Dict[str, List[Dict]]:
    """Identify missing nodes or edges based on graph structure and component data.

    Detects:
    1. Orphaned interfaces: Consumed interface with no provider
    2. Unmet dependencies: Required capability not provided by any component
    3. Implied mediators: Two components interact but incompatible interfaces (missing translator)
    4. Missing feedback: Known effect without path in graph
    5. Structural holes: High betweenness nodes (fragile single points of contact)
    6. Unexplained outputs: Component provides interface but no function generates it

    Returns dictionary of gap types with detected instances.
    """
    gaps = {
        'orphaned_interfaces': [],
        'unmet_dependencies': [],
        'implied_mediators': [],
        'structural_holes': [],
        'unexplained_outputs': [],
        'missing_bidirectional': []
    }

    # Collect all provided and consumed interfaces
    provided_interfaces = defaultdict(list)  # interface_type -> [component_ids]
    consumed_interfaces = defaultdict(list)  # interface_type -> [component_ids]

    for node_id in G.nodes():
        node_data = G.nodes[node_id]
        interfaces = node_data.get('interfaces', [])

        for iface in interfaces:
            if not isinstance(iface, dict):
                continue

            iface_type = iface.get('type', iface.get('interface_type', iface.get('name', 'unknown')))
            direction = iface.get('direction', 'unknown')

            if direction in ['provided', 'out', 'provides']:
                provided_interfaces[iface_type].append(node_id)
            elif direction in ['consumed', 'in', 'requires']:
                consumed_interfaces[iface_type].append(node_id)
            elif direction == 'bidirectional':
                provided_interfaces[iface_type].append(node_id)
                consumed_interfaces[iface_type].append(node_id)

    # 1. Detect orphaned interfaces (consumed but not provided)
    for iface_type, consumers in consumed_interfaces.items():
        if iface_type not in provided_interfaces or len(provided_interfaces[iface_type]) == 0:
            gaps['orphaned_interfaces'].append({
                'interface_type': iface_type,
                'consumers': consumers,
                'severity': 'warning',
                'description': f"Interface '{iface_type}' is consumed by {len(consumers)} component(s) but not provided by any",
                'implication': "Missing component that should provide this interface, or interface type mismatch",
                'recommendation': f"Add component that provides '{iface_type}' interface or verify interface naming"
            })

    # 2. Detect unmet dependencies
    all_provided_capabilities = set()
    for node_id in G.nodes():
        functions = G.nodes[node_id].get('functions', [])
        all_provided_capabilities.update(functions)

    for node_id in G.nodes():
        dependencies = G.nodes[node_id].get('dependencies', [])
        for dep in dependencies:
            # Check if any component provides this capability
            if dep not in G.nodes() and dep not in all_provided_capabilities:
                gaps['unmet_dependencies'].append({
                    'component': node_id,
                    'required_capability': dep,
                    'severity': 'warning',
                    'description': f"Component '{node_id}' requires '{dep}' but no component provides it",
                    'implication': "Missing component or function",
                    'recommendation': f"Add component that provides '{dep}' or add function to existing component"
                })

    # 3. Detect structural holes (high betweenness centrality)
    if G.number_of_nodes() > 2:
        try:
            betweenness = nx.betweenness_centrality(G)
            # Find nodes with exceptionally high betweenness (top 10% or > 0.5)
            threshold = 0.5
            high_betweenness_nodes = [(node, score) for node, score in betweenness.items() if score > threshold]

            for node, score in high_betweenness_nodes:
                # Check if removing this node disconnects the graph
                G_copy = G.copy()
                G_copy.remove_node(node)
                num_components = nx.number_weakly_connected_components(G_copy)

                if num_components > 1:
                    gaps['structural_holes'].append({
                        'broker_node': node,
                        'betweenness_centrality': round(score, 3),
                        'severity': 'info',
                        'description': f"Component '{node}' is a critical broker (betweenness={score:.3f})",
                        'implication': "System fragile; if this component fails, network disconnects",
                        'recommendation': f"Add redundant connections to bypass '{node}' or strengthen this component"
                    })
        except:
            pass  # Graph might not be suitable for betweenness calculation

    # 4. Detect unexplained outputs
    for node_id in G.nodes():
        node_data = G.nodes[node_id]
        interfaces = node_data.get('interfaces', [])
        functions = node_data.get('functions', [])

        for iface in interfaces:
            if not isinstance(iface, dict):
                continue

            direction = iface.get('direction', '')
            if direction in ['provided', 'out', 'provides']:
                iface_name = iface.get('name', iface.get('type', 'unknown'))

                # Check if any function mentions this interface
                function_str = ' '.join(str(f).lower() for f in functions)
                if iface_name.lower() not in function_str:
                    gaps['unexplained_outputs'].append({
                        'component': node_id,
                        'interface': iface_name,
                        'severity': 'info',
                        'description': f"Component '{node_id}' provides '{iface_name}' but no function describes how",
                        'implication': "Missing function documentation or hidden internal mechanism",
                        'recommendation': f"Document function that produces '{iface_name}' interface"
                    })

    # 5. Detect missing bidirectional connections
    # If A->B exists and B->A should exist (bidirectional) but doesn't
    for u, v, data in G.edges(data=True):
        if data.get('direction') == 'bidirectional':
            if not G.has_edge(v, u):
                gaps['missing_bidirectional'].append({
                    'from': u,
                    'to': v,
                    'severity': 'warning',
                    'description': f"Edge {u}->{v} marked bidirectional but reverse edge {v}->{u} missing",
                    'implication': "Inconsistent bidirectional relationship",
                    'recommendation': f"Add edge from '{v}' to '{u}' or change direction to 'directed'"
                })

    return gaps


# =============================================================================
# NETWORKX ANALYSIS - Comprehensive Graph Theory Methods
# =============================================================================

def analyze_centrality(G: nx.DiGraph) -> Dict[str, Any]:
    """Calculate all centrality measures.

    Returns:
        - degree_centrality: Number of connections (in + out)
        - betweenness_centrality: Frequency on shortest paths (brokerage)
        - closeness_centrality: Average distance to all others (reach)
        - eigenvector_centrality: Connected to well-connected nodes (influence)
        - pagerank: Importance based on incoming links
    """
    results = {}

    try:
        results['degree_centrality'] = nx.degree_centrality(G)
    except:
        results['degree_centrality'] = "Error computing degree centrality"

    try:
        results['betweenness_centrality'] = nx.betweenness_centrality(G)
    except:
        results['betweenness_centrality'] = "Error computing betweenness centrality"

    try:
        results['closeness_centrality'] = nx.closeness_centrality(G)
    except:
        results['closeness_centrality'] = "Error computing closeness centrality"

    try:
        results['eigenvector_centrality'] = nx.eigenvector_centrality(G, max_iter=1000)
    except:
        results['eigenvector_centrality'] = "Error computing eigenvector centrality (may not converge)"

    try:
        results['pagerank'] = nx.pagerank(G)
    except:
        results['pagerank'] = "Error computing PageRank"

    # Top nodes for each measure
    top_k = 5
    results['top_nodes'] = {}
    for measure, scores in results.items():
        if isinstance(scores, dict):
            top_nodes = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
            results['top_nodes'][measure] = top_nodes

    return results


def analyze_paths(G: nx.DiGraph) -> Dict[str, Any]:
    """Analyze path-related metrics.

    Returns:
        - shortest_paths: All-pairs shortest paths
        - diameter: Longest shortest path
        - average_path_length: Mean shortest path length
        - eccentricity: Maximum distance from each node
    """
    results = {}

    # For directed graphs, use weakly connected component
    if nx.is_weakly_connected(G):
        try:
            results['diameter'] = nx.diameter(G.to_undirected())
        except:
            results['diameter'] = "Graph not connected or empty"

        try:
            results['average_path_length'] = nx.average_shortest_path_length(G.to_undirected())
        except:
            results['average_path_length'] = "Error computing average path length"
    else:
        results['diameter'] = "Graph not connected (multiple components)"
        results['average_path_length'] = "Graph not connected"

    # Eccentricity (for each node)
    try:
        results['eccentricity'] = nx.eccentricity(G.to_undirected())
    except:
        results['eccentricity'] = "Error computing eccentricity"

    return results


def analyze_connectivity(G: nx.DiGraph) -> Dict[str, Any]:
    """Analyze graph connectivity.

    Returns:
        - connected_components: Number and size of components
        - node_connectivity: Min nodes to remove to disconnect
        - edge_connectivity: Min edges to remove to disconnect
        - bridges: Edges whose removal disconnects graph
    """
    results = {}

    # Connected components (use weakly connected for directed graphs)
    components = list(nx.weakly_connected_components(G))
    results['num_components'] = len(components)
    results['component_sizes'] = [len(c) for c in components]
    results['largest_component_size'] = max(results['component_sizes']) if components else 0

    # Node and edge connectivity (for largest component)
    if len(components) > 0:
        largest_component = max(components, key=len)
        subgraph = G.subgraph(largest_component)

        try:
            results['node_connectivity'] = nx.node_connectivity(subgraph.to_undirected())
        except:
            results['node_connectivity'] = "Error computing node connectivity"

        try:
            results['edge_connectivity'] = nx.edge_connectivity(subgraph.to_undirected())
        except:
            results['edge_connectivity'] = "Error computing edge connectivity"

        # Bridges
        try:
            bridges = list(nx.bridges(subgraph.to_undirected()))
            results['bridges'] = [{"from": u, "to": v} for u, v in bridges]
            results['num_bridges'] = len(bridges)
        except:
            results['bridges'] = "Error finding bridges"

    return results


def analyze_clustering(G: nx.DiGraph) -> Dict[str, Any]:
    """Analyze clustering and community structure.

    Returns:
        - clustering_coefficient: Degree of node clustering
        - transitivity: Global clustering coefficient
        - triangles: Number of triangles per node
    """
    results = {}

    # Convert to undirected for clustering
    G_undirected = G.to_undirected()

    try:
        results['clustering_coefficient'] = nx.clustering(G_undirected)
        results['average_clustering'] = nx.average_clustering(G_undirected)
    except:
        results['clustering_coefficient'] = "Error computing clustering coefficient"

    try:
        results['transitivity'] = nx.transitivity(G_undirected)
    except:
        results['transitivity'] = "Error computing transitivity"

    try:
        results['triangles'] = nx.triangles(G_undirected)
    except:
        results['triangles'] = "Error counting triangles"

    return results


def analyze_properties(G: nx.DiGraph) -> Dict[str, Any]:
    """Calculate general graph properties.

    Returns:
        - density: How close to complete graph
        - assortativity: Tendency of similar nodes to connect
        - reciprocity: Fraction of bidirectional edges
    """
    results = {}

    # Basic stats
    results['num_nodes'] = G.number_of_nodes()
    results['num_edges'] = G.number_of_edges()

    # Density
    try:
        results['density'] = nx.density(G)
    except:
        results['density'] = "Error computing density"

    # Degree assortativity
    try:
        results['degree_assortativity'] = nx.degree_assortativity_coefficient(G)
    except:
        results['degree_assortativity'] = "Error computing assortativity"

    # Reciprocity (for directed graphs)
    try:
        results['reciprocity'] = nx.reciprocity(G)
    except:
        results['reciprocity'] = "Error computing reciprocity"

    # Degree distribution
    degrees = [d for n, d in G.degree()]
    if degrees:
        results['degree_distribution'] = {
            'min': min(degrees),
            'max': max(degrees),
            'mean': sum(degrees) / len(degrees),
            'median': sorted(degrees)[len(degrees) // 2]
        }

    return results


def run_all_analysis(G: nx.DiGraph) -> Dict[str, Any]:
    """Run all NetworkX analysis methods and return comprehensive results."""
    print("Running comprehensive NetworkX analysis...")

    analysis_results = {
        'metadata': {
            'analysis_date': datetime.now().isoformat(),
            'num_nodes': G.number_of_nodes(),
            'num_edges': G.number_of_edges()
        }
    }

    print("  - Computing centrality measures...")
    analysis_results['centrality'] = analyze_centrality(G)

    print("  - Analyzing paths and distances...")
    analysis_results['paths'] = analyze_paths(G)

    print("  - Analyzing connectivity...")
    analysis_results['connectivity'] = analyze_connectivity(G)

    print("  - Analyzing clustering...")
    analysis_results['clustering'] = analyze_clustering(G)

    print("  - Computing graph properties...")
    analysis_results['properties'] = analyze_properties(G)

    return analysis_results


# =============================================================================
# ARCHITECTURAL ISSUE DETECTION (from v1, enhanced)
# =============================================================================

def detect_architectural_issues(G: nx.DiGraph) -> Dict[str, List[Dict]]:
    """Detect architectural problems (circular deps, orphans, etc.).

    Enhanced version from v1 with framework-agnostic support.
    """
    issues = {
        'circular_dependencies': [],
        'orphaned_nodes': [],
        'missing_interfaces': [],
        'inconsistent_protocols': [],
        'security_gaps': [],
        'performance_bottlenecks': [],
        'async_sync_consistency': []
    }

    # 1. Circular dependencies
    try:
        cycles = list(nx.simple_cycles(G))
        for cycle in cycles:
            if len(cycle) > 1:  # Ignore self-loops
                issues['circular_dependencies'].append({
                    'cycle': cycle,
                    'severity': 'error',
                    'description': f"Circular dependency detected: {' -> '.join(cycle)} -> {cycle[0]}",
                    'recommendation': "Break cycle by introducing interface, reversing dependency, or using event-driven pattern"
                })
    except:
        pass

    # 2. Orphaned nodes (no connections)
    for node in G.nodes():
        if G.degree(node) == 0:
            issues['orphaned_nodes'].append({
                'node': node,
                'severity': 'warning',
                'description': f"Component '{node}' has no connections to other components",
                'recommendation': "Verify if component should be connected or remove if unused"
            })

    # 3. Performance bottlenecks (high in-degree)
    for node in G.nodes():
        in_degree = G.in_degree(node)
        if in_degree > 5:
            issues['performance_bottlenecks'].append({
                'node': node,
                'in_degree': in_degree,
                'severity': 'info',
                'description': f"Component '{node}' has high fan-in ({in_degree} dependencies)",
                'recommendation': "Consider load testing, caching, or splitting into multiple components"
            })

    return issues


# =============================================================================
# OUTPUT GENERATION
# =============================================================================

def generate_output(G: nx.DiGraph, output_path: str, framework_config: Dict,
                   knowledge_gaps: Optional[Dict] = None,
                   architectural_issues: Optional[Dict] = None,
                   analysis_results: Optional[Dict] = None):
    """Generate system-of-systems graph JSON output."""

    # Convert graph to node-link format
    graph_data = nx.node_link_data(G)

    # Build output structure
    output = {
        'metadata': {
            'generated': datetime.now().isoformat(),
            'framework': framework_config.get('framework_name', 'Unknown'),
            'framework_id': framework_config.get('framework_id', 'unknown'),
            'component_term': framework_config.get('component_term', 'component'),
            'connection_term': framework_config.get('connection_term', 'connection'),
            'num_nodes': G.number_of_nodes(),
            'num_edges': G.number_of_edges(),
            'tool_version': '2.0'
        },
        'graph': graph_data
    }

    if knowledge_gaps:
        output['knowledge_gaps'] = knowledge_gaps
        # Summary
        total_gaps = sum(len(v) for v in knowledge_gaps.values())
        output['knowledge_gaps_summary'] = {
            'total_gaps': total_gaps,
            'by_type': {k: len(v) for k, v in knowledge_gaps.items()}
        }

    if architectural_issues:
        output['architectural_issues'] = architectural_issues
        # Summary
        total_issues = sum(len(v) for v in architectural_issues.values())
        output['architectural_issues_summary'] = {
            'total_issues': total_issues,
            'by_type': {k: len(v) for k, v in architectural_issues.items()}
        }

    if analysis_results:
        output['graph_analysis'] = analysis_results

    # Write output
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nOutput written to: {output_path}")
    print(f"Framework: {framework_config.get('framework_name')}")
    print(f"Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")

    if knowledge_gaps:
        total_gaps = sum(len(v) for v in knowledge_gaps.values())
        print(f"Knowledge gaps detected: {total_gaps}")

    if architectural_issues:
        total_issues = sum(len(v) for v in architectural_issues.values())
        print(f"Architectural issues detected: {total_issues}")


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='System-of-Systems Graph Generator v2.0 - Framework-Agnostic Edition',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Basic usage (UAF framework, auto-detected from working_memory.json)
  python3 system_of_systems_graph_v2.py /path/to/system/specs/machine/index.json

  # With knowledge gap detection
  python3 system_of_systems_graph_v2.py index.json --detect-gaps

  # With comprehensive NetworkX analysis
  python3 system_of_systems_graph_v2.py index.json --analyze-all

  # Specific analysis methods
  python3 system_of_systems_graph_v2.py index.json --centrality --paths --clustering

  # Custom output location
  python3 system_of_systems_graph_v2.py index.json -o custom_graph.json

Supported Frameworks:
  - UAF 1.2 (Unified Architecture Framework) - default
  - Systems Biology (gene networks, metabolic pathways)
  - Social Network Analysis (organizations, communities)
  - Ecological Systems (food webs, ecosystems)
  - Complex Adaptive Systems (markets, emergent systems)
  - Custom (user-defined frameworks)
        '''
    )

    parser.add_argument('index_file', help='Path to index.json file')
    parser.add_argument('-o', '--output', help='Output file path (default: system_of_systems_graph.json)')

    # Analysis flags
    parser.add_argument('--detect-gaps', action='store_true',
                       help='Enable knowledge gap detection')
    parser.add_argument('--analyze-issues', action='store_true',
                       help='Detect architectural issues (circular deps, orphans, etc.)')

    # NetworkX analysis options
    parser.add_argument('--centrality', action='store_true',
                       help='Compute centrality measures (degree, betweenness, closeness, eigenvector, PageRank)')
    parser.add_argument('--paths', action='store_true',
                       help='Analyze paths (shortest paths, diameter, average path length)')
    parser.add_argument('--connectivity', action='store_true',
                       help='Analyze connectivity (components, bridges, connectivity metrics)')
    parser.add_argument('--clustering', action='store_true',
                       help='Analyze clustering (clustering coefficient, transitivity)')
    parser.add_argument('--properties', action='store_true',
                       help='Compute graph properties (density, assortativity, reciprocity)')
    parser.add_argument('--analyze-all', action='store_true',
                       help='Run all analysis methods (centrality, paths, connectivity, clustering, properties)')

    args = parser.parse_args()

    # Determine system root from index file path
    index_path = os.path.abspath(args.index_file)
    system_root = os.path.dirname(os.path.dirname(index_path))  # Go up from specs/machine/

    print(f"System root: {system_root}")
    print(f"Index file: {index_path}")

    # Load framework configuration
    print("\nLoading framework configuration...")
    framework_config = load_framework_config(system_root)
    print(f"Framework: {framework_config['framework_name']} ({framework_config['framework_id']})")
    print(f"Terminology: {framework_config['component_term']} nodes connected by {framework_config['connection_term']} edges")

    # Load framework schema
    framework_schema = load_framework_registry(framework_config['framework_id'])

    # Load index
    print("\nLoading component index...")
    index = load_component_index(index_path)
    print(f"Found {len(index)} components in index")

    # Build graph
    print("\nBuilding system-of-systems graph...")
    G = build_universal_graph(index, framework_schema, system_root)

    # Optional: Detect knowledge gaps
    knowledge_gaps = None
    if args.detect_gaps:
        print("\nDetecting knowledge gaps...")
        # Need component data for gap detection
        component_data = {}
        for comp_id in G.nodes():
            raw_data = G.nodes[comp_id].get('raw', {})
            component_data[comp_id] = {
                'node_id': comp_id,
                'node_name': G.nodes[comp_id].get('name'),
                'node_type': G.nodes[comp_id].get('type'),
                'functions': G.nodes[comp_id].get('functions', []),
                'interfaces': G.nodes[comp_id].get('interfaces', []),
                'raw': raw_data
            }

        knowledge_gaps = detect_knowledge_gaps(G, component_data)
        total_gaps = sum(len(v) for v in knowledge_gaps.values())
        print(f"Detected {total_gaps} potential knowledge gaps")
        for gap_type, gaps in knowledge_gaps.items():
            if gaps:
                print(f"  - {gap_type}: {len(gaps)}")

    # Optional: Detect architectural issues
    architectural_issues = None
    if args.analyze_issues:
        print("\nDetecting architectural issues...")
        architectural_issues = detect_architectural_issues(G)
        total_issues = sum(len(v) for v in architectural_issues.values())
        print(f"Detected {total_issues} architectural issues")
        for issue_type, issues in architectural_issues.items():
            if issues:
                print(f"  - {issue_type}: {len(issues)}")

    # Optional: Run NetworkX analysis
    analysis_results = None
    if args.analyze_all or any([args.centrality, args.paths, args.connectivity,
                                args.clustering, args.properties]):
        analysis_results = {}

        if args.analyze_all or args.centrality:
            analysis_results['centrality'] = analyze_centrality(G)

        if args.analyze_all or args.paths:
            analysis_results['paths'] = analyze_paths(G)

        if args.analyze_all or args.connectivity:
            analysis_results['connectivity'] = analyze_connectivity(G)

        if args.analyze_all or args.clustering:
            analysis_results['clustering'] = analyze_clustering(G)

        if args.analyze_all or args.properties:
            analysis_results['properties'] = analyze_properties(G)

    # Generate output
    if args.output:
        output_path = args.output
    else:
        # Default output location
        output_path = os.path.join(system_root, 'specs', 'machine', 'graphs', 'system_of_systems_graph.json')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

    generate_output(G, output_path, framework_config, knowledge_gaps,
                   architectural_issues, analysis_results)

    print("\n✓ Graph generation complete!")


if __name__ == '__main__':
    main()
