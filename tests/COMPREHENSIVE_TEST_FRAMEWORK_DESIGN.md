# Reflow Comprehensive Test Framework - Design Document

**Version**: 1.0.0
**Created**: 2025-10-27
**Status**: Design Phase → Implementation

---

## Vision

Create a **comprehensive, modular test framework** that validates:

1. **Tool Capabilities** - Each tool performs its intended function correctly
2. **Workflow Steps** - Workflows call tools at the right time with right parameters
3. **End-to-End Flows** - Complete workflow sequences produce correct outputs
4. **Performance Baselines** - Track capabilities and performance over versions

### Design Principles

1. **Start Small, Scale Big** - Begin with a few tests, easy to add more
2. **Modular** - Each test category independent, can run separately
3. **Self-Documenting** - Each test explains what it validates and why
4. **CI/CD Ready** - Automated execution, exit codes, baseline reports
5. **Incremental** - Add new tests as features are added/changed

---

## Framework Architecture

```
tests/
├── run_all_tests.py                      # Master test runner (all categories)
├── test_framework/                       # Shared framework code
│   ├── __init__.py
│   ├── base_test.py                      # Base test class
│   ├── test_runner.py                    # Test discovery and execution
│   └── report_generator.py               # Baseline report generation
├── fixtures/                             # Test data organized by category
│   ├── tool_capabilities/                # Category 1: Tool-specific tests
│   │   ├── system_of_systems_graph/     # Tests for system_of_systems_graph_v2.py
│   │   │   ├── bottleneck_detection/
│   │   │   │   ├── README.md
│   │   │   │   ├── expected_output.json
│   │   │   │   └── specs/...
│   │   │   ├── centrality_analysis/
│   │   │   ├── orphaned_nodes/
│   │   │   ├── knowledge_gaps/          # Move existing tests here
│   │   │   ├── dag_validation/
│   │   │   ├── cycle_detection/
│   │   │   └── README.md
│   │   ├── validate_architecture/       # Tests for validate_architecture.py
│   │   │   ├── constraint_violations/
│   │   │   ├── missing_fields/
│   │   │   └── README.md
│   │   ├── generate_interface_contracts/ # Tests for generate_interface_contracts.py
│   │   │   ├── rest_api_contracts/
│   │   │   ├── grpc_contracts/
│   │   │   └── README.md
│   │   └── README.md                     # Tool capability testing overview
│   ├── workflow_steps/                   # Category 2: Workflow step validation
│   │   ├── SE-02_architecture_design/
│   │   │   ├── framework_selection/
│   │   │   ├── service_identification/
│   │   │   └── README.md
│   │   ├── SE-06_graph_generation/
│   │   │   ├── correct_tool_invocation/
│   │   │   ├── parameter_validation/
│   │   │   └── README.md
│   │   ├── D-07_pre_deployment/
│   │   │   ├── dependency_validation/
│   │   │   ├── module_structure/
│   │   │   └── README.md
│   │   └── README.md                     # Workflow step testing overview
│   └── end_to_end/                       # Category 3: Complete workflow sequences
│       ├── greenfield_system/
│       │   ├── simple_microservices/
│       │   └── README.md
│       ├── bottom_up_integration/
│       │   ├── legacy_integration/
│       │   └── README.md
│       └── README.md                     # End-to-end testing overview
├── reports/                              # Generated reports
│   ├── baseline/
│   │   ├── tool_capabilities_baseline.json
│   │   ├── workflow_steps_baseline.json
│   │   └── end_to_end_baseline.json
│   └── latest/
│       └── test_run_YYYYMMDD_HHMMSS.json
└── README.md                             # Framework documentation
```

---

## Test Categories

### Category 1: Tool Capabilities

**Purpose**: Validate that each tool performs its intended function correctly.

**Example**: `system_of_systems_graph_v2.py` has 25+ analysis features:
- Bottleneck detection
- Centrality analysis (degree, betweenness, closeness, eigenvector)
- Orphaned node detection
- Knowledge gap detection (6 types)
- DAG validation
- Cycle detection
- Strongly connected components
- Community detection
- Flow analysis

**Test Structure**:
```
fixtures/tool_capabilities/system_of_systems_graph/bottleneck_detection/
├── README.md                          # What is a bottleneck, why detect it
├── expected_output.json               # Expected bottlenecks
├── specs/machine/
│   ├── service_arch_index.json
│   └── service_arch/
│       ├── api_gateway_architecture.json  # 5 services depend on this → bottleneck
│       ├── service1_architecture.json
│       ├── service2_architecture.json
│       └── ...
```

**Test Execution**:
```python
# Run tool
result = subprocess.run([
    "python3", "tools/system_of_systems_graph_v2.py",
    "specs/machine/service_arch_index.json",
    "--centrality",  # Enable centrality analysis
    "--output", "detected_bottlenecks.json"
])

# Compare
expected = load_json("expected_output.json")
detected = load_json("detected_bottlenecks.json")

# Validate
assert detected['graph_analysis']['centrality']['degree_centrality']['api_gateway'] > 0.8
assert 'api_gateway' in detected['bottlenecks']  # High in-degree = bottleneck
```

**Examples to Implement**:
1. **Bottleneck Detection** - Service with high in-degree (many services depend on it)
2. **Centrality Analysis** - Identify critical nodes (degree, betweenness centrality)
3. **Orphaned Nodes** - Services with no incoming or outgoing edges
4. **DAG Validation** - Architecture should be acyclic (or identify cycles)
5. **Cycle Detection** - Circular dependencies between services
6. **Strongly Connected Components** - Groups of services with circular paths
7. **Community Detection** - Service clusters (Louvain algorithm)

### Category 2: Workflow Step Validation

**Purpose**: Validate that workflows call the right tools at the right time with correct parameters.

**Example**: Step SE-06 (Graph Generation) should:
1. Call `system_of_systems_graph_v2.py` with correct index path
2. Enable appropriate analysis flags based on framework
3. Detect knowledge gaps (`--detect-gaps`)
4. Generate output at correct location
5. Fail if validation errors found

**Test Structure**:
```
fixtures/workflow_steps/SE-06_graph_generation/correct_tool_invocation/
├── README.md                          # What SE-06 should do
├── expected_behavior.json             # Expected tool calls and parameters
├── input/
│   ├── context/working_memory.json    # Simulated workflow state
│   └── specs/machine/...              # Simulated architecture
└── validation_script.py               # Validate SE-06 behavior
```

**Test Execution**:
```python
# Simulate SE-06 execution
working_memory = load_json("input/context/working_memory.json")
framework_id = working_memory['framework_selection']['framework_id']

# Validate correct tool invocation
expected_flags = get_recommended_analyses(framework_id)  # From framework_registry.json
actual_command = simulate_step_SE06(working_memory)

# Check
assert "--detect-gaps" in actual_command
assert "--centrality" in actual_command if "centrality" in expected_flags
assert output_path_correct(actual_command, working_memory['paths']['system_root'])
```

**Examples to Implement**:
1. **SE-02 Architecture Design** - Creates correct architecture files
2. **SE-06 Graph Generation** - Calls graph tool with correct flags
3. **D-07 Pre-Deployment Validation** - Runs 3 validation tools in sequence
4. **BU-03 Gap Analysis** - Calls integration gap detection tool
5. **TO-02 Docker Compose** - Validates docker-compose.yml structure

### Category 3: End-to-End Workflow Sequences

**Purpose**: Validate complete workflow executions produce correct outputs.

**Example**: Greenfield microservices system (00a → 01a → 01c → 02 → DONE)
- Input: Empty system directory + requirements doc
- Expected: Complete architecture specs, system graph, ICDs, diagrams
- Validation: All artifacts created, validation gates pass, no errors

**Test Structure**:
```
fixtures/end_to_end/greenfield_system/simple_microservices/
├── README.md                          # System description
├── input/
│   ├── requirements.txt               # System requirements
│   └── initial_context.json           # Starting state
├── expected_output/
│   ├── specs/machine/                 # Expected architectures
│   ├── specs/machine/graphs/          # Expected system graph
│   └── specs/human/                   # Expected diagrams
└── workflow_sequence.json             # Which workflows to run
```

**Test Execution**:
```python
# Run workflow sequence
for workflow in ["00a-basic_setup", "01a-approach_detection", "01c-top_down_design", "02-artifacts_visualization"]:
    result = simulate_workflow_execution(workflow, input_state)
    assert result['status'] == 'success'
    input_state = result['output_state']  # Chain to next workflow

# Validate outputs
assert architecture_files_created(expected_count=3)
assert system_graph_valid()
assert icd_files_created(expected_count=6)
assert diagrams_generated(expected_count=4)
```

**Examples to Implement**:
1. **Greenfield Microservices** - 00a → 01a → 01c → 02
2. **Bottom-Up Integration** - 00a → 01a → 01b → 02
3. **Feature Update** - feature_update.json on existing system
4. **Architecture-Only** - 00a → 01a → 01c → 02 (minimal) → STOP

---

## Test Framework Components

### 1. Base Test Class (`test_framework/base_test.py`)

```python
class ReflowTest:
    """Base class for all Reflow tests"""

    def __init__(self, test_dir: Path):
        self.test_dir = test_dir
        self.test_name = test_dir.name
        self.category = self.get_category()

    def get_category(self) -> str:
        """Determine test category from path"""
        if "tool_capabilities" in str(self.test_dir):
            return "tool_capabilities"
        elif "workflow_steps" in str(self.test_dir):
            return "workflow_steps"
        elif "end_to_end" in str(self.test_dir):
            return "end_to_end"
        return "unknown"

    def load_expected(self) -> Dict:
        """Load expected output"""
        raise NotImplementedError

    def run(self) -> Dict:
        """Execute test"""
        raise NotImplementedError

    def validate(self, detected: Dict, expected: Dict) -> Tuple[bool, List[str]]:
        """Compare detected vs expected"""
        raise NotImplementedError
```

### 2. Test Runner (`test_framework/test_runner.py`)

```python
class ReflowTestRunner:
    """Discovers and executes tests"""

    def discover_tests(self, category: str = None) -> List[ReflowTest]:
        """Find all tests, optionally filtered by category"""
        pass

    def run_tests(self, tests: List[ReflowTest]) -> List[Dict]:
        """Execute tests and collect results"""
        pass

    def generate_report(self, results: List[Dict]) -> None:
        """Generate test report"""
        pass
```

### 3. Master Test Runner (`run_all_tests.py`)

```python
#!/usr/bin/env python3
"""
Reflow Comprehensive Test Suite

Runs all tests or filtered by category/tool/workflow.

Usage:
    python3 tests/run_all_tests.py
    python3 tests/run_all_tests.py --category tool_capabilities
    python3 tests/run_all_tests.py --tool system_of_systems_graph_v2.py
    python3 tests/run_all_tests.py --workflow SE-06
    python3 tests/run_all_tests.py --baseline
"""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", choices=["tool_capabilities", "workflow_steps", "end_to_end"])
    parser.add_argument("--tool", help="Filter by tool name")
    parser.add_argument("--workflow", help="Filter by workflow step")
    parser.add_argument("--baseline", action="store_true")
    args = parser.parse_args()

    runner = ReflowTestRunner()
    tests = runner.discover_tests(category=args.category, tool=args.tool, workflow=args.workflow)
    results = runner.run_tests(tests)

    if args.baseline:
        runner.generate_baseline_report(results)
```

---

## Starting Small: Initial Implementation

### Phase 1: Expand Tool Capability Tests (Current Priority)

**Goal**: Expand `system_of_systems_graph_v2.py` testing beyond knowledge gaps.

**Tests to Add**:
1. **Bottleneck Detection** (1-2 hours)
   - Create architecture with 1 high-degree node (api_gateway with 5 dependents)
   - Expected: High degree centrality, identified as bottleneck

2. **Orphaned Node Detection** (1 hour)
   - Create architecture with 1 service with no edges (orphaned_service)
   - Expected: Detected as orphaned (0 in-degree, 0 out-degree)

3. **Cycle Detection** (1-2 hours)
   - Create architecture with circular dependency (A→B→C→A)
   - Expected: Cycle detected, services identified

4. **DAG Validation** (30 min)
   - Reuse cycle detection test
   - Expected: DAG validation fails when cycles present

**Total Time**: ~4-5 hours
**Value**: Validates 4 critical features of flagship tool

### Phase 2: Add Workflow Step Tests (Future)

**Goal**: Validate SE-06 calls tools correctly.

**Tests to Add**:
1. **SE-06 Tool Invocation** - Correct flags based on framework
2. **SE-06 Output Location** - Correct path for system_of_systems_graph.json
3. **SE-06 Error Handling** - Fails gracefully on invalid architectures

### Phase 3: Add End-to-End Tests (Future)

**Goal**: Validate complete workflow sequences.

**Tests to Add**:
1. **Greenfield Flow** - 00a → 01a → 01c → 02
2. **Bottom-Up Flow** - 00a → 01a → 01b → 02

---

## Baseline Reporting

### Per-Category Baselines

```json
// reports/baseline/tool_capabilities_baseline.json
{
  "generated": "2025-10-27T12:00:00",
  "reflow_version": "3.7.0",
  "category": "tool_capabilities",
  "tools_tested": {
    "system_of_systems_graph_v2.py": {
      "total_tests": 10,
      "passed": 10,
      "failed": 0,
      "pass_rate": 100.0,
      "features_validated": [
        "bottleneck_detection",
        "centrality_analysis",
        "orphaned_nodes",
        "knowledge_gaps",
        "dag_validation",
        "cycle_detection"
      ]
    },
    "validate_architecture.py": {
      "total_tests": 5,
      "passed": 5,
      "failed": 0,
      "pass_rate": 100.0
    }
  }
}
```

---

## Benefits

1. **Comprehensive Validation** - Test tools, workflows, AND end-to-end flows
2. **Incremental Growth** - Start with a few tests, easy to add more
3. **Regression Prevention** - Catch breaking changes before release
4. **Performance Baseline** - Track capabilities over versions
5. **Documentation** - Tests show how tools/workflows should be used
6. **CI/CD Integration** - Automated quality assurance

---

## Implementation Plan

### Week 1: Foundation
- [x] Design framework architecture (this document)
- [ ] Implement base test classes
- [ ] Implement test runner
- [ ] Move existing knowledge gap tests to new structure
- [ ] Validate framework works with existing tests

### Week 2: Expand Tool Tests
- [ ] Add bottleneck detection test
- [ ] Add orphaned node detection test
- [ ] Add cycle detection test
- [ ] Add DAG validation test
- [ ] Generate baseline report for system_of_systems_graph_v2.py

### Week 3: Workflow Step Tests
- [ ] Add SE-06 tool invocation test
- [ ] Add D-07 validation sequence test
- [ ] Generate baseline report for workflow_steps

### Week 4: End-to-End Tests
- [ ] Add greenfield workflow sequence test
- [ ] Add bottom-up workflow sequence test
- [ ] Generate comprehensive baseline report

### Ongoing:
- [ ] Add tests as new features added
- [ ] Integrate into CI/CD pipeline
- [ ] Update baselines after major changes

---

## Next Steps

1. **Approve Design** - Review and approve this architecture
2. **Implement Base Classes** - Create test_framework/ components
3. **Restructure Existing Tests** - Move knowledge gap tests to new structure
4. **Add Bottleneck Test** - First new tool capability test
5. **Document** - Update tests/README.md with new structure

---

**Questions?**
- Is this architecture aligned with your vision?
- Should we prioritize different test types?
- Any specific tools/workflows to test first?

---

**Status**: Design complete, awaiting approval to implement
