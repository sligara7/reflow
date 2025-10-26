# Reflow Tools - Usage Summary

**Last Updated**: 2025-10-26
**Total Tools**: 16 (down from 24 - deleted 8 unused/legacy tools)
**Security Version**: v3.4.0 (Path Traversal Protection Added)

---

## 🔒 Security Features (v3.4.0+)

**All 16 tools now include path traversal protection** to prevent malicious file access.

### Security Module: `path_utils.py`

Located in `tools/path_utils.py`, this module provides:

#### Core Security Functions

**`sanitize_path(user_path, system_root, must_exist=False, strict=True, allow_symlinks=True)`**
- Validates all file paths stay within `system_root` boundaries
- Blocks path traversal attempts (`../../etc/passwd`)
- Blocks absolute paths outside system_root (`/etc/passwd`)
- Resolves symlinks and validates they don't escape system_root
- Returns validated `Path` object

**`validate_system_root(system_root)`**
- Validates system_root is a valid, existing directory
- Ensures system_root is not a file
- Returns validated `Path` object

**`is_safe_filename(filename, allow_dots=False)`**
- Checks filenames for path traversal characters
- Blocks directory separators (`/`, `\`)
- Blocks null bytes
- Validates leading dots based on `allow_dots` parameter

### What's Protected Against

All tools are protected against:

1. **Path Traversal Attacks**
   - Input: `../../etc/passwd`
   - Result: `PathSecurityError` - blocked before file access

2. **Absolute Path Escapes**
   - Input: `/etc/passwd`
   - Result: `PathSecurityError` - outside system root

3. **Symlink Attacks**
   - Symlinks pointing outside system_root are blocked
   - Symlinks within system_root are allowed (configurable)

4. **Null Byte Injection**
   - Input: `file\x00.txt`
   - Result: Blocked (ValueError or PathSecurityError)

5. **Cross-System Access**
   - Attempting to access `/system2/` from `/system1/` context
   - Result: `PathSecurityError`

### Usage in Tools

Every tool now follows this pattern:

```python
from path_utils import sanitize_path, validate_system_root, PathSecurityError

# 1. Validate system_root
try:
    system_root = validate_system_root(args.system_path)
except PathSecurityError as e:
    print(f"ERROR: Path security violation: {e}")
    sys.exit(1)

# 2. Sanitize all file paths
try:
    safe_file = sanitize_path("docs/README.md", system_root, must_exist=True)
    with open(safe_file) as f:
        content = f.read()
except PathSecurityError as e:
    print(f"ERROR: Path security violation: {e}")
    sys.exit(1)
```

### Testing

Comprehensive unit tests are available in `tests/unit/test_path_utils.py`:
- 28 tests covering all security scenarios
- Run with: `python -m pytest tests/unit/test_path_utils.py -v`
- All tests pass (100% coverage of security functions)

### Security Audit Trail

- **Issue #1 (SV-01)**: Path Traversal Vulnerabilities - Fixed in v3.4.0
- **Commits**: 9 parts (b22b4e9 through 756791c)
- **Tools Secured**: 16 of 16 (100%)
- **Lines Added**: ~1,100 lines of security code
- **Issue #2 (SV-02)**: JSON Schema Validation - Fixed in v3.4.0
- **Commits**: 5 parts (c3bec34, d76d592, a2bf267, 86ec69a, 2b68a6f)
- **Tools Updated**: 13 of 13 (100%)
- **JSON Loads Secured**: 38 of 38 (100%)

### JSON Validation Module: `json_utils.py`

**All 13 tools that load JSON files now use safe_load_json()** with comprehensive error handling and optional schema validation.

Located in `tools/json_utils.py`, this module provides:

#### Core JSON Validation Functions

**`safe_load_json(file_path, schema=None, file_type_description="JSON file")`**
- Validates JSON syntax before processing
- Optional JSON schema validation (uses jsonschema library)
- Helpful error messages with line/column numbers
- Context-specific error messages via `file_type_description`
- Returns parsed JSON data as dictionary

**`safe_load_json_with_schema_path(file_path, schema_path=None, file_type_description="JSON file")`**
- Convenience wrapper that loads schema from file
- Graceful fallback if schema file missing or invalid
- Same validation benefits as `safe_load_json()`

**`validate_required_fields(data, required_fields, file_description="JSON data")`**
- Validates that required fields are present
- Lists all missing fields in error message
- Raises `JSONValidationError` with clear guidance

**`validate_json_type(data, expected_type, field_name="root", file_description="JSON data")`**
- Validates JSON data is of expected type (dict, list, str, etc.)
- Shows expected vs actual type in error message
- Useful for type checking nested JSON structures

### What JSON Validation Protects Against

1. **Malformed JSON Syntax**
   - **Trailing commas**: `{"key": "value",}` → Error with helpful fix suggestion
   - **Single quotes**: `{'key': 'value'}` → Error suggesting double quotes
   - **Unquoted keys**: `{key: "value"}` → Error with quoting guidance
   - **Missing brackets**: `{"key": ["value1", "value2"` → Error showing line/column

2. **Invalid JSON Structure**
   - Schema validation ensures JSON matches expected format
   - Catches missing required fields before processing
   - Validates field types (string vs int vs array, etc.)
   - Prevents downstream crashes from malformed data

3. **File Encoding Issues**
   - Detects UTF-8 encoding errors
   - Provides clear guidance on fixing encoding problems

### Helpful Error Messages

JSON validation provides **context-specific error messages**:

**Example 1: Trailing Comma**
```
Invalid JSON syntax in workflow file: workflows/00-setup.json
Error at line 42, column 15: Expecting property name enclosed in double quotes

Common issues:
  - Missing closing bracket/brace
  - Trailing comma in array or object
  - Unquoted strings or keys
  - Single quotes instead of double quotes

Use a JSON validator (e.g., jsonlint.com) to debug the syntax error.
```

**Example 2: Schema Validation Failure**
```
Schema validation failed for service architecture: service_architecture.json
Error at 'metadata.version': '1.0' does not match '^[0-9]+\\.[0-9]+\\.[0-9]+$'

This means the JSON file structure doesn't match the expected format.
Please check the documentation for the correct service architecture structure.
```

**Example 3: Missing Required Field**
```
Missing required fields in workflow metadata:
  - workflow_id
  - version

Required fields: workflow_id, name, version, description
Please add the missing fields to the JSON file.
```

### Usage in Tools

All 13 tools now follow this pattern:

```python
from json_utils import safe_load_json, JSONValidationError

# Load JSON with syntax validation
try:
    data = safe_load_json(file_path, file_type_description="service architecture")
except JSONValidationError as e:
    print(f"ERROR: {e}")
    sys.exit(1)

# Or with schema validation
try:
    with open("schemas/workflow_schema.json") as f:
        schema = json.load(f)
    data = safe_load_json(file_path, schema=schema, file_type_description="workflow file")
except JSONValidationError as e:
    print(f"ERROR: {e}")
    sys.exit(1)
```

### Tools with JSON Validation

All 13 tools that load JSON now use safe_load_json():

1. **validate_workflow_files.py** - Workflow files (with schema validation)
2. **validate_port_registry.py** - Port registry
3. **system_of_systems_graph_v2.py** - Working memory, framework registry, component index, architectures
4. **validate_architecture.py** - Service architectures, interface registry, working memory
5. **validate_foundational_alignment.py** - Service architectures, architectural definitions, change proposals
6. **generate_interface_contracts.py** - Templates, component index, component architectures
7. **verify_component_contract.py** - Component specifications, test suites
8. **bootstrap_development_context.py** - JSON templates
9. **validate_directory_structure.py** - Behavioral rules
10. **analyze_features.py** - Working memory
11. **select_development_languages.py** - Build-ready config, service architectures, language config
12. **identify_integration_points.py** - System analysis files
13. **generate_rag_embeddings.py** - RAG config, workflows, embeddings metadata, knowledge base sources
14. **reflow_mcp_server.py** - Working memory, progress tracker, workflows, decision flow

### Testing

Comprehensive unit tests are available in `tests/unit/test_json_utils.py`:
- 24 tests covering all JSON validation scenarios
- Tests for malformed JSON (trailing commas, single quotes, missing brackets, etc.)
- Tests for schema validation success and failure
- Tests for helpful error messages
- Run with: `python -m pytest tests/unit/test_json_utils.py -v`
- All tests pass (100% coverage of JSON validation functions)

---

## Core Workflow Tools (Used in Every Execution)

### 1. `system_of_systems_graph_v2.py` ⭐ **FLAGSHIP TOOL**
**Purpose**: Generate system-of-systems graph with comprehensive NetworkX analysis  
**Used In**: SE-06 (Systems Engineering), SE-07 (Architecture Evolution), FU-02 (Feature Updates)  
**Features**:
- Framework-agnostic (UAF, Biology, Social, Ecological, CAS, Custom)
- Knowledge gap detection (--detect-gaps)
- Architectural issue detection (--analyze-issues)
- 10 NetworkX analysis types: centrality, paths, connectivity, clustering, properties, community, cycles, SCC, DAG, flow
- Explicit system-root argument for reliable path resolution

**Key Capabilities**:
```bash
# Basic usage
python3 system_of_systems_graph_v2.py specs/machine/index.json

# With comprehensive analysis (UAF systems)
python3 system_of_systems_graph_v2.py specs/machine/index.json \
  --detect-gaps --analyze-issues \
  --centrality --dag --scc --community --connectivity

# Biology systems (feedback loops expected)
python3 system_of_systems_graph_v2.py specs/machine/index.json \
  --detect-gaps --cycles --centrality --community --scc

# All analyses
python3 system_of_systems_graph_v2.py specs/machine/index.json --analyze-all
```

**Workflow Integration**: Fully utilized - workflows provide framework-specific analysis flag selection guidance

---

### 2. `validate_architecture.py`
**Purpose**: Validate service/component architecture files against UAF/framework schemas  
**Used In**: SE-03 (validation), SE-07 (post-update validation), FU-02 (feature update validation)  
**References**: 7 references across workflows  
**Validates**:
- JSON syntax
- Required fields presence
- UAF 1.2 compliance (or framework-specific compliance)
- service_id at top level (not nested)

---

### 3. `generate_interface_contracts.py`
**Purpose**: Generate Interface Contract Documents (ICDs) from architecture files  
**Used In**: AV-01 (Artifacts & Visualization)  
**References**: 2 references  
**Output**: Detailed ICDs for each interface in specs/machine/interfaces/

---

### 4. `bootstrap_development_context.py`
**Purpose**: Initialize development environment with dependencies, directory structure, context files  
**Used In**: D-01 (Development Initialization)  
**References**: 4 references  
**Creates**:
- Development environment (venv, dependencies)
- Dev-specific context files
- Language-specific project structure

---

### 5. `verify_component_contract.py`
**Purpose**: Verify service implementation matches architecture contract  
**Used In**: D-03, D-04, D-05 (Development phases)  
**References**: 6 references  
**Validates**: Implementation adheres to architecture specifications

---

## Validation & Quality Assurance Tools

### 6. `validate_directory_structure.py`
**Purpose**: Validate system directory structure matches Reflow requirements  
**Used In**: S-02 (Setup)  
**Validates**: specs/, docs/, context/, services/ directories exist

---

### 7. `validate_port_registry.py`
**Purpose**: Validate port assignments for UAF/IT systems - detect conflicts  
**Used In**: SE-03 (validation), SE-04 (deployment architecture)  
**References**: 3 references  
**Checks**: PC-01 through PC-05 (duplicate ports, port ranges, privileged ports, docker mappings)

---

### 8. `validate_foundational_alignment.py`
**Purpose**: Validate foundational documents align with architecture  
**Used In**: SE-03 (validation), SE-05 (consistency verification)  
**References**: 4 references  
**Validates**: Mission statement, scenarios, success criteria align with architecture

---

### 9. `validate_workflow_files.py` 🆕
**Purpose**: Validate workflow JSON files for syntax, structure, references  
**Used In**: CI/CD pipeline (not in workflows - development/maintenance tool)  
**Created**: 2025-10-25 (during meta-analysis)  
**Validates**:
- JSON syntax correctness
- Required fields (workflow_metadata, workflow_steps, completion)
- Step ID uniqueness
- Valid next_step references
- Tool/template references

---

## Analysis & Planning Tools

### 10. `analyze_features.py`
**Purpose**: Analyze feature requirements and identify required services  
**Used In**: SE-01 (System Analysis)  
**References**: 2 references  
**Input**: SYSTEM_MISSION_STATEMENT.md, USER_SCENARIOS.md  
**Output**: Initial service breakdown

---

### 11. `select_development_languages.py`
**Purpose**: Select appropriate development languages for services  
**Used In**: D-01 (Development Initialization)  
**References**: 2 references  
**Considers**: Service requirements, team preferences, architectural constraints

---

### 12. `identify_integration_points.py`
**Purpose**: Identify integration points for system-of-systems projects  
**Used In**: S-04 (System-of-Systems Decomposition - OPTIONAL), SE-04 (Architecture Reconciliation)  
**References**: 2 references  
**Use Case**: Multi-system integration projects

---

## Optional/Advanced Tools

### 13. `generate_rag_embeddings.py` (OPTIONAL)
**Purpose**: Generate RAG embeddings for context management  
**Used In**: S-03-A05 (Setup - optional RAG setup)  
**References**: 1 reference  
**Benefits**: Automatic context injection, degradation detection  
**Dependencies**: sentence-transformers, faiss-cpu, numpy

---

### 14. `rag_agent_wrapper.py` (OPTIONAL)
**Purpose**: Wrap LLM queries with RAG-enhanced context  
**Used In**: Throughout workflows if RAG enabled  
**References**: Mentioned in workflows but used dynamically  
**Strategies**: on_step_start, on_degradation_detected, on_tool_execution, periodic_refresh

---

### 15. `export_system_to_github.py` (OPTIONAL)
**Purpose**: Export architecture-only handoff package to GitHub  
**Used In**: AV-04 (Architecture-Only Handoff)  
**References**: 1 reference  
**Use Case**: When system design complete but development elsewhere

---

## Standalone Tools (Not in Workflows)

### 16. `reflow_mcp_server.py`
**Purpose**: Model Context Protocol server for Claude integration  
**Used In**: Standalone - enables Claude to interact with Reflow via MCP  
**References**: 0 workflow references (intentional - standalone utility)  
**Usage**:
```bash
python3 reflow_mcp_server.py --reflow-root /path/to/reflow --port 3000
```
**Capabilities**: Exposes workflows, tools, prompts via standardized MCP interface

---

## Deleted Tools (2025-10-25 Cleanup)

### Injection System (5 tools) - DELETED
- `inject_tools.py` - No longer needed
- `inject_workflows.py` - No longer needed
- `create_embedded_scripts.py` - No longer needed  
- `execute_injection_flow.py` - No longer needed
- `validate_injection_readiness.py` - No longer needed

**Reason**: Injection system was old implementation approach, not referenced in v3.0 workflows

---

### Legacy/Duplicate Tools (3 tools) - DELETED
- `system_of_systems_graph.py` - Replaced by v2, all workflows updated
- `retrieve_rag_context.py` - Redundant with rag_agent_wrapper.py
- `analyze_system_structure.py` - Purpose unclear, not referenced

---

## Tool Usage Best Practices

### For LLM Agents Executing Workflows

1. **Always use absolute paths**: `python3 {reflow_root}/tools/tool_name.py {system_root}`
2. **Read tool output carefully**: Many tools provide validation results and actionable guidance
3. **Use validation loops**: Run validation, fix issues, re-run (up to 5 iterations)
4. **Select appropriate analyses**: system_of_systems_graph_v2.py has framework-specific recommendations
5. **Check tool exit codes**: Non-zero exit code = fix required before proceeding

### Analysis Flag Selection (system_of_systems_graph_v2.py)

Workflows provide comprehensive guidance in SE-06-A02:
- Read framework_id from working_memory.json
- Load framework_registry.json for recommended_analyses
- Select high_priority + medium_priority analyses for your framework

**Examples**:
- **UAF**: --centrality --dag --scc --community --connectivity
- **Biology**: --cycles --centrality --community --scc
- **Social Networks**: --centrality --community --clustering --connectivity
- **Ecological**: --flow --centrality --connectivity --community --cycles (requires edge weights!)

---

## Tool Dependencies

Most tools have zero external dependencies (use Python stdlib). Exceptions:

- **system_of_systems_graph_v2.py**: Requires `networkx`, `matplotlib` (installed during meta-analysis)
- **generate_rag_embeddings.py**: Requires `sentence-transformers`, `faiss-cpu`, `numpy` (optional)
- **rag_agent_wrapper.py**: Same as generate_rag_embeddings.py
- **reflow_mcp_server.py**: Requires `mcp` package (Model Context Protocol - optional)

---

## Summary Statistics

- **Total Tools**: 16 (down from 24)
- **Core Workflow Tools**: 12 (always/often used)
- **Optional/Advanced Tools**: 3 (RAG system, export)
- **Standalone Tools**: 1 (MCP server)
- **Deleted**: 8 (33% reduction - injection system + legacy)
- **Workflow References**: 50+ total references across 6 workflows
- **Tools with 0 workflow references**: 2 (validate_workflow_files.py - CI/CD tool, reflow_mcp_server.py - standalone)

---

## Maintenance Notes

**Last Tool Audit**: 2025-10-25  
**Tools Added**: validate_workflow_files.py (meta-analysis)  
**Tools Deleted**: 8 (injection system, legacy v1 graph, redundant tools)  
**Workflows Updated**: 00-setup.json, 01-systems_engineering.json, feature_update.json (v1 → v2 references)

**Next Review**: When adding new workflows or deprecating features
