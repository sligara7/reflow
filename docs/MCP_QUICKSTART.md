# MCP Quick Start Guide

## 5-Minute Setup

### 1. Install Dependencies

```bash
pip install mcp
```

### 2. Test the Server

```bash
cd /path/to/reflow
python3 tools/reflow_mcp_server.py --reflow-root .
```

Server should start and wait for MCP client connections via stdio.

### 3. Run Example Client

```bash
cd examples
python3 mcp_client_example.py
```

Expected output:
```
REFLOW MCP CLIENT EXAMPLE
================================================================================

1. Listing available resources...

Found X resources:
  - Decision Flow Workflow
    URI: reflow://workflow/decision_flow
    Description: Main decision flow workflow definition
...
```

### 4. Configure Claude Desktop (Optional)

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

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

Restart Claude Desktop. You should see "reflow" in the MCP servers list.

### 5. Test with Claude

In Claude Desktop, try:

```
List available reflow resources
```

Claude should discover and list resources via MCP.

```
Get critical behavioral rules for reflow workflows
```

Claude should retrieve the `critical_behavioral_rules` prompt.

## Common Workflows

### Start a Workflow Step

```python
# Via MCP client
rules = await session.get_prompt("critical_behavioral_rules", {})
step_ctx = await session.get_prompt("step_start_context", {"step_id": "Arch-01"})
```

### Validate Architecture

```python
await session.call_tool("set_current_system", {"system_name": "my_system"})
result = await session.call_tool("validate_architecture", {})
```

### Retrieve RAG Context

```python
context = await session.call_tool(
    "retrieve_rag_context",
    {"query": "How do I validate?", "strategy": "on_user_query"}
)
```

## Troubleshooting

### "ImportError: No module named 'mcp'"
```bash
pip install mcp
```

### "RuntimeError: Invalid reflow root"
```bash
# Ensure you're pointing to the correct directory
python3 tools/reflow_mcp_server.py --reflow-root /absolute/path/to/reflow
```

### "Resource not found"
```bash
# Verify system exists
ls systems/my_system/context/
```

## Next Steps

- Read full documentation: `docs/MCP_INTEGRATION.md`
- Review example client: `examples/mcp_client_example.py`
- Integrate with RAG: `docs/RAG_CONTEXT_MANAGEMENT.md`

## Architecture Diagram

```
LLM Agent (Claude, GPT, etc.)
    ↓ MCP Protocol
Reflow MCP Server
    ↓
Reflow Workflow System (decision_flow.json, systems/, tools/)
```

**Key Advantage:** LLM agents can now discover and interact with reflow workflows through a standardized protocol instead of manual file reading and shell commands.
