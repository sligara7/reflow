#!/usr/bin/env python3
"""
DAG Complexity Metrics for Architectural Optimization

Measures "complexity" in Directed Acyclic Graphs (DAGs) through multiple
metrics categories, enabling Bayesian optimization of architectural designs.

Complexity Categories:
1. Size Metrics: Node count, edge count, size ratio
2. Structural Metrics: Density, longest path, branching factor, connectivity
3. Centrality Metrics: Degree, betweenness, closeness distributions
4. Information-Theoretic: Graph entropy, topological entropy
5. Architecture-Specific: Context consumption, service coupling, interface density

Usage:
    from dag_complexity_metrics import DAGComplexityMetrics

    metrics = DAGComplexityMetrics()
    complexity = metrics.compute_all(graph)
    score = metrics.compute_composite_score(graph, weights={...})

Version: 0.1.0
"""

import json
import math
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field, asdict
from collections import Counter

try:
    import networkx as nx
except ImportError:
    raise ImportError("NetworkX is required. Install with: pip install networkx>=3.0")


@dataclass
class SizeMetrics:
    """Size-based complexity metrics."""
    num_nodes: int = 0
    num_edges: int = 0
    size_ratio: float = 0.0  # edges / nodes
    isolated_nodes: int = 0
    leaf_nodes: int = 0  # nodes with out-degree 0
    root_nodes: int = 0  # nodes with in-degree 0


@dataclass
class StructuralMetrics:
    """Structure-based complexity metrics."""
    density: float = 0.0
    longest_path_length: int = 0
    average_path_length: float = 0.0
    diameter: int = 0
    avg_branching_factor: float = 0.0
    max_branching_factor: int = 0
    avg_in_degree: float = 0.0
    avg_out_degree: float = 0.0
    max_in_degree: int = 0
    max_out_degree: int = 0
    num_layers: int = 0  # DAG layers from topological sort
    width: int = 0  # max nodes in any layer


@dataclass
class CentralityMetrics:
    """Centrality distribution metrics."""
    avg_degree_centrality: float = 0.0
    std_degree_centrality: float = 0.0
    avg_betweenness_centrality: float = 0.0
    max_betweenness_centrality: float = 0.0
    avg_closeness_centrality: float = 0.0
    centrality_gini: float = 0.0  # inequality in centrality distribution
    hub_nodes: int = 0  # nodes with high centrality (> 2 std above mean)
    bottleneck_nodes: int = 0  # high betweenness but low degree


@dataclass
class InformationTheoreticMetrics:
    """Information-theoretic complexity metrics."""
    graph_entropy: float = 0.0  # based on degree distribution
    topological_entropy: float = 0.0  # based on path structure
    structural_information: float = 0.0  # minimum description length proxy
    edge_entropy: float = 0.0  # entropy of edge weight distribution


@dataclass
class ArchitectureMetrics:
    """Architecture-specific complexity metrics for Reflow."""
    total_context_consumption: float = 0.0
    max_path_context: float = 0.0
    avg_path_context: float = 0.0
    context_bottleneck_paths: int = 0  # paths exceeding threshold
    service_coupling: float = 0.0  # inter-service dependencies
    interface_density: float = 0.0  # interfaces per service
    function_distribution_entropy: float = 0.0  # how evenly functions distributed
    coordination_complexity: float = 0.0  # cross-service coordination


@dataclass
class CompositeComplexity:
    """Composite complexity score with all sub-metrics."""
    composite_score: float = 0.0
    size: SizeMetrics = field(default_factory=SizeMetrics)
    structural: StructuralMetrics = field(default_factory=StructuralMetrics)
    centrality: CentralityMetrics = field(default_factory=CentralityMetrics)
    information: InformationTheoreticMetrics = field(default_factory=InformationTheoreticMetrics)
    architecture: ArchitectureMetrics = field(default_factory=ArchitectureMetrics)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class DAGComplexityMetrics:
    """
    Computes comprehensive complexity metrics for DAGs.

    Designed for architectural optimization in Reflow's early phases:
    - Functional Analysis (FA)
    - Service Allocation (SE-01, SE-02)
    """

    # Default weights for composite score
    DEFAULT_WEIGHTS = {
        "size": 0.10,
        "structural": 0.25,
        "centrality": 0.20,
        "information": 0.15,
        "architecture": 0.30
    }

    # Context consumption threshold (tokens) - from Reflow standards
    CONTEXT_THRESHOLD = 40000

    def __init__(self, context_threshold: int = 40000):
        """
        Initialize complexity metrics calculator.

        Args:
            context_threshold: Token threshold for context bottleneck detection
        """
        self.context_threshold = context_threshold

    def compute_all(self, graph: nx.DiGraph) -> CompositeComplexity:
        """
        Compute all complexity metrics for a DAG.

        Args:
            graph: NetworkX directed graph (must be a DAG)

        Returns:
            CompositeComplexity with all metrics
        """
        if not nx.is_directed_acyclic_graph(graph):
            raise ValueError("Graph must be a DAG (Directed Acyclic Graph)")

        result = CompositeComplexity()
        result.size = self._compute_size_metrics(graph)
        result.structural = self._compute_structural_metrics(graph)
        result.centrality = self._compute_centrality_metrics(graph)
        result.information = self._compute_information_metrics(graph)
        result.architecture = self._compute_architecture_metrics(graph)

        return result

    def compute_composite_score(
        self,
        graph: nx.DiGraph,
        weights: Optional[Dict[str, float]] = None,
        normalize: bool = True
    ) -> float:
        """
        Compute a single composite complexity score.

        Args:
            graph: NetworkX directed graph (must be a DAG)
            weights: Optional custom weights for each metric category
            normalize: Whether to normalize to 0-1 range

        Returns:
            Composite complexity score (higher = more complex)
        """
        if weights is None:
            weights = self.DEFAULT_WEIGHTS

        metrics = self.compute_all(graph)

        # Normalize each category to 0-1 and compute weighted sum
        scores = {
            "size": self._normalize_size_score(metrics.size),
            "structural": self._normalize_structural_score(metrics.structural),
            "centrality": self._normalize_centrality_score(metrics.centrality),
            "information": self._normalize_information_score(metrics.information),
            "architecture": self._normalize_architecture_score(metrics.architecture)
        }

        composite = sum(
            weights.get(key, 0) * score
            for key, score in scores.items()
        )

        if normalize:
            total_weight = sum(weights.values())
            composite = composite / total_weight if total_weight > 0 else 0

        metrics.composite_score = composite
        return composite

    def _compute_size_metrics(self, graph: nx.DiGraph) -> SizeMetrics:
        """Compute size-based metrics."""
        metrics = SizeMetrics()

        metrics.num_nodes = graph.number_of_nodes()
        metrics.num_edges = graph.number_of_edges()

        if metrics.num_nodes > 0:
            metrics.size_ratio = metrics.num_edges / metrics.num_nodes

            # Count special node types
            for node in graph.nodes():
                in_deg = graph.in_degree(node)
                out_deg = graph.out_degree(node)

                if in_deg == 0 and out_deg == 0:
                    metrics.isolated_nodes += 1
                elif out_deg == 0:
                    metrics.leaf_nodes += 1
                if in_deg == 0 and out_deg > 0:
                    metrics.root_nodes += 1

        return metrics

    def _compute_structural_metrics(self, graph: nx.DiGraph) -> StructuralMetrics:
        """Compute structure-based metrics."""
        metrics = StructuralMetrics()

        if graph.number_of_nodes() == 0:
            return metrics

        # Density
        metrics.density = nx.density(graph)

        # Degree statistics
        in_degrees = [d for n, d in graph.in_degree()]
        out_degrees = [d for n, d in graph.out_degree()]

        if in_degrees:
            metrics.avg_in_degree = sum(in_degrees) / len(in_degrees)
            metrics.max_in_degree = max(in_degrees)

        if out_degrees:
            metrics.avg_out_degree = sum(out_degrees) / len(out_degrees)
            metrics.max_out_degree = max(out_degrees)
            metrics.avg_branching_factor = metrics.avg_out_degree
            metrics.max_branching_factor = metrics.max_out_degree

        # Longest path (DAG-specific)
        try:
            metrics.longest_path_length = nx.dag_longest_path_length(graph)
        except nx.NetworkXError:
            metrics.longest_path_length = 0

        # DAG layers
        try:
            layers = list(nx.topological_generations(graph))
            metrics.num_layers = len(layers)
            if layers:
                metrics.width = max(len(layer) for layer in layers)
        except nx.NetworkXError:
            pass

        # Path statistics (on weakly connected component)
        if nx.is_weakly_connected(graph):
            undirected = graph.to_undirected()
            if nx.is_connected(undirected):
                try:
                    metrics.diameter = nx.diameter(undirected)
                    metrics.average_path_length = nx.average_shortest_path_length(undirected)
                except nx.NetworkXError:
                    pass

        return metrics

    def _compute_centrality_metrics(self, graph: nx.DiGraph) -> CentralityMetrics:
        """Compute centrality distribution metrics."""
        metrics = CentralityMetrics()

        if graph.number_of_nodes() == 0:
            return metrics

        # Degree centrality
        degree_cent = nx.degree_centrality(graph)
        cent_values = list(degree_cent.values())

        if cent_values:
            metrics.avg_degree_centrality = sum(cent_values) / len(cent_values)
            metrics.std_degree_centrality = self._std(cent_values)

            # Gini coefficient for inequality
            metrics.centrality_gini = self._gini_coefficient(cent_values)

            # Hub nodes (> 2 std above mean)
            threshold = metrics.avg_degree_centrality + 2 * metrics.std_degree_centrality
            metrics.hub_nodes = sum(1 for v in cent_values if v > threshold)

        # Betweenness centrality
        betweenness = nx.betweenness_centrality(graph)
        between_values = list(betweenness.values())

        if between_values:
            metrics.avg_betweenness_centrality = sum(between_values) / len(between_values)
            metrics.max_betweenness_centrality = max(between_values)

            # Bottleneck nodes: high betweenness but low degree
            if cent_values:
                degree_threshold = metrics.avg_degree_centrality
                between_threshold = metrics.avg_betweenness_centrality + metrics.std_degree_centrality

                for node in graph.nodes():
                    if (betweenness.get(node, 0) > between_threshold and
                        degree_cent.get(node, 0) < degree_threshold):
                        metrics.bottleneck_nodes += 1

        # Closeness centrality
        try:
            closeness = nx.closeness_centrality(graph)
            close_values = list(closeness.values())
            if close_values:
                metrics.avg_closeness_centrality = sum(close_values) / len(close_values)
        except nx.NetworkXError:
            pass

        return metrics

    def _compute_information_metrics(self, graph: nx.DiGraph) -> InformationTheoreticMetrics:
        """Compute information-theoretic metrics."""
        metrics = InformationTheoreticMetrics()

        if graph.number_of_nodes() == 0:
            return metrics

        # Degree distribution entropy
        degrees = [d for n, d in graph.degree()]
        metrics.graph_entropy = self._entropy(degrees)

        # Topological entropy (based on path counts)
        # Approximated by layer structure entropy
        try:
            layers = list(nx.topological_generations(graph))
            layer_sizes = [len(layer) for layer in layers]
            metrics.topological_entropy = self._entropy(layer_sizes)
        except nx.NetworkXError:
            pass

        # Structural information (minimum description length proxy)
        # MDL ≈ log2(n) + log2(e) + edges * log2(n^2 / edges)
        n = graph.number_of_nodes()
        e = graph.number_of_edges()
        if n > 1 and e > 0:
            max_edges = n * (n - 1)  # directed graph
            metrics.structural_information = (
                math.log2(n) + math.log2(e) +
                e * math.log2(max_edges / e) if max_edges > e else 0
            )

        # Edge weight entropy
        weights = []
        for u, v, data in graph.edges(data=True):
            weight = data.get('weight', data.get('context_consumption', 1))
            if isinstance(weight, (int, float)):
                weights.append(weight)

        if weights:
            metrics.edge_entropy = self._entropy(weights)

        return metrics

    def _compute_architecture_metrics(self, graph: nx.DiGraph) -> ArchitectureMetrics:
        """Compute architecture-specific metrics for Reflow."""
        metrics = ArchitectureMetrics()

        if graph.number_of_nodes() == 0:
            return metrics

        # Context consumption analysis
        context_values = []
        for u, v, data in graph.edges(data=True):
            context = data.get('weight', data.get('context_consumption', 0))
            if isinstance(context, (int, float)):
                context_values.append(context)

        if context_values:
            metrics.total_context_consumption = sum(context_values)

            # Analyze paths for context bottlenecks
            try:
                # Find entry nodes (in-degree 0) and exit nodes (out-degree 0)
                entry_nodes = [n for n in graph.nodes() if graph.in_degree(n) == 0]
                exit_nodes = [n for n in graph.nodes() if graph.out_degree(n) == 0]

                path_contexts = []
                for entry in entry_nodes:
                    for exit_node in exit_nodes:
                        if nx.has_path(graph, entry, exit_node):
                            paths = list(nx.all_simple_paths(graph, entry, exit_node))
                            for path in paths[:100]:  # Limit for performance
                                path_context = self._compute_path_context(graph, path)
                                path_contexts.append(path_context)
                                if path_context > self.context_threshold:
                                    metrics.context_bottleneck_paths += 1

                if path_contexts:
                    metrics.max_path_context = max(path_contexts)
                    metrics.avg_path_context = sum(path_contexts) / len(path_contexts)
            except nx.NetworkXError:
                pass

        # Service coupling (for service allocation graphs)
        service_ids = set()
        for node, data in graph.nodes(data=True):
            service_id = data.get('service_id', data.get('allocated_to'))
            if service_id:
                service_ids.add(service_id)

        if len(service_ids) > 1:
            # Count cross-service edges
            cross_service_edges = 0
            for u, v in graph.edges():
                u_service = graph.nodes[u].get('service_id', graph.nodes[u].get('allocated_to'))
                v_service = graph.nodes[v].get('service_id', graph.nodes[v].get('allocated_to'))
                if u_service and v_service and u_service != v_service:
                    cross_service_edges += 1

            total_edges = graph.number_of_edges()
            if total_edges > 0:
                metrics.service_coupling = cross_service_edges / total_edges

            # Interface density (cross-service edges per service pair)
            num_service_pairs = len(service_ids) * (len(service_ids) - 1)
            if num_service_pairs > 0:
                metrics.interface_density = cross_service_edges / num_service_pairs

        # Function distribution entropy (how evenly distributed across services)
        functions_per_service = Counter()
        for node, data in graph.nodes(data=True):
            service_id = data.get('service_id', data.get('allocated_to', 'unassigned'))
            functions_per_service[service_id] += 1

        if functions_per_service:
            metrics.function_distribution_entropy = self._entropy(
                list(functions_per_service.values())
            )

        # Coordination complexity (services that talk to many other services)
        if service_ids:
            service_connections = {s: set() for s in service_ids}
            for u, v in graph.edges():
                u_service = graph.nodes[u].get('service_id', graph.nodes[u].get('allocated_to'))
                v_service = graph.nodes[v].get('service_id', graph.nodes[v].get('allocated_to'))
                if u_service and v_service and u_service != v_service:
                    service_connections[u_service].add(v_service)
                    service_connections[v_service].add(u_service)

            connection_counts = [len(conns) for conns in service_connections.values()]
            if connection_counts:
                # Coordination complexity = normalized variance of connections
                avg_conns = sum(connection_counts) / len(connection_counts)
                variance = sum((c - avg_conns) ** 2 for c in connection_counts) / len(connection_counts)
                max_variance = (len(service_ids) - 1) ** 2 / 4  # theoretical max
                if max_variance > 0:
                    metrics.coordination_complexity = variance / max_variance

        return metrics

    def _compute_path_context(self, graph: nx.DiGraph, path: List) -> float:
        """Compute total context consumption along a path."""
        total = 0
        for i in range(len(path) - 1):
            edge_data = graph.get_edge_data(path[i], path[i + 1], default={})
            context = edge_data.get('weight', edge_data.get('context_consumption', 0))
            if isinstance(context, (int, float)):
                total += context
        return total

    def _entropy(self, values: List[Union[int, float]]) -> float:
        """Compute entropy of a distribution."""
        if not values:
            return 0.0

        total = sum(values)
        if total == 0:
            return 0.0

        probabilities = [v / total for v in values if v > 0]
        return -sum(p * math.log2(p) for p in probabilities if p > 0)

    def _gini_coefficient(self, values: List[float]) -> float:
        """Compute Gini coefficient (0 = perfect equality, 1 = perfect inequality)."""
        if not values or len(values) < 2:
            return 0.0

        sorted_values = sorted(values)
        n = len(sorted_values)
        cumulative = sum((i + 1) * v for i, v in enumerate(sorted_values))
        total = sum(sorted_values)

        if total == 0:
            return 0.0

        return (2 * cumulative) / (n * total) - (n + 1) / n

    def _std(self, values: List[float]) -> float:
        """Compute standard deviation."""
        if not values or len(values) < 2:
            return 0.0

        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        return math.sqrt(variance)

    # Normalization functions for composite scoring
    def _normalize_size_score(self, metrics: SizeMetrics) -> float:
        """Normalize size metrics to 0-1 score."""
        # Higher nodes/edges = higher complexity
        # Use logarithmic scaling for reasonable bounds
        node_score = min(1.0, math.log10(metrics.num_nodes + 1) / 3)  # ~1000 nodes = 1.0
        edge_score = min(1.0, metrics.size_ratio / 5)  # 5 edges per node = 1.0
        isolated_penalty = min(1.0, metrics.isolated_nodes / max(1, metrics.num_nodes))

        return (node_score + edge_score + isolated_penalty) / 3

    def _normalize_structural_score(self, metrics: StructuralMetrics) -> float:
        """Normalize structural metrics to 0-1 score."""
        density_score = metrics.density
        path_score = min(1.0, metrics.longest_path_length / 20)  # 20 hops = 1.0
        branching_score = min(1.0, metrics.avg_branching_factor / 5)  # 5 avg = 1.0
        width_score = min(1.0, metrics.width / 50) if metrics.width > 0 else 0

        return (density_score + path_score + branching_score + width_score) / 4

    def _normalize_centrality_score(self, metrics: CentralityMetrics) -> float:
        """Normalize centrality metrics to 0-1 score."""
        gini_score = metrics.centrality_gini  # already 0-1
        hub_score = min(1.0, metrics.hub_nodes / 10)  # 10 hubs = 1.0
        bottleneck_score = min(1.0, metrics.bottleneck_nodes / 5)  # 5 bottlenecks = 1.0

        return (gini_score + hub_score + bottleneck_score) / 3

    def _normalize_information_score(self, metrics: InformationTheoreticMetrics) -> float:
        """Normalize information-theoretic metrics to 0-1 score."""
        # Entropy normalized by log2(n) for max possible entropy
        entropy_score = min(1.0, metrics.graph_entropy / 5)  # 5 bits = 1.0
        structural_score = min(1.0, metrics.structural_information / 1000)

        return (entropy_score + structural_score) / 2

    def _normalize_architecture_score(self, metrics: ArchitectureMetrics) -> float:
        """Normalize architecture-specific metrics to 0-1 score."""
        # Context bottleneck is most important
        context_score = min(1.0, metrics.max_path_context / (self.context_threshold * 4))
        bottleneck_score = min(1.0, metrics.context_bottleneck_paths / 10)
        coupling_score = metrics.service_coupling  # already 0-1 (ratio)
        coordination_score = metrics.coordination_complexity  # already 0-1

        return (context_score * 2 + bottleneck_score + coupling_score + coordination_score) / 5


def load_graph_from_json(path: Path) -> nx.DiGraph:
    """
    Load a NetworkX graph from Reflow JSON format.

    Args:
        path: Path to functional_architecture.json or service_architecture.json

    Returns:
        NetworkX DiGraph
    """
    with open(path, 'r') as f:
        data = json.load(f)

    # Handle node_link_data format (from system_of_systems_graph_v2.py)
    if 'nodes' in data and 'links' in data:
        return nx.node_link_graph(data, directed=True)

    # Handle functional_architecture.json format
    if 'functions' in data and 'dependencies' in data:
        G = nx.DiGraph()

        for func in data['functions']:
            G.add_node(
                func['function_id'],
                function_name=func.get('function_name', ''),
                function_type=func.get('function_type', ''),
                service_id=func.get('service_allocation', {}).get('service_id'),
                context_consumption=func.get('context_consumption', 0)
            )

        for dep in data['dependencies']:
            G.add_edge(
                dep['source_function'],
                dep['target_function'],
                dependency_type=dep.get('dependency_type', 'function_call'),
                weight=dep.get('weight', dep.get('context_consumption', 1)),
                probability=dep.get('probability', 1.0)
            )

        return G

    raise ValueError(f"Unknown graph format in {path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Compute DAG complexity metrics for architectural optimization"
    )
    parser.add_argument(
        "graph_path",
        type=Path,
        help="Path to graph JSON (functional_architecture.json or node_link format)"
    )
    parser.add_argument(
        "--context-threshold",
        type=int,
        default=40000,
        help="Context threshold for bottleneck detection (default: 40000)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output path for metrics JSON"
    )

    args = parser.parse_args()

    # Load graph
    graph = load_graph_from_json(args.graph_path)

    # Compute metrics
    metrics_calc = DAGComplexityMetrics(context_threshold=args.context_threshold)
    complexity = metrics_calc.compute_all(graph)
    composite_score = metrics_calc.compute_composite_score(graph)
    complexity.composite_score = composite_score

    # Output
    result = complexity.to_dict()
    result_json = json.dumps(result, indent=2)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(result_json)
        print(f"Metrics written to {args.output}")
    else:
        print(result_json)
