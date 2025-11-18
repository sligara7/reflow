# Reflow Testing Framework Guide

**Version**: 3.16.0
**Created**: 2025-11-18
**Purpose**: Automated testing infrastructure for Reflow workflows

---

## Overview

The Reflow Testing Framework enables automated validation of Reflow workflows by running them on pre-defined test systems and comparing outputs against expected results (ground truth).

### GAN-Inspired Architecture

The framework uses a **Generative Adversarial Network (GAN)** inspired approach:

**Agent A (Generator)**:
- Executes Reflow workflows to build/design systems
- Input: Requirements → Output: Architecture artifacts (functional_architecture.json, service_architecture.json, etc.)
- Goal: Produce valid, high-quality architectures that match requirements

**Agent B (Discriminator)**:
- Evaluates Agent A's outputs against expected ground truth
- Scores similarity and identifies gaps/differences
- Provides feedback on what's wrong or missing
- Goal: Distinguish between valid and invalid architectures

**Adversarial Loop** (Future Enhancement):
```
1. Agent A builds system using Reflow workflows
2. Agent B evaluates outputs, scores quality (0.0-1.0)
3. Agent B provides specific feedback to Agent A
4. Agent A iterates to improve based on feedback
5. Repeat until Agent B accepts (score >= 0.95)
```

This addresses the "conflict of interests" problem: Agent A and Agent B are separate, with Agent B having access to ground truth that Agent A does not see during generation.

---

## Framework Components

### 1. Test Systems (`tests/test_systems/`)

Each test case is a directory containing:

```
tests/test_systems/microservices_basic/
├── requirements.md              # Input: System requirements
├── expected_outputs/            # Ground truth (Agent B's reference)
│   ├── functional_architecture.json
│   ├── service_architecture.json
│   ├── interface_registry.json
│   └── ...
└── actual_outputs/              # Agent A's generated outputs
    └── (populated during test execution)
```

**Test Case Structure**:
- `requirements.md`: Functional and non-functional requirements (human-readable)
- `expected_outputs/`: Pre-defined correct outputs for the test case (ground truth)
- `actual_outputs/`: Generated outputs from workflow execution (cleared before each test)

**Existing Test Cases**:
1. **microservices_basic**: Simple e-commerce system (19 functions, 7 services)
2. **api_gateway_pattern**: API gateway architecture pattern (coming soon)
3. **event_driven_system**: Event-driven microservices (coming soon)

### 2. Test Runner (`tests/test_runner.py`)

**Purpose**: Orchestrates workflow execution on test systems (Agent A controller)

**Usage**:
```bash
# List available test cases
python3 tests/test_runner.py --list-tests

# Execute single workflow on test case
python3 tests/test_runner.py \
  --test-case microservices_basic \
  --workflow-path 01d-functional_analysis

# Execute complete workflow path
python3 tests/test_runner.py \
  --test-case microservices_basic \
  --workflow-path 00a,01d,01c,02

# Execute on all test cases
python3 tests/test_runner.py \
  --test-case all \
  --workflow-path 01d
```

**Key Functions**:
- `prepare_test_environment()`: Clears previous outputs, sets up test environment
- `execute_workflow_step()`: Runs single workflow on test case
- `execute_workflow_path()`: Runs sequence of workflows
- `run_test_suite()`: Runs tests across multiple test cases
- `save_results()`: Saves execution results to JSON

**Current Limitation**:
The test runner currently creates the test environment and provides execution instructions, but **LLM agent invocation is not yet automated**. For now, manual execution is required:

1. Test runner prepares environment
2. Human manually invokes Claude Code agent: `"Implement workflow X on system Y"`
3. Test runner captures outputs for validation

**Future Enhancement (v3.17.0)**: Automate Agent A invocation using Claude Code CLI API or subprocess to launch separate agent instance.

### 3. Test Validator (`tests/test_validator.py`)

**Purpose**: Compares actual outputs against expected outputs (Agent B - Discriminator)

**Usage**:
```bash
# Validate single test case
python3 tests/test_validator.py --test-case microservices_basic

# Validate with strict matching (exact match required)
python3 tests/test_validator.py --test-case microservices_basic --strict

# Validate all test cases
python3 tests/test_validator.py --test-case all

# Custom output location
python3 tests/test_validator.py \
  --test-case microservices_basic \
  --output custom_validation_report.json
```

**Validation Modes**:

1. **Relaxed Mode (Default)**:
   - Similarity >= 0.95: PASS ✅
   - Allows minor differences (timestamps, metadata, formatting)
   - Suitable for most tests

2. **Strict Mode (`--strict`)**:
   - Requires exact match (similarity = 1.0)
   - No tolerance for any differences
   - Suitable for regression testing

**Validation Process**:
1. Load expected outputs (ground truth)
2. Load actual outputs (Agent A's generation)
3. Deep comparison of JSON structures
4. Calculate similarity score using difflib SequenceMatcher
5. Identify specific differences (path-based)
6. Generate validation report

**Similarity Scoring**:
- `1.0`: Identical (100% match)
- `0.95-0.99`: Very similar (minor differences)
- `0.80-0.94`: Moderately similar (some differences)
- `< 0.80`: Significantly different

**Output**:
```json
{
  "test_case": "microservices_basic",
  "overall_pass": true,
  "file_comparisons": [
    {
      "file": "functional_architecture.json",
      "match": true,
      "similarity_score": 0.98,
      "differences": [
        "root.metadata.timestamp: Value mismatch",
        "root.functions[2].description: Minor wording difference"
      ]
    }
  ]
}
```

### 4. Test Report Generator (Future - v3.17.0)

**Purpose**: Generate human-readable test reports with visualizations

**Planned Features**:
- HTML/Markdown reports with diff visualization
- Trend analysis across test runs
- Coverage reports (which workflows tested, which not)
- Performance metrics (execution time per workflow)

---

## Creating New Test Cases

### Step 1: Create Test Case Directory

```bash
mkdir -p tests/test_systems/my_new_test/{expected_outputs,actual_outputs}
```

### Step 2: Write Requirements

Create `tests/test_systems/my_new_test/requirements.md`:

```markdown
# Test System: My New Test

**Purpose**: Description of what this test case validates

**Domain**: System domain (e.g., healthcare, finance, IoT)

## Functional Requirements

### FR-1: Requirement Name
- Detailed requirement description
- Acceptance criteria

## Non-Functional Requirements

### NFR-1: Performance
- Specific performance targets

## Expected Architecture (Ground Truth)

### Services:
1. Service A: Purpose
2. Service B: Purpose

### Expected Functions:
1. FunctionName: Description
```

### Step 3: Generate Expected Outputs

**Option A - Manual Creation**:
1. Run Reflow workflows manually on a similar system
2. Validate outputs are correct
3. Copy to `expected_outputs/`

**Option B - Capture from Known Good System**:
1. Use existing validated system as template
2. Copy relevant artifacts to `expected_outputs/`
3. Modify to match your test case requirements

**Option C - Use Reflow to Bootstrap** (Recommended):
```bash
# 1. Run Reflow workflows on test case
cd tests/test_systems/my_new_test
# Invoke: "Implement workflow 01d-functional_analysis on system in $(pwd)"

# 2. Review and validate outputs
# 3. If correct, move to expected_outputs
mv specs/machine/functional/functional_architecture.json expected_outputs/

# 4. Clean actual outputs for test
rm -rf context/ specs/
```

### Step 4: Add Test Case Metadata (Optional)

Create `tests/test_systems/my_new_test/test_metadata.json`:

```json
{
  "test_name": "my_new_test",
  "description": "Test case for X pattern",
  "workflows_tested": ["01d", "01c", "02"],
  "expected_duration_minutes": 15,
  "difficulty": "medium",
  "tags": ["microservices", "healthcare", "async"]
}
```

---

## Running Tests

### Complete Test Workflow

```bash
# 1. List available tests
python3 tests/test_runner.py --list-tests

# 2. Execute test (currently manual LLM invocation)
python3 tests/test_runner.py \
  --test-case microservices_basic \
  --workflow-path 01d

# (Manual step: Invoke Claude Code agent to execute workflow)

# 3. Validate outputs
python3 tests/test_validator.py --test-case microservices_basic

# 4. Review validation report
cat tests/validation_report.json
```

### Continuous Integration (Future)

```yaml
# .github/workflows/reflow-tests.yml
name: Reflow Workflow Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run test suite
        run: python3 tests/test_runner.py --test-case all --workflow-path 01d
      - name: Validate outputs
        run: python3 tests/test_validator.py --test-case all
```

---

## Test Coverage

### Current Coverage (v3.16.0)

| Workflow | Test Cases | Status |
|----------|-----------|--------|
| 00a-basic_setup | 0 | ❌ Not tested |
| 01a-approach_detection | 0 | ❌ Not tested |
| 01b-bottom_up | 0 | ❌ Not tested |
| 01c-top_down | 0 | ❌ Not tested |
| 01d-functional_analysis | 1 | ✅ microservices_basic |
| 02-artifacts_visualization | 0 | ❌ Not tested |
| 03a-development_implementation | 0 | ❌ Not tested |
| 03b-development_validation | 0 | ❌ Not tested |
| 04a-testing | 0 | ❌ Not tested |
| 04b-operations | 0 | ❌ Not tested |

### Target Coverage (v3.17.0)

- **Critical Workflows**: 3+ test cases each (01d, 01c, 03b)
- **Standard Workflows**: 2+ test cases each (01b, 02, 03a)
- **Operational Workflows**: 1+ test case each (04a, 04b)

---

## Adversarial Training Loop (Future - v3.17.0)

### Concept

Implement iterative improvement loop where Agent B's feedback helps Agent A improve:

```python
# tests/test_adversarial_loop.py

def adversarial_training_loop(test_case, max_iterations=5):
    """
    GAN-inspired iterative improvement loop.

    Args:
        test_case: Test case to run
        max_iterations: Maximum improvement iterations

    Returns:
        Final validation results
    """
    for iteration in range(max_iterations):
        print(f"\n=== Iteration {iteration + 1}/{max_iterations} ===")

        # Agent A: Generate architecture
        agent_a_output = run_workflow_with_agent_a(test_case)

        # Agent B: Discriminate (evaluate)
        validation = validate_with_agent_b(agent_a_output, test_case)

        # Success condition
        if validation.overall_pass:
            print(f"✅ PASS after {iteration + 1} iterations")
            return validation

        # Agent B: Generate improvement feedback
        feedback = generate_improvement_feedback(
            validation.differences,
            validation.similarity_score
        )

        # Agent A: Incorporate feedback for next iteration
        update_agent_a_context(feedback)

    print(f"❌ FAIL after {max_iterations} iterations")
    return validation
```

### Feedback Generation

Agent B analyzes differences and generates actionable feedback:

```python
def generate_improvement_feedback(differences, score):
    """
    Convert validation differences to actionable feedback.

    Example:
        Input: "root.functions[3].dependencies: Missing 'F-05'"
        Output: "Function F-04 is missing dependency on F-05.
                 According to requirements FR-3, this function needs
                 product details from ViewProductDetails (F-05)."
    """
    feedback = {
        "iteration_score": score,
        "improvements_needed": [],
        "priority": "high" if score < 0.8 else "medium"
    }

    for diff in differences:
        # Parse difference path
        if "dependencies" in diff:
            feedback["improvements_needed"].append({
                "type": "missing_dependency",
                "detail": diff,
                "suggestion": "Review functional flow in requirements"
            })
        elif "functions" in diff:
            feedback["improvements_needed"].append({
                "type": "function_definition",
                "detail": diff,
                "suggestion": "Check functional requirements alignment"
            })

    return feedback
```

---

## Use Cases

### 1. Regression Testing

**Scenario**: Ensure v3.16.0 doesn't break v3.15.0 behavior

```bash
# Run full test suite
python3 tests/test_validator.py --test-case all --strict

# Expected: All tests pass (outputs match ground truth)
```

### 2. Workflow Enhancement Validation

**Scenario**: Adding new feature to 01d-functional_analysis workflow

```bash
# 1. Run tests on current version (baseline)
python3 tests/test_validator.py --test-case all > baseline_results.json

# 2. Make workflow changes
# 3. Run tests on new version
python3 tests/test_validator.py --test-case all > new_results.json

# 4. Compare
diff baseline_results.json new_results.json
```

### 3. New Framework Validation

**Scenario**: Testing new architectural framework (e.g., Ecological Systems)

```bash
# 1. Create test case for ecological system
mkdir -p tests/test_systems/ecological_food_web/{expected_outputs,actual_outputs}

# 2. Define requirements (species, interactions, energy flow)
# 3. Run workflow with new framework
# 4. Validate against expected ecological architecture
python3 tests/test_validator.py --test-case ecological_food_web
```

---

## Separate Agent Execution (Claude Code CLI)

### Concept

Use separate Claude Code agent instances to avoid "conflict of interests":

**Agent A (Builder) - Isolated Context**:
```bash
# Terminal 1: Agent A executes workflow
claude-code --agent-id builder-agent \
  --context-dir tests/test_systems/microservices_basic/agent_a_context \
  --prompt "Implement workflow 01d-functional_analysis on system in $(pwd)"
```

**Agent B (Evaluator) - Separate Context**:
```bash
# Terminal 2: Agent B validates outputs
claude-code --agent-id evaluator-agent \
  --context-dir tests/test_systems/microservices_basic/agent_b_context \
  --prompt "Validate actual_outputs against expected_outputs using test_validator.py"
```

**Key Points**:
- Agent A has NO access to `expected_outputs/` (blind generation)
- Agent B has access to BOTH `expected_outputs/` and `actual_outputs/` (discriminator)
- Separate context directories prevent information leakage
- Agent B can provide feedback without Agent A seeing ground truth

---

## Metrics and Reporting

### Key Metrics

1. **Test Pass Rate**: Percentage of test cases passing
2. **Average Similarity Score**: Mean similarity across all comparisons
3. **Coverage**: Percentage of workflows with test cases
4. **Execution Time**: Time to run test suite
5. **Iteration Count**: Average iterations needed in adversarial loop (future)

### Example Report

```
========================================
REFLOW TEST SUITE REPORT
========================================
Date: 2025-11-18
Version: v3.16.0

Test Cases: 3
Workflows Tested: 1 (01d-functional_analysis)

RESULTS:
--------
✅ microservices_basic: PASS (98.5% similarity)
❌ api_gateway_pattern: FAIL (72.3% similarity)
✅ event_driven_system: PASS (96.1% similarity)

Pass Rate: 66.7% (2/3)
Average Similarity: 89.0%

COVERAGE:
---------
01d-functional_analysis: 3 test cases ✅
01c-top_down: 0 test cases ❌
03b-development_validation: 0 test cases ❌
```

---

## Limitations and Future Work

### Current Limitations (v3.16.0)

1. **Manual LLM Invocation**: Agent A execution not automated
2. **No Feedback Loop**: Agent B doesn't provide improvement feedback to Agent A
3. **Limited Test Cases**: Only 1 test case (microservices_basic)
4. **JSON-Only Comparison**: Doesn't validate visualizations or human docs
5. **No Performance Testing**: Doesn't measure execution time or resource usage

### Future Enhancements (v3.17.0)

1. **Automated Agent Invocation**:
   - Subprocess/API calls to Claude Code CLI
   - Separate agent instances for A and B
   - Adversarial feedback loop implementation

2. **Enhanced Validation**:
   - Mermaid diagram validation (structural correctness)
   - Markdown documentation quality scoring
   - Cross-artifact consistency checks

3. **Test Coverage Expansion**:
   - 10+ test cases covering all workflows
   - Domain-specific test suites (healthcare, finance, IoT)
   - Edge case tests (empty systems, single-service systems, etc.)

4. **Performance Testing**:
   - Execution time benchmarks
   - Context consumption tracking
   - Scalability tests (1000+ function systems)

5. **CI/CD Integration**:
   - GitHub Actions workflow
   - Automated test execution on PR
   - Test results posted as PR comments

6. **Adversarial Training**:
   - Iterative improvement loop
   - Feedback generation from Agent B to Agent A
   - Learning metrics (iterations to convergence)

---

## Contributing Test Cases

### Guidelines

1. **Clear Requirements**: Write unambiguous functional requirements
2. **Realistic Complexity**: Not too simple (3 functions) or too complex (500 functions)
3. **Domain Diversity**: Cover different domains (not all microservices)
4. **Expected Outputs Validated**: Ensure ground truth is actually correct
5. **Documentation**: Explain what aspect of Reflow this test validates

### Submission Process

1. Create test case in `tests/test_systems/your_test_name/`
2. Include `requirements.md` and `expected_outputs/`
3. Test locally with `test_validator.py`
4. Submit PR with test case and documentation
5. Maintainers review expected outputs for correctness

---

## Conclusion

The Reflow Testing Framework provides automated validation of Reflow workflows using a GAN-inspired architecture. By separating generation (Agent A) and discrimination (Agent B), we avoid the "conflict of interests" problem and enable objective testing.

**Current Status (v3.16.0)**: Infrastructure implemented, 1 test case available

**Next Steps (v3.17.0)**: Automate agent invocation, implement adversarial feedback loop, expand test coverage

**Long-Term Vision**: Comprehensive test suite with 50+ test cases, full CI/CD integration, adversarial training loop that continuously improves Reflow's workflow quality.

---

**Version History**:
- v3.16.0 (2025-11-18): Initial testing framework implementation
