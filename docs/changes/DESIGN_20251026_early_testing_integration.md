# Design Document: Early Testing Integration & Incremental Validation

**Design ID**: DD-2025-10-26-002
**Date**: 2025-10-26
**Status**: Proposed
**Related Documents**:
- Change Proposal: `CHANGE_PROPOSAL_20251026_early_testing_integration.md`
- Impact Analysis: `IMPACT_ANALYSIS_20251026_early_testing_integration.md`

---

## Purpose

This document provides **exact workflow changes** (delta highlighting) for implementing early testing integration throughout the Reflow workflow system. It shows before/after comparisons for all modified workflow files.

---

## Workflow Files to Modify

1. **workflows/01-systems_engineering.json** - Add 3 new actions
2. **workflows/03-development.json** - Add 1 new step + modify 4 existing steps
3. **workflows/04-testing_operations.json** - Add 1 new action, modify focus

---

## Part 1: Systems Engineering Workflow Changes

### File: `workflows/01-systems_engineering.json`

#### Change 1.1: Add SE-02-A08 - Define Operational Testing Objectives

**Location**: Step SE-02, after SE-02-A07 (port assignment), before SE-03

**New Action**:
```json
{
  "action_id": "SE-02-A08",
  "description": "Define operational testing objectives and testability requirements",
  "when": "During service architecture specification (SE-02)",
  "purpose": "Define how each service will be tested operationally, ensuring architecture is testable by design",
  "template": "operational_testing_objectives_template.json",
  "creates": "specs/machine/service_arch/{service}/operational_testing_objectives.json",
  "applicability": {
    "applies_to": "All frameworks",
    "note": "Testing strategy is universal - UAF services, biological systems, social networks all need testability"
  },
  "sections": {
    "testability_requirements": {
      "description": "Architectural features that enable testing",
      "includes": [
        "Health endpoints (/health, /ready) for services",
        "Observability hooks (metrics, logs, traces) for runtime inspection",
        "Configuration validation endpoints for deployment verification",
        "Test interfaces (stub dependencies, mock data sources)",
        "Deterministic behavior (avoid randomness that prevents reproducible tests)",
        "Graceful degradation patterns (predictable failure modes)"
      ],
      "examples": {
        "uaf_service": "REST /health endpoint, Prometheus /metrics, test database mode",
        "biological_model": "Observable state variables, simulation reproducibility via seed",
        "social_network": "Graph state export, query API for validation"
      }
    },
    "deployment_test_scenarios": {
      "description": "Tests to validate deployment configuration, not business logic",
      "scenarios": [
        {
          "scenario": "Startup validation",
          "test": "Service starts successfully with production-like configuration",
          "success_criteria": "Container starts, health endpoint responds 200 OK within 30s"
        },
        {
          "scenario": "Database connection",
          "test": "Service connects to database with correct permissions",
          "success_criteria": "Connection established, migrations run successfully as service user"
        },
        {
          "scenario": "Dependency handling",
          "test": "Service handles missing/failed dependencies gracefully",
          "success_criteria": "Circuit breaker trips, service returns 503 with clear error message"
        },
        {
          "scenario": "Configuration validation",
          "test": "Service validates configuration at startup",
          "success_criteria": "Invalid config detected, service fails fast with actionable error"
        },
        {
          "scenario": "Resource limits",
          "test": "Service operates within memory/CPU constraints",
          "success_criteria": "Container stays within limits (e.g., <512MB RAM) under load"
        }
      ]
    },
    "operational_acceptance_criteria": {
      "description": "Criteria for service to be considered deployment-ready",
      "criteria": [
        {
          "criterion": "Startup time",
          "target": "< 30 seconds from container start to health check passing",
          "rationale": "Fast startup enables rapid scaling and recovery"
        },
        {
          "criterion": "Health check response",
          "target": "< 100ms for /health endpoint",
          "rationale": "Orchestrators need fast health checks for rapid failure detection"
        },
        {
          "criterion": "Graceful shutdown",
          "target": "Completes in-flight requests within 30s on SIGTERM",
          "rationale": "Zero-downtime deployments require graceful draining"
        },
        {
          "criterion": "Crash recovery",
          "target": "Automatic restart and recovery without manual intervention",
          "rationale": "Production resilience requires self-healing"
        }
      ]
    },
    "smoke_test_requirements": {
      "description": "Fast tests (<30s) to validate basic functionality after deployment",
      "tests": [
        {
          "test": "CRUD operations",
          "what": "Create, read, update, delete primary entities",
          "time": "< 5 seconds",
          "purpose": "Verify core business logic works"
        },
        {
          "test": "Authentication",
          "what": "Valid token accepted, invalid token rejected",
          "time": "< 2 seconds",
          "purpose": "Verify security controls work"
        },
        {
          "test": "Database migrations",
          "what": "Schema matches expected version",
          "time": "< 1 second (query)",
          "purpose": "Verify database setup correct"
        },
        {
          "test": "Inter-service communication",
          "what": "Service can call dependencies and handle responses",
          "time": "< 5 seconds",
          "purpose": "Verify integration points work"
        }
      ]
    }
  },
  "llm_agent_instructions": [
    "For EACH service in architecture, create operational_testing_objectives.json",
    "Use template from templates/operational_testing_objectives_template.json",
    "Customize testability requirements based on service complexity and risk",
    "Define 3-5 deployment test scenarios per service",
    "Set concrete operational acceptance criteria with measurable targets",
    "Create smoke tests that run in < 30 seconds total",
    "Save to specs/machine/service_arch/{service}/operational_testing_objectives.json"
  ],
  "impact": "SE phase now produces testable architecture with clear testing objectives, not just functional specifications"
}
```

**Rationale**: Testing objectives defined during SE phase prevent "toss it over the fence" problem. Architecture becomes testable by design, not as an afterthought.

---

#### Change 1.2: Add SE-02-A09 - Service Risk Assessment

**Location**: Step SE-02, after SE-02-A08, before SE-03

**New Action**:
```json
{
  "action_id": "SE-02-A09",
  "description": "Perform risk assessment for each service to guide testing thoroughness",
  "when": "During service architecture specification (SE-02)",
  "purpose": "Identify high-risk services requiring more thorough testing (chaos tests, load tests, failover tests)",
  "template": "service_risk_assessment_template.json",
  "creates": "specs/machine/service_arch/{service}/risk_assessment.json",
  "applicability": {
    "applies_to": "All frameworks",
    "note": "Risk assessment is universal - applies to UAF services, biological models, social simulations"
  },
  "risk_categories": {
    "deployment_risk": {
      "description": "Likelihood of deployment failures",
      "factors": [
        "Complex dependencies (database, message queue, external APIs)",
        "Stateful migrations (schema changes, data transformations)",
        "Resource-intensive (high memory, CPU, or disk usage)",
        "Platform-specific (native dependencies, OS-level requirements)"
      ],
      "severity_levels": {
        "low": "Stateless service, minimal dependencies (e.g., utility APIs)",
        "medium": "Database-backed service with migrations",
        "high": "Distributed state, complex migrations, external integrations"
      }
    },
    "integration_risk": {
      "description": "Likelihood of integration failures",
      "factors": [
        "Tight coupling to other services (synchronous dependencies)",
        "Complex data flows (multi-hop, transformations)",
        "Protocol mismatches (REST vs gRPC vs messaging)",
        "External system dependencies (third-party APIs, legacy systems)"
      ],
      "severity_levels": {
        "low": "Standalone service, no external dependencies",
        "medium": "Calls 1-2 internal services asynchronously",
        "high": "Synchronous dependencies on 3+ services or external systems"
      }
    },
    "operational_risk": {
      "description": "Impact of service failure on system",
      "factors": [
        "On critical path (user-facing, revenue-generating)",
        "High traffic volume (>1000 req/sec)",
        "Data integrity critical (financial, health, personal data)",
        "No redundancy or failover"
      ],
      "severity_levels": {
        "low": "Non-critical, background job, batch processing",
        "medium": "Important feature, has degraded mode or redundancy",
        "high": "Critical path, high traffic, single point of failure"
      }
    }
  },
  "risk_matrix": {
    "description": "Overall risk score determines testing thoroughness",
    "calculation": "Average of deployment_risk, integration_risk, operational_risk (1-3 scale)",
    "risk_levels": {
      "low_risk": {
        "score_range": "1.0 - 1.5",
        "testing_strategy": "Standard testing (unit, integration, smoke tests)",
        "examples": "Logging service, metrics collector, static content API"
      },
      "medium_risk": {
        "score_range": "1.6 - 2.5",
        "testing_strategy": "Standard + load testing + contract testing",
        "examples": "Authentication service, notification service, search API"
      },
      "high_risk": {
        "score_range": "2.6 - 3.0",
        "testing_strategy": "Standard + load + chaos + failover + security pentesting",
        "examples": "Payment service, user data service, API gateway, database cluster"
      }
    }
  },
  "llm_agent_instructions": [
    "For EACH service, assess deployment_risk, integration_risk, operational_risk",
    "Assign severity level (1=low, 2=medium, 3=high) for each category",
    "Calculate overall risk score (average of three categories)",
    "Document rationale for each risk assessment",
    "High-risk services (score >= 2.6) must have chaos tests, load tests, failover tests in TO-05",
    "Save to specs/machine/service_arch/{service}/risk_assessment.json"
  ],
  "impact": "Testing strategy becomes risk-based, focusing effort on high-risk services instead of uniform testing for all"
}
```

**Rationale**: Not all services are equal risk. Risk assessment guides testing thoroughness, ensuring critical services get comprehensive testing (chaos, load, failover) while simple services get standard testing.

---

#### Change 1.3: Add SE-06-A06 - Define System Test Strategy

**Location**: Step SE-06, after SE-06-A05 (system graph generation), before SE-Post

**New Action**:
```json
{
  "action_id": "SE-06-A06",
  "description": "Define comprehensive test strategy for the entire system based on complete architecture",
  "when": "After system graph generation (SE-06), when complete architecture is known",
  "purpose": "Define testing strategy upfront so development implements tests per plan and operations executes tests",
  "template": "system_test_strategy_template.json",
  "creates": "specs/machine/system_test_strategy.json",
  "applicability": {
    "applies_to": "All frameworks",
    "note": "Testing strategy is universal across all system types"
  },
  "sections": {
    "unit_test_strategy": {
      "description": "Component-level testing strategy",
      "includes": [
        "Coverage targets (80% minimum for critical services, 60% for utilities)",
        "Test frameworks by language (pytest, Jest, JUnit)",
        "Mocking strategy (mock external dependencies, use real internal components)",
        "Test organization (one test file per source file, descriptive test names)"
      ]
    },
    "integration_test_strategy": {
      "description": "Cross-component testing strategy",
      "includes": [
        "Service pairs to test (based on system graph connections)",
        "Test environment (Docker Compose with test database/queue)",
        "Mocking approach (mock external systems, real internal services)",
        "Data setup/teardown (test fixtures, database seeds)"
      ],
      "integration_targets": {
        "description": "Which service pairs require integration tests",
        "source": "Derived from system_of_systems_graph.json edges",
        "example": "If character_service → session_service, test: 'Create character → Use in session'"
      }
    },
    "contract_test_strategy": {
      "description": "Consumer-driven contract testing",
      "approach": "Consumer defines expected contract, provider validates implementation",
      "tools": ["Pact", "Spring Cloud Contract", "verify_component_contract.py"],
      "includes": [
        "Which interfaces require contract tests (all external-facing APIs)",
        "Who owns contract definitions (consumers)",
        "Contract versioning strategy (semantic versioning)",
        "Provider validation frequency (on every commit)"
      ]
    },
    "performance_test_strategy": {
      "description": "Load, stress, and endurance testing",
      "test_types": [
        {
          "type": "Load testing",
          "purpose": "Verify system handles expected traffic",
          "scenarios": "1x, 2x, 5x expected load",
          "tools": ["JMeter", "Gatling", "k6"],
          "success_criteria": "p95 latency < 500ms at 2x load, p99 < 1000ms"
        },
        {
          "type": "Stress testing",
          "purpose": "Find breaking point",
          "scenarios": "Incrementally increase load until failure",
          "success_criteria": "System degrades gracefully, no data corruption"
        },
        {
          "type": "Soak testing",
          "purpose": "Verify stability over time (memory leaks, resource exhaustion)",
          "scenarios": "Run at expected load for 24-48 hours",
          "success_criteria": "No memory leaks, stable latency"
        }
      ],
      "target_metrics": {
        "availability": "99.9% uptime",
        "latency_p95": "< 500ms",
        "latency_p99": "< 1000ms",
        "throughput": "Based on expected user count (e.g., 1000 req/sec)"
      }
    },
    "security_test_strategy": {
      "description": "Vulnerability and penetration testing",
      "test_types": [
        {
          "type": "OWASP Top 10 testing",
          "scope": "All external-facing APIs",
          "tools": ["OWASP ZAP", "Burp Suite"],
          "includes": ["Injection", "Broken Auth", "XSS", "Insecure Deserialization"]
        },
        {
          "type": "Dependency scanning",
          "scope": "All third-party libraries",
          "tools": ["Snyk", "Dependabot", "npm audit"],
          "frequency": "On every commit (CI/CD)"
        },
        {
          "type": "Container scanning",
          "scope": "All Docker images",
          "tools": ["Trivy", "Aqua", "Clair"],
          "frequency": "On image build"
        },
        {
          "type": "Penetration testing",
          "scope": "Complete system",
          "frequency": "Before production release, quarterly thereafter",
          "performed_by": "External security firm (if budget allows) or internal red team"
        }
      ],
      "success_criteria": "No critical vulnerabilities, medium/low vulnerabilities documented with mitigation plan"
    },
    "operational_test_strategy": {
      "description": "Operational acceptance testing (focus of this change proposal)",
      "purpose": "Validate system survives real operational conditions (not ideal lab conditions)",
      "test_types": [
        {
          "type": "Deployment test",
          "scenarios": [
            "Cold start (fresh database, no state)",
            "Upgrade deployment (schema migration, existing data)",
            "Rollback (revert to previous version)"
          ],
          "success_criteria": "All services start healthy, smoke tests pass, no manual intervention"
        },
        {
          "type": "Failover test",
          "scenarios": [
            "Database failover (primary fails, standby promoted)",
            "Service instance failure (orchestrator restarts)",
            "Network partition (split brain handling)"
          ],
          "success_criteria": "Automatic recovery within RTO, no data loss within RPO"
        },
        {
          "type": "Chaos test (high-risk services only)",
          "scenarios": [
            "Random pod/container kills",
            "Network latency injection",
            "CPU/memory exhaustion",
            "Disk full"
          ],
          "tools": ["Chaos Monkey", "Litmus", "Gremlin"],
          "success_criteria": "System continues operating (degraded OK), no cascading failures"
        },
        {
          "type": "Backup and restore",
          "scenarios": [
            "Scheduled backup",
            "Point-in-time restore",
            "Disaster recovery (complete system restore)"
          ],
          "success_criteria": "Restore completes within RTO, data integrity validated"
        }
      ],
      "acceptance_criteria": {
        "description": "System ready for production when these criteria met",
        "criteria": [
          "All deployment tests pass (cold start, upgrade, rollback)",
          "Failover tests demonstrate automatic recovery",
          "Chaos tests (if high-risk services) show resilience",
          "Backup/restore validated"
        ]
      }
    }
  },
  "handoff_to_workflows": {
    "development_workflow": "Implements unit, integration, contract tests per this strategy (D-02 through D-05)",
    "testing_workflow": "Executes operational tests per this strategy (TO-01 through TO-05)",
    "note": "Testing strategy defined HERE (SE phase), implemented in Development, executed in Testing"
  },
  "llm_agent_instructions": [
    "Read system_of_systems_graph.json to understand complete architecture",
    "Read all service risk_assessment.json files to identify high-risk services",
    "Define unit test strategy (coverage targets, frameworks)",
    "Define integration test strategy (service pairs from graph edges)",
    "Define contract test strategy (all external APIs)",
    "Define performance test strategy (load scenarios based on expected usage)",
    "Define security test strategy (OWASP, dependency scanning, pentesting)",
    "Define operational test strategy (deployment, failover, chaos for high-risk, backup)",
    "Include success criteria for each test type with measurable targets",
    "Save to specs/machine/system_test_strategy.json"
  ],
  "impact": "Testing strategy defined during SE phase ensures testability is architected upfront, tests are comprehensive, and development/testing phases execute a pre-defined plan (not ad-hoc testing)"
}
```

**Rationale**: System test strategy defined during SE phase (when architecture complete) ensures:
1. Testing is comprehensive (covers all test types)
2. Development knows what tests to implement
3. Testing phase executes pre-defined plan (not inventing tests)
4. Testability is architectural decision, not operational afterthought

---

### Summary of SE Workflow Changes

**Workflow**: `workflows/01-systems_engineering.json`

**Modified Step**: SE-02 (Service Architecture Specification)
- **Added**: SE-02-A08 (Define Operational Testing Objectives) - after SE-02-A07
- **Added**: SE-02-A09 (Service Risk Assessment) - after SE-02-A08

**Modified Step**: SE-06 (System Graph Generation)
- **Added**: SE-06-A06 (Define System Test Strategy) - after SE-06-A05

**New Templates Required**:
1. `templates/operational_testing_objectives_template.json`
2. `templates/service_risk_assessment_template.json`
3. `templates/system_test_strategy_template.json`

**New Workflow Step Files**:
1. `workflow_steps/systems_engineering/SE-02-A08_operational_testing_objectives.json` (detailed action spec)
2. `workflow_steps/systems_engineering/SE-02-A09_risk_assessment.json` (detailed action spec)
3. `workflow_steps/systems_engineering/SE-06-A06_test_strategy.json` (detailed action spec)

**Backward Compatibility**: ✅ YES - All changes are additive (new actions), no existing actions modified

---

## Part 2: Development Workflow Changes

### File: `workflows/03-development.json`

#### Change 2.1: Add D-01-A06 - Optional Service Prototype (NEW OPTIONAL ACTION)

**Location**: Step D-01, after D-01-A05 (build_ready_index.json), before D-02

**New Action**:
```json
{
  "action_id": "D-01-A06",
  "description": "Create lightweight service prototype to validate architecture assumptions (OPTIONAL)",
  "when": "After environment bootstrap (D-01), before domain model implementation (D-02)",
  "user_prompt": {
    "ask": "Would you like to create a prototype to validate architecture assumptions before full implementation?",
    "options": [
      "Yes - Create prototype (recommended for complex deployments, unfamiliar tech stacks, uncertain permissions)",
      "No - Skip prototyping and proceed to full implementation"
    ],
    "default": "No",
    "when_to_recommend_yes": [
      "Complex deployment (database permissions, message queues, external integrations)",
      "Unfamiliar technology stack (first time using framework/platform)",
      "Uncertain operational environment (cloud permissions, network policies)",
      "High-risk service (score >= 2.6 from SE-02-A09)"
    ]
  },
  "if_yes": {
    "purpose": "Quickly validate architecture assumptions before investing in full implementation",
    "time_budget": "2-4 hours per service",
    "characteristics": {
      "minimal_implementation": "Stub business logic (hardcoded responses, no real algorithms)",
      "real_infrastructure": "Actual database, message queue, external APIs (not mocks)",
      "validates": [
        "Service starts successfully with production-like configuration",
        "Database connection works with correct permissions (service user, not postgres)",
        "Migrations run successfully as service user",
        "API responds (even with stub data)",
        "Inter-service communication works (routing, service discovery)",
        "Health endpoints functional",
        "Docker build succeeds",
        "Deployment configuration valid (ports, environment variables)"
      ]
    },
    "what_to_implement": [
      "Health endpoints (/health, /ready) - REAL",
      "One API endpoint per interface - STUB (return hardcoded JSON)",
      "Database connection - REAL (connect to actual database)",
      "One migration - REAL (create one table)",
      "Configuration loading - REAL (read environment variables)",
      "Logging - REAL (emit structured logs)",
      "Docker build - REAL (create working Dockerfile)"
    ],
    "what_NOT_to_implement": [
      "Business logic (stub it with hardcoded responses)",
      "Complete data models (create minimal schema, one table)",
      "Complete test suite (smoke test only)",
      "Full observability (basic logging sufficient)"
    ],
    "output": {
      "throwaway_or_skeleton": "Prototype can be thrown away OR used as skeleton for full implementation",
      "decision_criteria": {
        "throwaway_if": "Prototype reveals architectural issues requiring redesign",
        "skeleton_if": "Prototype validates architecture, expand to full implementation"
      }
    },
    "success_criteria": [
      "Prototype service starts successfully",
      "Health endpoint responds 200 OK",
      "Database connection established as service user",
      "Migration runs successfully",
      "One API endpoint responds (stub data OK)",
      "Docker build succeeds",
      "Smoke test passes"
    ],
    "benefit": "Catch architectural issues (permissions, deployment config, infrastructure) in 2-4 hours instead of discovering after full implementation"
  },
  "if_no": {
    "action": "Skip prototyping, proceed directly to D-02 (domain model implementation)"
  },
  "llm_agent_instructions": [
    "ASK user via AskUserQuestion tool if they want to prototype",
    "If YES:",
    "  - Create minimal prototype per characteristics above",
    "  - Focus on infrastructure validation, not business logic",
    "  - Time-box to 2-4 hours per service",
    "  - Run smoke test to validate prototype works",
    "  - Document findings (what worked, what didn't)",
    "  - Decide: throw away or use as skeleton",
    "If NO: Skip to D-02"
  ],
  "impact": "Optional prototyping catches architectural issues early for high-risk or complex services, preventing expensive rework"
}
```

**Rationale**: Prototyping is OPTIONAL but valuable for high-risk services. Validates architecture assumptions (database permissions, deployment config) in 2-4 hours before investing days in full implementation.

---

#### Change 2.2: Modify D-02, D-03, D-04, D-05 - Add "Prove It Works" Validation Gates

**Current State**: Each development step (D-02 through D-05) ends with "code written" but no validation that service actually runs in deployment configuration.

**New State**: Each step ends with lightweight "Prove It Works" validation (15-30 min automated checks).

**Pattern** (apply to D-02, D-03, D-04, D-05):

**At End of Each Step, Add New Final Action**: `D-0X-A99` (where X = 2, 3, 4, 5)

**Example for D-02** (apply same pattern to D-03, D-04, D-05):

```json
{
  "action_id": "D-02-A99",
  "description": "Prove It Works - Validate service runs with current implementation",
  "when": "After all D-02 actions complete, before proceeding to D-03",
  "purpose": "Catch deployment issues incrementally when introduced, not all at once during operational testing",
  "time_budget": "15-30 minutes (mostly automated)",
  "blocking": "RECOMMENDED - Strongly encourage fixing issues before proceeding",
  "validation_checks": [
    {
      "check": "Docker build succeeds",
      "command": "docker build --no-cache -t {service}:test services/{service}/",
      "success_criteria": "Image builds without errors",
      "failure_action": "Fix Dockerfile, dependency issues"
    },
    {
      "check": "Service starts in container",
      "command": "docker run -d --name {service}_test {service}:test",
      "success_criteria": "Container starts and stays running (not crash loop)",
      "failure_action": "Fix startup errors, missing dependencies, configuration issues"
    },
    {
      "check": "Health endpoint responds",
      "command": "docker exec {service}_test curl -f http://localhost:8000/health",
      "wait": "10 seconds for service to initialize",
      "success_criteria": "Health endpoint returns 200 OK",
      "failure_action": "Fix health endpoint implementation, service initialization"
    },
    {
      "check": "Logs clean (no errors/warnings at startup)",
      "command": "docker logs {service}_test",
      "success_criteria": "No ERROR or WARNING logs during startup",
      "failure_action": "Fix configuration, missing environment variables"
    },
    {
      "check": "Basic smoke test passes",
      "what": "Run one simple test against running container (e.g., GET /health, POST /api/entity)",
      "success_criteria": "Smoke test passes",
      "failure_action": "Fix API implementation, routing"
    },
    {
      "check": "Cleanup",
      "command": "docker rm -f {service}_test",
      "purpose": "Clean up test container"
    }
  ],
  "llm_agent_instructions": [
    "Build Docker image from scratch (no cache)",
    "Start container with production-like environment variables",
    "Wait 10 seconds for service initialization",
    "Check health endpoint responds 200 OK",
    "Check logs for errors/warnings",
    "Run basic smoke test (one API call)",
    "Stop and remove test container",
    "If ANY check fails: Document issue, strongly recommend fixing before proceeding",
    "Update dev_progress_tracker.json with validation results"
  ],
  "enforcement": {
    "blocking": false,
    "recommendation": "STRONGLY RECOMMENDED to fix issues before proceeding",
    "rationale": "Non-blocking to maintain workflow velocity, but issues compound if ignored"
  },
  "impact": "Deployment issues caught incrementally (per development step) instead of all at once during operational testing"
}
```

**Apply this pattern to**:
- **D-02**: After D-02-A04 (unit tests) → Add D-02-A99 (Prove It Works - Domain Model)
- **D-03**: After D-03-A05 (persistence tests) → Add D-03-A99 (Prove It Works - Persistence)
- **D-04**: After D-04-A07 (integration tests) → Add D-04-A99 (Prove It Works - Integration & Security)
- **D-05**: After D-05-A06 (coverage analysis) → Add D-05-A99 (Prove It Works - Observability)

**What Changes Per Step**:
- D-02 (Domain Model): Smoke test = Create one entity via API
- D-03 (Persistence): Smoke test = CRUD operations on database
- D-04 (Integration): Smoke test = Call one endpoint, verify authentication works
- D-05 (Observability): Smoke test = Verify metrics endpoint, logs emitted, health checks work

**Rationale**: Incremental "Prove It Works" validation catches deployment issues when they're introduced (easy to fix) instead of discovering 15+ issues all at once during operational testing (hard to diagnose).

---

#### Change 2.3: Add NEW STEP D-06.5 - Pre-Deployment Integration Validation

**Location**: New step BETWEEN D-06 (As-Built Architecture) and D-Post (Feedback Loop)

**Current Flow**: D-06 → D-Post
**New Flow**: D-06 → **D-06.5** → D-Post

**New Step**:
```json
{
  "step_id": "D-06.5",
  "name": "Pre-Deployment Integration Validation",
  "description": "Comprehensive validation before handoff to operational testing - catch 80-90% of deployment blockers",
  "phase": "validation",
  "step_file": "workflow_steps/development/D-06_5-PreDeploymentValidation.json",
  "when": "After D-06 (As-Built Architecture), before D-Post (Feedback Loop)",
  "purpose": "Prevent 'toss it over the fence' problem by validating system is deployment-ready before operational testing",
  "actions": [
    {
      "action_id": "D-06.5-A01",
      "description": "Dependency Validation - Ensure code dependencies match declared dependencies",
      "tool": "validate_dependencies.py (NEW)",
      "command_pattern": "python3 {reflow_root}/tools/validate_dependencies.py --system-root {system_root} --service {service}",
      "purpose": "Catch missing dependencies in requirements.txt before Docker build failures",
      "validates": [
        "All imports in Python code exist in requirements.txt/pyproject.toml",
        "No version conflicts between dependencies",
        "Dependencies can be installed (dry-run installation succeeds)",
        "No circular dependencies"
      ],
      "method": {
        "step1": "Scan all Python files with AST parser",
        "step2": "Extract all import statements (import X, from Y import Z)",
        "step3": "Read requirements.txt/pyproject.toml",
        "step4": "Compare: imports found in code vs packages in requirements",
        "step5": "Report missing packages, version conflicts"
      },
      "output": "Validation report with missing dependencies, conflicts",
      "prevents": "Category 1 issues - Dependencies not matching code (5 issues)"
    },
    {
      "action_id": "D-06.5-A02",
      "description": "Module Structure Validation - Ensure Python package structure is correct",
      "tool": "validate_module_structure.py (NEW)",
      "command_pattern": "python3 {reflow_root}/tools/validate_module_structure.py --system-root {system_root} --service {service}",
      "purpose": "Catch module structure issues (missing __init__.py, circular imports, shadowing) before ImportError at runtime",
      "validates": [
        "All packages have __init__.py files",
        "No circular imports (module A imports B, B imports A)",
        "All modules can be imported successfully",
        "No shadowed modules (models/ directory shadowing models.py file)"
      ],
      "method": {
        "step1": "Find all directories in src/ (potential packages)",
        "step2": "Check each directory has __init__.py",
        "step3": "Build dependency graph of imports",
        "step4": "Detect cycles using graph analysis",
        "step5": "Attempt to import all modules (ImportError detection)",
        "step6": "Detect shadowing (directory name == file name in parent)"
      },
      "output": "Validation report with missing __init__.py, circular imports, shadowed modules",
      "prevents": "Category 2 issues - Module/package structure (3 issues)"
    },
    {
      "action_id": "D-06.5-A03",
      "description": "Configuration Consistency Validation - Ensure code defaults match deployment config",
      "tool": "validate_configuration_consistency.py (NEW)",
      "command_pattern": "python3 {reflow_root}/tools/validate_configuration_consistency.py --system-root {system_root}",
      "purpose": "Catch configuration drift (code vs docker-compose) before connection failures at runtime",
      "validates": [
        "DATABASE_URL in code matches docker-compose.yml database configuration",
        "Service ports in code match docker-compose.yml port mappings",
        "Service users in code match docker-compose.yml user configuration",
        "Environment variables referenced in code exist in docker-compose.yml",
        "No hardcoded localhost (should use service names in docker network)"
      ],
      "method": {
        "step1": "Parse code to extract configuration defaults (DATABASE_URL, ports, service names)",
        "step2": "Parse docker-compose.yml to extract deployment configuration",
        "step3": "Compare DATABASE_URL format (postgresql:// vs postgresql+psycopg2://)",
        "step4": "Compare ports (code default vs docker-compose mapping)",
        "step5": "Compare service users (database user in code vs docker-compose)",
        "step6": "List all environment variables referenced in code",
        "step7": "Check environment variables exist in docker-compose.yml",
        "step8": "Detect hardcoded localhost references (should use service names)"
      },
      "output": "Validation report with configuration mismatches, missing env vars",
      "prevents": "Category 5 issues - Code-configuration mismatch (2 issues)"
    },
    {
      "action_id": "D-06.5-A04",
      "description": "Database Permission Validation - Ensure service user can run migrations and CRUD operations",
      "purpose": "Catch database permission issues (service user vs postgres superuser) before init_db() failures",
      "validates": [
        "Service user (not postgres) can run migrations (CREATE TABLE, ALTER TABLE)",
        "Service user has SELECT, INSERT, UPDATE, DELETE permissions",
        "init_db() succeeds with fresh database using service user credentials",
        "Migrations are idempotent (can run twice without errors)"
      ],
      "method": {
        "step1": "Start test database container with service user credentials",
        "step2": "Run migrations using service user (not postgres superuser)",
        "step3": "Verify tables created with correct ownership (service user, not postgres)",
        "step4": "Test CRUD operations (INSERT, SELECT, UPDATE, DELETE) as service user",
        "step5": "Drop database, run migrations again to test idempotency",
        "step6": "Clean up test database"
      },
      "environment": "Requires test database (docker-compose-test.yml or equivalent)",
      "output": "Validation report with permission errors, migration failures",
      "prevents": "Category 3 issues - Database configuration drift (4 issues)"
    },
    {
      "action_id": "D-06.5-A05",
      "description": "Docker Build Validation - Ensure Docker images build successfully without cache",
      "purpose": "Catch Docker build issues (pip timeouts, missing files) before CI/CD failures",
      "validates": [
        "Docker build succeeds without cache (--no-cache)",
        "No pip timeout errors (PIP_DEFAULT_TIMEOUT set appropriately)",
        "Image size reasonable (< 2GB for typical service)",
        "Security scan passes (Trivy/Snyk - no critical vulnerabilities)"
      ],
      "method": {
        "step1": "docker build --no-cache -t {service}:test services/{service}/",
        "step2": "Check build completes without errors",
        "step3": "Check image size (docker images {service}:test)",
        "step4": "Run security scan (trivy image {service}:test OR snyk container test {service}:test)",
        "step5": "Clean up test image"
      },
      "output": "Build log, image size, security scan results",
      "prevents": "Category 4 issues - Build infrastructure (1 issue)"
    },
    {
      "action_id": "D-06.5-A06",
      "description": "System-Wide Smoke Test - Ensure all services start and communicate",
      "purpose": "Validate complete system startup before operational testing",
      "validates": [
        "All services start and become healthy (docker-compose up -d)",
        "All health endpoints respond 200 OK within 60 seconds",
        "Inter-service communication works (service A can call service B)",
        "End-to-end scenario passes (one happy path through all services)",
        "No error logs during startup"
      ],
      "method": {
        "step1": "docker-compose up -d (start all services)",
        "step2": "Wait up to 60 seconds for all health checks to pass",
        "step3": "Check docker-compose ps (all services 'healthy' or 'running')",
        "step4": "Check docker-compose logs (no ERROR level logs)",
        "step5": "Run end-to-end smoke test (e.g., create user → create resource → fetch resource)",
        "step6": "docker-compose down (clean up)"
      },
      "output": "Smoke test results, service health status, logs",
      "prevents": "System-level integration issues discovered during TO-01"
    },
    {
      "action_id": "D-06.5-A07",
      "description": "Contract Validation - Ensure implementations match Interface Contract Documents",
      "tool": "verify_component_contract.py --strict",
      "command_pattern": "python3 {reflow_root}/tools/verify_component_contract.py {system_root} --all-services --strict",
      "purpose": "Ensure actual APIs match designed contracts before operational testing",
      "validates": [
        "All endpoints from ICDs are implemented",
        "Request/response schemas match ICD specifications",
        "Error responses follow documented patterns",
        "API versioning follows strategy (from SE-02-A07 ux_api_design.json)"
      ],
      "output": "Contract validation report with missing endpoints, schema mismatches",
      "prevents": "Contract violations discovered during TO-01-A03 (contract tests)"
    }
  ],
  "gates": [
    {
      "gate_id": "G-D-06.5",
      "name": "Pre-Deployment Integration Validation Gate",
      "checks": [
        "Dependency validation passes (no missing packages, no conflicts)",
        "Module structure validation passes (no circular imports, all __init__.py present)",
        "Configuration consistency validation passes (code matches docker-compose)",
        "Database permission validation passes (service user can run migrations)",
        "Docker build validation passes (all images build without errors)",
        "System-wide smoke test passes (all services start and communicate)",
        "Contract validation passes (all ICDs implemented correctly)"
      ],
      "blocking": true,
      "enforcement": "BLOCKING - Must pass all checks before proceeding to D-Post",
      "impact": "Prevents 80-90% of operational testing blockers (15+ issues from operational testing session)",
      "failure_action": "Fix issues before proceeding. Update working_memory.json with failure details."
    }
  ],
  "tools_used": [
    "validate_dependencies.py (NEW)",
    "validate_module_structure.py (NEW)",
    "validate_configuration_consistency.py (NEW)",
    "verify_component_contract.py (EXISTING)",
    "Docker",
    "Docker Compose"
  ],
  "outputs": [
    "Dependency validation report",
    "Module structure validation report",
    "Configuration consistency report",
    "Database permission validation report",
    "Docker build validation report",
    "System-wide smoke test results",
    "Contract validation report",
    "specs/machine/pre_deployment_validation_report.json"
  ],
  "template_used": "pre_deployment_validation_report_template.json",
  "execution_time": "30-60 minutes (mostly automated)",
  "next_step": "D-Post"
}
```

**Rationale**: D-06.5 is the **critical addition** that prevents "toss it over the fence" problem. Comprehensive validation catches 80-90% of operational testing blockers BEFORE handoff to testing phase.

---

### Summary of Development Workflow Changes

**Workflow**: `workflows/03-development.json`

**Modified Step**: D-01 (Initialization & Environment Bootstrap)
- **Added**: D-01-A06 (Optional Service Prototype) - after D-01-A05

**Modified Steps**: D-02, D-03, D-04, D-05 (All implementation steps)
- **Added**: D-0X-A99 (Prove It Works validation gate) - at end of each step
- D-02-A99: Validate domain model works
- D-03-A99: Validate persistence works
- D-04-A99: Validate integration & security works
- D-05-A99: Validate observability works

**New Step**: D-06.5 (Pre-Deployment Integration Validation) - BETWEEN D-06 and D-Post
- **7 new actions**: Dependency, module structure, configuration, database, Docker, smoke test, contract validation
- **New blocking gate**: G-D-06.5 (prevents 80-90% of operational testing blockers)

**New Tools Required**:
1. `tools/validate_dependencies.py` (300-400 lines)
2. `tools/validate_module_structure.py` (250-350 lines)
3. `tools/validate_configuration_consistency.py` (400-500 lines)

**New Templates Required**:
1. `templates/pre_deployment_validation_report_template.json`

**New Workflow Step Files**:
1. `workflow_steps/development/D-01-A06_optional_prototype.json`
2. `workflow_steps/development/D-02-A99_prove_it_works.json`
3. `workflow_steps/development/D-03-A99_prove_it_works.json`
4. `workflow_steps/development/D-04-A99_prove_it_works.json`
5. `workflow_steps/development/D-05-A99_prove_it_works.json`
6. `workflow_steps/development/D-06_5-PreDeploymentValidation.json` (complete step file)

**Backward Compatibility**: ✅ YES - All changes are additive (new optional action, new validation actions, new step), no existing actions removed

---

## Part 3: Testing & Operations Workflow Changes

### File: `workflows/04-testing_operations.json`

#### Change 3.1: Add TO-01-A00 - Validate Pre-Deployment Checklist

**Location**: Step TO-01, BEFORE TO-01-A01 (run unit tests)

**New Action**:
```json
{
  "action_id": "TO-01-A00",
  "description": "Validate pre-deployment checklist - ensure D-06.5 completed successfully",
  "when": "FIRST action in TO-01, before any operational testing begins",
  "purpose": "Verify system is deployment-ready per D-06.5 validation before investing time in operational testing",
  "validation_checks": [
    {
      "check": "D-06.5 step completed",
      "verify": "Read working_memory.json, check D-06.5 in completed_steps",
      "failure_action": "BLOCK - Return to development workflow, complete D-06.5"
    },
    {
      "check": "Pre-deployment validation report exists",
      "verify": "specs/machine/pre_deployment_validation_report.json exists and is recent",
      "failure_action": "BLOCK - Run D-06.5 validation"
    },
    {
      "check": "All D-06.5 validations passed",
      "verify": "Read pre_deployment_validation_report.json, check all validations status='pass'",
      "includes": [
        "Dependency validation: PASS",
        "Module structure validation: PASS",
        "Configuration consistency validation: PASS",
        "Database permission validation: PASS",
        "Docker build validation: PASS",
        "System-wide smoke test: PASS",
        "Contract validation: PASS"
      ],
      "failure_action": "BLOCK - Fix failing validations in D-06.5 before proceeding"
    },
    {
      "check": "All services in 'deployment-ready' state",
      "verify": "services/build_ready_index.json shows all services status='ready'",
      "failure_action": "WARN - Some services not ready, confirm before proceeding"
    }
  ],
  "llm_agent_instructions": [
    "Read working_memory.json to check D-06.5 completion",
    "Read specs/machine/pre_deployment_validation_report.json",
    "Verify all 7 validations passed (status='pass')",
    "If ANY validation failed: BLOCK and return error message",
    "If all passed: Proceed to TO-01-A01",
    "Document pre-deployment validation status in step_progress_tracker.json"
  ],
  "blocking": true,
  "enforcement": "BLOCKING - Cannot proceed to operational testing if D-06.5 not complete and passing",
  "impact": "Prevents wasting time on operational testing when fundamental deployment issues exist (caught by D-06.5)"
}
```

**Rationale**: TO-01-A00 is a **quality gate** ensuring D-06.5 (pre-deployment validation) completed successfully before operational testing begins. Prevents wasting time discovering issues that should have been caught in D-06.5.

---

#### Change 3.2: Modify TO-01 Description - Shift Focus to Operational Scenarios

**Current Description**:
```json
{
  "step_id": "TO-01",
  "name": "Development Test Execution (DTE)",
  "description": "Comprehensive testing in development environment"
}
```

**New Description**:
```json
{
  "step_id": "TO-01",
  "name": "Development Test Execution (DTE)",
  "description": "Comprehensive testing in development environment - focus on operational scenarios and edge cases",
  "note": "NEW FOCUS (post D-06.5): Assumes services already proven to work (via D-06.5). Testing focuses on operational scenarios, edge cases, and failure conditions - NOT basic functionality like 'does the service start' or 'can it connect to database' (those validated in D-06.5)."
}
```

**Additional Context in Step**:
```json
{
  "step_id": "TO-01",
  "focus_shift": {
    "before_D-06.5_addition": "Discovered basic integration and deployment issues (services don't start, missing dependencies, database permissions)",
    "after_D-06.5_addition": "Focuses on operational scenarios and edge cases (failure handling, load, edge cases) because basic functionality already validated",
    "what_TO-01_now_tests": [
      "Operational scenarios (from SE-02-A08 operational_testing_objectives.json)",
      "Edge cases and error handling (invalid input, missing data, boundary conditions)",
      "Failure scenarios (dependency fails, database unavailable, timeout)",
      "Security edge cases (malformed tokens, permission boundaries)",
      "Performance under normal load (not stress testing, that's TO-05)"
    ],
    "what_TO-01_no_longer_tests": [
      "Basic service startup (validated in D-0X-A99 and D-06.5-A06)",
      "Database connection and permissions (validated in D-06.5-A04)",
      "Missing dependencies (validated in D-06.5-A01)",
      "Module structure issues (validated in D-06.5-A02)",
      "Configuration drift (validated in D-06.5-A03)"
    ]
  }
}
```

**Rationale**: TO-01 focus shifts from "can it run at all?" (now validated by D-06.5) to "does it handle operational scenarios correctly?" This is more efficient use of operational testing time.

---

### Summary of Testing & Operations Workflow Changes

**Workflow**: `workflows/04-testing_operations.json`

**Modified Step**: TO-01 (Development Test Execution)
- **Added**: TO-01-A00 (Validate Pre-Deployment Checklist) - BEFORE TO-01-A01
- **Modified**: TO-01 description to shift focus to operational scenarios (basic functionality validated by D-06.5)

**New Workflow Step Files**:
1. `workflow_steps/testing_operations/TO-01-A00_pre_deployment_checklist.json`

**Backward Compatibility**: ✅ YES - One new action added, description updated (no breaking changes)

---

## Part 4: Workflow Step Files to Create/Update

### New Workflow Step Files Required

#### Systems Engineering
1. **`workflow_steps/systems_engineering/SE-02-A08_operational_testing_objectives.json`** (500-700 lines)
   - Detailed specification for SE-02-A08 action
   - Includes all sections: testability requirements, deployment scenarios, acceptance criteria, smoke tests
   - Examples for UAF, biology, social, ecological systems

2. **`workflow_steps/systems_engineering/SE-02-A09_risk_assessment.json`** (400-600 lines)
   - Detailed specification for SE-02-A09 action
   - Risk categories, severity levels, risk matrix
   - Testing strategy by risk level

3. **`workflow_steps/systems_engineering/SE-06-A06_test_strategy.json`** (800-1000 lines)
   - Detailed specification for SE-06-A06 action
   - All 6 test strategies: unit, integration, contract, performance, security, operational
   - Success criteria, tools, target metrics

#### Development
4. **`workflow_steps/development/D-01-A06_optional_prototype.json`** (400-500 lines)
   - Detailed specification for D-01-A06 optional prototype action
   - What to implement vs not implement
   - Success criteria, time budget

5. **`workflow_steps/development/D-02-A99_prove_it_works.json`** (300-400 lines)
   - Detailed specification for D-02-A99 validation gate
   - Docker build, startup, health check, smoke test for domain model

6. **`workflow_steps/development/D-03-A99_prove_it_works.json`** (300-400 lines)
   - Same pattern as D-02-A99, focused on persistence layer

7. **`workflow_steps/development/D-04-A99_prove_it_works.json`** (300-400 lines)
   - Same pattern, focused on integration & security

8. **`workflow_steps/development/D-05-A99_prove_it_works.json`** (300-400 lines)
   - Same pattern, focused on observability

9. **`workflow_steps/development/D-06_5-PreDeploymentValidation.json`** (1200-1500 lines)
   - **MOST CRITICAL** - Complete specification for new D-06.5 step
   - All 7 validation actions detailed
   - Gate G-D-06.5 specification

#### Testing & Operations
10. **`workflow_steps/testing_operations/TO-01-A00_pre_deployment_checklist.json`** (200-300 lines)
    - Detailed specification for TO-01-A00 pre-deployment checklist validation

---

## Part 5: Templates to Create

### 1. `templates/operational_testing_objectives_template.json` (400-500 lines)

**Structure**:
```json
{
  "template_version": "1.0.0",
  "service_name": "{service}",
  "framework": "{framework_id}",
  "testability_requirements": {
    "health_endpoints": [
      {
        "endpoint": "/health",
        "purpose": "Liveness check",
        "response": "200 OK if service alive",
        "implementation_note": "Returns immediately, no external dependencies"
      },
      {
        "endpoint": "/ready",
        "purpose": "Readiness check",
        "response": "200 OK if ready to serve traffic",
        "implementation_note": "Checks database connection, dependencies healthy"
      }
    ],
    "observability_hooks": [
      {
        "type": "metrics",
        "endpoint": "/metrics",
        "format": "Prometheus format",
        "includes": ["request_count", "request_duration", "error_rate"]
      },
      {
        "type": "structured_logging",
        "format": "JSON",
        "includes": ["timestamp", "level", "message", "context"]
      }
    ],
    "configuration_validation": {
      "endpoint": "/config/validate",
      "purpose": "Validate configuration at startup or on-demand",
      "response": "200 OK if config valid, 500 with errors if invalid"
    },
    "test_interfaces": [
      {
        "interface": "Test database mode",
        "purpose": "Use in-memory database for tests",
        "activation": "Environment variable TEST_MODE=true"
      },
      {
        "interface": "Mock external dependencies",
        "purpose": "Stub external APIs for integration tests",
        "activation": "Dependency injection with mock implementations"
      }
    ]
  },
  "deployment_test_scenarios": [
    {
      "scenario_id": "DTS-01",
      "name": "Cold start validation",
      "description": "Service starts successfully with fresh database",
      "test_steps": [
        "Start service container",
        "Wait for health endpoint to respond",
        "Verify logs show successful startup",
        "Verify database migrations ran"
      ],
      "success_criteria": "Service healthy within 30 seconds",
      "failure_modes": ["Timeout", "Migration failure", "Configuration error"]
    },
    {
      "scenario_id": "DTS-02",
      "name": "Database connection validation",
      "description": "Service connects to database with correct permissions",
      "test_steps": [
        "Start database container with service user",
        "Start service container",
        "Verify service can CREATE, SELECT, UPDATE, DELETE"
      ],
      "success_criteria": "All CRUD operations succeed",
      "failure_modes": ["Permission denied", "Connection refused", "Authentication failed"]
    }
    // ... more scenarios
  ],
  "operational_acceptance_criteria": [
    {
      "criterion_id": "OAC-01",
      "name": "Startup time",
      "target": "< 30 seconds",
      "measurement": "Time from container start to health endpoint 200 OK",
      "rationale": "Fast startup enables rapid scaling and recovery"
    }
    // ... more criteria
  ],
  "smoke_test_requirements": [
    {
      "test_id": "SMK-01",
      "name": "CRUD operations",
      "what": "Create, read, update, delete primary entity",
      "time_budget": "< 5 seconds",
      "purpose": "Verify core business logic works"
    }
    // ... more smoke tests
  ]
}
```

---

### 2. `templates/service_risk_assessment_template.json` (200-300 lines)

**Structure**:
```json
{
  "template_version": "1.0.0",
  "service_name": "{service}",
  "assessment_date": "{date}",
  "framework": "{framework_id}",
  "risk_categories": {
    "deployment_risk": {
      "score": 0,
      "severity": "low|medium|high",
      "factors": [
        {
          "factor": "Complex dependencies",
          "present": false,
          "description": "Database, message queue, external APIs"
        },
        {
          "factor": "Stateful migrations",
          "present": false,
          "description": "Schema changes, data transformations"
        }
        // ... more factors
      ],
      "rationale": "Explanation of score"
    },
    "integration_risk": {
      "score": 0,
      "severity": "low|medium|high",
      "factors": [],
      "rationale": ""
    },
    "operational_risk": {
      "score": 0,
      "severity": "low|medium|high",
      "factors": [],
      "rationale": ""
    }
  },
  "overall_risk_score": 0.0,
  "overall_risk_level": "low|medium|high",
  "testing_strategy": {
    "standard_tests": ["unit", "integration", "smoke"],
    "additional_tests": [],
    "rationale": "Based on overall_risk_level"
  }
}
```

---

### 3. `templates/system_test_strategy_template.json` (800-1000 lines)

**Structure**:
```json
{
  "template_version": "1.0.0",
  "system_name": "{system}",
  "framework": "{framework_id}",
  "created_date": "{date}",
  "unit_test_strategy": {
    "coverage_targets": {
      "critical_services": "80%",
      "utilities": "60%"
    },
    "frameworks_by_language": {
      "python": "pytest",
      "javascript": "Jest",
      "java": "JUnit 5"
    },
    "mocking_strategy": "Mock external dependencies, use real internal components",
    "test_organization": "One test file per source file, descriptive test names"
  },
  "integration_test_strategy": {
    "service_pairs_to_test": [
      {
        "consumer": "service_a",
        "provider": "service_b",
        "test_scenario": "Service A calls Service B API"
      }
    ],
    "test_environment": "Docker Compose with test database/queue",
    "mocking_approach": "Mock external systems, use real internal services"
  },
  "contract_test_strategy": {
    "approach": "Consumer-driven",
    "tools": ["Pact", "verify_component_contract.py"],
    "interfaces_requiring_tests": "All external-facing APIs",
    "versioning_strategy": "Semantic versioning"
  },
  "performance_test_strategy": {
    "test_types": [
      {
        "type": "Load testing",
        "purpose": "Verify system handles expected traffic",
        "scenarios": ["1x load", "2x load", "5x load"],
        "tools": ["JMeter", "k6"],
        "success_criteria": "p95 latency < 500ms at 2x load"
      }
    ],
    "target_metrics": {
      "availability": "99.9%",
      "latency_p95": "< 500ms",
      "latency_p99": "< 1000ms"
    }
  },
  "security_test_strategy": {
    "test_types": [
      {
        "type": "OWASP Top 10",
        "scope": "All external-facing APIs",
        "tools": ["OWASP ZAP"],
        "frequency": "Before release"
      }
    ]
  },
  "operational_test_strategy": {
    "test_types": [
      {
        "type": "Deployment test",
        "scenarios": ["Cold start", "Upgrade", "Rollback"],
        "success_criteria": "All services healthy, smoke tests pass"
      },
      {
        "type": "Failover test",
        "scenarios": ["Database failover", "Service failure"],
        "success_criteria": "Automatic recovery within RTO"
      }
    ],
    "acceptance_criteria": {
      "all_deployment_tests_pass": true,
      "failover_demonstrates_recovery": true
    }
  }
}
```

---

### 4. `templates/pre_deployment_validation_report_template.json` (300-400 lines)

**Structure**:
```json
{
  "template_version": "1.0.0",
  "validation_date": "{timestamp}",
  "system_name": "{system}",
  "workflow_step": "D-06.5",
  "validations": {
    "dependency_validation": {
      "status": "pass|fail",
      "tool": "validate_dependencies.py",
      "services_validated": ["{service1}", "{service2}"],
      "issues_found": [],
      "details": "All dependencies in requirements.txt match code imports"
    },
    "module_structure_validation": {
      "status": "pass|fail",
      "tool": "validate_module_structure.py",
      "issues_found": [],
      "details": "All packages have __init__.py, no circular imports"
    },
    "configuration_consistency_validation": {
      "status": "pass|fail",
      "tool": "validate_configuration_consistency.py",
      "issues_found": [],
      "details": "Code defaults match docker-compose.yml"
    },
    "database_permission_validation": {
      "status": "pass|fail",
      "issues_found": [],
      "details": "Service user can run migrations and CRUD operations"
    },
    "docker_build_validation": {
      "status": "pass|fail",
      "services_built": [],
      "issues_found": [],
      "details": "All Docker images build successfully"
    },
    "system_smoke_test": {
      "status": "pass|fail",
      "services_tested": [],
      "issues_found": [],
      "details": "All services start and communicate"
    },
    "contract_validation": {
      "status": "pass|fail",
      "tool": "verify_component_contract.py",
      "issues_found": [],
      "details": "All ICDs implemented correctly"
    }
  },
  "overall_status": "pass|fail",
  "blockers": [],
  "recommendations": [],
  "next_steps": "Proceed to D-Post if all pass, fix issues if any fail"
}
```

---

## Part 6: Tool Specifications

### Tool 1: `validate_dependencies.py` (300-400 lines, 8-12 hours)

**Purpose**: Validate all code imports exist in requirements.txt/pyproject.toml

**Algorithm**:
1. **Scan Python files** (AST parsing)
   - Find all `*.py` files in `services/{service}/src/`
   - Parse with `ast.parse()` to extract imports
   - Extract: `import X`, `from Y import Z`, `from Y.Z import A`
   - Build set of all imported modules (top-level package names)

2. **Read dependency manifests**
   - Read `requirements.txt` OR `pyproject.toml` (detect which exists)
   - Parse package names and versions
   - Build set of all declared packages

3. **Compare**
   - Missing dependencies: `imported_modules - declared_packages`
   - Report missing packages with example files where imported

4. **Validate dry-run installation** (optional, time-consuming)
   - Run `pip install --dry-run -r requirements.txt`
   - Detect version conflicts, incompatible packages

5. **Detect circular dependencies** (advanced)
   - Build dependency graph from package metadata
   - Detect cycles using graph analysis

**Output**: JSON report with missing dependencies, conflicts

---

### Tool 2: `validate_module_structure.py` (250-350 lines, 6-10 hours)

**Purpose**: Validate Python package structure (\_\_init\_\_.py, circular imports, shadowing)

**Algorithm**:
1. **Find all packages**
   - Walk directory tree, find all directories in `src/`
   - Potential packages = directories containing \_\_init\_\_.py OR Python files

2. **Check \_\_init\_\_.py**
   - For each package directory, check \_\_init\_\_.py exists
   - Report missing \_\_init\_\_.py

3. **Build import dependency graph**
   - Parse all Python files with AST
   - Extract imports: `A imports B`, `B imports C`
   - Build directed graph: nodes = modules, edges = imports

4. **Detect circular imports**
   - Run cycle detection algorithm (Tarjan's SCC or DFS)
   - Report cycles: `A → B → C → A`

5. **Test all modules can be imported**
   - Use `importlib.import_module()` to try importing each module
   - Catch `ImportError`, report which modules fail

6. **Detect shadowing**
   - Check for: directory `models/` and file `models.py` in same parent
   - Report shadowed modules

**Output**: JSON report with missing \_\_init\_\_.py, circular imports, shadowed modules

---

### Tool 3: `validate_configuration_consistency.py` (400-500 lines, 10-14 hours)

**Purpose**: Ensure code defaults match docker-compose.yml deployment configuration

**Algorithm**:
1. **Parse code defaults**
   - Scan Python files for configuration patterns:
     - `DATABASE_URL = os.getenv("DATABASE_URL", "default_value")`
     - `PORT = int(os.getenv("PORT", 8000))`
   - Extract default values using regex or AST
   - Build dictionary: `{"DATABASE_URL": "postgresql://...", "PORT": 8000}`

2. **Parse docker-compose.yml**
   - Use PyYAML to parse docker-compose.yml
   - Extract environment variables, ports, service names
   - Build dictionary: `{"environment": {...}, "ports": [...]}`

3. **Compare DATABASE_URL**
   - Code: `postgresql://user@host/db`
   - Docker: `postgresql+psycopg2://user@host/db`
   - Detect mismatch (missing `+psycopg2`)

4. **Compare ports**
   - Code default: `PORT=8000`
   - Docker mapping: `"8001:8000"`
   - Check consistency (container port matches code default)

5. **Compare service users**
   - Code: `DATABASE_URL = "postgresql://character_service@..."`
   - Docker: `POSTGRES_USER: session_service`
   - Detect mismatch

6. **Check environment variables**
   - List all environment variables referenced in code
   - Check each exists in docker-compose.yml `environment:` section
   - Report missing env vars

7. **Detect hardcoded localhost**
   - Scan code for `localhost`, `127.0.0.1`
   - In Docker network, should use service names (e.g., `character_service`)

**Output**: JSON report with configuration mismatches, missing env vars, hardcoded localhost

---

## Part 7: Implementation Phases

### Phase 1: Critical (Week 1-2) - 52 hours
**Goal**: Implement D-06.5 and validation tools (prevents 80-90% of blockers)

1. Create 3 validation tools (32 hours)
   - validate_dependencies.py (8-12h)
   - validate_module_structure.py (6-10h)
   - validate_configuration_consistency.py (10-14h)

2. Create D-06.5 step (16 hours)
   - workflow_steps/development/D-06_5-PreDeploymentValidation.json (8h)
   - Update workflows/03-development.json to add D-06.5 (2h)
   - Create pre_deployment_validation_report_template.json (4h)
   - Test D-06.5 on sample system (2h)

3. Update Development workflow with "Prove It Works" gates (4 hours)
   - Add D-02-A99, D-03-A99, D-04-A99, D-05-A99 to workflows/03-development.json
   - Create workflow step files for each

**Deliverable**: D-06.5 functional, catches 15+ blocker types

---

### Phase 2: Important (Week 2-3) - 28 hours
**Goal**: Add SE enhancements (testability objectives, risk, test strategy)

1. Create SE templates (8 hours)
   - operational_testing_objectives_template.json (3h)
   - service_risk_assessment_template.json (2h)
   - system_test_strategy_template.json (3h)

2. Create SE workflow step files (12 hours)
   - SE-02-A08_operational_testing_objectives.json (4h)
   - SE-02-A09_risk_assessment.json (3h)
   - SE-06-A06_test_strategy.json (5h)

3. Update SE workflow (4 hours)
   - Read workflows/01-systems_engineering.json in chunks (2h)
   - Add SE-02-A08, SE-02-A09, SE-06-A06 (2h)

4. Test SE changes (4 hours)
   - Create operational_testing_objectives.json for sample service
   - Create risk_assessment.json for sample service
   - Create system_test_strategy.json for sample system

**Deliverable**: SE phase produces testability requirements, risk assessments, test strategy

---

### Phase 3: Enhancements (Week 3-4) - 26 hours
**Goal**: Add optional prototype, update TO workflow, documentation

1. Add D-01-A06 optional prototype (6 hours)
   - workflow_steps/development/D-01-A06_optional_prototype.json (4h)
   - Update workflows/03-development.json (2h)

2. Update TO workflow (4 hours)
   - Add TO-01-A00 pre-deployment checklist (2h)
   - Update TO-01 description to shift focus (1h)
   - Create workflow_steps/testing_operations/TO-01-A00_pre_deployment_checklist.json (1h)

3. Documentation updates (16 hours)
   - Update README.md (2h)
   - Update CLAUDE.md (2h)
   - Update TOOL_USAGE_SUMMARY.md (3h)
   - Create EARLY_TESTING_INTEGRATION_GUIDE.md (4h)
   - Update RELEASE_NOTES.md for v3.6.0 (2h)
   - Update version manifest (1h)
   - Create migration guide for existing projects (2h)

**Deliverable**: Complete feature with documentation, ready for release

---

## Part 8: Success Criteria

### Validation Tests
- [ ] D-06.5 catches dependency issues (simulate missing package in requirements.txt)
- [ ] D-06.5 catches module structure issues (simulate circular import)
- [ ] D-06.5 catches database permission issues (simulate service user without CREATE permission)
- [ ] D-06.5 catches configuration drift (simulate DATABASE_URL mismatch)
- [ ] D-06.5 prevents progression when validation fails (blocking gate works)
- [ ] "Prove It Works" gates catch deployment issues incrementally

### Operational Testing Focus Shift
- [ ] TO-01 focuses on operational scenarios (not basic startup issues)
- [ ] TO-01-A00 blocks if D-06.5 not complete
- [ ] TO-01-A00 validates pre-deployment checklist successfully

### SE Phase Enhancements
- [ ] SE-02-A08 creates operational_testing_objectives.json
- [ ] SE-02-A09 creates risk_assessment.json with correct risk scores
- [ ] SE-06-A06 creates system_test_strategy.json with comprehensive test plan

### Backward Compatibility
- [ ] Existing systems can skip new SE actions (optional enhancements)
- [ ] D-06.5 can run on existing systems immediately
- [ ] No breaking changes to workflow structure

### Documentation
- [ ] All new tools documented in TOOL_USAGE_SUMMARY.md
- [ ] Early testing integration guide created
- [ ] README.md and CLAUDE.md updated
- [ ] Release notes for v3.6.0 complete

---

## Part 9: Backward Compatibility Verification

### Breaking Changes: NONE ✅

All changes are **additive**:
- New actions added to existing steps (SE-02, SE-06, D-01, TO-01)
- New step added (D-06.5)
- New validation actions added (D-0X-A99)
- New tools added
- New templates added

No existing actions removed or modified (except descriptions).

### Migration Path for Existing Systems

**Existing systems at D-06 or earlier**:
1. Continue workflow normally
2. When reaching D-06.5, system will prompt to run validation
3. Fix any issues found
4. Proceed to D-Post

**Existing systems already in TO-01**:
1. Can optionally return to D-06.5 and run validation
2. OR proceed with current testing (issues may be discovered)

**Existing systems in production**:
1. Not affected (changes only affect development/testing workflows)

---

## Part 10: Open Questions for User Approval

Before implementation (FU-04), user should review and approve:

1. **Tool Complexity**: Three new validation tools (validate_dependencies, validate_module_structure, validate_configuration_consistency) are 300-500 lines each. Approve complexity level?

2. **Blocking vs Non-Blocking Gates**:
   - D-06.5: BLOCKING (recommended)
   - D-0X-A99 "Prove It Works": NON-BLOCKING but strongly recommended
   - Approve enforcement levels?

3. **Optional Prototype (D-01-A06)**: Should this be optional or mandatory for high-risk services? Current design: OPTIONAL with user prompt.

4. **SE Phase Additions**: SE-02-A08, SE-02-A09, SE-06-A06 add ~15-20 min to SE workflow. Approve time investment?

5. **Backward Compatibility**: Confirm no breaking changes acceptable.

---

## Conclusion

This design document provides **exact specifications** for implementing early testing integration throughout Reflow workflows. Key changes:

1. **SE Phase**: Defines testability, risk, and test strategy upfront (3 new actions)
2. **Development Phase**: Incremental validation + comprehensive pre-deployment validation (D-06.5 + D-0X-A99 gates)
3. **Testing Phase**: Focus shifts to operational scenarios (TO-01-A00 + description update)

**Impact**: 80-90% reduction in operational testing blockers by catching issues incrementally during development.

**Next Steps**: User approval → FU-04 (Implementation) → FU-05 (Validation & Release)
