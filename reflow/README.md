# SAA Workflow Reflow

This directory contains a modular reflow of the original workflows:
- architecture_workflow.json
- service_development_workflow.json
- feature_update_workflow.json

Goals:
- Split large monolithic workflows into smaller, composable workflows
- Define clear, checklist-style entry/exit (handoff) criteria between workflows
- Provide a single decision flow that routes a request from concept to full operational development
- Preserve all existing assets; this reflow lives alongside them and does not modify originals

Structure:
- reflow/decision_flow.json — top-level router from concept to Architecture, Development, or Feature Update paths
- reflow/workflows_index.json — map of all sub-workflows and their purposes
- reflow/architecture/*.json — modular architecture workflows (A1–A6)
- reflow/development/*.json — modular development workflows (D1–D8, POST)
- reflow/feature_update/*.json — modular feature update workflows (F1–F5)

Handoff conventions:
- Each sub-workflow defines entry_conditions and handoff.produces. 
- To progress to the next workflow, ensure all produces artifacts exist and validations pass.
- Cross-cutting context rules (working directory isolation, refresh triggers) remain aligned with the originals.
- Parallelism-ready: use per-service focus files (context/focus/<service>.md), gates (context/sync/gates.json), and locks (context/sync/locks/) to enable safe concurrent execution.

Quick start:
- New concept/new system → decision_flow.json → architecture/Arch-01-SetupAndContext.json
- Existing system, feature change → decision_flow.json → feature_update/FU-01-ChangeProposal.json
- Architecture already complete (build_ready_index.json present) → decision_flow.json → development/Dev-01-InitBootstrap.json

This reflow mirrors the semantics of the original workflows while increasing maintainability and clarity.
