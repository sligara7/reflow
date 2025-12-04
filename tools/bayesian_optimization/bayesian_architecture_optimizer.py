#!/usr/bin/env python3
"""
Bayesian Architecture Optimizer for Reflow DAGs

Main orchestration module that combines:
- DAG complexity metrics
- Feature extraction
- Gaussian Process surrogate modeling
- Acquisition function optimization

to optimize architectural trade-offs in the functional analysis and
service allocation phases of Reflow.

Optimization Objectives (predefined):
- minimize_complexity: Overall complexity score
- minimize_context_bottlenecks: Context consumption on critical paths
- minimize_coupling: Service coupling and coordination complexity
- maximize_modularity: Function distribution and service independence
- custom: User-defined objective function

Architecture Mutations:
- Service allocation changes (move function to different service)
- Service merging (combine two services)
- Service splitting (split one service into two)
- Interface refactoring (change communication patterns)

Usage:
    from bayesian_architecture_optimizer import BayesianArchitectureOptimizer

    optimizer = BayesianArchitectureOptimizer(
        functional_architecture="specs/machine/functional_architecture.json"
    )

    # Run optimization
    result = optimizer.optimize(
        objective="minimize_context_bottlenecks",
        n_iterations=20,
        constraints={"max_services": 10}
    )

    # Get recommendations
    print(result.best_architecture)
    print(result.improvement_over_baseline)

Version: 0.1.0
"""

import json
import math
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Callable, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime
from copy import deepcopy
from enum import Enum

try:
    import networkx as nx
except ImportError:
    raise ImportError("NetworkX is required. Install with: pip install networkx>=3.0")

from .dag_complexity_metrics import (
    DAGComplexityMetrics,
    CompositeComplexity,
    load_graph_from_json
)
from .dag_feature_extractor import DAGFeatureExtractor, FeatureConfig
from .surrogate_model import GaussianProcessSurrogate, GPConfig, KernelType
from .acquisition_functions import (
    AcquisitionOptimizer,
    AcquisitionConfig,
    AcquisitionType,
    expected_improvement,
    batch_select
)


class ObjectiveType(Enum):
    """Predefined optimization objectives."""
    MINIMIZE_COMPLEXITY = "minimize_complexity"
    MINIMIZE_CONTEXT_BOTTLENECKS = "minimize_context_bottlenecks"
    MINIMIZE_COUPLING = "minimize_coupling"
    MAXIMIZE_MODULARITY = "maximize_modularity"
    MINIMIZE_COORDINATION = "minimize_coordination"
    BALANCE_MULTI_OBJECTIVE = "balance_multi_objective"
    CUSTOM = "custom"


class MutationType(Enum):
    """Types of architecture mutations."""
    REALLOCATE_FUNCTION = "reallocate_function"
    MERGE_SERVICES = "merge_services"
    SPLIT_SERVICE = "split_service"
    ADD_SERVICE = "add_service"
    CHANGE_INTERFACE = "change_interface"


@dataclass
class Constraint:
    """Optimization constraint."""
    name: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None

    def is_satisfied(self, value: float) -> bool:
        """Check if constraint is satisfied."""
        if self.min_value is not None and value < self.min_value:
            return False
        if self.max_value is not None and value > self.max_value:
            return False
        return True


@dataclass
class OptimizationConfig:
    """Configuration for the optimizer."""
    objective: ObjectiveType = ObjectiveType.MINIMIZE_COMPLEXITY
    n_iterations: int = 20
    n_initial_samples: int = 5
    batch_size: int = 1
    constraints: List[Constraint] = field(default_factory=list)
    exploration_weight: float = 0.1
    mutation_probability: float = 0.3
    seed: Optional[int] = None
    context_threshold: int = 40000

    # Multi-objective weights (for BALANCE_MULTI_OBJECTIVE)
    objective_weights: Dict[str, float] = field(default_factory=lambda: {
        "complexity": 0.2,
        "context_bottlenecks": 0.3,
        "coupling": 0.25,
        "coordination": 0.25
    })


@dataclass
class OptimizationResult:
    """Result of optimization run."""
    best_graph: Optional[nx.DiGraph] = None
    best_features: List[float] = field(default_factory=list)
    best_objective: float = float('inf')
    baseline_objective: float = float('inf')
    improvement_percentage: float = 0.0

    # History
    iteration_history: List[Dict[str, Any]] = field(default_factory=list)
    objective_history: List[float] = field(default_factory=list)

    # Recommendations
    recommendations: List[str] = field(default_factory=list)
    mutations_applied: List[Dict[str, Any]] = field(default_factory=list)

    # Timing
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    total_seconds: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (graph excluded)."""
        d = asdict(self)
        d.pop('best_graph', None)
        return d


class BayesianArchitectureOptimizer:
    """
    Bayesian optimizer for architectural DAGs.

    Uses Bayesian optimization to explore the space of possible
    architectural configurations and find optimal trade-offs.
    """

    def __init__(
        self,
        functional_architecture: Optional[Union[str, Path, nx.DiGraph]] = None,
        service_architecture: Optional[Union[str, Path]] = None,
        config: Optional[OptimizationConfig] = None
    ):
        """
        Initialize optimizer.

        Args:
            functional_architecture: Path to functional_architecture.json or graph
            service_architecture: Optional path to service_architecture.json
            config: Optimization configuration
        """
        self.config = config or OptimizationConfig()

        # Set random seed if provided
        if self.config.seed is not None:
            random.seed(self.config.seed)

        # Load initial graph
        if functional_architecture is not None:
            if isinstance(functional_architecture, nx.DiGraph):
                self.baseline_graph = functional_architecture
            else:
                self.baseline_graph = load_graph_from_json(Path(functional_architecture))
        else:
            self.baseline_graph = None

        self.service_architecture_path = service_architecture

        # Initialize components
        self.complexity_metrics = DAGComplexityMetrics(
            context_threshold=self.config.context_threshold
        )
        self.feature_extractor = DAGFeatureExtractor()

        self.gp = GaussianProcessSurrogate(GPConfig(
            kernel=KernelType.MATERN_52,
            length_scale=1.0,
            normalize_y=True
        ))

        self.acquisition = AcquisitionOptimizer(AcquisitionConfig(
            acquisition_type=AcquisitionType.EXPECTED_IMPROVEMENT,
            minimize=True,
            xi=self.config.exploration_weight
        ))

        # Tracking
        self._evaluated_graphs: List[nx.DiGraph] = []
        self._evaluated_features: List[List[float]] = []
        self._evaluated_objectives: List[float] = []

    def optimize(
        self,
        objective: Optional[Union[str, ObjectiveType, Callable]] = None,
        n_iterations: Optional[int] = None,
        constraints: Optional[Dict[str, Any]] = None
    ) -> OptimizationResult:
        """
        Run Bayesian optimization.

        Args:
            objective: Objective to optimize (string, enum, or callable)
            n_iterations: Number of optimization iterations
            constraints: Dict of constraint name -> (min, max) or single value

        Returns:
            OptimizationResult with best configuration and history
        """
        if self.baseline_graph is None:
            raise ValueError("No baseline graph provided. Set functional_architecture in constructor.")

        # Parse objective
        if objective is not None:
            if isinstance(objective, str):
                self.config.objective = ObjectiveType(objective)
            elif isinstance(objective, ObjectiveType):
                self.config.objective = objective
            elif callable(objective):
                self.config.objective = ObjectiveType.CUSTOM
                self._custom_objective = objective

        if n_iterations is not None:
            self.config.n_iterations = n_iterations

        # Parse constraints
        if constraints:
            for name, value in constraints.items():
                if isinstance(value, tuple):
                    self.config.constraints.append(Constraint(name, value[0], value[1]))
                else:
                    # Single value treated as max
                    self.config.constraints.append(Constraint(name, max_value=value))

        # Start optimization
        result = OptimizationResult()
        result.start_time = datetime.now().isoformat()

        # Evaluate baseline
        baseline_features = self.feature_extractor.extract(self.baseline_graph)
        baseline_objective = self._evaluate_objective(self.baseline_graph)
        result.baseline_objective = baseline_objective

        self._evaluated_graphs.append(deepcopy(self.baseline_graph))
        self._evaluated_features.append(baseline_features)
        self._evaluated_objectives.append(baseline_objective)

        # Generate initial samples
        print(f"Generating {self.config.n_initial_samples} initial samples...")
        for i in range(self.config.n_initial_samples - 1):
            mutated = self._generate_mutation(self.baseline_graph)
            features = self.feature_extractor.extract(mutated)
            obj = self._evaluate_objective(mutated)

            self._evaluated_graphs.append(mutated)
            self._evaluated_features.append(features)
            self._evaluated_objectives.append(obj)

            print(f"  Sample {i+1}: objective = {obj:.4f}")

        # Fit initial GP
        self.gp.fit(self._evaluated_features, self._evaluated_objectives)

        # Main optimization loop
        print(f"\nRunning {self.config.n_iterations} optimization iterations...")
        for iteration in range(self.config.n_iterations):
            # Generate candidate mutations
            candidates = self._generate_candidates(n_candidates=20)
            candidate_features = [self.feature_extractor.extract(g) for g in candidates]

            # Get GP predictions
            means, stds = self.gp.predict(candidate_features)

            # Select best candidate using acquisition function
            best_so_far = min(self._evaluated_objectives)
            selected_indices = self.acquisition.select(
                candidate_features, means, stds, best_so_far,
                n_select=self.config.batch_size
            )

            # Evaluate selected candidates
            for idx in selected_indices:
                selected_graph = candidates[idx]
                selected_features = candidate_features[idx]
                selected_obj = self._evaluate_objective(selected_graph)

                # Check constraints
                if not self._check_constraints(selected_graph):
                    selected_obj += 1000  # Penalty for constraint violation

                self._evaluated_graphs.append(selected_graph)
                self._evaluated_features.append(selected_features)
                self._evaluated_objectives.append(selected_obj)

                # Update history
                result.iteration_history.append({
                    "iteration": iteration,
                    "objective": selected_obj,
                    "predicted_mean": means[idx],
                    "predicted_std": stds[idx],
                    "best_so_far": min(self._evaluated_objectives)
                })
                result.objective_history.append(selected_obj)

            # Refit GP
            self.gp.fit(self._evaluated_features, self._evaluated_objectives)

            current_best = min(self._evaluated_objectives)
            print(f"  Iteration {iteration + 1}: best = {current_best:.4f}")

        # Compile results
        best_idx = min(range(len(self._evaluated_objectives)),
                      key=lambda i: self._evaluated_objectives[i])

        result.best_graph = self._evaluated_graphs[best_idx]
        result.best_features = self._evaluated_features[best_idx]
        result.best_objective = self._evaluated_objectives[best_idx]
        result.improvement_percentage = (
            (baseline_objective - result.best_objective) / baseline_objective * 100
            if baseline_objective != 0 else 0
        )

        # Generate recommendations
        result.recommendations = self._generate_recommendations(
            self.baseline_graph,
            result.best_graph
        )

        result.end_time = datetime.now().isoformat()

        print(f"\nOptimization complete!")
        print(f"  Baseline objective: {baseline_objective:.4f}")
        print(f"  Best objective: {result.best_objective:.4f}")
        print(f"  Improvement: {result.improvement_percentage:.1f}%")

        return result

    def _evaluate_objective(self, graph: nx.DiGraph) -> float:
        """Evaluate objective function on graph."""
        if self.config.objective == ObjectiveType.CUSTOM:
            return self._custom_objective(graph)

        metrics = self.complexity_metrics.compute_all(graph)

        if self.config.objective == ObjectiveType.MINIMIZE_COMPLEXITY:
            return self.complexity_metrics.compute_composite_score(graph)

        elif self.config.objective == ObjectiveType.MINIMIZE_CONTEXT_BOTTLENECKS:
            # Weighted combination of context metrics
            return (
                0.4 * min(1.0, metrics.architecture.max_path_context / (self.config.context_threshold * 4)) +
                0.3 * min(1.0, metrics.architecture.context_bottleneck_paths / 10) +
                0.3 * min(1.0, metrics.architecture.total_context_consumption / (self.config.context_threshold * 10))
            )

        elif self.config.objective == ObjectiveType.MINIMIZE_COUPLING:
            return (
                0.5 * metrics.architecture.service_coupling +
                0.3 * metrics.architecture.interface_density +
                0.2 * metrics.centrality.centrality_gini
            )

        elif self.config.objective == ObjectiveType.MAXIMIZE_MODULARITY:
            # Negate because we minimize
            modularity = (
                0.4 * metrics.architecture.function_distribution_entropy / 5 +  # normalized
                0.3 * (1 - metrics.architecture.service_coupling) +
                0.3 * (1 - metrics.architecture.coordination_complexity)
            )
            return -modularity

        elif self.config.objective == ObjectiveType.MINIMIZE_COORDINATION:
            return (
                0.5 * metrics.architecture.coordination_complexity +
                0.3 * min(1.0, metrics.centrality.bottleneck_nodes / 5) +
                0.2 * metrics.structural.avg_branching_factor / 5
            )

        elif self.config.objective == ObjectiveType.BALANCE_MULTI_OBJECTIVE:
            weights = self.config.objective_weights
            score = 0.0

            if "complexity" in weights:
                score += weights["complexity"] * self.complexity_metrics.compute_composite_score(graph)
            if "context_bottlenecks" in weights:
                score += weights["context_bottlenecks"] * min(1.0,
                    metrics.architecture.max_path_context / (self.config.context_threshold * 4))
            if "coupling" in weights:
                score += weights["coupling"] * metrics.architecture.service_coupling
            if "coordination" in weights:
                score += weights["coordination"] * metrics.architecture.coordination_complexity

            return score

        return self.complexity_metrics.compute_composite_score(graph)

    def _generate_mutation(self, graph: nx.DiGraph) -> nx.DiGraph:
        """Generate a random mutation of the graph."""
        mutated = deepcopy(graph)

        mutation_type = random.choice(list(MutationType))

        if mutation_type == MutationType.REALLOCATE_FUNCTION:
            self._mutate_reallocate(mutated)
        elif mutation_type == MutationType.MERGE_SERVICES:
            self._mutate_merge_services(mutated)
        elif mutation_type == MutationType.SPLIT_SERVICE:
            self._mutate_split_service(mutated)
        elif mutation_type == MutationType.CHANGE_INTERFACE:
            self._mutate_change_interface(mutated)

        return mutated

    def _mutate_reallocate(self, graph: nx.DiGraph) -> None:
        """Reallocate a function to a different service."""
        nodes = list(graph.nodes())
        if not nodes:
            return

        # Pick random node
        node = random.choice(nodes)

        # Get existing services
        services = set()
        for n, data in graph.nodes(data=True):
            service = data.get('service_id', data.get('allocated_to'))
            if service:
                services.add(service)

        if not services:
            return

        # Assign to random service (possibly same)
        new_service = random.choice(list(services))
        if 'service_id' in graph.nodes[node]:
            graph.nodes[node]['service_id'] = new_service
        if 'allocated_to' in graph.nodes[node]:
            graph.nodes[node]['allocated_to'] = new_service

    def _mutate_merge_services(self, graph: nx.DiGraph) -> None:
        """Merge two services into one."""
        services = {}
        for n, data in graph.nodes(data=True):
            service = data.get('service_id', data.get('allocated_to'))
            if service:
                if service not in services:
                    services[service] = []
                services[service].append(n)

        if len(services) < 2:
            return

        # Pick two random services
        service_list = list(services.keys())
        s1, s2 = random.sample(service_list, 2)

        # Merge s2 into s1
        for node in services[s2]:
            if 'service_id' in graph.nodes[node]:
                graph.nodes[node]['service_id'] = s1
            if 'allocated_to' in graph.nodes[node]:
                graph.nodes[node]['allocated_to'] = s1

    def _mutate_split_service(self, graph: nx.DiGraph) -> None:
        """Split a service into two."""
        services = {}
        for n, data in graph.nodes(data=True):
            service = data.get('service_id', data.get('allocated_to'))
            if service:
                if service not in services:
                    services[service] = []
                services[service].append(n)

        # Find service with at least 2 functions
        splittable = [(s, nodes) for s, nodes in services.items() if len(nodes) >= 2]
        if not splittable:
            return

        service, nodes = random.choice(splittable)

        # Create new service name
        new_service = f"{service}_split_{random.randint(1, 1000)}"

        # Move half the nodes
        to_move = random.sample(nodes, len(nodes) // 2)
        for node in to_move:
            if 'service_id' in graph.nodes[node]:
                graph.nodes[node]['service_id'] = new_service
            if 'allocated_to' in graph.nodes[node]:
                graph.nodes[node]['allocated_to'] = new_service

    def _mutate_change_interface(self, graph: nx.DiGraph) -> None:
        """Change edge weight/communication pattern."""
        edges = list(graph.edges())
        if not edges:
            return

        edge = random.choice(edges)

        # Modify weight
        current_weight = graph.edges[edge].get('weight', 1000)
        delta = random.uniform(-0.3, 0.3)
        new_weight = max(100, current_weight * (1 + delta))
        graph.edges[edge]['weight'] = new_weight

        # Possibly change dependency type
        if random.random() < 0.3:
            dep_types = ['function_call', 'data_flow', 'control_flow', 'async']
            graph.edges[edge]['dependency_type'] = random.choice(dep_types)

    def _generate_candidates(self, n_candidates: int = 20) -> List[nx.DiGraph]:
        """Generate candidate mutations for evaluation."""
        candidates = []

        # Use previous best as starting points
        if self._evaluated_objectives:
            best_indices = sorted(
                range(len(self._evaluated_objectives)),
                key=lambda i: self._evaluated_objectives[i]
            )[:3]

            for idx in best_indices:
                base_graph = self._evaluated_graphs[idx]
                n_from_this = n_candidates // len(best_indices)

                for _ in range(n_from_this):
                    candidates.append(self._generate_mutation(base_graph))

        # Fill remaining with baseline mutations
        while len(candidates) < n_candidates:
            candidates.append(self._generate_mutation(self.baseline_graph))

        return candidates

    def _check_constraints(self, graph: nx.DiGraph) -> bool:
        """Check if graph satisfies all constraints."""
        metrics = self.complexity_metrics.compute_all(graph)

        for constraint in self.config.constraints:
            if constraint.name == "max_services":
                services = set()
                for n, data in graph.nodes(data=True):
                    s = data.get('service_id', data.get('allocated_to'))
                    if s:
                        services.add(s)
                if not constraint.is_satisfied(len(services)):
                    return False

            elif constraint.name == "max_path_length":
                if not constraint.is_satisfied(metrics.structural.longest_path_length):
                    return False

            elif constraint.name == "max_coupling":
                if not constraint.is_satisfied(metrics.architecture.service_coupling):
                    return False

            elif constraint.name == "max_context":
                if not constraint.is_satisfied(metrics.architecture.max_path_context):
                    return False

        return True

    def _generate_recommendations(
        self,
        baseline: nx.DiGraph,
        optimized: nx.DiGraph
    ) -> List[str]:
        """Generate human-readable recommendations."""
        recommendations = []

        baseline_metrics = self.complexity_metrics.compute_all(baseline)
        optimized_metrics = self.complexity_metrics.compute_all(optimized)

        # Compare service allocation
        baseline_services = set()
        optimized_services = set()

        for n, data in baseline.nodes(data=True):
            s = data.get('service_id', data.get('allocated_to'))
            if s:
                baseline_services.add(s)

        for n, data in optimized.nodes(data=True):
            s = data.get('service_id', data.get('allocated_to'))
            if s:
                optimized_services.add(s)

        if len(optimized_services) < len(baseline_services):
            recommendations.append(
                f"Consider consolidating services: {len(baseline_services)} -> {len(optimized_services)}"
            )
        elif len(optimized_services) > len(baseline_services):
            recommendations.append(
                f"Consider splitting services for better modularity: {len(baseline_services)} -> {len(optimized_services)}"
            )

        # Context improvement
        if optimized_metrics.architecture.max_path_context < baseline_metrics.architecture.max_path_context:
            improvement = (1 - optimized_metrics.architecture.max_path_context /
                         baseline_metrics.architecture.max_path_context) * 100
            recommendations.append(
                f"Context consumption reduced by {improvement:.1f}% on critical paths"
            )

        # Coupling improvement
        if optimized_metrics.architecture.service_coupling < baseline_metrics.architecture.service_coupling:
            recommendations.append(
                f"Service coupling reduced: {baseline_metrics.architecture.service_coupling:.2f} -> "
                f"{optimized_metrics.architecture.service_coupling:.2f}"
            )

        # Coordination improvement
        if optimized_metrics.architecture.coordination_complexity < baseline_metrics.architecture.coordination_complexity:
            recommendations.append(
                f"Coordination complexity reduced: {baseline_metrics.architecture.coordination_complexity:.2f} -> "
                f"{optimized_metrics.architecture.coordination_complexity:.2f}"
            )

        if not recommendations:
            recommendations.append("Current architecture is near optimal for the specified objective")

        return recommendations

    def save_result(self, result: OptimizationResult, path: Path) -> None:
        """Save optimization result to JSON."""
        output = {
            "optimization_result": result.to_dict(),
            "config": {
                "objective": self.config.objective.value,
                "n_iterations": self.config.n_iterations,
                "context_threshold": self.config.context_threshold
            },
            "metadata": {
                "tool": "bayesian_architecture_optimizer",
                "version": "0.1.0",
                "generated": datetime.now().isoformat()
            }
        }

        with open(path, 'w') as f:
            json.dump(output, f, indent=2)


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Bayesian optimization for architectural DAGs"
    )
    parser.add_argument(
        "functional_architecture",
        type=Path,
        help="Path to functional_architecture.json"
    )
    parser.add_argument(
        "--objective",
        type=str,
        default="minimize_complexity",
        choices=[o.value for o in ObjectiveType if o != ObjectiveType.CUSTOM],
        help="Optimization objective"
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=20,
        help="Number of optimization iterations"
    )
    parser.add_argument(
        "--max-services",
        type=int,
        help="Maximum number of services constraint"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output path for results JSON"
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Random seed for reproducibility"
    )

    args = parser.parse_args()

    # Build constraints
    constraints = {}
    if args.max_services:
        constraints["max_services"] = args.max_services

    # Create optimizer
    config = OptimizationConfig(
        n_iterations=args.iterations,
        seed=args.seed
    )

    optimizer = BayesianArchitectureOptimizer(
        functional_architecture=args.functional_architecture,
        config=config
    )

    # Run optimization
    result = optimizer.optimize(
        objective=args.objective,
        constraints=constraints
    )

    # Output results
    if args.output:
        optimizer.save_result(result, args.output)
        print(f"\nResults saved to {args.output}")
    else:
        print("\n=== Recommendations ===")
        for rec in result.recommendations:
            print(f"  - {rec}")

        print(f"\n=== Summary ===")
        print(f"  Baseline: {result.baseline_objective:.4f}")
        print(f"  Best: {result.best_objective:.4f}")
        print(f"  Improvement: {result.improvement_percentage:.1f}%")


if __name__ == "__main__":
    main()
