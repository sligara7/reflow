"""
Bayesian Optimization for Architectural DAGs

This module provides Bayesian optimization capabilities for optimizing
architectural Directed Acyclic Graphs (DAGs) in the Reflow framework.

Focuses on early-phase architecture optimization:
- Functional Analysis (FA phases)
- Functional Allocation to Services (SE phases)

Key Components:
- dag_complexity_metrics: Measures DAG complexity via multiple metrics
- dag_feature_extractor: Converts DAGs to feature vectors for optimization
- surrogate_model: Gaussian Process surrogate for modeling objective function
- acquisition_functions: EI, UCB, PI for proposing next architectures
- bayesian_architecture_optimizer: Main orchestration module

Usage:
    from tools.bayesian_optimization import BayesianArchitectureOptimizer

    optimizer = BayesianArchitectureOptimizer(
        functional_architecture_path="specs/machine/functional_architecture.json",
        service_architecture_path="specs/machine/service_architecture.json"
    )

    result = optimizer.optimize(
        objective="minimize_context_bottlenecks",
        constraints={"max_services": 10, "max_path_length": 8}
    )

Version: 0.1.0 (Experimental)
"""

__version__ = "0.1.0"

from .dag_complexity_metrics import DAGComplexityMetrics
from .dag_feature_extractor import DAGFeatureExtractor
from .surrogate_model import GaussianProcessSurrogate
from .acquisition_functions import (
    expected_improvement,
    upper_confidence_bound,
    probability_of_improvement
)
from .bayesian_architecture_optimizer import BayesianArchitectureOptimizer

__all__ = [
    "DAGComplexityMetrics",
    "DAGFeatureExtractor",
    "GaussianProcessSurrogate",
    "BayesianArchitectureOptimizer",
    "expected_improvement",
    "upper_confidence_bound",
    "probability_of_improvement",
]
