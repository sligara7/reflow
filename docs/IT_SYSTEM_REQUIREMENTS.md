# IT System Requirements (UAF with Human Users)

**Reflow Version**: 3.7.0
**Last Updated**: 2025-10-27
**Applicability**: UAF framework systems with human users or external API access

---

## Overview

This document provides comprehensive guidance for IT systems (UAF framework) that serve human users or expose external APIs. These requirements are **architectural decisions** that must be addressed during the **systems engineering phase** (SE-02), not retrofitted during testing or operations.

**Why This Matters**: Retrofitting security, deployment, and UX after launch is **10-100x more expensive** than designing correctly upfront.

**When to Apply**: Steps SE-02-A05 through SE-02-A08 during architecture design (workflow `01b-bottom_up_integration.json` or `01c-top_down_design.json`)

---

## ⚠️ Design Upfront, Not Retrofit

**IMPORTANT**: IT systems with human users/external APIs **MUST** address these areas upfront (not afterthoughts):

1. **Security** - Authentication, authorization, encryption, audit logging
2. **Deployment Ease** - One-command deployment, automated rollback
3. **User Experience** - Intuitive APIs, clear errors, documentation
4. **Operational Environment** - Design for failures, attacks, scale

**Rationale**:
- Security vulnerabilities are exponentially harder to fix after launch
- Poor deployment architecture causes costly program delays
- Bad UX/API design requires complete rewrites, not patches
- Operational issues discovered in production cause budget overages

**Cost Impact**: Proper upfront design prevents 80-90% of deployment blockers and saves 10-100x in rework costs.

---

## Security Architecture (SE-02-A05)

### Applicability

✅ **Apply if**:
- UAF with human users (web/mobile apps)
- UAF with external API access
- Sensitive data (PII, financial, health)

❌ **Skip if**:
- Internal machine-to-machine only
- No sensitive data
- Purely batch/offline processing

### Template

Use: `templates/security_architecture_template.json`

### Required Sections

#### 1. Authentication
- **Methods**: JWT, OAuth2, SAML, OpenID Connect
- **MFA**: REQUIRED for admin users, RECOMMENDED for all users
- **Token Management**: Secure storage, rotation, expiration
- **Session Management**: Timeout policies, secure cookies

#### 2. Authorization
- **Model**: RBAC (Role-Based Access Control) or ABAC (Attribute-Based)
- **Roles**: Define roles (admin, user, read-only, etc.)
- **Permissions**: Granular permissions per resource
- **Enforcement**: Centralized policy enforcement point

#### 3. API Gateway (MANDATORY for human-facing systems)
- **Single Entry Point**: All external traffic through gateway
- **Authentication**: JWT validation, OAuth2 flows
- **Rate Limiting**: Per-user, per-endpoint limits
- **SSL/TLS**: TLS 1.2+ REQUIRED, certificate management
- **Request Filtering**: Input validation, payload size limits

**⚠️ CRITICAL**: API gateway MUST be **fully implemented**, not orphaned scaffolding. SE-06 orphaned service detection will flag missing implementations.

#### 4. Rate Limiting
- **Per-User Limits**: e.g., 100 requests/min per authenticated user
- **Login Attempt Limits**: e.g., 5 failed attempts per 15 minutes
- **IP-Based Limits**: Fallback for unauthenticated endpoints
- **Graduated Response**: Warning → throttling → temporary ban

#### 5. Input Validation
- **XSS Prevention**: Escape all user inputs
- **SQL Injection Prevention**: Parameterized queries, ORM usage
- **CSRF Protection**: Tokens for state-changing operations
- **File Upload Validation**: Type checking, size limits, scanning

#### 6. Encryption
- **In-Transit**: TLS 1.2+ for all external connections
- **At-Rest**: AES-256 for sensitive data (PII, credentials, financial)
- **Key Management**: AWS KMS, HashiCorp Vault, or equivalent
- **Database**: Encrypted columns for sensitive fields

#### 7. Audit Logging
- **Events to Log**:
  - Authentication attempts (success/failure)
  - Authorization decisions (access granted/denied)
  - Data access (read/write to sensitive resources)
  - Administrative actions (user creation, permission changes)
  - System changes (configuration updates, deployments)
- **Log Format**: Structured JSON with timestamps, user IDs, IP addresses
- **Retention**: Compliance-driven (GDPR: 30 days, HIPAA: 6 years, PCI-DSS: 1 year)
- **Protection**: Immutable logs, separate storage from application

### Validation Gate

**Step**: SE-03-A05 (BLOCKING)

**Checks**:
- `security_architecture.json` exists
- API gateway defined (for human-facing systems)
- Authentication method specified
- Encryption at-rest for sensitive data
- Audit logging configured

**Failures Block Progress**: YES - Cannot proceed to SE-04 without passing

### Common Issues and Fixes

| Issue | Severity | Impact | Fix |
|-------|----------|--------|-----|
| Missing/orphaned API gateway | CRITICAL | System non-functional | Implement gateway fully |
| Weak auth (no MFA) | HIGH RISK | Compromised accounts | Add MFA for admins minimum |
| No encryption at rest | HIGH RISK | Data breach risk | Encrypt sensitive data columns |
| Missing rate limiting | MEDIUM | DDoS vulnerability | Add per-user/IP limits |
| Poor audit logging | MEDIUM | Compliance failure | Log auth + data access events |

---

## Deployment Architecture (SE-02-A06)

### Philosophy: SIMPLICITY FIRST

**Goal**: Enable any developer to deploy the system in <10 minutes with one command.

**Anti-Pattern**: Overcomplicated orchestration (Kubernetes for 3 services) slows iteration velocity.

### Template

Use: `templates/deployment_architecture_template.json`

### Deployment Principles

1. **One-Command Deploy**: `docker-compose up -d` (or equivalent)
2. **Fast Onboarding**: <10 min setup for new developer
3. **Fast Rollback**: <5 min automated rollback on failure
4. **Clear Documentation**: Step-by-step README, no tribal knowledge

### Required Components

#### 1. Containerization
- **Tool**: Docker (default) or Podman
- **Dockerfiles**: Multi-stage builds (build → runtime)
- **Image Scanning**: Trivy, Clair, or AWS ECR scanning
- **Registry**: DockerHub, AWS ECR, GitHub Container Registry

#### 2. Orchestration
- **Default**: Docker Compose (for <10 services, <1000 req/sec)
- **Scale Up**: Kubernetes (if HA, auto-scaling, multi-region needed)
- **Don't Overcomplicate**: Use simplest tool that meets requirements

#### 3. CI/CD Pipeline
- **Stages**: Build → Test → Deploy
- **Triggers**: Git push to main/develop branch
- **Rollback**: Automatic on test failure or health check failure
- **Versioning**: Semantic versioning (v1.2.3)

#### 4. Health Checks
- **Endpoints**: `/health` (readiness), `/ready` (liveness)
- **Checks**: Database connectivity, external API reachability, resource usage
- **Response**: 200 OK if healthy, 503 Service Unavailable if degraded

#### 5. Monitoring
- **Metrics**: Prometheus (request rate, latency, error rate)
- **Logging**: Centralized (ELK, Loki, CloudWatch)
- **Alerting**: PagerDuty, Slack, email for critical issues
- **Dashboards**: Grafana for visualization

#### 6. Backup & Disaster Recovery
- **RTO** (Recovery Time Objective): How long to restore? (1 hour, 4 hours, 24 hours)
- **RPO** (Recovery Point Objective): How much data loss acceptable? (5 min, 1 hour, 24 hours)
- **Backup Frequency**: Hourly, daily, weekly based on RPO
- **Restore Testing**: Monthly restore drills

### Validation Gate

**Step**: SE-03-A06 (BLOCKING)

**Checks**:
- `deployment_architecture.json` exists
- Containerization strategy defined (Docker/Podman)
- CI/CD pipeline outlined
- Health check endpoints specified
- RTO/RPO targets documented

### Common Issues and Fixes

| Issue | Severity | Impact | Fix |
|-------|----------|--------|-----|
| Overcomplicated orchestration | MEDIUM | Slows iteration | Use Docker Compose for simple systems |
| No health checks | HIGH | Can't detect failures | Add `/health` and `/ready` endpoints |
| Manual deployment | HIGH | Error-prone, slow | Automate with CI/CD pipeline |
| Missing rollback plan | MEDIUM | Slow recovery | Document rollback steps, automate |

---

## UX & API Design (SE-02-A07)

### Design Targets

- **Time to first success**: <5 minutes for new user
- **API time to first call**: <5 minutes for new developer
- **Task success rate**: >95% for common tasks
- **Error recovery rate**: >90% for errors with clear messages

### Template

Use: `templates/ux_api_design_template.json`

### Required Elements

#### 1. RESTful API Design
- **Naming**: Consistent, intuitive resource names (`/api/v1/users`, not `/getUserData`)
- **HTTP Methods**: GET (read), POST (create), PUT (update), DELETE (delete)
- **Status Codes**: 200 (success), 201 (created), 400 (bad request), 401 (unauthorized), 404 (not found), 500 (server error)
- **Pagination**: Cursor-based or offset/limit for large collections

#### 2. User-Friendly Errors
**Bad**: `500 Internal Server Error`
**Good**: `400 Bad Request: Email is required. Please provide a valid email address.`

**Components**:
- **Error Code**: Machine-readable (e.g., `EMAIL_REQUIRED`)
- **Message**: Human-readable explanation
- **Field**: Which field caused the error
- **Help Link**: Documentation URL for resolution

#### 3. API Documentation (MANDATORY)
- **OpenAPI Spec**: Swagger/OpenAPI 3.0 specification
- **Swagger UI**: Interactive API explorer
- **Code Examples**: cURL, Python, JavaScript examples for each endpoint
- **Getting Started Guide**: 5-minute quickstart

#### 4. Versioning
- **Strategy**: URL path versioning (`/api/v1/users`, `/api/v2/users`)
- **Deprecation Policy**: 6-month notice before removing old versions
- **Changelog**: Document breaking changes

#### 5. Performance
- **Latency Targets**: p50 <100ms, p95 <500ms, p99 <1000ms
- **Caching**: Redis/Memcached for frequently accessed data
- **Compression**: Gzip responses for large payloads

### Validation Gate

**Step**: SE-03-A07 (BLOCKING)

**Checks**:
- `ux_api_design.json` exists
- API naming conventions defined
- Error message format specified
- OpenAPI spec commitment documented
- Performance targets set

### Common Issues and Fixes

| Issue | Severity | Impact | Fix |
|-------|----------|--------|-----|
| Inconsistent naming | MEDIUM | Developer confusion | Create naming guide, enforce in review |
| Poor error messages | HIGH | Users can't recover | Add field names, descriptions, help links |
| Missing docs | CRITICAL | Can't use API | Generate OpenAPI spec, add Swagger UI |
| Orphaned API gateway | CRITICAL | System non-functional | Implement gateway fully |

---

## Operational Environment Design (SE-02-A08)

### CRITICAL PRINCIPLE

**Operational environment is an ARCHITECTURAL DECISION made NOW**, not an operational problem solved during testing.

**Why**: Designing for operational realities (failures, attacks, scale) UPFRONT is **10-100x cheaper** than retrofitting.

### Template

Use: `templates/operational_environment_template.json` (1100+ lines)

### Design for Reality

Systems face these operational challenges:

**Failures**:
- Network failures, partitions (AWS region outages)
- Resource exhaustion (CPU, memory, disk full)
- Cascading failures (one service takes down others)
- Third-party outages (payment gateway down)

**Attacks**:
- DDoS (volumetric attacks, application-layer attacks)
- Injection (SQL injection, XSS, command injection)
- Credential stuffing (automated login attempts)
- Data exfiltration

**Scale**:
- Traffic spikes (10x normal load during events)
- Data growth (10 GB → 10 TB over 2 years)
- Geographic expansion (single region → multi-region)

**Operational Issues**:
- Configuration drift (prod config different from staging)
- Data corruption (bit rot, application bugs)
- Monitoring blind spots (no alerts for degraded state)

### 10 IT-Specific Considerations (UPFRONT Design)

#### 1. Service Decomposition
- **Domain-Driven Design**: Bounded contexts per business domain
- **Single Responsibility**: Each service does one thing well
- **Data Ownership**: Each service owns its data (no shared databases)
- **Loose Coupling**: Services communicate via APIs, not direct DB access

#### 2. Containerization
- **Docker from Day One**: Consistent dev/prod environments
- **Multi-Stage Dockerfiles**: Separate build and runtime stages
- **Image Scanning**: Trivy/Clair in CI/CD pipeline
- **Base Images**: Use official images (python:3.11-slim, not python:latest)

#### 3. Infrastructure as Code (IaC)
- **Ansible**: `deploy.yml`, `rollback.yml`, `scale.yml` playbooks
- **Terraform**: AWS resource provisioning (VPC, EC2, RDS, S3)
- **Version Control**: All IaC in Git, peer-reviewed changes
- **Idempotency**: Scripts can run multiple times safely

#### 4. CI/CD Integration
- **Pipeline Stages**:
  1. Lint (code style, security scanning)
  2. Test (unit, integration, 80% coverage required)
  3. Build (Docker image, semantic versioning)
  4. Deploy (staging → production)
- **Automated Testing**: No manual testing for regression
- **Semantic Versioning**: v1.2.3 (major.minor.patch)

#### 5. Scalability & Resilience
- **Auto-Scaling**: CPU/memory-based scaling (scale at 70% utilization)
- **Circuit Breakers**: Hystrix, Resilience4j (fail fast on downstream errors)
- **Retries**: Exponential backoff with jitter (2s, 4s, 8s delays)
- **Timeouts**: All external calls have timeouts (5s for fast APIs, 30s for slow)
- **Bulkheads**: Isolate thread pools per downstream service

#### 6. Security & Compliance
- **IAM Roles**: Least privilege (service-specific roles, not admin)
- **VPC Design**: Private subnets for services, public for load balancers only
- **Encryption**: TLS 1.2+ in-transit, AES-256 at-rest
- **Compliance**: GDPR (data residency, right to deletion), HIPAA (BAA, audit logs), PCI-DSS (tokenization)

#### 7. Monitoring & Observability
- **Metrics**: Prometheus (RED: Request rate, Error rate, Duration)
- **Logging**: Structured JSON logs with correlation IDs
- **Tracing**: Distributed tracing (Jaeger, Zipkin) for cross-service requests
- **Alerting**: Alert on SLO violations (p95 latency >500ms, error rate >1%)

#### 8. Service Discovery
- **AWS Cloud Map**: DNS-based service discovery
- **Consul**: Service mesh with health checking
- **Kubernetes DNS**: Native K8s service discovery
- **API Gateway**: Single entry point for external clients

#### 9. Cost Management
- **Right-Sizing**: Match instance size to actual usage (don't over-provision)
- **Spot Instances**: 70% cost savings for non-critical workloads
- **Auto-Scale to Zero**: Non-prod environments scale to 0 outside business hours
- **Cost Monitoring**: AWS Cost Explorer, budget alerts at 80% threshold

#### 10. Testing & Rollback Strategy
Define test types NOW (not during testing phase):

**Unit Tests**:
- **Coverage**: 80% minimum
- **Frequency**: Every commit
- **Scope**: Individual functions/classes

**Integration Tests**:
- **Scope**: Multi-service interactions with real APIs/DBs
- **Environment**: Isolated test environment (not prod)
- **Frequency**: Every deployment to staging

**Performance Tests**:
- **Load Levels**: 2x, 5x, 10x normal load
- **Targets**: p95 <500ms at 5x load
- **Tools**: JMeter, Gatling, k6

**Security Tests**:
- **OWASP Top 10**: Automated scanning (OWASP ZAP, Burp Suite)
- **Penetration Testing**: Annual third-party pentests
- **Dependency Scanning**: Snyk, Dependabot for vulnerable libraries

**Chaos Engineering**:
- **Failure Injection**: Kill instances, add network latency, exhaust resources
- **Tools**: Chaos Monkey, Gremlin, AWS Fault Injection Simulator
- **Frequency**: Weekly in staging, monthly in production

**Operational Tests**:
- **Scenarios**: Multi-AZ failover, database failover, auto-scaling, backup/restore
- **Frequency**: Quarterly drills
- **Runbooks**: Document procedures for each scenario

### Success Criteria

Define operational targets upfront:

**Availability**:
- 99.9% (8.76 hours downtime/year) - Standard SaaS
- 99.95% (4.38 hours downtime/year) - High availability
- 99.99% (52.56 minutes downtime/year) - Mission critical

**Recovery Time Objective (RTO)**:
- 1 hour - Standard
- 15 minutes - High priority
- 5 minutes - Mission critical

**Recovery Point Objective (RPO)**:
- 1 hour - Standard (1 hour of data loss acceptable)
- 15 minutes - High priority
- 5 minutes - Mission critical (near-zero data loss)

**Performance**:
- p50 <100ms - Fast user experience
- p95 <500ms - Acceptable user experience
- p99 <1000ms - Edge case tolerance

### Validation Gate

**Step**: SE-03-A08 (BLOCKING)

**Checks**:
- `operational_environment.json` exists
- Availability target defined (99.x%)
- RTO/RPO documented
- Testing strategy outlined (unit, integration, performance, security, chaos, operational)
- Failure scenarios identified (network, resource, cascading)

### Cost Impact

**NOT designing for operations upfront causes**:
- **Budget overages**: 20-50% over budget due to rework
- **Program delays**: 3-6 month delays for operational retrofitting
- **Team burnout**: Firefighting vs. building

**Proper upfront design prevents 80-90% of deployment blockers.**

---

## Orphaned Service Detection (UAF)

### Problem

**Orphaned Service**: A service defined in architecture (`service_architecture.json`) but never implemented, or implemented as empty scaffolding only.

**Impact**: System appears complete in architecture but fails at runtime.

### Example

```json
// service_architecture.json
{
  "service_id": "api_gateway",
  "service_name": "API Gateway",
  ...
}
```

```python
# services/api_gateway/main.py (ORPHANED)
# TODO: Implement API gateway
pass  # <-- Only 1 line, no real implementation
```

**Result**: System fails because API gateway doesn't actually route requests.

### Detection

**Step**: SE-06
**Tool**: `python3 tools/system_of_systems_graph_v2.py index.json --detect-gaps`

**Checks**:
1. **Architecture exists but no code**: Service in `service_architecture.json` but no directory in `services/`
2. **Scaffolding only**: Service directory exists but <50 lines of code, no functions/classes
3. **Empty __init__.py**: Python packages with only `__init__.py`, no actual modules

**Output**: `specs/machine/graphs/system_of_systems_graph.json` → `architectural_issues.unimplemented_services`

### Resolution

**Before SE-06 validation**:
- Remove orphaned services from architecture (if not needed)
- OR implement fully (minimum viable functionality)

**Blocking**: SE-06 validation FAILS if critical services (e.g., api_gateway) are orphaned.

---

## IT System Requirements Checklist

Use this checklist before proceeding from SE-03 validation gate.

### For UAF with Human Users OR External APIs

- [ ] **Security Architecture** (`security_architecture.json` created)
  - [ ] Authentication method defined (JWT/OAuth2/SAML)
  - [ ] Authorization model defined (RBAC/ABAC)
  - [ ] API gateway exists in architecture
  - [ ] API gateway will be **fully implemented** (not orphaned)
  - [ ] Rate limiting configured
  - [ ] Encryption at-rest for sensitive data
  - [ ] Audit logging configured
- [ ] **Deployment Architecture** (`deployment_architecture.json` created)
  - [ ] Containerization strategy (Docker/Podman)
  - [ ] Orchestration choice (Docker Compose/K8s)
  - [ ] CI/CD pipeline outlined
  - [ ] Health check endpoints defined (`/health`, `/ready`)
  - [ ] Monitoring/logging strategy
  - [ ] RTO/RPO targets set
- [ ] **UX/API Design** (`ux_api_design.json` created)
  - [ ] API naming conventions defined
  - [ ] Error message format specified
  - [ ] OpenAPI documentation commitment
  - [ ] Performance targets (p95 <500ms)
  - [ ] Versioning strategy
- [ ] **Operational Environment** (`operational_environment.json` created)
  - [ ] Availability target (99.x%)
  - [ ] Testing strategy defined (unit, integration, perf, security, chaos, operational)
  - [ ] Failure scenarios identified
  - [ ] Success criteria documented
- [ ] **Validation Gates Passed**
  - [ ] SE-03-A05 (Security) - BLOCKING
  - [ ] SE-03-A06 (Deployment) - BLOCKING
  - [ ] SE-03-A07 (UX/API) - BLOCKING
  - [ ] SE-03-A08 (Operations) - BLOCKING

### For UAF IT Systems (All)

- [ ] **Port Registry** (`port_registry.json` created and validated)
  - [ ] Ports categorized (App: 8000-8099, Internal: 8100-8199, Data: 8200-8299, Infrastructure: 8300-8399)
  - [ ] No duplicate primary ports (PC-01)
  - [ ] No port overlap (PC-02)
- [ ] **Health Checks** defined
  - [ ] `/health` endpoint (readiness)
  - [ ] `/ready` endpoint (liveness)
- [ ] **Deployment Documentation**
  - [ ] README with setup instructions
  - [ ] One-command deploy documented
  - [ ] Rollback procedure documented

---

## Related Documentation

- **Reflow Guide**: [CLAUDE.md](../CLAUDE.md) - LLM agent comprehensive guide
- **Tool Reference**: [TOOL_USAGE_SUMMARY.md](TOOL_USAGE_SUMMARY.md) - All 29 Reflow tools
- **Port Management**: See CLAUDE.md "Port Management (UAF/IT Only)" section
- **Templates**: `templates/security_architecture_template.json`, `templates/deployment_architecture_template.json`, `templates/ux_api_design_template.json`, `templates/operational_environment_template.json`
- **Workflows**: `workflows/01b-bottom_up_integration.json`, `workflows/01c-top_down_design.json` (Steps SE-02-A05 through SE-02-A08)

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-10-27 | Initial extraction from CLAUDE.md for v3.7.0 release |

---

**For questions or issues**: [GitHub Issues](https://github.com/sligara7/reflow/issues)
