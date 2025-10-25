# Reflow Tooling Issues: Root Causes and Permanent Fixes

**Date**: 2025-10-25
**Context**: Issues encountered during meta-analysis (Reflow analyzing itself)
**Severity**: **HIGH** - These issues affect every workflow execution
**Status**: Documented for permanent resolution

---

## Issue #1: Path Resolution Inconsistency in system_of_systems_graph_v2.py

### Problem Encountered

When running `system_of_systems_graph_v2.py`, the tool exhibits inconsistent path resolution behavior:

```bash
# Command executed:
python3 tools/system_of_systems_graph_v2.py specs/machine/index.json

# What happened:
System root: /home/user/reflow/specs  ← Tool derives this from index.json location
Index file: /home/user/reflow/specs/machine/index.json

# Then looks for files relative to system root:
Looking for: /home/user/reflow/specs/service_arch/...  ✗ WRONG
Should look: /home/user/reflow/specs/machine/service_arch/...  ✓ CORRECT
```

### Root Cause

**File**: `tools/system_of_systems_graph_v2.py` lines 183-198

```python
def build_universal_graph(index: Dict[str, str], framework_schema: Dict, system_root: str):
    """
    Args:
        system_root: System root directory for resolving relative paths
    """
    # Problem: system_root is derived from parent of index.json directory
    # If index.json is at: /path/to/specs/machine/index.json
    # system_root becomes: /path/to/specs/
    # But paths in index.json like "machine/service_arch/..." are relative to /path/to/specs/
    # This works! BUT...
```

The issue is **how system_root is derived**:

```python
# In main() function (line ~800):
index_path = Path(args.index_file).resolve()
system_root = str(index_path.parent.parent)  # Goes up TWO levels

# Example:
# index_file = "specs/machine/index.json"
# index_path.parent = "specs/machine/"
# index_path.parent.parent = "specs/"  ← This becomes system_root
```

**The Confusion**:
- Is `specs/` the system root? Or `specs/machine/`?
- Should paths in index.json be relative to `specs/` or `specs/machine/`?
- Different users will have different assumptions

### Why This Plagues Workflows

1. **LLM agents guess at path structure** - No clear specification in documentation
2. **Trial and error required** - Agents run tool, get error, adjust paths, repeat
3. **Inconsistent with other tools** - Other tools use different path resolution logic
4. **Documentation ambiguity** - CLAUDE.md doesn't specify exact path requirements for index.json

### Permanent Fix

**Option A: Explicit System Root Argument (RECOMMENDED)**

```python
# Change signature:
def main():
    parser = argparse.ArgumentParser(...)
    parser.add_argument('index_file', help='Path to index.json')
    parser.add_argument('--system-root', required=False,
                       help='System root directory. If not provided, derived from index.json location')

    args = parser.parse_args()

    if args.system_root:
        system_root = Path(args.system_root).resolve()
    else:
        # Derive from index.json location (current behavior)
        index_path = Path(args.index_file).resolve()
        system_root = index_path.parent.parent

    print(f"System root: {system_root}")
    print(f"Index file: {index_path}")
    print(f"Note: Paths in index.json are relative to {system_root}")
```

**Usage**:
```bash
# Explicit system root (no guessing):
python3 tools/system_of_systems_graph_v2.py specs/machine/index.json --system-root /home/user/my_system

# Or use path from working_memory.json:
python3 tools/system_of_systems_graph_v2.py specs/machine/index.json --system-root $(cat context/working_memory.json | jq -r '.path_configuration.system_root')
```

**Option B: Read System Root from working_memory.json (ALTERNATIVE)**

```python
def load_system_root_from_context(index_path: Path) -> Path:
    """Load system_root from working_memory.json."""
    # Try to find working_memory.json relative to index.json
    possible_paths = [
        index_path.parent.parent / "context" / "working_memory.json",  # specs/context/working_memory.json
        index_path.parent.parent.parent / "context" / "working_memory.json",  # system_root/context/working_memory.json
    ]

    for wm_path in possible_paths:
        if wm_path.exists():
            with open(wm_path) as f:
                data = json.load(f)
            return Path(data['path_configuration']['system_root'])

    raise FileNotFoundError("Could not find working_memory.json to determine system_root")

# In main():
system_root = load_system_root_from_context(Path(args.index_file))
print(f"System root loaded from working_memory.json: {system_root}")
```

---

## Issue #2: Template vs. Tool Schema Mismatch

### Problem Encountered

Architecture files generated from template guidance **fail validation** by the graph tool.

**Template Structure** (`templates/service_architecture_template.json`):
```json
{
  "service_id": "my_service",  ← TOP LEVEL (lines 5)
  "service_name": "My Service",
  "interfaces": [...],
  ...
}
```

**BUT** LLM agents often generate:
```json
{
  "metadata": {
    "service_id": "my_service",  ← NESTED (seems more organized?)
    "service_name": "My Service"
  },
  "system_view": {
    "interfaces": [...]
  },
  ...
}
```

**Why?** Because:
1. UAF documentation suggests nested metadata sections
2. Nested structure seems more organized to LLMs
3. Template has `template_description` field suggesting metadata pattern

**Tool Expectation** (`tools/system_of_systems_graph_v2.py` line 129):
```python
universal = {
    'node_id': component_data.get(node_schema['id_field']),  # Looks at TOP LEVEL
    ...
}

node_schema = {
    "id_field": "service_id",  # Expects "service_id" at top level
    ...
}
```

### Why This Plagues Workflows

1. **LLM agents generate invalid files** - Follow organizational instincts, not tool requirements
2. **No validation until graph generation** - Agent completes SE-02, gets to SE-06, then fails
3. **Error messages unhelpful** - "Missing required field 'service_id'" doesn't say "expected at top level"
4. **Templates lack schema files** - No JSON schema to validate against

### Permanent Fix

**Fix #1: Add JSON Schema Files (REQUIRED)**

Create `templates/schemas/service_architecture_schema.json`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "UAF Service Architecture",
  "type": "object",
  "required": ["service_id", "service_name", "interfaces"],
  "properties": {
    "service_id": {
      "type": "string",
      "description": "Unique identifier for this service (lowercase, underscores)",
      "pattern": "^[a-z_][a-z0-9_]*$"
    },
    "service_name": {
      "type": "string",
      "description": "Human-readable service name"
    },
    "interfaces": {
      "type": "array",
      "items": { "$ref": "#/definitions/interface" }
    },
    ...
  },
  "definitions": {
    "interface": {
      "type": "object",
      "required": ["name", "interface_type", "direction"],
      ...
    }
  }
}
```

**Fix #2: Update Template with Schema Reference**

```json
{
  "$schema": "../schemas/service_architecture_schema.json",
  "template_version": "1.0",
  "service_id": "REPLACE_WITH_SERVICE_ID",
  "service_name": "REPLACE_WITH_SERVICE_NAME",
  ...
}
```

**Fix #3: Add Validation Tool**

Create `tools/validate_service_architecture.py`:

```python
import json
import jsonschema

def validate_architecture_file(file_path: str, schema_path: str):
    """Validate service architecture against JSON schema."""
    with open(file_path) as f:
        data = json.load(f)

    with open(schema_path) as f:
        schema = json.load(f)

    try:
        jsonschema.validate(instance=data, schema=schema)
        print(f"✓ {file_path} is valid")
        return True
    except jsonschema.ValidationError as e:
        print(f"✗ {file_path} is INVALID:")
        print(f"  Error: {e.message}")
        print(f"  Path: {'.'.join(str(p) for p in e.path)}")
        return False
```

**Usage in SE-02**:
```bash
# After generating architecture file:
python3 tools/validate_service_architecture.py \
  specs/machine/service_arch/my_service/service_architecture.json \
  templates/schemas/service_architecture_schema.json
```

---

## Issue #3: Inconsistent Error Messages Across Tools

### Problem Encountered

Different tools report errors in different formats, making it hard for LLM agents to parse and fix:

**Example 1** - `system_of_systems_graph_v2.py`:
```
Warning: Error processing s_01_path_configuration: Missing required field 'service_id' in component data
```

**Example 2** - `validate_architecture.py`:
```
ERROR: Invalid architecture file: /path/to/file.json
  - Missing required field: interfaces
```

**Example 3** - JSON parser:
```
json.decoder.JSONDecodeError: Expecting ',' delimiter: line 917 column 11 (char 56442)
```

### Why This Plagues Workflows

1. **LLM agents can't reliably parse errors** - Each tool uses different format
2. **Difficult to automate fixes** - No structured error output (JSON)
3. **Poor user experience** - Human users also confused by inconsistent messages

### Permanent Fix

**Standardize Error Output Format**

Create `tools/error_reporter.py`:

```python
import json
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ValidationError:
    severity: str  # "ERROR", "WARNING", "INFO"
    tool: str  # Name of tool reporting error
    file_path: str  # File with issue
    error_code: str  # E001, W002, etc.
    message: str  # Human-readable description
    location: Optional[str] = None  # Line number, field path, etc.
    suggestion: Optional[str] = None  # How to fix

    def to_dict(self):
        return {
            "severity": self.severity,
            "tool": self.tool,
            "file": self.file_path,
            "code": self.error_code,
            "message": self.message,
            "location": self.location,
            "suggestion": self.suggestion
        }

class ErrorReporter:
    def __init__(self, tool_name: str):
        self.tool_name = tool_name
        self.errors = []

    def add_error(self, file_path: str, error_code: str, message: str,
                  location: str = None, suggestion: str = None, severity: str = "ERROR"):
        error = ValidationError(
            severity=severity,
            tool=self.tool_name,
            file_path=file_path,
            error_code=error_code,
            message=message,
            location=location,
            suggestion=suggestion
        )
        self.errors.append(error)

    def report_human(self):
        """Human-readable output."""
        for err in self.errors:
            print(f"{err.severity}: {err.message}")
            print(f"  File: {err.file_path}")
            if err.location:
                print(f"  Location: {err.location}")
            if err.suggestion:
                print(f"  Fix: {err.suggestion}")

    def report_json(self):
        """Machine-readable output."""
        return json.dumps({
            "tool": self.tool_name,
            "total_errors": len([e for e in self.errors if e.severity == "ERROR"]),
            "total_warnings": len([e for e in self.errors if e.severity == "WARNING"]),
            "errors": [e.to_dict() for e in self.errors]
        }, indent=2)
```

**Usage**:
```python
# In system_of_systems_graph_v2.py:
reporter = ErrorReporter("system_of_systems_graph_v2")

reporter.add_error(
    file_path=file_path,
    error_code="E001",
    message="Missing required field 'service_id'",
    location="top level (expected service_id at root, not nested in metadata)",
    suggestion="Add 'service_id' field at top level of JSON file, or move from metadata.service_id to top level"
)

# Output both formats:
reporter.report_human()  # For humans reading terminal

# And save JSON for LLM agents:
with open("validation_errors.json", "w") as f:
    f.write(reporter.report_json())
```

---

## Issue #4: Working Memory Path Resolution

### Problem Encountered

Tools need to find `working_memory.json` but it's not always in a predictable location:

```
Possible locations:
  /home/user/my_system/context/working_memory.json  ← Standard
  /home/user/reflow/context/working_memory.json     ← When analyzing reflow itself
  ../context/working_memory.json                     ← Relative to current dir
```

### Why This Plagues Workflows

1. **Tools make assumptions** - "context/ is always in system_root"
2. **Fails when analyzing reflow** - Meta-analysis breaks assumptions
3. **No fallback logic** - Tool can't find file, crashes instead of degrading gracefully

### Permanent Fix

Create `tools/path_resolver.py`:

```python
from pathlib import Path
from typing import Optional
import json

class PathResolver:
    """Resolve paths to common workflow artifacts with fallback logic."""

    def __init__(self, starting_path: Path = None):
        self.starting_path = starting_path or Path.cwd()

    def find_working_memory(self) -> Optional[Path]:
        """Find working_memory.json using multiple strategies."""
        search_paths = [
            # Strategy 1: Explicit environment variable
            Path(os.environ.get('REFLOW_SYSTEM_ROOT', '')) / 'context' / 'working_memory.json',

            # Strategy 2: Relative to current directory
            self.starting_path / 'context' / 'working_memory.json',

            # Strategy 3: Walk up directory tree
            *[p / 'context' / 'working_memory.json' for p in self.starting_path.parents],

            # Strategy 4: Common locations
            Path.home() / 'reflow' / 'context' / 'working_memory.json',
            Path('/home/user/reflow/context/working_memory.json'),
        ]

        for path in search_paths:
            if path.exists():
                return path.resolve()

        return None

    def get_system_root(self) -> Path:
        """Get system_root from working_memory.json or infer from directory structure."""
        wm_path = self.find_working_memory()

        if wm_path:
            with open(wm_path) as f:
                data = json.load(f)
            return Path(data['path_configuration']['system_root'])

        # Fallback: Assume current directory is system root
        return self.starting_path.resolve()

    def get_reflow_root(self) -> Path:
        """Get reflow_root from working_memory.json or infer from tool location."""
        wm_path = self.find_working_memory()

        if wm_path:
            with open(wm_path) as f:
                data = json.load(f)
            return Path(data['path_configuration']['reflow_root'])

        # Fallback: Assume this tool is in reflow/tools/
        return Path(__file__).parent.parent.resolve()

# Usage in tools:
resolver = PathResolver()
system_root = resolver.get_system_root()
reflow_root = resolver.get_reflow_root()
```

---

## Issue #5: No Pre-Flight Validation

### Problem Encountered

LLM agents run workflow steps and only discover errors when tools fail:

```
SE-02: Create architecture files ✓
SE-03: Validate templates ✓
SE-04: ...more work... ✓
SE-05: ...more work... ✓
SE-06: Generate graph ✗ FAILS - architecture files invalid!
  ↑ Agent wasted 30 minutes, now has to backtrack
```

### Why This Plagues Workflows

1. **Late error detection** - Errors discovered steps after they're introduced
2. **Wasted work** - Agent continues working with invalid artifacts
3. **Context drift** - By SE-06, agent may have forgotten details from SE-02

### Permanent Fix

**Create Pre-Flight Validation Tool**

Create `tools/preflight_check.py`:

```python
def preflight_check_se06():
    """Pre-flight checks before SE-06 (graph generation)."""
    print("Running pre-flight checks for SE-06 (System Graph Generation)...")

    checks = [
        check_index_exists(),
        check_architecture_files_exist(),
        check_architecture_files_valid_json(),
        check_architecture_files_have_service_id(),
        check_working_memory_paths_valid(),
    ]

    if all(checks):
        print("✓ All pre-flight checks passed")
        return True
    else:
        print("✗ Pre-flight checks failed - fix issues before proceeding")
        return False

def check_architecture_files_have_service_id():
    """Verify all architecture files have service_id at TOP LEVEL."""
    print("Checking: Architecture files have service_id at top level...")

    for arch_file in Path("specs/machine/service_arch").glob("*/service_architecture*.json"):
        with open(arch_file) as f:
            data = json.load(f)

        if 'service_id' not in data:  # TOP LEVEL check
            print(f"  ✗ {arch_file.name}: Missing top-level 'service_id'")
            if 'metadata' in data and 'service_id' in data['metadata']:
                print(f"    Found service_id in metadata - move to top level!")
            return False

    print("  ✓ All architecture files have top-level service_id")
    return True

# Usage in workflow:
if __name__ == "__main__":
    import sys
    step = sys.argv[1] if len(sys.argv) > 1 else "unknown"

    if step == "SE-06":
        if not preflight_check_se06():
            sys.exit(1)
```

**Integrate into SE-06**:
```bash
# SE-06-A01: Pre-flight check
python3 tools/preflight_check.py SE-06 || exit 1

# SE-06-A02: Generate graph (only runs if pre-flight passed)
python3 tools/system_of_systems_graph_v2.py specs/machine/index.json
```

---

## Summary of Permanent Fixes

| Issue | Root Cause | Permanent Fix | Priority |
|-------|-----------|---------------|----------|
| **Path resolution inconsistency** | Tool derives system_root ambiguously | Add `--system-root` arg + read from working_memory.json | 🔴 **CRITICAL** |
| **Template/tool schema mismatch** | No JSON schema, agents guess structure | Add JSON schema files + validation tool | 🔴 **CRITICAL** |
| **Inconsistent error messages** | Each tool uses own format | Standardize error reporting (JSON + human) | 🟡 **HIGH** |
| **Working memory path issues** | Hard-coded assumptions about location | Create PathResolver with fallback logic | 🟡 **HIGH** |
| **Late error detection** | No pre-flight checks | Add preflight validation before critical steps | 🟢 **MEDIUM** |

---

## Implementation Plan

### Phase 1: Critical Fixes (Week 1)

1. **Add JSON schemas** for all template files
   - `service_architecture_schema.json`
   - `index_schema.json`
   - `working_memory_schema.json`

2. **Update system_of_systems_graph_v2.py**
   - Add `--system-root` argument
   - Read from working_memory.json if no arg provided
   - Improve error messages with location details

3. **Create validate_service_architecture.py**
   - Validate against JSON schema
   - Check top-level service_id field
   - Run in SE-03 validation gate

### Phase 2: Standardization (Week 2)

4. **Create ErrorReporter class**
   - Standardize error format across all tools
   - Add to existing tools incrementally

5. **Create PathResolver class**
   - Handle working_memory.json location
   - Use in all tools that need system_root/reflow_root

6. **Update all templates**
   - Add `$schema` reference
   - Include examples of valid vs invalid
   - Document common mistakes

### Phase 3: Pre-Flight Validation (Week 3)

7. **Create preflight_check.py**
   - Pre-flight checks for SE-06, AV-01, D-01, TO-02
   - Integrate into workflow steps
   - Add to quality gates

8. **Add to CI/CD**
   - Validate all JSON files in repo
   - Check schemas on template changes
   - Run preflight checks in test suite

---

## Testing Strategy

### Test Cases

1. **Meta-analysis test**: Run Reflow on itself (what we just did)
   - Should complete without path errors
   - Should validate all generated files
   - Should detect intentional errors

2. **Multi-framework test**: Create system using each framework
   - UAF, Systems Biology, Social Network, Ecological, CAS
   - Verify tools work with all frameworks

3. **Error injection test**: Introduce known errors
   - Missing service_id
   - Invalid JSON syntax
   - Wrong path formats
   - Verify error messages helpful

4. **Path resolution test**: Test various directory structures
   - System in subdirectory
   - System in parent directory
   - Reflow and system in same directory
   - Verify all scenarios work

---

## Success Metrics

After implementing fixes, these should be true:

1. ✅ **Zero path resolution errors** in normal workflows
2. ✅ **Zero template/tool mismatches** - schemas prevent this
3. ✅ **Errors caught in SE-03** (validation), not SE-06 (graph generation)
4. ✅ **Error messages include fix suggestions** - LLM agents self-correct
5. ✅ **Meta-analysis completes successfully** - Reflow can fully analyze itself

---

**Next Steps**: Implement Phase 1 fixes (JSON schemas + path resolution), then re-run meta-analysis to verify fixes work.
