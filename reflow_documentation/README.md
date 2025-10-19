# Process Improvements (Reflow)

Purpose
- Provide a single place for the LLM agent to capture generic, system-agnostic process improvements while executing workflows.
- Human reviewers can periodically curate suggestions and incorporate approved changes into the reflow.

Directory layout
- process_improvements/inbox/       # append-only, raw suggestions (JSONL or MD)
- process_improvements/curated/     # curated suggestions grouped by theme
- process_improvements/applied/     # accepted & implemented changes with references to diffs/commits

Authoring rules (LLM)
- MUST be generic. Do NOT include system names, service names, internal paths, secrets, or user-specific details.
- Prefer actionable, concise suggestions with a clear rationale.
- Include category and impacted workflow area (e.g., architecture A2, development D5, feature_update F2).
- Provide evidence refs (paths to public templates/tools/specs in this repo) if useful.

JSONL format (recommended)
- One JSON object per line, using the template in template.json.
- Write to process_improvements/inbox/inbox.jsonl (append, no edits to previous lines).

Review cadence (human)
- On-demand or time-based (e.g., weekly). Move accepted items to curated/, then to applied/ after implementation.
