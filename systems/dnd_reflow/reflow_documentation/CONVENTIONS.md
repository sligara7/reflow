# Reflow conventions: iteration, context, and artifact layout

This document defines the conventions used across all reflow workflows.

Non-interactive CLI policy
- All workflow instructions must follow shared/CLI_POLICY.md.
- Do not use here-docs or interactive prompts.
- Ask for permission before any write/modify/delete operation.

1) Iterative flow and change tolerance
- Every sub-workflow declares iteration_paths that specify where to go when validation fails or a change is requested mid-flight.
- New/changed/removed features during development should route through the Feature Update path (FU-02 Arch Re-Engineering), then return to the current development stage once specs are re-aligned.
- Validations that fail at any point may route back to the most local corrective workflow (e.g., from Arch-05 back to Arch-02).

2) Context management for finite LLM context
- All workflows share refresh triggers and snapshot rules from shared/context_policies.json.
- Long-running steps require periodic checkpoints (context checkpoints) and refreshes.
- Each step starts by reasserting system_name, current stage/step, next action, and outstanding gates.
- Self-improvement: after refresh completion or step exit, the agent appends generic suggestions to reflow/process_improvements/inbox/inbox.jsonl per template (see Section 6).

3) Artifact segregation (clear folder delineation)
We separate working/context artifacts, machine-readable system engineering specs, human-facing docs/visualizations, and code.

Recommended directory structure under systems/<system_name>/:
- context/                          # ephemeral or in-progress context artifacts
  - process_log.md
  - working_memory.json
  - step_progress_tracker.json | dev_progress_tracker.json
  - current_focus.md | dev_current_focus.md
  - context_checkpoint.md | dev_context_checkpoint.md
  - focus/                          # per-service focus files for parallelism
    - <service>.md
  - checkpoints/                    # per-service checkpoints
    - <service>.md
  - sync/                           # concurrency coordination
    - locks/                        # exclusive resource locks (JSON files)
    - gates.json                    # array of open/closed await gates
- specs/
  - machine/                       # LLM- and automation-facing structured artifacts
    - index.json
    - service_arch/                # per-service spec roots
      - <service>/
        - service_architecture.json
        - api_contracts.json
        - data_models.json
        - integration_tests.json
        - infrastructure.json
        - testing_requirements.json
        - observability.json
        - compliance.json
        - cicd_pipeline.json
        - interface_contracts/     # generated ICDs if per-service
    - interfaces/                  # system-wide ICDs (if centralized)
    - graphs/
      - system_of_systems_graph.json
    - registries/
      - interface_registry.json
    - build_ready_index.json
  - human/                         # human-facing docs, reports, visuals
    - ARCHITECTURE_CONTEXT_SUMMARY.md
    - visualizations/
      - ARCHITECTURE_VISUALIZATION.md
      - level1_architecture.mmd
      - level2_architecture.mmd
      - level3_architecture.mmd
    - FUNCTIONAL_TEST_STRATEGY.md
    - BUILD_INSTRUCTIONS.md
    - SYSTEM_MISSION_STATEMENT.md
    - USER_SCENARIOS.md
    - SUCCESS_CRITERIA.md
    - operational_test_scenarios/
    - release_notes.md
    - migration_instructions.md
    - reports/
      - validation_reports/
      - operational_validation_report.md
      - mission_alignment_assessment.md
      - user_acceptance_results.md
- code/                             # codebases for services (if colocated)
  - <service>/
    - ... service code ...

Notes:
- The reflow does not move or modify existing artifacts. When generating new artifacts, prefer the segregated structure above.
- Index files (index.json, build_ready_index.json) should use absolute paths to canonical locations, allowing legacy & new paths to coexist.
- Tools should read from canonical index.json and write new artifacts into specs/machine where applicable.

4) Handoff conventions
- Optional await gates: steps may declare gates they wait on (e.g., icd_stable for an interface). Use context/sync/gates.json to coordinate across agents.
- Exclusive updates (index.json, interface_registry, build_ready_index.json) require a lock under context/sync/locks/ per templates/lock_template.json before changes.
- Each sub-workflow specifies handoff.produces listing the artifacts required by the next workflow.
- Handoffs are validated by checking presence and (when possible) tool validation of produced artifacts.

5) Compatibility and migration
- Legacy artifacts (e.g., service_architecture.json located directly under systems/<system_name>/<service>/) remain valid.
- Prefer writing new or regenerated artifacts under specs/machine. If both exist, index.json must point to the authoritative one.

6) Continuous self-improvement (process) & parallelism
- Inbox: /home/ajs7/project/saa/reflow/process_improvements/inbox/inbox.jsonl (JSONL, one object per line)
- Template: /home/ajs7/project/saa/reflow/process_improvements/template.json
- Rules: Suggestions must be generic and redact any system/service specifics.
- Curate regularly: move accepted items to curated/ and, after implementation, to applied/ with references to diffs or commits.

Parallelism quick rules:
- Use per-service focus files under context/focus/<service>.md to prevent global focus contention.
- Use gates.json to coordinate when a team must await another’s contract or schema stability.
- Acquire locks for exclusive resources before edits, and release (delete) the lock file upon completion or TTL expiry.
- Prefer small-scoped changes to reduce lock hold time.
- Inbox: /home/ajs7/project/saa/reflow/process_improvements/inbox/inbox.jsonl (JSONL, one object per line)
- Template: /home/ajs7/project/saa/reflow/process_improvements/template.json
- Rules: Suggestions must be generic and redact any system/service specifics.
- Curate regularly: move accepted items to curated/ and, after implementation, to applied/ with references to diffs or commits.
