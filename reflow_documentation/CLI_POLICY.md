# Non-interactive CLI policy for reflow

Objective
- Ensure all workflow instructions and automation use non-interactive, single-shot commands. Avoid any prompts that leave the shell waiting for user input.

Hard rules
- DO NOT use here-docs (e.g., `<<EOF`, `<<'PY'`) in suggested or automated commands.
- DO NOT require interactive shells or REPL sessions (python, node, psql, etc.) unless explicitly requested and justified.
- Prefer idempotent, non-destructive commands by default (read-only or dry-run when available).
- For any operation that writes, modifies, or deletes files, ask for user confirmation before executing.
- Provide complete, copy-pasteable commands with all necessary flags and paths. No placeholders for secrets; use environment variables if needed.

Patterns
- Allowed: `python3 -c "import json,sys; print('ok')"`
- Allowed: `jq -e . file.json` (fails non-zero on invalid JSON)
- Allowed: `find … -print` with explicit absolute paths
- Disallowed: `python3 - << 'PY'` … here-doc blocks
- Disallowed: `python3` (REPL) awaiting input

Agent behavior
- When a command is necessary: state intent, ask permission if the command modifies files, then run the single-shot command.
- For long tasks: split into small, verifiable non-interactive steps, checkpointing per shared/context_policies.json.
