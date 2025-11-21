# Change Proposal: Deployment Environment Specification Workflow

**Version**: v3.19.0
**Date**: 2025-11-21
**Status**: IMPLEMENTING

## Problem Statement

Currently, deployment environment information is scattered across multiple workflows and is often treated as an afterthought rather than an upfront design consideration:

| Current Location | Content | Issue |
|------------------|---------|-------|
| SE-04 (Deployment Architecture) | Reconciles logical vs deployment architecture | Comes AFTER service implementation starts |
| AV-02-A04 | Deployment diagrams | Visualization only, no specification |
| D-06_5 | Pre-deployment validation | Catches issues AFTER development |
| service_architecture.json | deployment_architecture section | Often incomplete or added late |

**Root Cause**: No dedicated workflow step asks "WHERE and HOW will this system run?" BEFORE development begins.

**Impact**:
- Developers make containerization decisions without knowing target platform
- Security requirements discovered late cause rework
- Scaling constraints not considered during initial design
- Infrastructure dependencies (databases, message queues) added reactively
- Monitoring/observability bolted on rather than designed in

## Proposed Solution

### New Workflow: 02b-deployment_environment.json

Insert a dedicated workflow between artifacts visualization (02) and development implementation (03a):

```
01d-functional_analysis
       ↓
02-artifacts_visualization
       ↓
[NEW] 02b-deployment_environment  ← "WHERE and HOW will this run?"
       ↓
03a-development_implementation
```

### Workflow Steps

#### DE-01: Deployment Environment Specification

Define the operational context BEFORE development begins:

| Action | Purpose |
|--------|---------|
| DE-01-A01 | Identify target deployment platforms (cloud, on-prem, hybrid, edge) |
| DE-01-A02 | Define containerization strategy (Docker, K8s, serverless, bare metal) |
| DE-01-A03 | Specify scaling requirements (horizontal/vertical, auto-scaling triggers) |
| DE-01-A04 | Document security constraints (network policies, secrets management, compliance) |
| DE-01-A05 | Define observability requirements (logging, metrics, tracing, alerting) |
| DE-01-A06 | List infrastructure dependencies (databases, caches, queues, external APIs) |
| DE-01-A07 | Generate deployment_environment_spec.json |
| DE-01-A08 | Validate spec completeness and consistency |

#### DE-02: Deployment Environment Validation

Ensure the spec is actionable:

| Action | Purpose |
|--------|---------|
| DE-02-A01 | Cross-reference with service_architecture.json |
| DE-02-A02 | Validate infrastructure dependencies are documented |
| DE-02-A03 | Check security requirements against compliance frameworks |
| DE-02-A04 | Update service_architecture.json with deployment_architecture section |

### New Artifacts

#### specs/deployment/deployment_environment_spec.json

```json
{
  "spec_version": "1.0.0",
  "target_platforms": {
    "primary": "kubernetes",
    "secondary": ["docker-compose"],
    "rationale": "Production on K8s, local dev on docker-compose"
  },
  "containerization": {
    "strategy": "docker",
    "base_images": {},
    "registry": "",
    "build_strategy": "multi-stage"
  },
  "scaling": {
    "strategy": "horizontal",
    "min_replicas": 1,
    "max_replicas": 10,
    "triggers": ["cpu > 80%", "queue_depth > 100"]
  },
  "security": {
    "network_policies": [],
    "secrets_management": "vault",
    "tls_required": true,
    "compliance_frameworks": []
  },
  "observability": {
    "logging": { "format": "json", "aggregator": "" },
    "metrics": { "provider": "", "scrape_interval": "15s" },
    "tracing": { "provider": "", "sample_rate": 0.1 },
    "alerting": { "provider": "", "channels": [] }
  },
  "infrastructure_dependencies": {
    "databases": [],
    "caches": [],
    "message_queues": [],
    "external_apis": [],
    "file_storage": []
  }
}
```

## Benefits

1. **Prevents deployment surprises**: Infrastructure requirements captured upfront
2. **Informs development decisions**: Developers know target platform before writing code
3. **Enables early infrastructure provisioning**: Ops can start provisioning while dev proceeds
4. **Reduces late-stage rework**: 3-5 days saved per service (typical deployment constraint rework)
5. **Improves security posture**: Security requirements designed in, not bolted on
6. **Better observability**: Logging/metrics/tracing considered from start

## Integration with Existing Workflows

### Workflow Progression Update

```
00a-basic_setup → [00b-framework_selection?] → 01a-approach_detection
       ↓
01b/01c/01d (architecture phase)
       ↓
02-artifacts_visualization
       ↓
[NEW] 02b-deployment_environment  ← INSERT HERE
       ↓
03a-development_implementation
       ↓
03b-development_validation → 04a-testing → 04b-operations
```

### Updates to Existing Workflows

1. **02-artifacts_visualization.json**: Add `next_step: "02b-deployment_environment"` (conditional on intent to develop)
2. **03a-development_implementation.json**: Add prerequisite check for deployment_environment_spec.json
3. **workflows_master_index.json**: Add new workflow entry

### Updates to Documentation

1. **CLAUDE.md**: Add workflow to progression, describe new workflow
2. **IT_SYSTEM_REQUIREMENTS.md**: Cross-reference deployment environment step

## Files Changed

| File | Change |
|------|--------|
| `workflows/02b-deployment_environment.json` | NEW - Main workflow file |
| `workflow_steps/deployment/DE-01-DeploymentEnvironmentSpecification.json` | NEW - Step definition |
| `templates/deployment_environment_spec_template.json` | NEW - Spec template |
| `workflows/workflows_master_index.json` | Add new workflow |
| `workflows/02-artifacts_visualization.json` | Update next_step |
| `CLAUDE.md` | Update workflow progression |

## Implementation Status

- [x] Change proposal created
- [ ] New workflow 02b-deployment_environment.json created
- [ ] Workflow step DE-01 created
- [ ] Template created
- [ ] Master index updated
- [ ] CLAUDE.md updated
- [ ] Committed and pushed
