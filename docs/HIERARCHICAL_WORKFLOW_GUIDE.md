# Hierarchical Workflow Guide

**Version**: 1.0.0
**Created**: 2025-12-04

## Overview

Reflow now supports a **hierarchical workflow structure** that organizes workflows into phases, with a master orchestrator managing transitions between phases. This addresses the critical problem of **architecture drift** during development and testing.

## The Problem This Solves

### Architecture Drift

During development and testing, LLMs tend to:
1. Stay in the P3 (Development) ↔ P4 (Validation) loop indefinitely
2. Make small fixes that accumulate into significant drift
3. Lose context of the original architecture design
4. End up with implementation that doesn't match the designed architecture

### Two Development Paradigms

Different projects have different needs:
- **Personal/Exploratory**: Architecture should evolve with implementation
- **Enterprise/Approved**: Implementation must conform to locked architecture

The hierarchical workflow supports both with **dual-mode operation**.

## Phase Structure

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MASTER ORCHESTRATOR                               │
│                  (workflow_master.json)                              │
└─────────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
   ┌─────────┐          ┌──────────┐          ┌──────────┐
   │   P0    │────────▶ │    P1    │────────▶ │    P2    │
   │ SETUP   │          │ ANALYSIS │          │   ARCH   │
   └─────────┘          └──────────┘          └──────────┘
                                                    │
                                                    │ creates
                                                    │ architecture
                                                    │ anchor
                                                    ▼
                                              ┌──────────┐
                         ┌───────────────────▶│    P3    │
                         │                    │ DEVELOP  │◀──┐
                         │                    └──────────┘   │
                         │                          │        │
                         │                          ▼        │ iteration
                    RESYNC               ┌──────────┐   │ budget
                    PROTOCOL             │    P4    │───┘
                         │               │ VALIDATE │
                         │               └──────────┘
                         │                     │
                         └─────────────────────┤ if budget exceeded
                                               │
                                               ▼
                                         ┌──────────┐
                                         │    P5    │
                                         │ OPERATE  │
                                         └──────────┘
```

### Phase Descriptions

| Phase | Name | Purpose | Key Outputs |
|-------|------|---------|-------------|
| P0 | Setup & Config | Initialize project, set development mode | working_memory.json |
| P1 | Functional Analysis | Define WHAT functions exist | functional_architecture.json |
| P2 | Architecture & Allocation | Define WHERE functions live | service_architecture.json, **architecture_anchor** |
| P3 | Development | Implement services | Service code, tests |
| P4 | Validation | Test and verify | Test results, drift detection |
| P5 | Operations | Deploy and operate | Production system |
| PM | Meta & Maintenance | Improve system or Reflow | Updates, fixes |

## Development Modes

### Flexible Mode (Personal/Exploratory)

```
Architecture evolves with implementation
```

- **Philosophy**: Implementation reveals requirements
- **Drift Response**: Update architecture to match reality
- **New Requirements**: Implement first, document after
- **Resync Action**: Auto-update architecture files

**Use when**:
- Personal projects
- Exploratory development
- Agile environments
- Requirements are unclear upfront

### Rigid Mode (Enterprise/Approved)

```
Implementation must conform to architecture
```

- **Philosophy**: Architecture is the source of truth
- **Drift Response**: Realign implementation to match design
- **New Requirements**: Document as change request, await approval
- **Resync Action**: Revert implementation or create CR

**Use when**:
- Enterprise projects
- Regulated environments
- Approved requirements
- Formal change management needed

## Key Mechanisms

### 1. Architecture Anchor

Created when transitioning from P2 to P3, the anchor captures:
- Checksums of architecture files
- Design intent summary
- Key decisions
- Constraints
- Service/function counts

**Purpose**: Provides a reference point to detect drift and remind the LLM of the original design.

### 2. Iteration Budgets

Limits the number of P3↔P4 loops before forcing a resync:
- Default: 3 iterations
- Configurable during P0 setup
- Cannot be bypassed

**Purpose**: Prevents infinite fix loops that cause drift.

### 3. Resync Protocol

Triggered when iteration budget is exceeded:

1. **Halt** current work
2. **Detect** drift (compare implementation to anchor)
3. **Present** comparison to user
4. **Resolve** based on mode:
   - Flexible: Update architecture
   - Rigid: Revert or create change request
5. **Reset** iteration counter
6. **Continue** development

### 4. Discovered Requirements Tracking

When new functionality is discovered during P3/P4:

**Flexible Mode**:
```json
// context/discovered_requirements.json
{
  "id": "DR-001",
  "description": "Need retry logic for auth",
  "rationale": "Network resilience",
  "architecture_updated": false
}
```

**Rigid Mode**:
```json
// context/change_requests.json
{
  "id": "CR-001",
  "description": "Need retry logic for auth",
  "status": "pending_approval",
  "blocking_services": ["UserService"]
}
```

## File Structure

```
workflows/
├── workflow_master.json              # Master orchestrator
├── phase_transitions.json            # Transition rules
├── resync_protocol.json              # Resync procedure
└── phases/
    ├── P0_setup/
    │   └── phase_definition.json
    ├── P1_functional_analysis/
    │   └── phase_definition.json
    ├── P2_architecture_allocation/
    │   └── phase_definition.json
    ├── P3_development/
    │   └── phase_definition.json
    ├── P4_validation/
    │   └── phase_definition.json
    ├── P5_operations/
    │   └── phase_definition.json
    └── PM_meta/
        └── phase_definition.json
```

## Working Memory Updates

The `working_memory.json` template now includes:

```json
{
  "phase_tracking": {
    "current_phase": "P0",
    "current_phase_name": "Setup & Configuration",
    "phase_entered_at": "timestamp",
    "phase_history": [],
    "within_resync": false
  },
  "development_mode": {
    "mode": "flexible | rigid",
    "configured_at": "timestamp",
    "rigid_settings": {...},
    "flexible_settings": {...}
  },
  "iteration_tracking": {
    "P3_P4_loops_budget": 3,
    "current_count": 0,
    "last_resync": null,
    "resync_history": []
  },
  "architecture_anchor": {
    "exists": false,
    "checksums": {...},
    "design_intent": {...},
    "llm_reminder": "..."
  },
  "discovered_items": {
    "pending_discovered_requirements": 0,
    "pending_change_requests": 0
  }
}
```

## LLM Instructions

### On Phase Entry
1. Read `phase_definition.json` for current phase
2. Read `architecture_anchor` from working_memory.json
3. Check `iteration_tracking` status
4. Re-ground in design intent

### On Phase Exit
1. Verify exit criteria met
2. Update working_memory.json
3. If P2→P3: Create architecture_anchor

### On Iteration (P3↔P4)
1. Increment iteration counter
2. Check if budget exceeded
3. If exceeded: Trigger resync_protocol

### On Discovering New Requirement
- **Flexible**: Implement it, add to discovered_requirements.json
- **Rigid**: STOP, add to change_requests.json, continue other work

## Usage Examples

### Starting a New Project

```
User: "Implement workflow in github.com/sligara7/reflow/workflows/workflow_master.json"

LLM:
1. Read workflow_master.json
2. Start at P0
3. Ask about development mode (flexible/rigid)
4. Configure iteration budget
5. Proceed through phases
```

### Resuming After Break

```
User: "Continue workflow from context/working_memory.json"

LLM:
1. Read working_memory.json
2. Check current_phase
3. Read architecture_anchor
4. Check iteration_tracking
5. Resume from current position
```

### When Resync is Triggered

```
LLM: "Resync protocol triggered - iteration budget exceeded"

1. Run drift detection
2. Present: "Implementation has drifted 25% from design"
3. Flexible: "I will update architecture to match. Confirm?"
4. Rigid: "Choose: (A) Revert implementation or (B) Create change request"
5. Execute resolution
6. Reset counter
7. Continue development
```

## Integration with Bayesian Optimization

The Bayesian Architecture Optimization module is integrated into P2:

```json
// P2_architecture_allocation/phase_definition.json
{
  "workflows": [
    ...
    {
      "id": "02c-bayesian_optimization",
      "name": "Bayesian Architecture Optimization",
      "tool": "tools/bayesian_optimization/bayesian_architecture_optimizer.py",
      "required": false,
      "description": "OPTIONAL: Use Bayesian optimization to explore service allocation trade-offs"
    }
  ]
}
```

**When to use**:
- Complex architectures (>5 services)
- Unclear trade-offs between allocation strategies
- Context consumption concerns
- High service coupling

## Benefits

1. **Prevents drift**: Architecture anchor and iteration budgets
2. **Mode flexibility**: Supports both agile and formal development
3. **Clear phases**: Know exactly where you are in the process
4. **Forced resyncs**: Cannot avoid architecture review
5. **Audit trail**: Resync history documents all synchronizations
6. **LLM context management**: Re-inject design intent at transitions

## Migration from Flat Workflows

The hierarchical structure is additive - existing flat workflows continue to work. To adopt the hierarchical approach:

1. Start with `workflow_master.json` instead of individual workflows
2. Configure development mode during P0
3. Let the master orchestrator manage phase transitions
4. Architecture anchor is created automatically at P2→P3

## Troubleshooting

### "Resync triggered too often"
Increase `iteration_tracking.P3_P4_loops_budget` (default: 3)

### "Architecture anchor is stale"
Regenerate by returning to P2 (architecture phase)

### "Drift score is always high"
Check that architecture files are being updated (flexible mode) or that implementation is conforming (rigid mode)

### "Can't exit P4 to P5"
All blocking quality gates must pass and drift score must be below threshold

## Summary

The hierarchical workflow structure:
- Organizes 17 workflows into 7 logical phases
- Prevents architecture drift via anchors and iteration budgets
- Supports dual development modes (flexible/rigid)
- Forces periodic architecture review via resync protocol
- Integrates Bayesian optimization for architecture trade-offs
- Maintains audit trail of all synchronizations
