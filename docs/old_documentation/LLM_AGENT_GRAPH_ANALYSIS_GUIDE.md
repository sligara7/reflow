# LLM Agent Guide: System-of-Systems Graph Analysis

## Overview
The `system_of_systems_graph.py` tool creates a machine-readable JSON representation of your system architecture that LLM agents can analyze to detect and fix architectural issues automatically.

## How It Works

### 1. Graph Generation
```bash
python3 ./tools/system_of_systems_graph.py systems/<system_name>/index.json --analyze-issues
```

This creates two JSON files:
- **`system_of_systems_graph.json`** - NetworkX graph structure
- **`architecture_issues.json`** - Detected problems with fix guidance

### 2. Graph JSON Structure
```json
{
  "directed": true,
  "nodes": [
    {
      "id": "auth_service",
      "label": "Authentication Service",
      "level": "service", 
      "raw": { /* Complete service_architecture.json data */ }
    }
  ],
  "links": [
    {
      "source": "web_frontend",
      "target": "auth_service",
      "type": "dependency"
    }
  ],
  "metadata": {
    "node_count": 5,
    "edge_count": 8,
    "usage_instructions": [/* How to analyze this data */]
  }
}
```

### 3. Issues JSON Structure
```json
{
  "summary": {
    "critical_issues": 2,
    "warning_issues": 1,
    "action_required": true
  },
  "architectural_issues": {
    "circular_dependencies": [
      {
        "cycle": ["service_a", "service_b", "service_a"],
        "severity": "critical",
        "recommendation": "Consider introducing async communication"
      }
    ],
    "orphaned_nodes": [...],
    "performance_bottlenecks": [...],
    "security_gaps": [...],
    "inconsistent_protocols": [...]
  },
  "llm_agent_instructions": {
    "fix_workflow": [/* Step-by-step fix process */],
    "common_fixes": {/* Specific solutions by issue type */}
  }
}
```

## LLM Agent Workflow

### Step 1: Parse and Prioritize Issues
```python
# LLM agent should:
1. Load architecture_issues.json
2. Check if summary.action_required == true
3. Address issues in priority order: critical → warning → medium → info
4. For each issue, read the specific recommendation
```

### Step 2: Analyze System Topology
```python
# LLM agent should:
1. Load system_of_systems_graph.json
2. Understand the nodes (services) and their relationships
3. Cross-reference with raw service data in nodes[].raw
4. Identify missing connections or problematic patterns
```

### Step 3: Apply Specific Fixes

#### Critical Issues (Fix Immediately)
- **Circular Dependencies**: Break cycles by introducing async communication or refactoring service boundaries
- **Security Gaps**: Add authentication/authorization interfaces for exposed services

#### Warning Issues (Fix Before Deployment)  
- **Orphaned Nodes**: Remove unused services or add missing connections
- **Performance Bottlenecks**: Split services with too many connections

#### Medium/Info Issues (Quality Improvements)
- **Inconsistent Protocols**: Standardize communication patterns
- **Missing Documentation**: Add interface descriptions

### Step 4: Update Architecture Files
```python
# LLM agent should:
1. Modify service_architecture.json files to resolve issues
2. Add/remove interfaces as needed
3. Update dependencies sections
4. Ensure all changes maintain UAF 1.2 compliance
```

### Step 5: Verify Fixes
```bash
# Re-run analysis to confirm issues are resolved
python3 ./tools/system_of_systems_graph.py systems/<system_name>/index.json --analyze-issues
```

## Common Issue Types & Fixes

### 🔴 Circular Dependencies
**Problem**: Services depend on each other in cycles
**LLM Fix**: 
- Introduce async messaging between services
- Use event-driven architecture
- Refactor service boundaries to remove circular logic

### 🟡 Orphaned Nodes  
**Problem**: Services with no connections
**LLM Fix**:
- Remove service if not needed
- Add missing interface definitions
- Connect to appropriate system components

### 🟡 Performance Bottlenecks
**Problem**: Services with excessive connections
**LLM Fix**:
- Split service into smaller components  
- Add load balancing or caching layers
- Reduce direct dependencies

### 🟠 Security Gaps
**Problem**: Services missing authentication
**LLM Fix**:
- Add auth_required: true to interface definitions
- Create authentication service interfaces
- Implement authorization checks

### 🔵 Inconsistent Protocols
**Problem**: Too many communication patterns
**LLM Fix**:
- Standardize on REST APIs for synchronous communication
- Use message queues for async communication
- Document protocol choices in interface contracts

## Success Criteria for LLM Agents

### ✅ Healthy Architecture
- Zero critical issues
- Zero warning issues  
- All services connected appropriately
- Clear communication patterns

### ✅ Validation Commands
```bash
# Should show "healthy" status
python3 ./tools/system_of_systems_graph.py systems/<system_name>/index.json --analyze-issues

# Should pass without critical issues  
python3 ./tools/validate_architecture.py systems/<system_name>
```

## Integration with Decision Flow

The decision flow automatically uses this tool in quality gates:
- **Architecture Phase**: Validates system decomposition
- **Interface Design**: Checks interface completeness  
- **Quality Gates**: Ensures no critical issues before proceeding

LLM agents should treat critical issues as **blocking** - the workflow cannot proceed until they're resolved.

## Example LLM Agent Response

```
Analyzing system architecture...

🔍 Found 3 issues in architecture_issues.json:
- 1 critical: Circular dependency between auth_service ↔ user_service  
- 2 warnings: payment_service is orphaned, api_gateway has 8+ connections

🔧 Applying fixes:
1. Breaking circular dependency by introducing async user.events queue
2. Connecting payment_service to order_service via REST interface
3. Splitting api_gateway into api_gateway + request_router services

✅ Re-running validation... All critical issues resolved!
```

This workflow ensures LLM agents can automatically detect and resolve architectural problems using the structured JSON analysis output.