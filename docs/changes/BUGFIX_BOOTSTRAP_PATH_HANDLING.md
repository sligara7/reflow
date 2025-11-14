# Bugfix: Bootstrap Tool Path Handling (v3.14.2)

**Date**: 2025-11-13
**Issue**: `bootstrap_development_context.py` fails with path duplication when passed absolute path
**Fix**: Auto-detect when system_name argument is a path vs simple name

## Problem Statement

User reported:
```bash
python3 /home/ajs7/project/reflow/tools/bootstrap_development_context.py /home/ajs7/project/xrpl4 2>&1

❌ Error: Parent directory /home/ajs7/project/xrpl4/systems/home/ajs7/project does not exist
```

### Root Cause

**Line 262** (original code):
```python
if args.system_path is None:
    # Default to systems/<system_name> relative to current directory
    args.system_path = f"systems/{args.system_name}"
```

When user passed `/home/ajs7/project/xrpl4` as `system_name`:
1. Script set `args.system_path = "systems//home/ajs7/project/xrpl4"`
2. This resolved from cwd to `/home/ajs7/project/xrpl4/systems/home/ajs7/project/xrpl4`
3. Parent directory check failed → error

**Why This Happened**:
- Tool expected `system_name` to be a simple name like `"xrpl4"`
- But users naturally pass full paths like `/home/ajs7/project/xrpl4`
- No logic to detect when argument is path vs name

## Solution

Enhanced argument handling to **auto-detect** path vs name (lines 260-270):

```python
# Determine system path and name
# If system_name looks like a path (contains / or is absolute), use it as the path
if args.system_path is None:
    if "/" in args.system_name or Path(args.system_name).is_absolute():
        # system_name is actually a path
        args.system_path = args.system_name
        # Extract actual system name from path
        args.system_name = Path(args.system_name).name
    else:
        # system_name is just a name, create default path
        args.system_path = f"systems/{args.system_name}"
```

### Behavior Changes

| Input | Old Behavior | New Behavior |
|-------|--------------|--------------|
| `xrpl4` | `system_path = "systems/xrpl4"` | ✅ Same (backward compatible) |
| `/home/ajs7/project/xrpl4` | ❌ Path duplication error | ✅ `system_path = "/home/ajs7/project/xrpl4"`, `name = "xrpl4"` |
| `../myproject` | ❌ Path duplication error | ✅ `system_path = "../myproject"`, `name = "myproject"` |
| `./systems/foo` | ❌ Path duplication error | ✅ `system_path = "./systems/foo"`, `name = "foo"` |

### Updated Help Text

```
positional arguments:
  system_name           Name of the system being developed, or path to system
                        directory

options:
  --system-path SYSTEM_PATH
                        Path to system directory (default:
                        systems/<system_name>, or uses system_name if it's a
                        path)
```

## Validation

Tested with Python logic simulation:
```python
test_path_handling('/home/ajs7/project/xrpl4')
  → system_name: xrpl4
  → system_path: /home/ajs7/project/xrpl4  ✅

test_path_handling('xrpl4')
  → system_name: xrpl4
  → system_path: systems/xrpl4  ✅

test_path_handling('../myproject')
  → system_name: myproject
  → system_path: ../myproject  ✅
```

## Impact

### Before Fix
Users had to know the exact calling convention:
```bash
# ❌ Natural usage - FAILS
python3 bootstrap_development_context.py /home/ajs7/project/xrpl4

# ✅ Required usage - WORKS but unintuitive
python3 bootstrap_development_context.py xrpl4 --system-path /home/ajs7/project/xrpl4
```

### After Fix
Natural usage now works:
```bash
# ✅ Natural usage - NOW WORKS
python3 bootstrap_development_context.py /home/ajs7/project/xrpl4

# ✅ Original usage - STILL WORKS (backward compatible)
python3 bootstrap_development_context.py xrpl4

# ✅ Explicit usage - STILL WORKS
python3 bootstrap_development_context.py xrpl4 --system-path /home/ajs7/project/xrpl4
```

## Backward Compatibility

✅ **100% backward compatible**
- Existing calls with simple names (`xrpl4`) work identically
- Explicit `--system-path` usage unchanged
- Only adds new behavior for path-like arguments

## Files Changed

- `tools/bootstrap_development_context.py` (lines 252-270)

## Related Issues

This is a common UX pattern issue with CLI tools:
- Users expect to pass paths directly
- Tools often expect names + optional path flags
- Solution: Auto-detect and handle both cases

## Version

- **Reflow Version**: v3.14.2 (unreleased)
- **Compatible With**: All versions (backward compatible)
- **Bug Introduced**: Unknown (likely v3.4.0 when path security was added)

## Prevention

For future CLI tools in Reflow:
1. **Detect path vs name** for arguments that could be either
2. **Test with absolute paths** in addition to simple names
3. **Document both usage patterns** in help text
4. **Use `Path.name` extraction** when path given but name needed
