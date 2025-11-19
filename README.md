# Reflow - Systems Engineering Workflow

**Version 3.17.0** | LLM-driven systems engineering with proactive drift prevention

## What is Reflow?

Reflow guides LLM agents through designing, architecting, and building complex systems. It provides structured workflows, automated validation, and comprehensive tooling for creating production-ready architectures.

**Key capabilities:**
- **Service interface contracts**: Embedded hooks warn LLMs before breaking changes (v3.17.0)
- **GAN-inspired testing**: Separate Generator/Discriminator agents validate workflow outputs (v3.16.0)
- **Architecture sync loop**: Keeps architecture aligned with implementation during development (v3.15.0)
- **Framework-agnostic**: Software (UAF), biology, social networks, ecosystems, workflows, custom frameworks
- **Automatic approach detection**: Bottom-up (existing components) or top-down (greenfield)
- **Production-ready from day one**: Security, deployment, monitoring, testing built-in
- **Self-sharpening**: Analyzes and optimizes its own implementation after each update

## Quick Start

### Setup
```bash
# Clone Reflow
git clone https://github.com/sligara7/reflow
mkdir ~/projects/my_system

# Start workflow
"Implement workflow in /path/to/reflow/workflows/00a-basic_setup.json on system in ~/projects/my_system"

# Resume work later
"Continue workflow from context/working_memory.json in ~/projects/my_system"
```

### Web-Based (GitHub Codespaces / Claude Code)
```
# Codespaces (free tier available)
Create codespace → clone reflow → "Implement workflow in /workspaces/reflow/workflows/00a-basic_setup.json on system /workspaces/my_system"

# Claude Code (requires Pro/Max)
"Implement workflow in github.com/sligara7/reflow/workflows/00a-basic_setup.json on system github.com/yourname/my_system"
```

## Core Workflows

### New System (Greenfield)
```
00a-basic_setup → 01a-approach_detection → 01c-top_down_design → 02-artifacts → 03a-development → 03b-validation → 04a-testing → 04b-operations
```

### Existing Components (Bottom-Up Integration)
```
00a-basic_setup → 01a-approach_detection → 01b-bottom_up_integration → 02-artifacts → 03a-development → 03b-validation → 04a-testing → 04b-operations
```

### Functional Analysis Only
```
00a-basic_setup → 01d-functional_analysis → (stakeholder validation) → STOP or continue to 01b/01c
```

### Feature Updates
```
# For other systems
feature_update.json

# For Reflow itself (auto-triggers meta-analysis)
98-reflow_feature_update.json
```

### Reflow Meta-Analysis (Self-Sharpening)
```
# Automatic (runs after Reflow feature updates)
98-reflow_feature_update.json (includes steps RFU-03, RFU-04, RFU-05)

# Manual (comprehensive quarterly health check)
99-meta_analysis.json (steps META-01 through META-08)
```

## Testing Reflow Workflows (NEW in v3.16.0)

Automated testing infrastructure using GAN-inspired architecture:

**Agent A (Generator)**: Executes workflows blind (no access to expected outputs)
**Agent B (Discriminator)**: Validates outputs against ground truth

```bash
# List available test cases
python3 tests/test_runner.py --list-tests

# Validate workflow outputs
python3 tests/test_validator.py --test-case microservices_basic

# Validate all test cases (strict mode)
python3 tests/test_validator.py --test-case all --strict
```

**Benefits:**
- Regression testing for workflow changes
- Objective evaluation (separate generation from validation)
- No "conflict of interests" - agents have different information access
- Foundation for adversarial training loop

See [tests/README.md](tests/README.md) and [docs/TESTING_GUIDE.md](docs/TESTING_GUIDE.md) for details.

## What You Get

**Machine-readable artifacts:**
- Versioned component/service architecture files
- System of systems graph with NetworkX analysis
- Interface Contract Documents (ICDs)
- Port registry, version manifest

**Human-readable artifacts:**
- Mermaid diagrams (system, service, sequence, deployment)
- Architecture documentation and ADRs

**Implementation & operations:**
- Fully implemented services with 80%+ test coverage
- CI/CD pipelines, Docker Compose deployment
- Monitoring and alerting

**Quality assurance:**
- 10 quality gates (7 blocking)
- Automated validation and contract compliance
- Architecture synchronization enforcement (v3.15.0)

## Requirements

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Python | 3.8+ | Core runtime |
| networkx | 3.0+ | Graph operations |
| LLM Agent | Claude/GPT-4 | Workflow execution |
| Docker | optional | Deployment validation |
| Pixi | latest | Recommended for fast dependency management |

### Installation

**Recommended: Using Pixi**
```bash
curl -fsSL https://pixi.sh/install.sh | bash
cd reflow
pixi install
pixi run python tools/<tool_name>.py <args>
```

**Alternative: Using pip**
```bash
pip install networkx>=3.0
python3 tools/<tool_name>.py <args>
```

## Supported Frameworks

- **UAF 1.2** - Software/hardware systems
- **Systems Biology** - Gene networks, metabolic pathways
- **Social Network Analysis** - Organizations, communities
- **Ecological Systems** - Food webs, species interactions
- **Complex Adaptive Systems** - Markets, emergent systems
- **Decision Flow** - Workflows, state machines, decision processes
- **Custom** - LLM-generated for novel domains

## Documentation

**Core Guides:**
- [CLAUDE.md](CLAUDE.md) - Complete LLM agent guide (v3.16.0)
- [TESTING_GUIDE.md](docs/TESTING_GUIDE.md) - GAN-inspired testing framework ⭐ NEW
- [TOOL_USAGE_SUMMARY.md](docs/TOOL_USAGE_SUMMARY.md) - All 32+ tools
- [META_ANALYSIS_GUIDE.md](docs/META_ANALYSIS_GUIDE.md) - Self-sharpening workflow guide

**Framework-Specific:**
- [NETWORKX_ANALYSIS_GUIDE.md](docs/NETWORKX_ANALYSIS_GUIDE.md) - Framework-specific analysis
- [DECISION_FLOW_FRAMEWORK.md](docs/DECISION_FLOW_FRAMEWORK.md) - Decision flow documentation

**Integration & Workflows:**
- [BOTTOM_UP_INTEGRATION_DESIGN.md](docs/BOTTOM_UP_INTEGRATION_DESIGN.md) - Bottom-up integration
- [GIT_AUTOMATION_GUIDE.md](docs/GIT_AUTOMATION_GUIDE.md) - Automatic git commits
- [IT_SYSTEM_REQUIREMENTS.md](docs/IT_SYSTEM_REQUIREMENTS.md) - IT system requirements

**Testing:**
- [tests/README.md](tests/README.md) - Quick start for testing framework ⭐ NEW

## Recent Updates

**v3.16.0 (2025-11-18)** - GAN-Inspired Testing Framework ⭐ NEW
- Automated workflow validation using Generator/Discriminator architecture
- Test runner (`test_runner.py`) orchestrates workflow execution
- Test validator (`test_validator.py`) compares outputs against ground truth
- Similarity scoring (0.0-1.0) with strict/relaxed modes
- First test case: `microservices_basic` (e-commerce, 19 functions, 7 services)
- Foundation for adversarial training loop (future)
- **Impact**: Regression testing, objective validation, continuous quality improvement

**v3.15.0 (2025-11-18)** - Architecture Synchronization Loop
- Architecture versioning tool (`version_architecture.py`) with semantic versioning
- D-06.5 workflow step: Iterative architecture synchronization during development
- Enforces MANDATORY sync when similarity < 0.7
- Root cause classification (requirements_creep, performance_optimization, etc.)
- Operational testing architecture update loop (TO-05-A05.5, TO-05-A05.6)
- **Impact**: Prevents stale architecture docs, complete audit trail

**v3.12.0 (2025-11-04)** - Self-Sharpening Architecture
- Meta-analysis workflow (99-meta_analysis.json) with META-05B implementation refinement
- Automatic meta-analysis (98-reflow_feature_update.json) for Reflow updates
- Functional architecture analysis tool with context consumption tracking
- Continuous self-improvement loop

**v3.11.0 (2025-11-05)** - Pixi Package Manager Integration
- Fast, reproducible Python environments with pixi.toml
- 2-5x faster than pip with lockfile for reproducibility

**v3.10.0 (2025-11-04)** - Language-Native Interface Contracts
- Python ABC, TypeScript, Rust, C++, Java, Go interface generation
- Compile-time/runtime validation, IDE autocomplete

**v3.7.0 (2025-10-27)** - 60-95% LLM Context Reduction
- Modular workflows: Load only what you need
- Automatic approach detection

See [CHANGELOG.md](CHANGELOG.md) for complete version history.

## Contributing

Contributions welcome. For major changes, open an issue first.

**Adding Test Cases:**
1. Create directory in `tests/test_systems/your_test_name/`
2. Add `requirements.md` with functional requirements
3. Create `expected_outputs/` with ground truth artifacts
4. Test with `test_validator.py`
5. Submit PR

See [docs/TESTING_GUIDE.md](docs/TESTING_GUIDE.md#contributing-test-cases) for details.

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Version 3.16.0** - LLM-driven systems engineering with GAN-inspired automated testing

[Documentation](docs/) • [Testing Guide](docs/TESTING_GUIDE.md) • [Meta-Analysis Guide](docs/META_ANALYSIS_GUIDE.md) • [Issues](https://github.com/sligara7/reflow/issues)
