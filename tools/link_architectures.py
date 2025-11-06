#!/usr/bin/env python3
"""
Link Architectures Tool for Chain Reflow

Core execution tool that links two system_of_systems_graph.json files by:
1. Discovering touchpoints (interfaces, dependencies, shared components)
2. Creating edges between the graphs
3. Preserving both architectures' metadata
4. Generating integrated graph output

This is the PRIMARY execution tool that workflows delegate to.
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class Touchpoint:
    """Represents a connection point between two architectures"""
    source_graph: str
    source_node: str
    target_graph: str
    target_node: str
    touchpoint_type: str  # "interface", "dependency", "data_flow", "shared_component"
    confidence: float
    rationale: str
    bidirectional: bool = False


class GraphLinker:
    """Links two architecture graphs by discovering and creating touchpoints"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.touchpoints: List[Touchpoint] = []

    def load_graph(self, filepath: Path) -> Dict[str, Any]:
        """Load architecture graph from JSON"""
        if self.verbose:
            print(f"Loading graph: {filepath}")

        with open(filepath, 'r') as f:
            graph = json.load(f)

        # Validate basic structure (flexible - accept various formats)
        has_metadata = 'architecture_metadata' in graph or 'system_metadata' in graph or 'metadata' in graph
        has_nodes = 'nodes' in graph or 'components' in graph or 'functions' in graph or 'services' in graph

        if not (has_metadata or has_nodes):
            raise ValueError(f"Invalid graph format: {filepath} - needs metadata or node/component list")

        return graph

    def discover_touchpoints(self,
                           graph_a: Dict[str, Any],
                           graph_b: Dict[str, Any],
                           graph_a_name: str,
                           graph_b_name: str) -> List[Touchpoint]:
        """
        Discover touchpoints between two graphs.

        Touchpoint discovery strategies:
        1. Name matching (similar node names)
        2. Interface matching (provides/requires)
        3. Dependency matching (explicit dependencies)
        4. Data flow matching (shared data types)
        """
        touchpoints = []

        nodes_a = self._extract_nodes(graph_a)
        nodes_b = self._extract_nodes(graph_b)

        if self.verbose:
            print(f"Discovering touchpoints between {graph_a_name} ({len(nodes_a)} nodes) and {graph_b_name} ({len(nodes_b)} nodes)")

        # Strategy 1: Name-based matching
        touchpoints.extend(self._match_by_name(nodes_a, nodes_b, graph_a_name, graph_b_name))

        # Strategy 2: Interface matching (provides/requires)
        touchpoints.extend(self._match_by_interface(graph_a, graph_b, graph_a_name, graph_b_name))

        # Strategy 3: Dependency matching
        touchpoints.extend(self._match_by_dependency(graph_a, graph_b, graph_a_name, graph_b_name))

        # Strategy 4: Data flow matching
        touchpoints.extend(self._match_by_dataflow(nodes_a, nodes_b, graph_a_name, graph_b_name))

        if self.verbose:
            print(f"Discovered {len(touchpoints)} touchpoints")

        return touchpoints

    def _extract_nodes(self, graph: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract node list from graph (handles multiple formats)"""
        if 'nodes' in graph:
            return graph['nodes']
        elif 'components' in graph:
            return graph['components']
        elif 'functions' in graph:
            return graph['functions']
        else:
            return []

    def _match_by_name(self,
                      nodes_a: List[Dict],
                      nodes_b: List[Dict],
                      graph_a_name: str,
                      graph_b_name: str) -> List[Touchpoint]:
        """Match nodes by similar names"""
        touchpoints = []

        for node_a in nodes_a:
            node_a_id = node_a.get('id', node_a.get('function_id', ''))
            node_a_name = node_a.get('name', node_a.get('function_name', '')).lower()

            for node_b in nodes_b:
                node_b_id = node_b.get('id', node_b.get('function_id', ''))
                node_b_name = node_b.get('name', node_b.get('function_name', '')).lower()

                # Simple similarity: shared keywords
                words_a = set(node_a_name.split())
                words_b = set(node_b_name.split())
                overlap = words_a & words_b

                if len(overlap) >= 2:  # At least 2 shared words
                    confidence = len(overlap) / max(len(words_a), len(words_b))
                    touchpoints.append(Touchpoint(
                        source_graph=graph_a_name,
                        source_node=node_a_id,
                        target_graph=graph_b_name,
                        target_node=node_b_id,
                        touchpoint_type="shared_component",
                        confidence=confidence,
                        rationale=f"Name similarity: shared keywords {overlap}",
                        bidirectional=True
                    ))

        return touchpoints

    def _match_by_interface(self,
                           graph_a: Dict,
                           graph_b: Dict,
                           graph_a_name: str,
                           graph_b_name: str) -> List[Touchpoint]:
        """Match by interface contracts (provides/requires)"""
        touchpoints = []

        # Extract interfaces (handle both dict and nested dict formats)
        interfaces_dict_a = graph_a.get('interfaces', {})
        interfaces_dict_b = graph_b.get('interfaces', {})

        # Format 1: interfaces as list
        interfaces_a = interfaces_dict_a if isinstance(interfaces_dict_a, list) else []
        interfaces_b = interfaces_dict_b if isinstance(interfaces_dict_b, list) else []

        # Format 2: interfaces as dict with provided/required keys
        provided_a = interfaces_dict_a.get('provided', []) if isinstance(interfaces_dict_a, dict) else []
        required_b = interfaces_dict_b.get('required', []) if isinstance(interfaces_dict_b, dict) else []

        # Match provided from A with required from B
        for prov in provided_a:
            if isinstance(prov, dict):
                prov_endpoint = prov.get('endpoint', prov.get('interface_id', ''))

                for req in required_b:
                    if isinstance(req, dict):
                        req_endpoint = req.get('endpoint', req.get('interface_id', ''))

                        # Simple match: same endpoint path
                        if prov_endpoint and req_endpoint and prov_endpoint in req_endpoint:
                            touchpoints.append(Touchpoint(
                                source_graph=graph_a_name,
                                source_node=graph_a.get('service_id', 'system'),
                                target_graph=graph_b_name,
                                target_node=graph_b.get('service_id', 'system'),
                                touchpoint_type="interface",
                                confidence=0.9,
                                rationale=f"Interface match: {prov_endpoint}",
                                bidirectional=False
                            ))

        # Legacy format support
        for iface_a in interfaces_a:
            if isinstance(iface_a, dict) and iface_a.get('type') == 'provides':
                iface_a_id = iface_a.get('interface_id', '')

                for iface_b in interfaces_b:
                    if isinstance(iface_b, dict) and iface_b.get('type') == 'requires':
                        iface_b_id = iface_b.get('interface_id', '')

                        if iface_a_id == iface_b_id:
                            touchpoints.append(Touchpoint(
                                source_graph=graph_a_name,
                                source_node=iface_a.get('component_id', 'unknown'),
                                target_graph=graph_b_name,
                                target_node=iface_b.get('component_id', 'unknown'),
                                touchpoint_type="interface",
                                confidence=0.9,
                                rationale=f"Interface match: {iface_a_id}",
                                bidirectional=False
                            ))

        return touchpoints

    def _match_by_dependency(self,
                            graph_a: Dict,
                            graph_b: Dict,
                            graph_a_name: str,
                            graph_b_name: str) -> List[Touchpoint]:
        """Match by explicit dependencies"""
        touchpoints = []

        # Check if either graph explicitly lists dependencies on the other
        deps_a = graph_a.get('dependencies', {}).get('requires', [])
        deps_b = graph_b.get('dependencies', {}).get('requires', [])

        for dep in deps_a:
            if dep.get('system') == graph_b_name:
                touchpoints.append(Touchpoint(
                    source_graph=graph_a_name,
                    source_node=dep.get('component', 'system_level'),
                    target_graph=graph_b_name,
                    target_node=dep.get('component', 'system_level'),
                    touchpoint_type="dependency",
                    confidence=0.95,
                    rationale="Explicit dependency declaration",
                    bidirectional=False
                ))

        for dep in deps_b:
            if dep.get('system') == graph_a_name:
                touchpoints.append(Touchpoint(
                    source_graph=graph_b_name,
                    source_node=dep.get('component', 'system_level'),
                    target_graph=graph_a_name,
                    target_node=dep.get('component', 'system_level'),
                    touchpoint_type="dependency",
                    confidence=0.95,
                    rationale="Explicit dependency declaration",
                    bidirectional=False
                ))

        return touchpoints

    def _match_by_dataflow(self,
                          nodes_a: List[Dict],
                          nodes_b: List[Dict],
                          graph_a_name: str,
                          graph_b_name: str) -> List[Touchpoint]:
        """Match by data flow (output of A matches input of B)"""
        touchpoints = []

        for node_a in nodes_a:
            outputs_a = node_a.get('outputs', [])
            node_a_id = node_a.get('id', node_a.get('function_id', ''))

            for node_b in nodes_b:
                inputs_b = node_b.get('inputs', [])
                node_b_id = node_b.get('id', node_b.get('function_id', ''))

                # Check if any output of A matches input of B
                shared_data = set(outputs_a) & set(inputs_b)
                if shared_data:
                    touchpoints.append(Touchpoint(
                        source_graph=graph_a_name,
                        source_node=node_a_id,
                        target_graph=graph_b_name,
                        target_node=node_b_id,
                        touchpoint_type="data_flow",
                        confidence=0.8,
                        rationale=f"Data flow: {shared_data}",
                        bidirectional=False
                    ))

        return touchpoints

    def create_linked_graph(self,
                           graph_a: Dict[str, Any],
                           graph_b: Dict[str, Any],
                           graph_a_name: str,
                           graph_b_name: str,
                           touchpoints: List[Touchpoint]) -> Dict[str, Any]:
        """
        Create integrated graph from two graphs and their touchpoints.

        Strategy: Merge graphs while preserving provenance
        """
        if self.verbose:
            print(f"Creating linked graph with {len(touchpoints)} touchpoints")

        linked_graph = {
            "architecture_metadata": {
                "name": f"Linked: {graph_a_name} + {graph_b_name}",
                "description": f"Integration of {graph_a_name} and {graph_b_name}",
                "created": datetime.now().isoformat(),
                "source_graphs": [graph_a_name, graph_b_name],
                "framework": graph_a.get('architecture_metadata', {}).get('framework', 'unknown'),
                "linking_tool": "link_architectures.py v1.0.0"
            },
            "nodes": [],
            "edges": [],
            "touchpoints": []
        }

        # Add all nodes from both graphs with provenance
        nodes_a = self._extract_nodes(graph_a)
        nodes_b = self._extract_nodes(graph_b)

        for node in nodes_a:
            node_copy = node.copy()
            node_copy['provenance'] = graph_a_name
            linked_graph['nodes'].append(node_copy)

        for node in nodes_b:
            node_copy = node.copy()
            node_copy['provenance'] = graph_b_name
            linked_graph['nodes'].append(node_copy)

        # Add existing edges from both graphs
        edges_a = graph_a.get('edges', []) + graph_a.get('function_dependencies', [])
        edges_b = graph_b.get('edges', []) + graph_b.get('function_dependencies', [])

        for edge in edges_a:
            edge_copy = edge.copy()
            edge_copy['provenance'] = graph_a_name
            linked_graph['edges'].append(edge_copy)

        for edge in edges_b:
            edge_copy = edge.copy()
            edge_copy['provenance'] = graph_b_name
            linked_graph['edges'].append(edge_copy)

        # Add touchpoint edges (the new cross-graph connections)
        for tp in touchpoints:
            linked_graph['touchpoints'].append(asdict(tp))

            # Create edge representation
            edge = {
                "source": tp.source_node,
                "target": tp.target_node,
                "type": tp.touchpoint_type,
                "confidence": tp.confidence,
                "rationale": tp.rationale,
                "cross_graph": True,
                "provenance": "linking_analysis"
            }
            linked_graph['edges'].append(edge)

            if tp.bidirectional:
                reverse_edge = edge.copy()
                reverse_edge['source'] = tp.target_node
                reverse_edge['target'] = tp.source_node
                linked_graph['edges'].append(reverse_edge)

        return linked_graph

    def link_graphs(self,
                   graph_a_path: Path,
                   graph_b_path: Path,
                   output_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Main linking function: Load graphs, discover touchpoints, create linked graph.
        """
        # Load graphs
        graph_a = self.load_graph(graph_a_path)
        graph_b = self.load_graph(graph_b_path)

        graph_a_name = graph_a.get('architecture_metadata', {}).get('name', graph_a_path.stem)
        graph_b_name = graph_b.get('architecture_metadata', {}).get('name', graph_b_path.stem)

        # Discover touchpoints
        touchpoints = self.discover_touchpoints(graph_a, graph_b, graph_a_name, graph_b_name)
        self.touchpoints = touchpoints

        # Create linked graph
        linked_graph = self.create_linked_graph(graph_a, graph_b, graph_a_name, graph_b_name, touchpoints)

        # Save if output path provided
        if output_path:
            with open(output_path, 'w') as f:
                json.dump(linked_graph, f, indent=2)
            if self.verbose:
                print(f"Linked graph saved to: {output_path}")

        return linked_graph


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Link two architecture graphs by discovering touchpoints",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Link two graphs
  python3 link_architectures.py graph_a.json graph_b.json --output linked.json

  # Verbose mode
  python3 link_architectures.py graph_a.json graph_b.json --verbose

  # Output touchpoints summary
  python3 link_architectures.py graph_a.json graph_b.json --format text
        """
    )

    parser.add_argument('graph_a', type=Path,
                       help='Path to first architecture graph (JSON)')
    parser.add_argument('graph_b', type=Path,
                       help='Path to second architecture graph (JSON)')
    parser.add_argument('--output', '-o', type=Path,
                       help='Output file path (optional)')
    parser.add_argument('--format', '-f', choices=['json', 'text'], default='json',
                       help='Output format (default: json)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')

    args = parser.parse_args()

    # Validate inputs
    if not args.graph_a.exists():
        print(f"Error: Graph A not found: {args.graph_a}", file=sys.stderr)
        sys.exit(1)

    if not args.graph_b.exists():
        print(f"Error: Graph B not found: {args.graph_b}", file=sys.stderr)
        sys.exit(1)

    try:
        linker = GraphLinker(verbose=args.verbose)
        linked_graph = linker.link_graphs(args.graph_a, args.graph_b, args.output)

        # Output results
        if args.format == 'text':
            print("\n" + "="*80)
            print("ARCHITECTURE LINKING RESULTS")
            print("="*80)
            print(f"\nGraph A: {args.graph_a}")
            print(f"Graph B: {args.graph_b}")
            print(f"\nTouchpoints discovered: {len(linker.touchpoints)}")

            for i, tp in enumerate(linker.touchpoints, 1):
                print(f"\n[{i}] {tp.touchpoint_type.upper()}")
                print(f"    {tp.source_graph}::{tp.source_node} → {tp.target_graph}::{tp.target_node}")
                print(f"    Confidence: {tp.confidence:.2f}")
                print(f"    Rationale: {tp.rationale}")
                if tp.bidirectional:
                    print(f"    (Bidirectional)")

            print(f"\n{'='*80}\n")
        elif args.format == 'json':
            print(json.dumps(linked_graph, indent=2))

        sys.exit(0)

    except Exception as e:
        print(f"Error during linking: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
