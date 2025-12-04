#!/usr/bin/env python3
"""
Example: Optimize Functional Architecture

This example demonstrates how to use Bayesian optimization to find
optimal service allocations for a functional architecture.

Usage:
    python examples/optimize_functional_architecture.py path/to/functional_architecture.json

Example with synthetic graph:
    python examples/optimize_functional_architecture.py --synthetic
"""

import json
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    import networkx as nx
except ImportError:
    print("Error: NetworkX is required. Install with: pip install networkx>=3.0")
    sys.exit(1)

from bayesian_optimization import (
    BayesianArchitectureOptimizer,
    DAGComplexityMetrics,
    DAGFeatureExtractor,
    OptimizationConfig,
    ObjectiveType
)
from bayesian_optimization.dag_complexity_metrics import load_graph_from_json


def create_synthetic_architecture() -> nx.DiGraph:
    """Create a synthetic functional architecture for demonstration."""
    G = nx.DiGraph()

    # Define functions with service allocations
    functions = [
        # API Gateway service
        ("F001", {"function_name": "AuthenticateRequest", "function_type": "validate", "service_id": "api_gateway"}),
        ("F002", {"function_name": "RouteRequest", "function_type": "process", "service_id": "api_gateway"}),

        # User service
        ("F003", {"function_name": "GetUserProfile", "function_type": "read", "service_id": "user_service"}),
        ("F004", {"function_name": "UpdateUserProfile", "function_type": "write", "service_id": "user_service"}),
        ("F005", {"function_name": "ValidateUserData", "function_type": "validate", "service_id": "user_service"}),

        # Order service
        ("F006", {"function_name": "CreateOrder", "function_type": "write", "service_id": "order_service"}),
        ("F007", {"function_name": "ProcessPayment", "function_type": "process", "service_id": "order_service"}),
        ("F008", {"function_name": "ValidateOrder", "function_type": "validate", "service_id": "order_service"}),
        ("F009", {"function_name": "GetOrderHistory", "function_type": "read", "service_id": "order_service"}),

        # Inventory service
        ("F010", {"function_name": "CheckInventory", "function_type": "read", "service_id": "inventory_service"}),
        ("F011", {"function_name": "ReserveInventory", "function_type": "write", "service_id": "inventory_service"}),
        ("F012", {"function_name": "ReleaseInventory", "function_type": "write", "service_id": "inventory_service"}),

        # Notification service
        ("F013", {"function_name": "SendEmail", "function_type": "process", "service_id": "notification_service"}),
        ("F014", {"function_name": "SendSMS", "function_type": "process", "service_id": "notification_service"}),

        # Analytics service
        ("F015", {"function_name": "LogEvent", "function_type": "write", "service_id": "analytics_service"}),
        ("F016", {"function_name": "GenerateReport", "function_type": "read", "service_id": "analytics_service"}),
    ]

    for func_id, attrs in functions:
        G.add_node(func_id, **attrs)

    # Define dependencies with context consumption weights
    dependencies = [
        # API flow
        ("F001", "F002", {"weight": 2000, "dependency_type": "function_call"}),
        ("F002", "F003", {"weight": 3000, "dependency_type": "function_call"}),
        ("F002", "F006", {"weight": 4000, "dependency_type": "function_call"}),

        # User service internal
        ("F005", "F004", {"weight": 1500, "dependency_type": "control_flow"}),

        # Order flow (complex cross-service coordination)
        ("F006", "F008", {"weight": 2500, "dependency_type": "function_call"}),
        ("F008", "F010", {"weight": 5000, "dependency_type": "function_call"}),  # Cross-service!
        ("F010", "F011", {"weight": 3000, "dependency_type": "function_call"}),
        ("F011", "F007", {"weight": 6000, "dependency_type": "data_flow"}),  # Cross-service!
        ("F007", "F013", {"weight": 2000, "dependency_type": "async"}),  # Cross-service!
        ("F007", "F015", {"weight": 1000, "dependency_type": "async"}),  # Cross-service!

        # Error handling
        ("F007", "F012", {"weight": 2000, "dependency_type": "error_flow"}),  # Cross-service!

        # User profile in order
        ("F006", "F003", {"weight": 3500, "dependency_type": "data_flow"}),  # Cross-service!

        # Analytics
        ("F006", "F015", {"weight": 500, "dependency_type": "async"}),  # Cross-service!
        ("F004", "F015", {"weight": 500, "dependency_type": "async"}),  # Cross-service!
    ]

    for source, target, attrs in dependencies:
        G.add_edge(source, target, **attrs)

    return G


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Optimize functional architecture example")
    parser.add_argument("path", nargs="?", type=Path, help="Path to functional_architecture.json")
    parser.add_argument("--synthetic", action="store_true", help="Use synthetic architecture")
    parser.add_argument("--objective", type=str, default="minimize_context_bottlenecks",
                       help="Optimization objective")
    parser.add_argument("--iterations", type=int, default=15, help="Number of iterations")

    args = parser.parse_args()

    # Load or create graph
    if args.synthetic:
        print("Creating synthetic architecture...")
        graph = create_synthetic_architecture()
    elif args.path:
        print(f"Loading architecture from {args.path}...")
        graph = load_graph_from_json(args.path)
    else:
        print("No path provided. Using synthetic architecture.")
        graph = create_synthetic_architecture()

    print(f"Graph: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges")

    # Analyze baseline
    print("\n=== Baseline Analysis ===")
    metrics = DAGComplexityMetrics()
    complexity = metrics.compute_all(graph)

    print(f"Size: {complexity.size.num_nodes} nodes, {complexity.size.num_edges} edges")
    print(f"Structural:")
    print(f"  Longest path: {complexity.structural.longest_path_length}")
    print(f"  Layers: {complexity.structural.num_layers}")
    print(f"  Avg branching: {complexity.structural.avg_branching_factor:.2f}")
    print(f"Architecture:")
    print(f"  Total context: {complexity.architecture.total_context_consumption:.0f}")
    print(f"  Max path context: {complexity.architecture.max_path_context:.0f}")
    print(f"  Context bottleneck paths: {complexity.architecture.context_bottleneck_paths}")
    print(f"  Service coupling: {complexity.architecture.service_coupling:.2f}")
    print(f"  Coordination complexity: {complexity.architecture.coordination_complexity:.2f}")

    # Extract features
    extractor = DAGFeatureExtractor()
    features = extractor.extract(graph)
    print(f"\nFeature vector dimension: {len(features)}")

    # Run optimization
    print(f"\n=== Running Bayesian Optimization ===")
    print(f"Objective: {args.objective}")
    print(f"Iterations: {args.iterations}")

    config = OptimizationConfig(
        n_iterations=args.iterations,
        n_initial_samples=5,
        seed=42  # For reproducibility
    )

    optimizer = BayesianArchitectureOptimizer(
        functional_architecture=graph,
        config=config
    )

    result = optimizer.optimize(
        objective=args.objective,
        constraints={"max_services": 10}
    )

    # Print results
    print("\n=== Optimization Results ===")
    print(f"Baseline objective: {result.baseline_objective:.4f}")
    print(f"Best objective: {result.best_objective:.4f}")
    print(f"Improvement: {result.improvement_percentage:.1f}%")

    print("\n=== Recommendations ===")
    for rec in result.recommendations:
        print(f"  • {rec}")

    # Compare metrics
    if result.best_graph is not None:
        print("\n=== Optimized Architecture Metrics ===")
        opt_complexity = metrics.compute_all(result.best_graph)
        print(f"Service coupling: {complexity.architecture.service_coupling:.2f} → {opt_complexity.architecture.service_coupling:.2f}")
        print(f"Coordination: {complexity.architecture.coordination_complexity:.2f} → {opt_complexity.architecture.coordination_complexity:.2f}")
        print(f"Max path context: {complexity.architecture.max_path_context:.0f} → {opt_complexity.architecture.max_path_context:.0f}")

    # Show iteration history
    print("\n=== Iteration History ===")
    best_so_far = float('inf')
    for i, obj in enumerate(result.objective_history[:10]):  # First 10
        best_so_far = min(best_so_far, obj)
        print(f"  {i+1}: {obj:.4f} (best: {best_so_far:.4f})")
    if len(result.objective_history) > 10:
        print(f"  ... ({len(result.objective_history) - 10} more iterations)")


if __name__ == "__main__":
    main()
