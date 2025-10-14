# Coordination and synchronization (parallel development)

Purpose
- Enable multiple agents/teams to work concurrently without conflicting focus or overwriting shared artifacts.

Key files (under systems/<system_name>/context/)
- focus/<service>.md: per-service current focus (use template in reflow/templates/per_service_focus_template.md)
- checkpoints/<service>.md: per-service context checkpoint
- sync/locks/: per-resource lock files (use reflow/templates/lock_template.json)
- sync/gates.json: array of gate items (use reflow/templates/gate_item_template.json for each)

Guidelines
- Prefer per-service focus files over global focus for concurrent work.
- Use locks for exclusive operations (index.json, interface registry, build_ready_index.json). Keep lock TTL small and release promptly.
- Use gates.json to record awaits like icd_stable or schema_ready across services.
- Declare optional awaits in steps (documentation) and check gates before proceeding.
- Keep changes small to minimize coordination overhead.
