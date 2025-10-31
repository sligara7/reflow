# Workflow Step Test: IT Requirements - Systems Biology

## Workflow Steps

**SE-02-A05**: Security Architecture
**SE-02-A06**: Deployment Architecture
**SE-02-A07**: UX/API Design
**SE-02-A08**: Operational Environment

## Framework

**Systems Biology**

## Purpose

Validate that IT requirement steps **are SKIPPED** for Systems Biology framework.

## Conditional Logic

**Condition**: `framework_id == 'uaf' AND has_human_users`

**Action**: If false (biology, not UAF), skip SE-02-A05 through SE-02-A08

## Scenario

**System**: Protein interaction network (biological system)

## Expected Behavior

**Steps SE-02-A05 through A08 should**:
1. Check framework is UAF → FALSE (it's biology)
2. Skip all 4 IT requirement steps
3. **NOT create** any IT architecture files:
   - No `security_architecture.json`
   - No `deployment_architecture.json`
   - No `ux_api_design.json`
   - No `operational_environment.json`
4. Continue to next applicable workflow step

## Why IT Requirements Don't Apply

Protein networks don't need:
- **API Gateways**: Proteins don't have REST APIs
- **Docker**: Can't containerize proteins
- **MFA**: Proteins don't authenticate users
- **OpenAPI Docs**: No API to document
- **CI/CD Pipelines**: Don't deploy proteins to Kubernetes

These concepts are **nonsensical** for biological systems!

## Pass Criteria

- No IT architecture files exist
- All 4 steps skipped gracefully (no errors)
- Workflow continues to biology-relevant steps

## Related Tests

- `it_requirements_uaf` - UAF web app → all IT steps execute
