# Process Improvement: Component Specification Format Alignment

**Date:** 2025-10-18  
**System:** dnd_reflow  
**Category:** Generic Process Improvement

## Issue

The `verify_component_contract.py` tool expects component specifications with this schema:
- `interfaces_provided` - Array of provided interfaces with `interface_id` and `contract_reference`
- `interfaces_consumed` - Array of consumed interfaces with `interface_id`
- `maturity_level` - Integer indicating development maturity (1-5)
- `functional_requirements` - Array of testable requirements

However, current component specifications in `specs/component_specs/<service>/component_specification.json` contain:
- `component_id` - Component identifier
- `contracts` - Array of ICD file paths (not interface objects)
- `provided_endpoints` - Array of HTTP endpoint definitions
- No maturity_level or functional_requirements

## Current State

✅ **Directory structure aligned** - specs/machine/ exists with portable relative paths
✅ **Service architecture files exist** - specs/machine/service_arch/ contains service_architecture.json with proper schema
✅ **Component specs exist** - specs/component_specs/ directories created for all services
❌ **Component spec schema mismatch** - Current format doesn't match tool expectations

## Recommendation

**Type:** Generic process improvement (consider for future implementation)

### Option 1: Update Tool
Modify `verify_component_contract.py` to accept current component_specification.json format and map:
- `provided_endpoints` → `interfaces_provided`
- `contracts` paths → Load ICD files to populate interface metadata
- Auto-detect maturity from implementation code analysis

### Option 2: Update Component Specs
Regenerate component_specification.json files from service_architecture.json to match tool schema:
- Extract provided interfaces from service_architecture.json
- Build proper interface objects with metadata
- Add maturity_level based on implementation completeness
- Add testable functional requirements from ICD files

### Option 3: Use Service Architecture Directly
Use `specs/machine/service_arch/*/service_architecture.json` directly with verification tool:
- These files have the correct schema with all required information
- Tool can be updated to accept this primary source
- Reduces duplication and maintenance burden

## Current Impact

- D06 CONTRACT_VERIFICATION phase can proceed using existing test suites
- Service architectures already have complete specifications
- 18+ integration tests passing (character, coordinator, llm services)
- Quality gates assessable through existing test results

## Implementation Priority

**Consider later** - Current system can progress without this alignment
- Development is proceeding successfully without component spec tool
- Real contract verification happening through integration tests
- Generic process improvement doesn't block system development

## Files Involved

- `/home/ajs7/project/reflow/tools/verify_component_contract.py`
- `/home/ajs7/project/reflow/systems/dnd_reflow/specs/component_specs/*/component_specification.json`
- `/home/ajs7/project/reflow/systems/dnd_reflow/specs/machine/service_arch/*/service_architecture.json`
