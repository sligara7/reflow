# Reflow Testing Framework

**Version**: 3.16.0
**Purpose**: Automated validation of Reflow workflows using GAN-inspired architecture

---

## Quick Start

### 1. List Available Test Cases

```bash
python3 tests/test_runner.py --list-tests
```

### 2. Run Test Validator

```bash
# Validate single test case
python3 tests/test_validator.py --test-case microservices_basic

# Validate all test cases
python3 tests/test_validator.py --test-case all
```

### 3. Review Results

```bash
cat tests/validation_report.json
```

---

## What's Inside

```
tests/
├── test_runner.py              # Orchestrates workflow execution (Agent A controller)
├── test_validator.py           # Validates outputs vs ground truth (Agent B - discriminator)
├── test_systems/               # Test cases
│   ├── microservices_basic/    # E-commerce test case
│   │   ├── requirements.md     # Input requirements
│   │   ├── expected_outputs/   # Ground truth
│   │   └── actual_outputs/     # Generated during test
│   ├── api_gateway_pattern/    # (Coming soon)
│   └── event_driven_system/    # (Coming soon)
└── README.md                   # This file
```

---

## GAN-Inspired Architecture

**Agent A (Generator)**: Executes Reflow workflows to build systems
**Agent B (Discriminator)**: Evaluates outputs against ground truth

This separates generation from evaluation, avoiding "conflict of interests."

---

## Full Documentation

See [docs/TESTING_GUIDE.md](../docs/TESTING_GUIDE.md) for:
- Complete usage instructions
- Creating new test cases
- Adversarial training loop (future)
- CI/CD integration
- Separate agent execution

---

## Current Limitations (v3.16.0)

1. **Manual LLM invocation** - Agent A execution not automated yet
2. **Limited test cases** - Only microservices_basic implemented
3. **No feedback loop** - Agent B doesn't provide improvement feedback to Agent A yet

These will be addressed in v3.17.0.

---

## Example: Running a Test

```bash
# 1. Prepare test environment
python3 tests/test_runner.py \
  --test-case microservices_basic \
  --workflow-path 01d

# 2. (Manual) Execute workflow using Claude Code
#    "Implement workflow 01d-functional_analysis on system in
#     tests/test_systems/microservices_basic"

# 3. Validate outputs
python3 tests/test_validator.py --test-case microservices_basic

# 4. Review results
# PASS ✅ or FAIL ❌ with similarity score and specific differences
```

---

## Contributing

To add a new test case:

1. Create directory: `tests/test_systems/your_test_name/`
2. Add `requirements.md` with functional requirements
3. Create `expected_outputs/` with ground truth artifacts
4. Test with `test_validator.py`
5. Submit PR

See [docs/TESTING_GUIDE.md](../docs/TESTING_GUIDE.md#creating-new-test-cases) for details.

---

**Questions?** See [docs/TESTING_GUIDE.md](../docs/TESTING_GUIDE.md) or open an issue.
