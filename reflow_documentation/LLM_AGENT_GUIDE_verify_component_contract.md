# LLM Agent Guide: verify_component_contract.py

## Tool Purpose
Verify component implementations satisfy interface contracts to provide **integration guarantee**. When verification passes, following the contracts ensures successful integration.

## When to Use This Tool
- **Dev-04-IntegrationAndSecurity**: Before integrating components
- **Quality Gate**: CONTRACT_VERIFICATION in development pipeline  
- **Pre-Integration**: Catch contract violations before integration testing
- **Release Validation**: Ensure components meet contract obligations

## Command Format
```bash
python verify_component_contract.py <component_spec_file> [--verbose]
```

## Expected JSON Output Structure
```json
{
  "component_id": "user-service-v1.2",
  "verification_status": "passed|warning|failed",
  "compliance_score": 0.95,
  "contract_coverage": 0.92,
  "issues_found": [...],
  "verification_details": {...},
  "integration_guarantee": "guaranteed|conditional|blocked",
  "llm_agent_instructions": {
    "next_actions": [...],
    "fix_guidance": {...},
    "integration_status": "..."
  }
}
```

## LLM Agent Workflow

### 1. Analyze Verification Status
```
IF verification_status == "passed":
  - Component ready for integration
  - Integration guarantee provided
  - Proceed with integration testing
  
ELIF verification_status == "warning":
  - Review warnings in issues_found
  - Assess risk vs. integration timeline
  - Consider conditional integration
  
ELSE verification_status == "failed":
  - Integration blocked until fixes
  - Follow fix_guidance for each issue
  - Re-run verification after fixes
```

### 2. Parse Issues Found
```python
for issue in results['issues_found']:
  severity = issue['severity']  # critical, major, minor
  category = issue['category']  # interface_mismatch, protocol_violation, etc.
  
  if severity == "critical":
    # Block integration - must fix
    # Use issue['fix_suggestions'] for resolution
  elif severity == "major":
    # Strong recommendation to fix
    # May proceed with risk assessment
  else:
    # Minor issue - document and track
```

### 3. Integration Decision Logic
```
integration_guarantee = results['integration_guarantee']

IF integration_guarantee == "guaranteed":
  - Proceed with integration
  - Contract compliance verified
  - Success probability: High
  
ELIF integration_guarantee == "conditional":
  - Review conditions in verification_details
  - Mitigate identified risks
  - Monitor integration closely
  
ELSE integration_guarantee == "blocked":
  - Do not proceed with integration
  - Fix critical contract violations
  - Re-verify before integration
```

### 4. Follow Next Actions
```python
next_actions = results['llm_agent_instructions']['next_actions']

for action in next_actions:
  if "fix contract violation" in action:
    # Address specific contract issue
    # Update component implementation
    
  elif "update interface" in action:
    # Coordinate interface contract changes
    # Notify dependent components
    
  elif "re-verify" in action:
    # Run verification again after fixes
    # Confirm integration readiness
```

## Integration Guarantee Framework

### Guarantee Levels
- **Guaranteed**: Component fully satisfies contracts, integration will succeed
- **Conditional**: Component mostly compliant, integration possible with risk mitigation
- **Blocked**: Critical violations present, integration will fail

### Contract Verification Checklist
1. **Interface Compliance**: All required interfaces implemented
2. **Protocol Adherence**: Communication protocols followed correctly
3. **Data Contract**: Input/output formats match specifications
4. **Error Handling**: Proper error responses and recovery
5. **Security Requirements**: Authentication/authorization implemented
6. **Performance Constraints**: Meets SLA requirements

## Quality Gate Integration

### In Development Pipeline
```json
{
  "quality_gate": "CONTRACT_VERIFICATION",
  "tool": "verify_component_contract.py",
  "criteria": {
    "verification_status": "passed",
    "compliance_score": ">= 0.90",
    "critical_issues": "== 0"
  },
  "failure_action": "block_integration"
}
```

### Automated Decision Making
```python
def should_proceed_with_integration(results):
    if results['verification_status'] == 'failed':
        return False
    
    if results['compliance_score'] < 0.85:
        return False
    
    critical_issues = [i for i in results['issues_found'] 
                      if i['severity'] == 'critical']
    if critical_issues:
        return False
    
    return True
```

## Common Issue Patterns

### Interface Mismatches
- **Problem**: Component interface doesn't match contract
- **Detection**: `interface_mismatch` category in issues
- **Fix**: Update component to implement required interface methods

### Protocol Violations  
- **Problem**: Communication protocol not followed
- **Detection**: `protocol_violation` category in issues
- **Fix**: Correct message formats, headers, status codes

### Data Contract Violations
- **Problem**: Input/output data doesn't match schema
- **Detection**: `data_contract_violation` category in issues  
- **Fix**: Validate and correct data serialization/deserialization

### Missing Error Handling
- **Problem**: Component doesn't handle errors per contract
- **Detection**: `error_handling` category in issues
- **Fix**: Implement proper error responses and recovery

## Best Practices for LLM Agents

1. **Always verify before integration** - Run this tool before any component integration
2. **Parse structured output** - Use JSON output for automated decision making
3. **Follow fix guidance** - Use specific recommendations in issues_found
4. **Re-verify after fixes** - Confirm resolution before proceeding
5. **Document decisions** - Record verification results and integration decisions
6. **Monitor compliance trends** - Track compliance scores over time

## Success Metrics
- **Compliance Score**: > 90% for production integration
- **Critical Issues**: 0 for guaranteed integration
- **Contract Coverage**: > 85% for adequate verification
- **Integration Success Rate**: Track actual vs. predicted integration success

## Error Recovery
- If verification fails, use `fix_guidance` in results
- Address issues by severity (critical first)
- Re-run verification after each fix iteration
- Consider interface contract updates if patterns emerge

This tool provides the crucial **integration guarantee** that enables confident component integration in complex distributed systems.