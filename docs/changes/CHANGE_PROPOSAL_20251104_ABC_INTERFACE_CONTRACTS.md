# Change Proposal: ABC Interface Contracts

**Date**: 2025-11-04
**Proposal ID**: CP-2025-11-04-001
**Feature**: Language-Specific Interface Contracts (Python ABC, TypeScript, Rust, C++)
**Priority**: High
**Workflow Version**: 3.9.1 → 3.10.0

## Executive Summary

Add automatic generation of **strongly-typed interface contracts** using language-specific constructs (Python ABC abstract classes, TypeScript interfaces, Rust traits, C++ abstract classes) during the development workflow. This provides compile-time/runtime interface enforcement between services, complementing the existing JSON-based Interface Contract Documents (ICDs).

## Business Justification

### Current Gap

Reflow generates comprehensive **JSON-based ICDs** (`generate_interface_contracts.py`) during SE phase, but these are documentation-only. Developers must manually:
1. Read JSON ICDs
2. Implement interfaces in their chosen language
3. Hope they got it right (no compile-time validation)
4. Discover interface mismatches at integration testing (expensive to fix)

### Proposed Solution

**Automatically generate language-native interface contracts** from the existing `system_of_systems_graph.json` during development phase (D-01):
- **Python**: ABC (Abstract Base Classes) from `abc` module
- **TypeScript**: Interface declarations
- **Rust**: Trait definitions
- **C++**: Abstract base classes with pure virtual functions
- **Java**: Interface declarations
- **Go**: Interface types

These provide:
- ✅ **Compile-time validation** (TypeScript, Rust, C++, Java)
- ✅ **Runtime validation** (Python ABC with `@abstractmethod`)
- ✅ **IDE autocomplete** (all languages)
- ✅ **Type safety** (prevents interface drift)
- ✅ **Early error detection** (at development time, not integration time)

### Impact

**Time Savings**: 3-5 days per service
- Catch interface mismatches at compile/import time (minutes) vs integration testing (days)
- Reduce integration debugging from days to hours
- Prevent "works on my machine" interface drift

**Quality Improvement**:
- Contract compliance guaranteed by language runtime/compiler
- Interface changes force updates to all consumers (fail-fast)
- Eliminate entire class of integration bugs

## Feature Description

### New Tool: `generate_interface_abc.py`

**Purpose**: Generate language-native interface contracts from `system_of_systems_graph.json`

**Inputs**:
- `specs/machine/graphs/system_of_systems_graph.json` (edges = interfaces)
- `specs/machine/development_language_configuration.json` (language per service)
- `specs/machine/interfaces/{interface}_icd.json` (detailed interface specs)

**Outputs** (per interface):
```
services/{consumer_service}/interfaces/
  ├── {provider_service}_interface.py         (Python ABC)
  ├── {provider_service}_interface.ts         (TypeScript interface)
  ├── {provider_service}_interface.rs         (Rust trait)
  ├── {provider_service}_interface.hpp        (C++ abstract class)
  └── {provider_service}_interface.java       (Java interface)
```

**Example Output (Python ABC)**:
```python
# services/recommendation_service/interfaces/user_service_interface.py
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime

class UserServiceInterface(ABC):
    """
    Interface contract for User Service
    Provider: user_service
    Consumer: recommendation_service
    Generated from: system_of_systems_graph.json
    """

    @abstractmethod
    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Get user profile by ID

        Args:
            user_id: Unique user identifier (required)

        Returns:
            Dict with keys: user_id, name, email, preferences

        Raises:
            UserNotFoundException: If user_id not found
            AuthenticationError: If authentication fails
        """
        pass

    @abstractmethod
    def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """
        Update user preferences

        Args:
            user_id: Unique user identifier (required)
            preferences: Dictionary of preference key-value pairs

        Returns:
            True if update successful, False otherwise

        Raises:
            ValidationError: If preferences schema invalid
        """
        pass
```

**Example Output (TypeScript)**:
```typescript
// services/recommendation_service/interfaces/UserServiceInterface.ts
export interface UserServiceInterface {
  /**
   * Get user profile by ID
   * @param userId - Unique user identifier
   * @returns Promise resolving to user profile object
   * @throws UserNotFoundException if user_id not found
   */
  getUserProfile(userId: string): Promise<UserProfile>;

  /**
   * Update user preferences
   * @param userId - Unique user identifier
   * @param preferences - Preference key-value pairs
   * @returns Promise resolving to boolean success indicator
   */
  updateUserPreferences(userId: string, preferences: Record<string, any>): Promise<boolean>;
}

export interface UserProfile {
  userId: string;
  name: string;
  email: string;
  preferences: Record<string, any>;
}
```

**Example Output (Rust)**:
```rust
// services/recommendation_service/interfaces/user_service_interface.rs
use std::collections::HashMap;
use async_trait::async_trait;

#[async_trait]
pub trait UserServiceInterface {
    /// Get user profile by ID
    ///
    /// # Arguments
    /// * `user_id` - Unique user identifier
    ///
    /// # Returns
    /// UserProfile struct
    ///
    /// # Errors
    /// * `UserNotFoundException` if user_id not found
    async fn get_user_profile(&self, user_id: &str) -> Result<UserProfile, ServiceError>;

    /// Update user preferences
    async fn update_user_preferences(&self, user_id: &str, preferences: HashMap<String, serde_json::Value>) -> Result<bool, ServiceError>;
}

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct UserProfile {
    pub user_id: String,
    pub name: String,
    pub email: String,
    pub preferences: HashMap<String, serde_json::Value>,
}
```

### Integration into Workflow

**New Action: D-01-A03 - Generate Interface ABC Contracts**

Location: `workflow_steps/development/D-01-InitBootstrap.json`

```json
{
  "action_id": "D-01-A03",
  "description": "Generate language-native interface contracts (ABC, traits, etc.)",
  "tool": "generate_interface_abc.py",
  "command_pattern": "python3 {reflow_root}/tools/generate_interface_abc.py {system_root}",
  "when": "After D-01-A02 (development context bootstrap)",
  "purpose": "Generate strongly-typed interface contracts for compile-time/runtime validation",
  "outputs": [
    "services/{service}/interfaces/{provider}_interface.{ext} (one per dependency)"
  ],
  "language_mapping": {
    "Python": ".py (ABC abstract classes)",
    "TypeScript": ".ts (interface declarations)",
    "Rust": ".rs (trait definitions)",
    "C++": ".hpp (abstract base classes)",
    "Java": ".java (interface declarations)",
    "Go": ".go (interface types)"
  },
  "usage_in_development": [
    "Provider services: Implement the interface (class MyService(ProviderInterface))",
    "Consumer services: Import the interface for type hints",
    "Tests: Mock using the interface for contract testing"
  ]
}
```

**Workflow Sequence Update**:
```
D-01-A01: Select development languages ✅ (existing)
D-01-A02: Bootstrap development context ✅ (existing)
D-01-A03: Generate interface ABC contracts ⭐ (NEW)
D-01-A04: Setup dependency management ✅ (existing)
...
```

## Impact Analysis

### Affected Components

1. **Workflows** (1 file modified):
   - `workflow_steps/development/D-01-InitBootstrap.json` - Add D-01-A03 action

2. **Tools** (1 new tool):
   - `tools/generate_interface_abc.py` (NEW) - Multi-language interface generator

3. **Templates** (6 new templates):
   - `templates/interface_abc_python_template.py` (NEW)
   - `templates/interface_abc_typescript_template.ts` (NEW)
   - `templates/interface_abc_rust_template.rs` (NEW)
   - `templates/interface_abc_cpp_template.hpp` (NEW)
   - `templates/interface_abc_java_template.java` (NEW)
   - `templates/interface_abc_go_template.go` (NEW)

4. **Documentation** (3 files modified):
   - `docs/CLAUDE.md` - Add feature description
   - `docs/TOOL_USAGE_SUMMARY.md` - Add tool documentation
   - `docs/RELEASE_NOTES_v3.10.0.md` (NEW) - Feature release notes

5. **Dependencies**:
   - No new Python dependencies (uses stdlib only)
   - Generated code may require language-specific imports:
     - Python: `from abc import ABC, abstractmethod` (stdlib)
     - TypeScript: No dependencies (native syntax)
     - Rust: `async-trait` crate (if async methods)
     - C++: Standard library (no dependencies)
     - Java: No dependencies (native syntax)
     - Go: No dependencies (native syntax)

### Breaking Changes

**NONE** - This is a purely additive feature.

Existing systems continue to work without ABC interfaces. New systems can opt-in during D-01-A03.

### Data Model Changes

**NONE** - Uses existing `system_of_systems_graph.json` and ICD files.

### Deployment Changes

**NONE** - No changes to deployment or infrastructure.

### Interface Changes

**Enhancement only** - Adds code-based contracts alongside existing JSON ICDs.

## Implementation Considerations

### Design Principles

1. **Framework-agnostic**: Works with UAF, Systems Biology, Social Networks, etc.
2. **Language-agnostic**: Template-based approach allows easy addition of new languages
3. **Idiomatic code**: Generated interfaces follow language best practices
4. **Documentation-rich**: Generated code includes comprehensive docstrings/comments
5. **Type-safe**: Use strongest typing available in each language

### Algorithm

```python
# Pseudocode for generate_interface_abc.py

1. Load system_of_systems_graph.json
2. Load development_language_configuration.json
3. For each edge in graph (edge = interface):
   a. Get provider_service, consumer_service
   b. Get consumer's language from config
   c. Load ICD file for interface details (method signatures, params, returns)
   d. Select template based on language
   e. Generate interface file:
      - Class/trait name: {ProviderService}Interface
      - Methods: Extracted from ICD input/output specs
      - Type hints: Map JSON schema types to language types
      - Docstrings: From ICD descriptions and constraints
   f. Write to services/{consumer}/interfaces/{provider}_interface.{ext}
4. Generate summary report
```

### Type Mapping (JSON Schema → Language Types)

| JSON Schema Type | Python | TypeScript | Rust | C++ | Java | Go |
|-----------------|--------|------------|------|-----|------|-----|
| string | str | string | String | std::string | String | string |
| integer | int | number | i64/u64 | int64_t | long | int64 |
| number | float | number | f64 | double | double | float64 |
| boolean | bool | boolean | bool | bool | boolean | bool |
| array | List[T] | T[] | Vec<T> | std::vector<T> | List<T> | []T |
| object | Dict[str, Any] | Record<string, any> | HashMap<String, Value> | std::map<std::string, json> | Map<String, Object> | map[string]interface{} |
| null | None | null | Option<T> | nullptr | null | nil |

### Error Handling

- **Missing ICD**: Warn and generate basic interface with placeholder methods
- **Unsupported language**: Skip with warning, log to console
- **Invalid JSON schema**: Default to generic types (Any, object, etc.)

### Testing Strategy

1. **Unit tests**: Test type mapping, template rendering, file generation
2. **Integration tests**: Generate interfaces for sample system, verify syntax
3. **Language-specific validation**:
   - Python: Import generated ABC, verify abstractmethod enforcement
   - TypeScript: Compile with `tsc`, verify type checking
   - Rust: Compile with `rustc`, verify trait syntax
   - C++: Compile with `g++`, verify abstract class

## Alternatives Considered

### Alternative 1: Manual Interface Definition

**Rejected** - High developer burden, error-prone, no guarantee of alignment with ICDs.

### Alternative 2: Code Generation from OpenAPI/Protobuf

**Rejected** - Requires additional conversion step (JSON ICD → OpenAPI/Protobuf → code). Our approach is more direct.

### Alternative 3: Runtime Schema Validation Only

**Rejected** - Catches errors at runtime, not compile-time. Defeats purpose of strong typing.

## Success Criteria

1. ✅ Tool generates syntactically valid interface files for all 6 languages
2. ✅ Generated Python ABCs enforce `@abstractmethod` at runtime
3. ✅ Generated TypeScript interfaces pass `tsc` type checking
4. ✅ Generated Rust traits compile with `rustc`
5. ✅ Developer can implement service by inheriting/implementing generated interface
6. ✅ Interface mismatches caught at compile/import time (not integration time)
7. ✅ Documentation updated with examples and usage guidance

## Rollout Plan

### Phase 1: Python ABC (v3.10.0)
- Implement Python ABC generation first (most common language)
- Test on sample Python system
- Release as v3.10.0

### Phase 2: TypeScript, Rust, C++ (v3.10.1)
- Add TypeScript, Rust, C++ templates
- Test on polyglot system
- Release as v3.10.1

### Phase 3: Java, Go (v3.10.2)
- Add Java, Go templates
- Full multi-language support
- Release as v3.10.2

## Migration Guide

**For existing systems**: No migration required (backward compatible).

**For new systems using ABC interfaces**:

1. Run D-01-A03 during development workflow
2. Import generated interfaces in your service code:
   ```python
   from interfaces.user_service_interface import UserServiceInterface

   class UserService(UserServiceInterface):
       def get_user_profile(self, user_id: str) -> Dict[str, Any]:
           # Implementation
           return {"user_id": user_id, "name": "Alice", ...}
   ```
3. Run tests - ABC will enforce method signatures

## Questions & Risks

### Questions

1. ✅ Should we generate interfaces for all edges or only external APIs? **Answer: All edges**
2. ✅ Should consumers import from provider's repo or copy locally? **Answer: Copy locally (avoid cross-service dependencies)**
3. ⚠️ How to handle interface versioning? **Answer: Version with ICD version (future enhancement)**

### Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Generated code has syntax errors | Low | High | Extensive testing, language-specific validators |
| Type mapping incomplete | Medium | Medium | Start with common types, expand based on usage |
| Developers bypass interfaces | Low | Medium | Document benefits, make opt-in clear |
| Interface drift (ICD updated, ABC not regenerated) | Medium | High | Add validation tool to check ICD-ABC alignment (future) |

## Timeline

- **Day 1**: Implement Python ABC generator and templates (6 hours)
- **Day 2**: Update workflow, test on sample system (4 hours)
- **Day 3**: Documentation, release v3.10.0 (2 hours)
- **Total**: 12 hours for Phase 1 (Python ABC)

## Approval

This change proposal requires approval before implementation per FU-01 gate (G-FU-01 Foundational Alignment Gate).

**Change Type**: ⭐ **Feature Addition** (non-breaking)
**Version Impact**: Minor version bump (3.9.1 → 3.10.0)

---

**Prepared by**: Claude (LLM Agent)
**Date**: 2025-11-04
**Status**: AWAITING APPROVAL
