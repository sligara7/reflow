# MCP (Model Context Protocol) Integration for Reflow

## Overview

The Reflow MCP server provides a standardized interface for LLM agents to interact with reflow workflows. Instead of manually reading files and executing shell commands, LLM agents can use the MCP protocol to:

- **Discover resources** (workflow state, system context, etc.)
- **Invoke tools** (validation, RAG retrieval, etc.)
- **Get prompt templates** (critical rules, step context, etc.)

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     LLM Agent (MCP Client)                    │
├──────────────────────────────────────────────────────────────┤
│  • Discovers available resources                             │
│  • Reads workflow state via URIs                             │
│  • Calls tools with type-safe arguments                      │
│  • Gets pre-formatted prompt templates                       │
└────────────────────┬─────────────────────────────────────────┘
                     │ MCP Protocol (JSON-RPC over stdio)
┌────────────────────┴─────────────────────────────────────────┐
│              Reflow MCP Server (reflow_mcp_server.py)        │
├──────────────────────────────────────────────────────────────┤
│  Resources:                                                   │
│    • reflow://workflow/decision_flow                         │
│    • reflow://system/{name}/context/memory                   │
│    • reflow://system/{name}/context/progress                 │
│    • reflow://rag/{name}/status                              │
│                                                               │
│  Tools:                                                       │
│    • set_current_system                                      │
│    • validate_architecture                                   │
│    • generate_rag_embeddings                                 │
│    • retrieve_rag_context                                    │
│    • verify_system_isolation                                 │
│    • get_current_step_instructions                           │
│                                                               │
│  Prompts:                                                     │
│    • critical_behavioral_rules                               │
│    • step_start_context                                      │
│    • degradation_correction                                  │
│    • system_context                                          │
└──────────────────────────────────────────────────────────────┘
                     │
┌────────────────────┴─────────────────────────────────────────┐
│                  Reflow Workflow System                       │
├──────────────────────────────────────────────────────────────┤
│  • decision_flow.json                                         │
│  • systems/{system_name}/context/*                           │
│  • tools/*.py                                                 │
│  • templates/*.json                                           │
└──────────────────────────────────────────────────────────────┘
```

## Setup

### 1. Install MCP SDK

```bash
pip install mcp
```

### 2. Start the MCP Server

```bash
# From reflow root
python3 tools/reflow_mcp_server.py --reflow-root .
```

The server runs in stdio mode and communicates via JSON-RPC.

### 3. Configure Your MCP Client

For Claude Desktop (example config in `~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "reflow": {
      "command": "python3",
      "args": [
        "/path/to/reflow/tools/reflow_mcp_server.py",
        "--reflow-root",
        "/path/to/reflow"
      ]
    }
  }
}
```

For custom Python clients:

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(
    command="python3",
    args=["tools/reflow_mcp_server.py", "--reflow-root", "."]
)

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        # Use session...
```

## Resources

Resources are read-only data sources that LLM agents can access.

### Workflow Resources

| URI | Description | MIME Type |
|-----|-------------|-----------|
| `reflow://workflow/decision_flow` | Main workflow definition | application/json |

### System Resources

| URI Pattern | Description | MIME Type |
|-------------|-------------|-----------|
| `reflow://system/{name}/context/memory` | Working memory (state) | application/json |
| `reflow://system/{name}/context/progress` | Step progress tracker | application/json |
| `reflow://system/{name}/context/focus` | Current focus document | text/markdown |
| `reflow://system/{name}/context/log` | Process execution log | text/markdown |

### System Info Resources

| URI Pattern | Description | MIME Type |
|-------------|-------------|-----------|
| `reflow://systems/{name}/info` | System structure info | application/json |

### RAG Resources

| URI Pattern | Description | MIME Type |
|-------------|-------------|-----------|
| `reflow://rag/{name}/status` | RAG embeddings status | application/json |

### Validation Resources

| URI | Description | MIME Type |
|-----|-------------|-----------|
| `reflow://validation/tools_status` | Validation tools availability | application/json |

### Usage Example

```python
# List all resources
resources = await session.list_resources()

# Read decision_flow.json
content = await session.read_resource("reflow://workflow/decision_flow")
decision_flow = json.loads(content.contents[0].text)

# Read system context
memory = await session.read_resource("reflow://system/my_system/context/memory")
```

## Tools

Tools are operations that LLM agents can invoke with type-safe arguments.

### set_current_system

Set the active system for subsequent operations.

**Input:**
```json
{
  "system_name": "my_system"
}
```

**Output:**
```json
{
  "success": true,
  "current_system": "my_system",
  "system_path": "/path/to/systems/my_system"
}
```

### validate_architecture

Validate service architecture files for a system.

**Input:**
```json
{
  "system_name": "my_system"  // Optional if current system is set
}
```

**Output:**
```json
{
  "tool": "validate_architecture",
  "system": "my_system",
  "exit_code": 0,
  "stdout": "...",
  "success": true
}
```

### generate_rag_embeddings

Generate or update RAG embeddings for a system.

**Input:**
```json
{
  "system_name": "my_system",  // Optional
  "force_rebuild": false       // Optional
}
```

**Output:**
```json
{
  "tool": "generate_rag_embeddings",
  "system": "my_system",
  "exit_code": 0,
  "success": true
}
```

### retrieve_rag_context

Retrieve relevant context using RAG semantic search.

**Input:**
```json
{
  "query": "How do I validate architecture?",
  "strategy": "on_user_query",  // Optional
  "system_name": "my_system"     // Optional
}
```

**Output:**
```json
{
  "strategy": "on_user_query",
  "critical_context": [...],
  "high_priority_context": [...],
  ...
}
```

### verify_system_isolation

Verify that the system is properly isolated (correct working directory).

**Input:**
```json
{
  "system_name": "my_system"  // Optional
}
```

**Output:**
```json
{
  "system_name": "my_system",
  "memory_system_name": "my_system",
  "isolated": true,
  "system_path": "/path/to/systems/my_system"
}
```

### get_current_step_instructions

Get detailed instructions for the current workflow step.

**Input:**
```json
{
  "system_name": "my_system"  // Optional
}
```

**Output:**
```json
{
  "current_step": "Arch-01",
  "instructions": {
    "id": "Arch-01",
    "description": "...",
    ...
  }
}
```

### Usage Example

```python
# Set current system
result = await session.call_tool(
    name="set_current_system",
    arguments={"system_name": "my_system"}
)

# Validate architecture
validation = await session.call_tool(
    name="validate_architecture",
    arguments={}  # Uses current system
)

# Retrieve RAG context
context = await session.call_tool(
    name="retrieve_rag_context",
    arguments={
        "query": "validation requirements",
        "strategy": "on_user_query"
    }
)
```

## Prompts

Prompts are pre-formatted context templates that LLM agents can request.

### critical_behavioral_rules

Returns CRITICAL_BEHAVIORAL_RULES from decision_flow.json.

**Arguments:** None

**Returns:**
```
**CRITICAL BEHAVIORAL RULES - MANDATORY**

**NEVER GENERATE REPORTS:**
- NEVER generate a report after completing a step or substep
- NEVER summarize what you just did unless explicitly requested
...

**MANDATORY WORKFLOW ADHERENCE:**
- READ decision_flow.json AND current workflow step file BEFORE every action
- VERIFY current step/substep from step_progress_tracker.json matches decision_flow
...
```

### step_start_context

Returns context for starting a specific workflow step.

**Arguments:**
```json
{
  "step_id": "Arch-01"
}
```

**Returns:**
```
**STEP START CONTEXT: Arch-01**

**CRITICAL RULES:**
- NEVER generate a report after completing a step or substep
- NEVER summarize what you just did unless explicitly requested
...

**CURRENT STEP INSTRUCTIONS:**
Step: Arch-01
Description: Setup system isolation and load context

Full Instructions:
```json
{
  "id": "Arch-01",
  ...
}
```
```

### degradation_correction

Returns corrective context when degradation is detected.

**Arguments:**
```json
{
  "signal_type": "report_generation_attempt"
}
```

**Returns:**
```
**DEGRADATION DETECTED: report_generation_attempt**

**CORRECTIVE ACTION REQUIRED**

**NEVER GENERATE REPORTS:**
- NEVER generate a report after completing a step or substep
...

**STOP CURRENT ACTION AND REVIEW THESE RULES BEFORE PROCEEDING**
```

### system_context

Returns complete system context (memory, progress, focus).

**Arguments:**
```json
{
  "system_name": "my_system"  // Optional
}
```

**Returns:**
```
**SYSTEM CONTEXT: my_system**

**Working Memory:**
```json
{
  "system_name": "my_system",
  ...
}
```

**Progress Tracker:**
```json
{
  "current_step": "Arch-01",
  ...
}
```

**Current Focus:**
[content from current_focus.md]
```

### Usage Example

```python
# Get critical rules (always load this first)
rules = await session.get_prompt(
    name="critical_behavioral_rules",
    arguments={}
)

# Get step context
step_context = await session.get_prompt(
    name="step_start_context",
    arguments={"step_id": "Arch-01"}
)

# Get system context
system_ctx = await session.get_prompt(
    name="system_context",
    arguments={"system_name": "my_system"}
)

# Use in LLM prompt
full_prompt = f"""
{rules.messages[0].content.text}

{step_context.messages[0].content.text}

USER QUERY: {user_question}
"""
```

## Workflow Integration Patterns

### Pattern 1: Step Start

```python
async def start_workflow_step(session, step_id):
    # 1. Get critical rules (MANDATORY)
    rules = await session.get_prompt("critical_behavioral_rules", {})
    
    # 2. Get step instructions
    step_ctx = await session.get_prompt("step_start_context", {"step_id": step_id})
    
    # 3. Verify system isolation
    isolation = await session.call_tool("verify_system_isolation", {})
    
    # 4. Get current system context
    sys_ctx = await session.get_prompt("system_context", {})
    
    # 5. Build LLM prompt
    prompt = f"{rules.messages[0].content.text}\n\n{step_ctx.messages[0].content.text}"
    
    return prompt
```

### Pattern 2: Degradation Detection

```python
async def handle_degradation(session, agent_response):
    # Detect if agent is generating a report
    if "generating report" in agent_response.lower():
        # Get corrective context
        correction = await session.get_prompt(
            "degradation_correction",
            {"signal_type": "report_generation_attempt"}
        )
        
        # Re-inject critical context
        return correction.messages[0].content.text
```

### Pattern 3: Tool Execution

```python
async def validate_and_proceed(session, system_name):
    # 1. Set current system
    await session.call_tool("set_current_system", {"system_name": system_name})
    
    # 2. Verify isolation
    isolation = await session.call_tool("verify_system_isolation", {})
    if not isolation["isolated"]:
        raise RuntimeError("System isolation breach!")
    
    # 3. Validate architecture
    validation = await session.call_tool("validate_architecture", {})
    
    return validation
```

## Advantages Over Manual Approach

| Aspect | Manual (Current) | MCP (New) |
|--------|------------------|-----------|
| **Resource Discovery** | Hardcoded paths | `list_resources()` |
| **Type Safety** | None (shell strings) | JSON Schema validation |
| **Error Handling** | Parse stdout/stderr | Structured MCP errors |
| **Tool Invocation** | Shell commands | `call_tool()` with validation |
| **Context Injection** | Manual file reads | `get_prompt()` templates |
| **Standardization** | Reflow-specific | Works with any MCP client |
| **Prompt Assembly** | Manual concatenation | Pre-formatted templates |
| **State Management** | Manual tracking | Server manages current system |

## Integration with RAG

MCP and RAG complement each other:

- **MCP**: Standardized access layer (discover, read, execute)
- **RAG**: Intelligent context retrieval (semantic search, prioritization)

Use together:
```python
# MCP: Discover and set system
await session.call_tool("set_current_system", {"system_name": "my_system"})

# MCP + RAG: Retrieve context semantically
context = await session.call_tool(
    "retrieve_rag_context",
    {"query": "validation requirements", "strategy": "on_user_query"}
)

# MCP: Get pre-formatted prompt
rules = await session.get_prompt("critical_behavioral_rules", {})

# Combine for LLM
full_context = f"{rules.messages[0].content.text}\n\n{context}"
```

## Testing

Run the example client:

```bash
cd examples
python3 mcp_client_example.py
```

## MCP Client Configuration Files

### Claude Desktop

`~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)
`%APPDATA%\Claude\claude_desktop_config.json` (Windows)
`~/.config/Claude/claude_desktop_config.json` (Linux)

```json
{
  "mcpServers": {
    "reflow": {
      "command": "python3",
      "args": [
        "/absolute/path/to/reflow/tools/reflow_mcp_server.py",
        "--reflow-root",
        "/absolute/path/to/reflow"
      ]
    }
  }
}
```

### Other MCP Clients

Refer to your MCP client's documentation for configuration. The reflow MCP server uses stdio transport and is compatible with any MCP client that supports:
- JSON-RPC 2.0
- stdio transport
- MCP protocol version 2024-11-05 or later

## Troubleshooting

### Server won't start
```bash
# Check if MCP SDK is installed
python3 -c "import mcp; print(mcp.__version__)"

# Check if reflow root is valid
python3 tools/reflow_mcp_server.py --reflow-root .
```

### Resources not found
```bash
# Verify system exists
ls systems/

# Check context files
ls systems/my_system/context/
```

### Tool execution fails
```bash
# Verify tools exist
ls tools/*.py

# Check tool dependencies
python3 -c "import networkx, faiss"
```

## References

- MCP Specification: https://modelcontextprotocol.io/
- MCP Python SDK: https://github.com/modelcontextprotocol/python-sdk
- Reflow MCP Server: `tools/reflow_mcp_server.py`
- Example Client: `examples/mcp_client_example.py`
