# LLM Agent Guide: Interface Contract Generation Tool

## Overview
The `generate_interface_contracts.py` tool creates detailed Interface Contract Documents (ICDs) from service architecture specifications, enabling independent component development with guaranteed integration success.

## Tool Purpose vs Other Tools

| Tool | Purpose | Output | LLM Usage |
|------|---------|---------|-----------|
| `system_of_systems_graph.py` | **Analyze** topology & detect issues | Graph + Issues JSON | Fix architectural problems |
| `validate_architecture.py` | **Validate** compliance & consistency | Validation Results JSON | Fix template/consistency issues |
| `generate_interface_contracts.py` | **Generate** development specifications | Individual ICD JSON files | Implement components independently |

**This tool is NOT redundant** - it creates the actual development artifacts that enable guaranteed integration.

## How It Works

### 1. Contract Generation
```bash
python3 ./tools/generate_interface_contracts.py systems/<system_name>
```

This analyzes service_architecture.json files and creates:
- **Individual ICD files**: `interfaces/<interface_id>.json` for each interface relationship
- **Summary file**: `interfaces/interfaces_summary.json` with overview and LLM guidance

### 2. Generated ICD Structure
Each interface contract includes complete specifications:

```json
{
  "interface_id": "auth_service_to_user_service_authenticate",
  "provider_component": "auth_service",
  "consumer_component": "user_service", 
  "interaction_type": "synchronous",
  "contract": {
    "input_specification": {
      "format": "json",
      "schema": { /* Complete JSON schema */ },
      "constraints": ["Authentication required", "Rate limit: 1000/hour"],
      "examples": [ /* Concrete examples */ ],
      "validation_rules": []
    },
    "output_specification": {
      "format": "json", 
      "schema": { /* Response schema */ },
      "success_criteria": "Response matches schema and contains expected fields",
      "examples": [ /* Response examples */ ],
      "validation_rules": []
    },
    "error_handling": {
      "error_conditions": [
        {"error_id": "INVALID_INPUT", "condition": "Input does not match schema", "severity": "high"}
      ],
      "error_responses": [],
      "retry_policy": {"applicable": "no", "max_retries": 3},
      "fallback_behavior": "Log error and return error response to consumer"
    },
    "timing_constraints": {
      "max_latency": "500ms",
      "throughput_requirements": "1000 requests/sec",
      "synchronization_requirements": "depends_on_interaction_type"
    }
  },
  "integration_tests": {
    "test_scenarios": [
      {"scenario_id": "happy_path", "description": "Valid input produces expected output"},
      {"scenario_id": "error_handling", "description": "Invalid input produces appropriate error"}
    ],
    "contract_verification": {
      "provider_verification": "Provider must implement interface matching specification",
      "consumer_verification": "Consumer must call interface according to specification",
      "integration_verification": "Run integration test scenarios to verify end-to-end interaction"
    }
  }
}
```

### 3. Summary JSON Structure
```json
{
  "system_path": "/path/to/system",
  "generation_date": "2025-10-14T...",
  "total_interfaces": 5,
  "llm_development_instructions": {
    "purpose": "Generated ICD files provide complete interface specifications for independent component development",
    "usage_workflow": [
      "1. Locate the ICD file for the interface you're implementing",
      "2. For provider components: Implement interface to satisfy output_specification",
      "3. For consumer components: Send requests matching input_specification format",
      "4. Follow error_handling specifications for robust error management",
      "5. Use integration_tests scenarios to verify contract compliance",
      "6. Generated contracts guarantee integration success when followed precisely"
    ],
    "contract_guarantee": "If both provider and consumer implement according to their respective ICD specifications, integration will succeed without additional coordination"
  },
  "interfaces": [
    {
      "interface_id": "auth_service_to_user_service_authenticate",
      "provider": "auth_service",
      "consumer": "user_service",
      "file_path": "interfaces/auth_service_to_user_service_authenticate.json",
      "development_guidance": {
        "provider_requirements": "Implement auth_service to satisfy output_specification",
        "consumer_requirements": "Implement user_service to send requests matching input_specification",
        "integration_confidence": "high_confidence_if_contracts_followed"
      }
    }
  ]
}
```

## LLM Agent Development Workflow

### Step 1: Load Interface Contracts
```python
# LLM agent developing a component should:
1. Load interfaces/interfaces_summary.json to see all available contracts
2. Identify which interfaces the component provides vs consumes
3. Load specific ICD files for interfaces being implemented
```

### Step 2: Implement Provider Components
For components that **provide** interfaces:

```python
# LLM agent should:
1. Read contract.output_specification to understand required response format
2. Implement component to return responses matching the schema
3. Handle all error_conditions specified in error_handling section
4. Meet timing_constraints for performance requirements
5. Follow integration_tests scenarios to verify implementation
```

**Example Provider Implementation:**
```python
# From ICD: auth_service provides authenticate interface
# output_specification requires: {"user_id": str, "token": str, "expires_at": datetime}

def authenticate(username, password):
    # Implement according to output_specification
    if valid_credentials(username, password):
        return {
            "user_id": get_user_id(username),
            "token": generate_jwt_token(),
            "expires_at": datetime.now() + timedelta(hours=24)
        }
    else:
        # Follow error_handling specification
        raise AuthenticationError("INVALID_CREDENTIALS")
```

### Step 3: Implement Consumer Components  
For components that **consume** interfaces:

```python
# LLM agent should:
1. Read contract.input_specification to understand required request format
2. Send requests that exactly match the expected schema
3. Handle all error_responses specified in error_handling section
4. Implement retry_policy if applicable
5. Process responses according to output_specification format
```

**Example Consumer Implementation:**
```python
# From ICD: user_service consumes authenticate interface
# input_specification requires: {"username": str, "password": str}

def login_user(username, password):
    # Send request matching input_specification
    auth_request = {
        "username": username,
        "password": password
    }
    
    try:
        # Call according to contract specification
        response = auth_service.authenticate(auth_request)
        # Process response according to output_specification
        return {
            "user_id": response["user_id"],
            "session_token": response["token"]
        }
    except AuthenticationError as e:
        # Handle errors according to error_handling specification
        if e.error_id == "INVALID_CREDENTIALS":
            return {"error": "Login failed", "retry_allowed": True}
```

### Step 4: Verify Contract Compliance
```python
# LLM agent should:
1. Use integration_tests scenarios to verify implementation
2. Ensure all test scenarios pass before considering component complete
3. Verify both happy path and error handling scenarios
4. Confirm timing_constraints are met under load
```

## Integration with Decision Flow

The tool is used in the **Interface Design** phase:
- **After interface deduction**: Generate contracts from identified interfaces
- **Before component development**: Provide specifications for independent development
- **When interfaces change**: Regenerate contracts to maintain consistency

## Contract-First Development Benefits

### ✅ **Guaranteed Integration Success**
- If both provider and consumer follow their respective contract specifications, integration will succeed
- No coordination required between development teams
- Eliminates integration surprises and failures

### ✅ **Independent Development**
- Teams can develop components in parallel using contract specifications
- No need to wait for other components to be complete
- Mock implementations can be created from contract specifications

### ✅ **Clear Requirements**
- Complete input/output schemas eliminate ambiguity
- Error handling specifications ensure robust implementations
- Performance constraints provide clear targets

### ✅ **Automated Testing**
- Integration test scenarios provide verification criteria
- Contract verification guidelines ensure proper implementation
- Mock specifications enable isolated testing

## Example LLM Agent Response

```
Generating interface contracts...

📊 Analysis Results:
- Found 3 service components with 8 interface relationships
- Generated 8 complete ICD files in interfaces/ directory
- Created interfaces_summary.json with development guidance

📋 Generated Interface Contracts:
- auth_service_to_user_service_authenticate.json
- user_service_to_profile_service_get_profile.json  
- api_gateway_to_auth_service_verify_token.json
- ... (5 more)

🤖 LLM Development Ready:
✅ All interfaces have complete specifications for independent development
✅ Provider/consumer requirements clearly defined in each contract
✅ Integration test scenarios provided for verification
✅ Following contracts precisely guarantees integration success

Next Steps:
1. Use ICD files as authoritative interface specifications
2. Implement components according to contract requirements
3. Verify implementation using integration test scenarios
```

## Success Criteria

### ✅ **Complete Contract Coverage**
- Every interface relationship has a generated ICD file
- All contracts include input/output specifications, error handling, and test scenarios
- Summary file provides clear development guidance

### ✅ **Development Ready**
- LLM agents can implement components independently using contracts
- No additional coordination required between component teams
- Integration success guaranteed when contracts are followed

The `generate_interface_contracts.py` tool bridges the gap between architectural design and component implementation, providing the detailed specifications needed for guaranteed integration success in large-scale system development.