# Reflow - Systems Engineering Workflow

**Version 3.12.0** | LLM-driven systems engineering with self-sharpening architecture

## What is Reflow?

Reflow guides LLM agents through designing, architecting, and building complex systems. It provides structured workflows, automated validation, and comprehensive tooling for creating production-ready architectures.

**Key capabilities:**
- Framework-agnostic: Software (UAF), biology, social networks, ecosystems, workflows, custom frameworks
- Automatic approach detection: Bottom-up (existing components) or top-down (greenfield)
- Production-ready from day one: Security, deployment, monitoring, testing built-in
- Self-sharpening: Analyzes and optimizes its own implementation after each update

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

## Self-Sharpening Architecture (NEW in v3.12.0)

Reflow analyzes and improves itself after each update:

1. **Functional architecture analysis** - Detects context bottlenecks, gaps, inefficiencies
2. **Implementation refinement** - Fixes workflows, tools, schemas based on analysis
3. **Continuous improvement** - Every Reflow update triggers automatic optimization

**Tools:**
- `analyze_functional_architecture.py` - Analyze functional flows and context consumption
- `98-reflow_feature_update.json` - Feature update with automatic meta-analysis
- `99-meta_analysis.json` - Comprehensive meta-analysis workflow

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

- [TOOL_USAGE_SUMMARY.md](docs/TOOL_USAGE_SUMMARY.md) - All 32+ tools
- [META_ANALYSIS_GUIDE.md](docs/META_ANALYSIS_GUIDE.md) - Self-sharpening workflow guide
- [NETWORKX_ANALYSIS_GUIDE.md](docs/NETWORKX_ANALYSIS_GUIDE.md) - Framework-specific analysis
- [DECISION_FLOW_FRAMEWORK.md](docs/DECISION_FLOW_FRAMEWORK.md) - Decision flow documentation
- [BOTTOM_UP_INTEGRATION_DESIGN.md](docs/BOTTOM_UP_INTEGRATION_DESIGN.md) - Bottom-up integration
- [GIT_AUTOMATION_GUIDE.md](docs/GIT_AUTOMATION_GUIDE.md) - Automatic git commits

## Recent Updates

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

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Version 3.12.0** - LLM-driven systems engineering with self-sharpening architecture

[Documentation](docs/) • [Meta-Analysis Guide](docs/META_ANALYSIS_GUIDE.md) • [Issues](https://github.com/sligara7/reflow/issues)
