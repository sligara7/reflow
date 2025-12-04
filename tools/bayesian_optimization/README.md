# Bayesian Optimization for Architectural DAGs

**Version**: 0.1.0 (Experimental)
**Status**: Research/Exploration Module

## Overview

This module explores using **Bayesian Optimization** to optimize architectural trade-offs in Reflow's Directed Acyclic Graphs (DAGs). It focuses on the early phases of system design:

- **Functional Analysis (FA)** - Defining what functions exist and how they interact
- **Functional Allocation (SE-01, SE-02)** - Allocating functions to services

The key insight is that architectural DAGs have many interconnected properties (complexity, coupling, context consumption, coordination) that are difficult to optimize manually. Bayesian optimization provides a principled way to explore this trade-off space.

## Why Bayesian Optimization?

Traditional optimization requires knowing the gradient of the objective function. For architectural complexity:

1. **The objective is expensive to evaluate** - Computing complexity metrics requires graph analysis
2. **The search space is discrete/combinatorial** - Service allocations, interface patterns
3. **Multiple competing objectives** - Low coupling vs. high cohesion, simplicity vs. flexibility
4. **No analytical gradient** - We can evaluate complexity, but not differentiate it

Bayesian optimization is designed for exactly this scenario:
- Uses a probabilistic surrogate model (Gaussian Process) to model the objective
- Balances exploration (uncertainty) and exploitation (predicted optima)
- Typically finds good solutions in 10-50 evaluations

## Theory

### 1. DAG Complexity Metrics

"Complexity" in a DAG is multi-dimensional. We measure:

| Category | Metrics | Purpose |
|----------|---------|---------|
| **Size** | nodes, edges, ratio | Scale of architecture |
| **Structural** | density, longest path, branching, layers | Topology shape |
| **Centrality** | degree, betweenness, bottlenecks | Critical nodes |
| **Information** | graph entropy, topological entropy | Information content |
| **Architecture** | context consumption, coupling, coordination | Reflow-specific |

### 2. Feature Engineering

To apply Bayesian optimization, we convert DAGs to fixed-length feature vectors:

```
DAG → [num_nodes, density, longest_path, coupling, context, ...] → ℝ^d
```

This featurization captures the essential properties while enabling the GP to learn patterns.

### 3. Gaussian Process Surrogate

The GP models the unknown objective function:

```
f(x) ~ GP(m(x), k(x, x'))
```

Where:
- `m(x)` is the prior mean (we use zero)
- `k(x, x')` is the covariance kernel (RBF or Matern)

Given observations, the GP provides:
- **Predicted mean**: Expected objective value
- **Predicted variance**: Uncertainty in prediction

### 4. Acquisition Functions

Acquisition functions balance exploration vs. exploitation:

| Function | Formula | Behavior |
|----------|---------|----------|
| **Expected Improvement (EI)** | E[max(0, f_best - f(x))] | Most popular, automatic balance |
| **Upper Confidence Bound (UCB)** | μ(x) + κσ(x) | Tunable exploration via κ |
| **Probability of Improvement (PI)** | P(f(x) < f_best) | Conservative |
| **Thompson Sampling** | Sample from posterior | Natural exploration |

### 5. Optimization Loop

```
1. Initialize with random samples
2. Fit GP to observed (features, objectives)
3. For each iteration:
   a. Generate candidate architecture mutations
   b. Predict mean/variance with GP
   c. Compute acquisition values
   d. Select best acquisition → evaluate objective
   e. Update GP
4. Return best observed architecture
```

## Architecture Mutations

The optimizer explores architecture space through mutations:

| Mutation | Description |
|----------|-------------|
| **Reallocate Function** | Move function to different service |
| **Merge Services** | Combine two services |
| **Split Service** | Split service into two |
| **Change Interface** | Modify edge weight/pattern |

## Optimization Objectives

Predefined objectives:

| Objective | Description |
|-----------|-------------|
| `minimize_complexity` | Overall composite complexity score |
| `minimize_context_bottlenecks` | Context consumption on critical paths |
| `minimize_coupling` | Service coupling and interface density |
| `maximize_modularity` | Function distribution and independence |
| `minimize_coordination` | Cross-service coordination complexity |
| `balance_multi_objective` | Weighted combination of above |

## Installation

No additional dependencies beyond Reflow's standard requirements:

```bash
# Core requirement (already in Reflow)
pip install networkx>=3.0

# Optional (for faster computation)
pip install numpy
```

## Usage

### Basic Usage

```python
from tools.bayesian_optimization import BayesianArchitectureOptimizer

# Initialize with functional architecture
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
for rec in result.recommendations:
    print(f"- {rec}")

print(f"Improvement: {result.improvement_percentage:.1f}%")
```

### Command Line

```bash
# Basic optimization
python -m tools.bayesian_optimization.bayesian_architecture_optimizer \
    specs/machine/functional_architecture.json \
    --objective minimize_coupling \
    --iterations 30 \
    --output optimization_results.json

# With constraints
python -m tools.bayesian_optimization.bayesian_architecture_optimizer \
    specs/machine/functional_architecture.json \
    --objective minimize_context_bottlenecks \
    --max-services 8 \
    --seed 42
```

### Computing Complexity Metrics Only

```python
from tools.bayesian_optimization import DAGComplexityMetrics, load_graph_from_json

graph = load_graph_from_json("specs/machine/functional_architecture.json")
metrics = DAGComplexityMetrics()

complexity = metrics.compute_all(graph)
print(f"Nodes: {complexity.size.num_nodes}")
print(f"Longest path: {complexity.structural.longest_path_length}")
print(f"Service coupling: {complexity.architecture.service_coupling}")
print(f"Context bottlenecks: {complexity.architecture.context_bottleneck_paths}")

# Composite score
score = metrics.compute_composite_score(graph)
print(f"Overall complexity: {score:.4f}")
```

### Extracting Features

```python
from tools.bayesian_optimization import DAGFeatureExtractor, load_graph_from_json

graph = load_graph_from_json("specs/machine/functional_architecture.json")
extractor = DAGFeatureExtractor()

features = extractor.extract(graph)
feature_names = extractor.get_feature_names()

for name, value in zip(feature_names, features):
    print(f"{name}: {value:.4f}")
```

### Custom Objective Function

```python
def my_objective(graph):
    """Custom objective: minimize path variance."""
    import networkx as nx

    paths = []
    for source in [n for n in graph.nodes() if graph.in_degree(n) == 0]:
        for target in [n for n in graph.nodes() if graph.out_degree(n) == 0]:
            if nx.has_path(graph, source, target):
                paths.append(nx.shortest_path_length(graph, source, target))

    if not paths:
        return 0

    mean_path = sum(paths) / len(paths)
    variance = sum((p - mean_path)**2 for p in paths) / len(paths)
    return variance

optimizer = BayesianArchitectureOptimizer(
    functional_architecture="specs/machine/functional_architecture.json"
)

result = optimizer.optimize(objective=my_objective)
```

## Module Structure

```
tools/bayesian_optimization/
├── __init__.py                      # Package exports
├── README.md                        # This documentation
├── dag_complexity_metrics.py        # Complexity measurement
├── dag_feature_extractor.py         # DAG → feature vector
├── surrogate_model.py               # Gaussian Process implementation
├── acquisition_functions.py         # EI, UCB, PI, Thompson Sampling
├── bayesian_architecture_optimizer.py  # Main orchestration
└── examples/                        # Usage examples
    └── (future examples)
```

## Constraints

Supported constraints:

| Constraint | Description |
|------------|-------------|
| `max_services` | Maximum number of services |
| `max_path_length` | Maximum DAG longest path |
| `max_coupling` | Maximum service coupling ratio |
| `max_context` | Maximum path context consumption |

## Output Format

The optimization result includes:

```json
{
  "optimization_result": {
    "best_objective": 0.342,
    "baseline_objective": 0.567,
    "improvement_percentage": 39.7,
    "recommendations": [
      "Consider consolidating services: 8 -> 6",
      "Context consumption reduced by 23.4% on critical paths"
    ],
    "iteration_history": [...]
  },
  "config": {
    "objective": "minimize_context_bottlenecks",
    "n_iterations": 20
  },
  "metadata": {
    "tool": "bayesian_architecture_optimizer",
    "version": "0.1.0"
  }
}
```

## Integration with Reflow Workflows

This module is designed to integrate with:

- **FA-06**: Automated functional gap closure
- **SE-02-A00**: Service organization strategy analysis
- **SE-02-A05**: Service architecture refinement

Future workflow integration:
```json
{
  "action_id": "SE-02-A00B",
  "action": "Bayesian Architecture Optimization (OPTIONAL)",
  "description": "Run Bayesian optimization to explore service allocation trade-offs",
  "tools": ["bayesian_architecture_optimizer.py"]
}
```

## Limitations

1. **Experimental Status**: This is a research module, not production-ready
2. **Computational Cost**: GP inference is O(n³) in observations
3. **Discrete Search Space**: Mutations are random; could benefit from structured search
4. **No Pareto Optimization**: Multi-objective is weighted sum, not true Pareto
5. **Graph Size**: May struggle with very large graphs (>500 nodes)

## Future Directions

1. **Graph Kernels**: Use Weisfeiler-Lehman kernel instead of feature extraction
2. **Multi-Fidelity**: Use cheap approximations before expensive evaluations
3. **Pareto Optimization**: True multi-objective with Pareto frontier
4. **Constraint Learning**: Learn constraints from user feedback
5. **Transfer Learning**: Reuse GP across similar architectures

## References

1. Shahriari et al. (2016). "Taking the Human Out of the Loop: A Review of Bayesian Optimization"
2. Snoek et al. (2012). "Practical Bayesian Optimization of Machine Learning Algorithms"
3. Neural Architecture Search literature for graph-based BO approaches

## Contributing

This is an experimental module. Contributions welcome:
- Additional objective functions
- Graph kernel implementations
- Performance improvements
- Workflow integration
