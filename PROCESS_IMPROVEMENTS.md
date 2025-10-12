# Process Improvements Log

Purpose
- Track improvements and lessons learned while using service_development_workflow.json and architecture_workflow.json during the MVP build.

Initial observations
- Graph edges for async dependencies: The architecture analyzer needs explicit logical dependencies for non-HTTP interfaces to avoid “orphaned” components (we added character_service → llm_service).
- Internal-only services: Security gap warnings are raised when interfaces don’t require auth. Clarify “internal-only, gated by gateway/network policy” in security sections and consider updating analyzers to treat this as sufficient.
- Artifact directory validation: The validator expects service_architecture.json in some artifact directories; add minimal markers (interfaces/, deployment/, docs/) to avoid false negatives.
- Consistency between build_ready_index and service_development_workflow: Keep build order/groups in sync with development stages to avoid rework.
- LLM schemas: Requiring session_id and request_id early improved isolation and testability across services.

Proposed workflow enhancements
- Development workflow bootstrap command: Add a small script to create dev tracking files (dev_progress_tracker.json, dev_current_focus.md, dev_process_log.md) per system.
- Analyzer rule toggles: Introduce configuration to mark certain services as internal-only to suppress irrelevant auth warnings.
- Async interface registry: Extend interface_registry.json to explicitly record pub/sub dependencies so graph generation doesn’t need guessing.
- Test runner scaffolding: Provide minimal scripts to exercise integration_tests.json scenarios (HTTP + AMQP smoke tests).
- Quality gate automation: Integrate a basic pre-commit or CI task to verify SPEC_ALIGNMENT automatically (compare code endpoints with api_contracts.json).

New observations (2025-10-12)
- Development tracking bootstrap: The workflow calls for dev_progress_tracker.json/dev_current_focus.md/dev_process_log.md; added manual scaffolding. Improvement: provide a bootstrap CLI (tools/run_development_workflow.py) to create/update these consistently.
- Test stage hints: Add a minimal pytest template and guidance to each service’s dev_setup/README.md for consistency.
- JSONSchema ergonomics: For weapon damage, regexes are easy to get wrong; consider allowing either canonical dice strings (e.g., "1d8+2") or structured {die:"d8", count:1, bonus:2} to simplify validation.
- Creature schema scope: Creature sheets can be very broad. Consider optional "statblock_compat" hints to map legacy monster fields to the full-sheet format.

Next actions
- Provide a D4 fast-path rule for stateless services (no persistence): allow marking SPEC_ALIGNMENT=N/A with justification to reduce overhead.
- Add a tools/run_development_workflow.py skeleton referenced in service_development_workflow.json to bootstrap dev tracking files.
- Add a simple test runner template that reads integration_tests.json and executes smoke tests locally.
- Document internal-only policy in architecture_workflow or analyzer docs, with a convention key (e.g., security.internal_only=true).
