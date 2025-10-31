# Workflow Step Test: IT Requirements - UAF Web App

## Workflow Steps

**SE-02-A05**: Security Architecture
**SE-02-A06**: Deployment Architecture
**SE-02-A07**: UX/API Design
**SE-02-A08**: Operational Environment

## Framework

**UAF 1.2** with human users

## Purpose

Validate that IT requirement steps **execute** for UAF systems with human users.

## Conditional Logic

**Condition**: `framework_id == 'uaf' AND (user_facing == true OR external_api == true)`

**Action**: If true, execute SE-02-A05 through SE-02-A08

## Scenario

**System**: Web application with human users (user_facing: true)

## Expected Behavior

**Steps SE-02-A05 through A08 should**:
1. Check framework is UAF → TRUE
2. Check system has human users (user_facing OR external_api) → TRUE
3. Execute all 4 IT requirement steps:
   - SE-02-A05: Create `security_architecture.json` (auth, API gateway, MFA)
   - SE-02-A06: Create `deployment_architecture.json` (Docker, CI/CD, health checks)
   - SE-02-A07: Create `ux_api_design.json` (RESTful, OpenAPI, errors)
   - SE-02-A08: Create `operational_environment.json` (10 IT considerations)

## Why IT Requirements Apply

UAF systems with human users need:
- **Security**: Authentication, authorization, API gateway
- **Deployment**: One-command deploy, automated rollback
- **UX**: Intuitive APIs, clear error messages
- **Operations**: Design for failures, attacks, scale

## Pass Criteria

- All 4 files created:
  - `specs/machine/security_architecture.json`
  - `specs/machine/deployment_architecture.json`
  - `specs/machine/ux_api_design.json`
  - `specs/machine/operational_environment.json`
- Security architecture includes API gateway
- Deployment includes Docker/containerization
- UX includes OpenAPI documentation

## Related Tests

- `it_requirements_biology` - Different framework → all IT steps skipped
