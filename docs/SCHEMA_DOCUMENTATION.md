# Reflow JSON Schema Documentation

**Version**: 3.4.0
**Last Updated**: 2025-10-26

## Overview

Reflow uses JSON Schema (draft-07) to validate workflow files, ensuring structural correctness and preventing configuration errors.

## Schema Files

### `schemas/workflow_schema.json`

Validates workflow JSON files in `workflows/` directory.

**Validated Files**:
- `00-setup.json`
- `01-systems_engineering.json`
- `02-artifacts_visualization.json`
- `03-development.json`
- `04-testing_operations.json`
- `feature_update.json`

## Workflow Schema Structure

### Top-Level Properties

```json
{
  "workflow_metadata": { ... },      // REQUIRED - Workflow identification
  "path_configuration": { ... },     // OPTIONAL - Path requirements
  "entry_points": { ... },           // OPTIONAL - Workflow entry scenarios
  "context_management": { ... },     // OPTIONAL - Context tracking config
  "workflow_steps": [ ... ],         // REQUIRED - Ordered workflow steps
  "completion": { ... },             // OPTIONAL - Completion criteria
  "prerequisites": { ... }           // OPTIONAL - Prerequisites
}
```

### `workflow_metadata` (REQUIRED)

Identifies the workflow and tracks versioning.

**Required Fields**:
- `workflow_id` (string): Workflow identifier matching pattern `^[0-9]{2}-[a-z_]+$|^feature_update$`
  - Examples: `"00-setup"`, `"01-systems_engineering"`, `"feature_update"`
- `name` (string): Human-readable workflow name
- `version` (string): Semantic version matching pattern `^[0-9]+\.[0-9]+\.[0-9]+$`
  - Examples: `"1.0.0"`, `"1.1.0"`, `"2.0.0"`
- `description` (string): Detailed workflow description

**Optional Fields**:
- `created_from` (string): Origin/migration information
- `last_updated` (string): Last update date (YYYY-MM-DD format)
- `purpose` (string): Primary purpose of this workflow

**Example**:
```json
{
  "workflow_metadata": {
    "workflow_id": "01-systems_engineering",
    "name": "Systems Engineering Workflow",
    "version": "1.2.0",
    "description": "Architecture design and validation workflow",
    "last_updated": "2025-10-24",
    "purpose": "Design system architecture following UAF 1.2 standards"
  }
}
```

### `workflow_steps` (REQUIRED)

Array of workflow steps executed in order.

**Required Fields** (per step):
- `step_id` (string): Unique step identifier
  - Flexible format allows: `S-01`, `SE-02`, `D-Post`, `S-04-decision`, `AV-00-decision`
- `name` (string): Step name
- `description` (string): Detailed step description
- `phase` (string): Workflow phase (flexible - any string)
  - Common values: `"setup"`, `"architecture"`, `"development"`, `"testing"`, `"validation"`

**Optional Fields** (per step):
- `step_file` (string): Path to detailed step definition file
  - Pattern: `^workflow_steps/.+\.json$`
  - Example: `"workflow_steps/setup/S-01-PathConfiguration.json"`
- `rationale` (string): Why this step exists
- `actions` (array): Actions to perform in this step (see Actions section below)
- `tools_used` (array of strings): Reflow tools invoked in this step
  - Flexible format allows descriptions: `"system_of_systems_graph_v2.py"`, `"tool.py (optional)"`
- `outputs` (array of strings): Files or artifacts created by this step
- `gates` (array): Quality gates for this step (see Gates section below)
- `next_step` (string or object): Next step ID or conditional routing
  - Simple: `"S-02"`, `"SE-03"`, `"complete"`, `"completed"`
  - Conditional: See Conditional Routing section below
- `optional` (boolean): Whether this step is optional (default: false)
- `skip_if` (object): Conditions under which to skip this step

**Example**:
```json
{
  "step_id": "SE-02",
  "name": "Design Service Architectures",
  "description": "Create architecture files for each service",
  "phase": "architecture",
  "actions": [
    {
      "action_id": "SE-02-A01",
      "description": "Design service architecture",
      "success_criteria": "Architecture file created and validated"
    }
  ],
  "tools_used": ["validate_architecture.py"],
  "outputs": ["specs/machine/service_arch/service_architecture.json"],
  "gates": [
    {
      "gate_id": "G-SE-02",
      "name": "Architecture Validation",
      "checks": ["All required fields present", "Valid JSON schema"],
      "blocking": true,
      "severity": "critical"
    }
  ],
  "next_step": "SE-03"
}
```

### Actions

Actions define specific tasks within a workflow step.

**Required Fields**:
- `action_id` (string): Unique action identifier (flexible format)
  - Examples: `"S-01-A01"`, `"SE-02-A03"`, `"D-Post-A04"`
- `description` (string): What the action does

**Optional Fields**:
- `command_pattern` (string): Command template to execute
- `user_prompt` (object): Interactive prompt for user input
- `verification` (string): How to verify action completion
- `success_criteria` (string OR array of strings): Criteria for success
  - String: `"All tests pass"`
  - Array: `["Test coverage >= 80%", "No critical errors"]`
- `store_in` (string): Where to store results
- `details` (string): Additional details

**Example**:
```json
{
  "action_id": "SE-06-A02",
  "description": "Select framework-appropriate NetworkX analyses",
  "success_criteria": [
    "system_of_systems_graph_v2.py completes without errors",
    "Framework-appropriate analyses selected and run successfully",
    "Generated graph shows cohesive system (no orphans, no unexplained cycles)"
  ],
  "verification": "Check system_of_systems_graph.json contains networkx_analysis section",
  "store_in": "specs/machine/graphs/system_of_systems_graph.json"
}
```

### Gates

Quality gates enforce validation before proceeding.

**Required Fields**:
- `gate_id` (string): Unique gate identifier matching pattern `^G-[A-Z]+-[0-9]{2}$`
  - Examples: `"G-SE-01"`, `"G-D-05"`
- `name` (string): Gate name
- `checks` (array of strings): List of validation checks (minimum 1)

**Optional Fields**:
- `blocking` (boolean): Whether gate failure blocks progression
  - **NOTE**: Made optional in schema (some workflows don't specify)
  - Default assumption: `true` for critical gates
- `enforcement` (object): Two-tier enforcement (v1.1.0+)
  - `tier_1_critical` (array of strings): Critical checks that must pass
  - `tier_2_important` (array of strings): Important checks that should pass
- `severity` (string): Gate severity level
  - Allowed values: `"critical"`, `"warning"`, `"info"`
- `tools` (array of strings): Tools used for gate validation

**Example**:
```json
{
  "gate_id": "G-SE-01",
  "name": "Architecture Validation",
  "checks": [
    "All service architectures have valid JSON syntax",
    "All required UAF fields present",
    "No circular dependencies detected",
    "All interfaces properly defined"
  ],
  "blocking": true,
  "enforcement": {
    "tier_1_critical": [
      "Valid JSON syntax",
      "No circular dependencies"
    ],
    "tier_2_important": [
      "All interfaces documented",
      "Performance requirements specified"
    ]
  },
  "severity": "critical",
  "tools": ["validate_architecture.py"]
}
```

### Conditional Routing (`next_step`)

Supports conditional branching based on runtime decisions.

**Simple Format**:
```json
"next_step": "SE-03"
```

**Conditional Format**:
```json
"next_step": {
  "default": "SE-03",
  "conditional": [
    {
      "condition": "if user chose architecture-only mode",
      "step": "AV-01"
    },
    {
      "condition": "if user chose full implementation",
      "step": "D-01"
    }
  ]
}
```

**Completion Values**:
- `"complete"` or `"completed"`: Workflow ends here

### `completion` (OPTIONAL)

Defines workflow completion criteria and next workflow transition.

**Fields**:
- `next_workflow` (string or null): Next workflow ID to transition to (without .json extension)
  - String: `"01-systems_engineering"`, `"feature_update"`
  - Null: No next workflow (final workflow in chain)
- `outputs_required` (array of strings): Required outputs for completion
- `quality_gates_passed` (array of strings): Gates that must pass

**Example**:
```json
{
  "completion": {
    "next_workflow": "01-systems_engineering",
    "outputs_required": [
      "context/working_memory.json",
      "docs/system_description.md"
    ],
    "quality_gates_passed": ["G-S-03"]
  }
}
```

## Schema Validation

### Using `validate_workflow_files.py`

```bash
# Validate all workflows
python3 tools/validate_workflow_files.py workflows/

# Validate single workflow
python3 tools/validate_workflow_files.py workflows/01-systems_engineering.json
```

**Output Example**:
```
✓ Loaded workflow schema from /path/to/reflow/schemas/workflow_schema.json
Validating workflows in: /path/to/reflow/workflows
======================================================================

📄 Validating: 01-systems_engineering.json
  ✓ JSON syntax valid
  ✓ Schema validation passed
  ✓ Required top-level fields present
  ✓ workflow_metadata fields valid
  ✓ Step IDs unique (8 steps)
  ✓ Step references valid
  ✅ 01-systems_engineering.json is VALID
```

### Programmatic Validation (Python)

```python
import json
import jsonschema

# Load schema
with open("schemas/workflow_schema.json") as f:
    schema = json.load(f)

# Load workflow file
with open("workflows/01-systems_engineering.json") as f:
    workflow = json.load(f)

# Validate
try:
    jsonschema.validate(workflow, schema)
    print("✅ Workflow is valid")
except jsonschema.ValidationError as e:
    print(f"❌ Validation error: {e.message}")
    print(f"   Path: {'.'.join(str(p) for p in e.path)}")
```

## Common Validation Errors

### Error: Missing Required Field

```
✗ SCHEMA VALIDATION ERROR at 'workflow_metadata': 'version' is a required property
```

**Fix**: Add missing required field to `workflow_metadata`.

### Error: Invalid Pattern

```
✗ SCHEMA VALIDATION ERROR at 'workflow_metadata.workflow_id': '1-systems' does not match '^[0-9]{2}-[a-z_]+$|^feature_update$'
```

**Fix**: Ensure `workflow_id` starts with two digits: `"01-systems_engineering"` not `"1-systems"`.

### Error: Type Mismatch

```
✗ SCHEMA VALIDATION ERROR at 'workflow_steps.0.gates.0.blocking': True is not of type 'boolean'
```

**Fix**: Ensure boolean values are lowercase: `true` not `True`.

### Error: Invalid Next Step

```
✗ Invalid next_step reference: SE-02 → SE-99 (step does not exist)
```

**Fix**: Ensure `next_step` references an existing `step_id` or use `"complete"`.

## Schema Design Principles

### Flexibility vs. Strictness

The Reflow workflow schema balances validation strictness with real-world flexibility:

**Flexible Patterns**:
- `step_id`: Allows various formats (`S-01`, `SE-02`, `D-Post`, `S-04-decision`)
- `phase`: Any string (workflows use many phase names)
- `tools_used`: Allows descriptions like `"tool.py (optional)"`
- `action_id`: Flexible format to accommodate different step prefixes

**Strict Requirements**:
- `workflow_id`: Must match `^[0-9]{2}-[a-z_]+$` or be `feature_update`
- `version`: Must be semantic version `^[0-9]+\.[0-9]+\.[0-9]+$`
- `gate_id`: Must match `^G-[A-Z]+-[0-9]{2}$`

**Rationale**: Schema should validate structure, not enforce naming conventions. This allows workflows to evolve naturally while catching genuine errors.

### Optional Fields Philosophy

Many fields are optional to support:
- **Progressive Enhancement**: Workflows can start simple, add detail later
- **Backward Compatibility**: Existing workflows don't break when new fields added
- **Use Case Diversity**: Different workflows have different needs

**Example**: `blocking` field in gates is optional because some workflows use `severity` instead.

## Schema Versioning

Schema follows semantic versioning aligned with Reflow versions:

- **Major Version**: Breaking changes (e.g., required field becomes mandatory)
- **Minor Version**: New optional fields or relaxed constraints
- **Patch Version**: Bug fixes, documentation updates

**Current Version**: Aligned with Reflow v3.4.0

## Future Schema Enhancements

Planned improvements for future versions:

1. **Template Schema**: Validate template JSON files
2. **Architecture Schema**: Validate service_architecture.json files
3. **Context Schema**: Validate working_memory.json structure
4. **Step Definition Schema**: Validate workflow_steps/*.json files
5. **Cross-Schema References**: Validate references between schemas (e.g., tool names)

## References

- **JSON Schema Specification**: https://json-schema.org/draft-07/schema
- **JSON Schema Validator**: https://github.com/python-jsonschema/jsonschema
- **Reflow Workflow Files**: `workflows/*.json`
- **Validation Tool**: `tools/validate_workflow_files.py`

## Change Log

### v3.4.0 (2025-10-26)
- Initial workflow schema creation (Issue #8: SCHEMAS-01)
- Validates all 6 existing workflow files successfully
- Integrated into `validate_workflow_files.py` tool
- Flexible patterns for real-world workflow variations
