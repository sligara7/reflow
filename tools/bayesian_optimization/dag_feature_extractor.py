#!/usr/bin/env python3
"""
DAG Feature Extractor for Bayesian Optimization

Converts DAG structures into fixed-length feature vectors suitable for
Gaussian Process surrogate models in Bayesian optimization.

Features are extracted at multiple levels:
1. Global Features: Graph-level statistics
2. Structural Features: Topology-based metrics
3. Distribution Features: Statistical summaries of node/edge attributes
4. Architecture Features: Reflow-specific metrics
5. Spectral Features: Eigenvalue-based graph descriptors

Usage:
    from dag_feature_extractor import DAGFeatureExtractor

    extractor = DAGFeatureExtractor()
    features = extractor.extract(graph)  # Returns numpy array or list
    feature_names = extractor.get_feature_names()

Version: 0.1.0
"""

import json
import math
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from collections import Counter

try:
    import networkx as nx
except ImportError:
    raise ImportError("NetworkX is required. Install with: pip install networkx>=3.0")

# Optional numpy for array operations
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False


@dataclass
class FeatureConfig:
    """Configuration for feature extraction."""
    include_global: bool = True
    include_structural: bool = True
    include_distribution: bool = True
    include_architecture: bool = True
    include_spectral: bool = True
    normalize: bool = True
    n_percentiles: int = 5  # Number of percentiles for distribution features
    max_spectral_features: int = 10  # Max eigenvalues to include


class DAGFeatureExtractor:
    """
    Extracts fixed-length feature vectors from DAGs for Bayesian optimization.

    The feature vector is designed to capture:
    - Scale: How large is the architecture?
    - Structure: How is it organized (deep vs wide, sparse vs dense)?
    - Distribution: How are attributes distributed across nodes/edges?
    - Architecture: Reflow-specific patterns (context, services, coupling)
    - Spectral: Graph structure via adjacency matrix eigenvalues
    """

    GLOBAL_FEATURE_NAMES = [
        "num_nodes", "num_edges", "density", "is_weakly_connected",
        "num_weakly_components", "num_roots", "num_leaves"
    ]

    STRUCTURAL_FEATURE_NAMES = [
        "longest_path_length", "avg_path_length", "diameter",
        "avg_in_degree", "avg_out_degree", "max_in_degree", "max_out_degree",
        "num_layers", "max_layer_width", "avg_layer_width",
        "branching_factor_mean", "branching_factor_std"
    ]

    DISTRIBUTION_FEATURE_NAMES = [
        # Degree distribution (percentiles)
        "degree_min", "degree_p25", "degree_p50", "degree_p75", "degree_max",
        # Centrality distribution
        "betweenness_mean", "betweenness_std", "betweenness_max",
        "closeness_mean", "closeness_std",
        # Edge weight distribution (if present)
        "edge_weight_mean", "edge_weight_std", "edge_weight_max"
    ]

    ARCHITECTURE_FEATURE_NAMES = [
        # Context consumption
        "total_context", "max_path_context", "context_bottleneck_ratio",
        # Service allocation
        "num_services", "functions_per_service_mean", "functions_per_service_std",
        "service_coupling", "interface_density",
        # Function types
        "read_ratio", "write_ratio", "process_ratio", "decide_ratio",
        # Coordination
        "coordination_complexity", "cross_service_edge_ratio"
    ]

    SPECTRAL_FEATURE_NAMES = [
        # Adjacency spectrum
        "spectral_radius", "spectral_gap",
        "eigenvalue_1", "eigenvalue_2", "eigenvalue_3",
        # Laplacian spectrum
        "algebraic_connectivity", "laplacian_energy"
    ]

    def __init__(self, config: Optional[FeatureConfig] = None):
        """
        Initialize feature extractor.

        Args:
            config: Feature extraction configuration
        """
        self.config = config or FeatureConfig()
        self._feature_names = self._build_feature_names()

    def _build_feature_names(self) -> List[str]:
        """Build list of feature names based on config."""
        names = []
        if self.config.include_global:
            names.extend(self.GLOBAL_FEATURE_NAMES)
        if self.config.include_structural:
            names.extend(self.STRUCTURAL_FEATURE_NAMES)
        if self.config.include_distribution:
            names.extend(self.DISTRIBUTION_FEATURE_NAMES)
        if self.config.include_architecture:
            names.extend(self.ARCHITECTURE_FEATURE_NAMES)
        if self.config.include_spectral:
            names.extend(self.SPECTRAL_FEATURE_NAMES)
        return names

    def get_feature_names(self) -> List[str]:
        """Get ordered list of feature names."""
        return self._feature_names.copy()

    def get_feature_dimension(self) -> int:
        """Get dimension of feature vector."""
        return len(self._feature_names)

    def extract(self, graph: nx.DiGraph) -> List[float]:
        """
        Extract feature vector from DAG.

        Args:
            graph: NetworkX directed graph (should be a DAG)

        Returns:
            List of feature values (order matches get_feature_names())
        """
        features = []

        if self.config.include_global:
            features.extend(self._extract_global_features(graph))
        if self.config.include_structural:
            features.extend(self._extract_structural_features(graph))
        if self.config.include_distribution:
            features.extend(self._extract_distribution_features(graph))
        if self.config.include_architecture:
            features.extend(self._extract_architecture_features(graph))
        if self.config.include_spectral:
            features.extend(self._extract_spectral_features(graph))

        if self.config.normalize:
            features = self._normalize_features(features)

        return features

    def extract_to_dict(self, graph: nx.DiGraph) -> Dict[str, float]:
        """
        Extract features as a named dictionary.

        Args:
            graph: NetworkX directed graph

        Returns:
            Dictionary mapping feature names to values
        """
        features = self.extract(graph)
        return dict(zip(self._feature_names, features))

    def _extract_global_features(self, graph: nx.DiGraph) -> List[float]:
        """Extract global graph features."""
        n = graph.number_of_nodes()
        e = graph.number_of_edges()

        # Count root and leaf nodes
        roots = sum(1 for node in graph.nodes() if graph.in_degree(node) == 0)
        leaves = sum(1 for node in graph.nodes() if graph.out_degree(node) == 0)

        # Connectivity
        weakly_connected = 1.0 if nx.is_weakly_connected(graph) else 0.0
        num_components = nx.number_weakly_connected_components(graph)

        return [
            float(n),
            float(e),
            nx.density(graph) if n > 0 else 0.0,
            weakly_connected,
            float(num_components),
            float(roots),
            float(leaves)
        ]

    def _extract_structural_features(self, graph: nx.DiGraph) -> List[float]:
        """Extract structural/topological features."""
        features = []

        # Longest path
        try:
            longest_path = nx.dag_longest_path_length(graph)
        except nx.NetworkXError:
            longest_path = 0
        features.append(float(longest_path))

        # Average path length and diameter (on undirected version)
        if graph.number_of_nodes() > 1 and nx.is_weakly_connected(graph):
            undirected = graph.to_undirected()
            try:
                avg_path = nx.average_shortest_path_length(undirected)
                diameter = nx.diameter(undirected)
            except nx.NetworkXError:
                avg_path = 0.0
                diameter = 0
        else:
            avg_path = 0.0
            diameter = 0

        features.append(avg_path)
        features.append(float(diameter))

        # Degree statistics
        in_degrees = [d for n, d in graph.in_degree()]
        out_degrees = [d for n, d in graph.out_degree()]

        features.append(self._safe_mean(in_degrees))
        features.append(self._safe_mean(out_degrees))
        features.append(float(max(in_degrees)) if in_degrees else 0.0)
        features.append(float(max(out_degrees)) if out_degrees else 0.0)

        # Layer structure
        try:
            layers = list(nx.topological_generations(graph))
            layer_sizes = [len(layer) for layer in layers]
            num_layers = len(layers)
            max_width = max(layer_sizes) if layer_sizes else 0
            avg_width = self._safe_mean(layer_sizes)
        except nx.NetworkXError:
            num_layers = 0
            max_width = 0
            avg_width = 0.0

        features.append(float(num_layers))
        features.append(float(max_width))
        features.append(avg_width)

        # Branching factor statistics
        features.append(self._safe_mean(out_degrees))
        features.append(self._safe_std(out_degrees))

        return features

    def _extract_distribution_features(self, graph: nx.DiGraph) -> List[float]:
        """Extract distribution-based features."""
        features = []

        # Degree distribution
        degrees = [d for n, d in graph.degree()]
        if degrees:
            sorted_degrees = sorted(degrees)
            n = len(sorted_degrees)
            features.append(float(sorted_degrees[0]))  # min
            features.append(float(sorted_degrees[int(n * 0.25)]))  # p25
            features.append(float(sorted_degrees[int(n * 0.50)]))  # p50
            features.append(float(sorted_degrees[int(n * 0.75)]))  # p75
            features.append(float(sorted_degrees[-1]))  # max
        else:
            features.extend([0.0] * 5)

        # Betweenness centrality
        if graph.number_of_nodes() > 0:
            betweenness = list(nx.betweenness_centrality(graph).values())
            features.append(self._safe_mean(betweenness))
            features.append(self._safe_std(betweenness))
            features.append(max(betweenness) if betweenness else 0.0)
        else:
            features.extend([0.0] * 3)

        # Closeness centrality
        if graph.number_of_nodes() > 0:
            try:
                closeness = list(nx.closeness_centrality(graph).values())
                features.append(self._safe_mean(closeness))
                features.append(self._safe_std(closeness))
            except nx.NetworkXError:
                features.extend([0.0] * 2)
        else:
            features.extend([0.0] * 2)

        # Edge weight distribution
        weights = []
        for u, v, data in graph.edges(data=True):
            weight = data.get('weight', data.get('context_consumption', 1.0))
            if isinstance(weight, (int, float)):
                weights.append(float(weight))

        if weights:
            features.append(self._safe_mean(weights))
            features.append(self._safe_std(weights))
            features.append(max(weights))
        else:
            features.extend([0.0] * 3)

        return features

    def _extract_architecture_features(self, graph: nx.DiGraph) -> List[float]:
        """Extract Reflow architecture-specific features."""
        features = []

        # Context consumption
        total_context = 0.0
        for u, v, data in graph.edges(data=True):
            context = data.get('weight', data.get('context_consumption', 0))
            if isinstance(context, (int, float)):
                total_context += context

        features.append(total_context)

        # Max path context (sample paths for efficiency)
        max_path_context = 0.0
        bottleneck_count = 0
        context_threshold = 40000

        try:
            entry_nodes = [n for n in graph.nodes() if graph.in_degree(n) == 0]
            exit_nodes = [n for n in graph.nodes() if graph.out_degree(n) == 0]

            path_count = 0
            for entry in entry_nodes[:5]:  # Limit for performance
                for exit_node in exit_nodes[:5]:
                    if nx.has_path(graph, entry, exit_node):
                        for path in list(nx.all_simple_paths(graph, entry, exit_node))[:20]:
                            path_context = sum(
                                graph.edges[path[i], path[i+1]].get('weight', 0)
                                for i in range(len(path) - 1)
                            )
                            max_path_context = max(max_path_context, path_context)
                            if path_context > context_threshold:
                                bottleneck_count += 1
                            path_count += 1
        except nx.NetworkXError:
            pass

        features.append(max_path_context)
        features.append(bottleneck_count / max(1, path_count) if path_count > 0 else 0.0)

        # Service allocation analysis
        services = Counter()
        for node, data in graph.nodes(data=True):
            service_id = data.get('service_id', data.get('allocated_to', 'unassigned'))
            services[service_id] += 1

        num_services = len([s for s in services if s != 'unassigned'])
        features.append(float(num_services))

        service_sizes = [c for s, c in services.items() if s != 'unassigned']
        features.append(self._safe_mean(service_sizes))
        features.append(self._safe_std(service_sizes))

        # Service coupling (cross-service edges / total edges)
        cross_service = 0
        total_edges = graph.number_of_edges()
        for u, v in graph.edges():
            u_service = graph.nodes[u].get('service_id', graph.nodes[u].get('allocated_to'))
            v_service = graph.nodes[v].get('service_id', graph.nodes[v].get('allocated_to'))
            if u_service and v_service and u_service != v_service:
                cross_service += 1

        features.append(cross_service / max(1, total_edges))

        # Interface density
        num_service_pairs = num_services * (num_services - 1) if num_services > 1 else 1
        features.append(cross_service / num_service_pairs)

        # Function type ratios
        type_counts = Counter()
        for node, data in graph.nodes(data=True):
            func_type = data.get('function_type', 'unknown')
            type_counts[func_type] += 1

        total_funcs = max(1, sum(type_counts.values()))
        features.append(type_counts.get('read', 0) / total_funcs)
        features.append(type_counts.get('write', 0) / total_funcs)
        features.append(type_counts.get('process', 0) / total_funcs)
        features.append(type_counts.get('decide', 0) / total_funcs)

        # Coordination complexity
        if num_services > 1:
            service_connections = {s: set() for s in services if s != 'unassigned'}
            for u, v in graph.edges():
                u_service = graph.nodes[u].get('service_id', graph.nodes[u].get('allocated_to'))
                v_service = graph.nodes[v].get('service_id', graph.nodes[v].get('allocated_to'))
                if u_service and v_service and u_service != v_service:
                    if u_service in service_connections:
                        service_connections[u_service].add(v_service)

            connection_counts = [len(c) for c in service_connections.values()]
            features.append(self._safe_std(connection_counts) / max(1, num_services - 1))
        else:
            features.append(0.0)

        features.append(cross_service / max(1, total_edges))

        return features

    def _extract_spectral_features(self, graph: nx.DiGraph) -> List[float]:
        """Extract spectral (eigenvalue-based) features."""
        features = []

        if graph.number_of_nodes() < 2:
            return [0.0] * 7  # Return zeros for empty/tiny graphs

        try:
            # Convert to adjacency matrix
            if HAS_NUMPY:
                adj = nx.to_numpy_array(graph)
                eigenvalues = np.linalg.eigvals(adj)
                eigenvalues = np.sort(np.abs(eigenvalues))[::-1]

                # Spectral radius (largest eigenvalue)
                spectral_radius = float(eigenvalues[0]) if len(eigenvalues) > 0 else 0.0
                features.append(spectral_radius)

                # Spectral gap (difference between first two eigenvalues)
                spectral_gap = float(eigenvalues[0] - eigenvalues[1]) if len(eigenvalues) > 1 else 0.0
                features.append(spectral_gap)

                # Top 3 eigenvalues
                for i in range(3):
                    if i < len(eigenvalues):
                        features.append(float(eigenvalues[i]))
                    else:
                        features.append(0.0)

                # Laplacian spectrum
                undirected = graph.to_undirected()
                laplacian = nx.laplacian_matrix(undirected).toarray()
                lap_eigenvalues = np.sort(np.linalg.eigvals(laplacian))

                # Algebraic connectivity (second smallest Laplacian eigenvalue)
                algebraic_conn = float(lap_eigenvalues[1]) if len(lap_eigenvalues) > 1 else 0.0
                features.append(algebraic_conn)

                # Laplacian energy
                lap_energy = float(np.sum(np.abs(lap_eigenvalues)))
                features.append(lap_energy)

            else:
                # Fallback without numpy - use NetworkX approximations
                features.extend([0.0] * 7)

        except Exception:
            features.extend([0.0] * (7 - len(features)))

        return features[:7]  # Ensure exactly 7 features

    def _normalize_features(self, features: List[float]) -> List[float]:
        """
        Apply log-scaling and bounding to features.

        This helps Gaussian Processes work better with features
        that have different scales.
        """
        normalized = []
        for f in features:
            if f > 0:
                # Log-scale large values
                if f > 100:
                    f = 100 + math.log(f - 99)
                normalized.append(f)
            else:
                normalized.append(f)

        return normalized

    def _safe_mean(self, values: List[float]) -> float:
        """Compute mean, handling empty lists."""
        return sum(values) / len(values) if values else 0.0

    def _safe_std(self, values: List[float]) -> float:
        """Compute standard deviation, handling empty lists."""
        if not values or len(values) < 2:
            return 0.0
        mean = self._safe_mean(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        return math.sqrt(variance)


def extract_features_from_file(
    path: Path,
    config: Optional[FeatureConfig] = None
) -> Tuple[List[float], List[str]]:
    """
    Convenience function to extract features from a Reflow graph file.

    Args:
        path: Path to graph JSON
        config: Optional feature config

    Returns:
        Tuple of (feature_values, feature_names)
    """
    from .dag_complexity_metrics import load_graph_from_json

    graph = load_graph_from_json(path)
    extractor = DAGFeatureExtractor(config)

    return extractor.extract(graph), extractor.get_feature_names()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Extract feature vector from DAG for Bayesian optimization"
    )
    parser.add_argument(
        "graph_path",
        type=Path,
        help="Path to graph JSON"
    )
    parser.add_argument(
        "--no-normalize",
        action="store_true",
        help="Disable feature normalization"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output path for features JSON"
    )

    args = parser.parse_args()

    # Load graph
    from dag_complexity_metrics import load_graph_from_json
    graph = load_graph_from_json(args.graph_path)

    # Extract features
    config = FeatureConfig(normalize=not args.no_normalize)
    extractor = DAGFeatureExtractor(config)
    features = extractor.extract_to_dict(graph)

    # Output
    result = {
        "source": str(args.graph_path),
        "num_features": len(features),
        "features": features
    }
    result_json = json.dumps(result, indent=2)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(result_json)
        print(f"Features written to {args.output}")
    else:
        print(result_json)
