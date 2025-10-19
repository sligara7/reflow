# LLM Agent Guide: Architecture Validation Tool

## Overview
The `validate_architecture.py` tool validates service_architecture.json files for template compliance and architectural consistency, providing structured JSON output for automated LLM analysis and fixing.

## How It Works

### 1. Validation Execution
```bash
python3 ./tools/validate_architecture.py systems/<system_name>
```

This validates all service_architecture.json files and outputs structured JSON results with:
- **Check results** by category (interface_consistency, resource_isolation, dependency_cycles)
- **Detailed issues** with descriptions and fix recommendations
- **LLM agent instructions** for automated resolution

### 2. Output JSON Structure
```json
{
  "timestamp": "2025-10-14T...",
  "system": "my_system",
  "checks": {
    "interface_consistency": {
      "status": "fail",
      "issues": [...]
    },
    "resource_isolation": {
      "status": "pass", 
      "issues": []
    },
    "dependency_cycles": {
      "status": "fail",
      "issues": [...]
    }
  },
  "issues": [
    {
      "type": "interface_mismatch",
      "service": "auth_service",
      "interface": "login",
      "field": "auth_required",
      "severity": "high",
      "description": "Interface 'login' field 'auth_required' mismatch...",
      "recommendation": "Update auth_required for interface 'login'...",
      "service_value": true,
      "registry_value": false
    }
  ],
  "llm_agent_instructions": {
    "total_issues": 3,
    "critical_issues": 2,
    "action_required": true,
    "fix_workflow": [...],
    "common_fixes": {...}
  }
}
```

## LLM Agent Workflow

### Step 1: Parse Validation Results
```python
# LLM agent should:
1. Load validation results JSON
2. Check if llm_agent_instructions.action_required == true
3. Identify critical (high severity) issues that must be fixed first
4. Review specific issues with descriptions and recommendations
```

### Step 2: Categorize Issues by Type
- **interface_missing**: Service declares interface not in interface_registry.json
- **interface_mismatch**: Service interface definition doesn't match registry
- **circular_dependency**: Services have cyclic dependencies
- **shared_resource**: Multiple services access same resources
- **missing_architecture**: Service directories lack service_architecture.json

### Step 3: Apply Systematic Fixes

#### High Severity Issues (Fix Immediately)
These prevent proper system operation:

##### Interface Missing
```json
{
  "type": "interface_missing",
  "service": "auth_service", 
  "interface": "login",
  "recommendation": "Add interface 'login' to interface_registry.json for service 'auth_service'"
}
```
**LLM Fix**: Add the missing interface definition to interface_registry.json

##### Interface Mismatch  
```json
{
  "type": "interface_mismatch",
  "service": "auth_service",
  "interface": "login", 
  "field": "auth_required",
  "service_value": true,
  "registry_value": false,
  "recommendation": "Update auth_required for interface 'login'..."
}
```
**LLM Fix**: Align the field values between service_architecture.json and interface_registry.json

##### Circular Dependency
```json
{
  "type": "circular_dependency",
  "cycle": ["auth_service", "user_service", "auth_service"],
  "recommendation": "Break dependency cycle by introducing async communication..."
}
```
**LLM Fix**: Refactor service boundaries or introduce async messaging

#### Medium Severity Issues (Fix Before Deployment)

##### Shared Resource
```json
{
  "type": "shared_resource",
  "resource": "user_database",
  "performer": "mysql_server",
  "recommendation": "Implement resource isolation by dedicating resources..."
}
```
**LLM Fix**: Implement proper resource isolation patterns

##### Missing Architecture
```json
{
  "type": "missing_architecture",
  "path": "/path/to/service_dir",
  "recommendation": "Create service_architecture.json file using template"
}
```
**LLM Fix**: Create missing service_architecture.json file using service template

### Step 4: Update Architecture Files

#### Fix Interface Issues
```python
# LLM agent should:
1. Load interface_registry.json
2. Add missing interface definitions
3. Align mismatched field values
4. Save updated interface_registry.json
```

#### Fix Service Files
```python
# LLM agent should:
1. Load service_architecture.json files
2. Update interface definitions to match registry
3. Remove circular dependencies by refactoring
4. Ensure proper resource isolation
5. Save updated service files
```

#### Create Missing Files
```python
# LLM agent should:
1. Identify directories with missing service_architecture.json
2. Use service_architecture_template.json as base
3. Populate with appropriate service details
4. Save new service_architecture.json files
```

### Step 5: Verify Fixes
```bash
# Re-run validation to confirm all issues resolved
python3 ./tools/validate_architecture.py systems/<system_name>
```

## Integration with Decision Flow

The validation tool is used in multiple quality gates:
- **Architecture Phase**: Validates template compliance 
- **Interface Design**: Checks interface consistency
- **Quality Gates**: Ensures no critical validation failures

LLM agents should treat high severity issues as **blocking** - the workflow cannot proceed until they're resolved.

## Common Fix Patterns

### Interface Registry Updates
```json
// Add missing interface to interface_registry.json
{
  "interfaces": {
    "auth_service": {
      "login": {
        "path": "/api/v1/login",
        "method": "POST", 
        "auth_required": false,
        "input_schema": {...},
        "output_schema": {...}
      }
    }
  }
}
```

### Service Architecture Updates
```json
// Update service_architecture.json to match registry
{
  "service_name": "Authentication Service",
  "interfaces": [
    {
      "name": "login",
      "path": "/api/v1/login",
      "method": "POST",
      "auth_required": false  // Match registry value
    }
  ]
}
```

### Dependency Refactoring
```json
// Break circular dependency using async communication
{
  "dependencies": [
    "user_events_queue"  // Instead of direct "user_service" 
  ],
  "async_interfaces": [
    {
      "name": "user_created_event",
      "type": "event_consumer"
    }
  ]
}
```

## Success Criteria for LLM Agents

### ✅ Healthy Validation
- All checks show "status": "pass"
- Zero high severity issues
- All services have proper interface definitions
- No circular dependencies

### ✅ Validation Commands
```bash
# Should exit with code 0 and show "VALIDATION PASSED"
python3 ./tools/validate_architecture.py systems/<system_name>

# Should show healthy architecture
python3 ./tools/system_of_systems_graph.py systems/<system_name>/index.json --analyze-issues
```

## Example LLM Agent Response

```
Validating architecture files...

🔍 Found 4 validation issues:
- 2 high severity: interface_mismatch in auth_service.login, circular_dependency auth_service ↔ user_service
- 2 medium severity: shared_resource user_database, missing_architecture in payment_service

🔧 Applying fixes:
1. Updating auth_service interface 'login' auth_required: false → true to match registry
2. Breaking circular dependency by introducing user_events_queue for async communication  
3. Creating dedicated payment_database resource for payment_service
4. Creating service_architecture.json for payment_service using template

✅ Re-running validation... All checks now pass!
```

This structured approach ensures LLM agents can automatically detect and resolve architectural validation problems using the comprehensive JSON analysis output.