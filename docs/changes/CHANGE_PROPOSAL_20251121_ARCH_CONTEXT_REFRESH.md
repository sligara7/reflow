# Change Proposal: Architectural Context Refresh During Development

**Version**: v3.19.1
**Date**: 2025-11-21
**Status**: IMPLEMENTING

## Problem Statement

During long development phases (D-01 through D-07), the LLM develops services one at a time over potentially days or weeks. This leads to "tunnel vision" where the LLM:

- Forgets how the current service fits into the system of systems
- Loses track of interface contracts with other services
- Makes decisions that optimize locally but may conflict with the broader architecture
- Doesn't consider downstream consumers or upstream dependencies

**Root Cause**: No mechanism to periodically remind the LLM of the architectural context during development.

**Impact**:
- Services developed in isolation may not integrate well
- Interface mismatches discovered late during integration testing
- Architectural drift from designed system
- Decisions made without considering system-wide implications

## Proposed Solution

### Architectural Context Refresh Pattern

Add a recurring **Architectural Context Refresh** action at the start of each major development step (D-01, D-02, D-04, etc.) for each service:

```
D-XX-A00_ARCH_CONTEXT: Architectural Context Refresh
├── Read system_of_systems_graph.json
│   └── Extract: Where does this service fit? Who calls it? Who does it call?
├── Read service_architecture.json for current service
│   └── Extract: What are the key responsibilities? Data models? Interfaces?
├── Read interface_registry.json
│   └── Extract: What contracts must this service fulfill?
└── Generate brief context summary (in LLM's working context)
```

### Action Definition

```json
{
  "action_id": "D-XX-A00_ARCH_CONTEXT",
  "name": "Architectural Context Refresh",
  "description": "Re-ground in system architecture before developing this service",
  "when": "START of each development step (D-01, D-02, D-04, etc.) for EACH service",
  "purpose": "Maintain architectural awareness during long development phases",
  "mandatory": true,
  "time_budget": "2-3 minutes",
  "actions": [
    {
      "step": 1,
      "action": "Read system_of_systems_graph.json",
      "extract": [
        "Services that CALL this service (upstream/consumers)",
        "Services that this service CALLS (downstream/dependencies)",
        "Critical data flows involving this service"
      ]
    },
    {
      "step": 2,
      "action": "Read current service's service_architecture.json",
      "extract": [
        "Service purpose and responsibilities",
        "Key allocated functions",
        "Data models and their relationships",
        "External and internal interfaces"
      ]
    },
    {
      "step": 3,
      "action": "Read interface_registry.json",
      "extract": [
        "Interfaces this service PROVIDES (must implement)",
        "Interfaces this service CONSUMES (must call correctly)",
        "Contract versions and compatibility requirements"
      ]
    },
    {
      "step": 4,
      "action": "Generate context summary",
      "format": "Brief summary in LLM working context (not written to file)",
      "include": [
        "This service in one sentence",
        "Key upstream consumers (who depends on me)",
        "Key downstream dependencies (who do I depend on)",
        "Critical interfaces to implement/consume",
        "Any deployment constraints from deployment_environment_spec.json"
      ]
    }
  ],
  "output": "Mental model refresh - no file output, just context awareness",
  "llm_instruction": "Before implementing ANY code in this step, read and internalize the architectural context. Keep this context in mind for ALL implementation decisions."
}
```

### Integration Points

| Step | When | What to Refresh |
|------|------|-----------------|
| D-01 (Init) | Before selecting languages/frameworks | Overall system architecture, deployment environment |
| D-02 (Domain) | Before implementing domain models | Service responsibilities, data models, internal interfaces |
| D-04 (Integration) | Before implementing APIs | External interfaces, contracts, consumers/dependencies |
| D-05 (Observability) | Before adding observability | System-wide observability strategy, correlation IDs |
| D-06 (Pre-deployment) | Before validation | Full architecture alignment check |

## Benefits

1. **Prevents architectural drift** - Regular reminders keep LLM aligned
2. **Informs local decisions** - Decisions made with system-wide context
3. **Catches mismatches early** - Interface issues spotted before implementation
4. **Reduces integration failures** - Services developed with consumers in mind
5. **Lightweight overhead** - 2-3 minutes per step is minimal compared to rework

## Files Changed

| File | Change |
|------|--------|
| `workflows/03a-development_implementation.json` | Add D-XX-A00_ARCH_CONTEXT to D-01, D-02, D-04 |
| `workflows/03b-development_validation.json` | Add to D-05, D-06, D-07 |
| `CLAUDE.md` | Document the pattern |

## Implementation Status

- [x] Change proposal created
- [ ] 03a-development_implementation.json updated
- [ ] 03b-development_validation.json updated
- [ ] CLAUDE.md updated
- [ ] Committed and pushed
