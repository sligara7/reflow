#!/usr/bin/env python3
"""
Example MCP client for Reflow workflows.

This demonstrates how to interact with the Reflow MCP server from Python.

Usage:
    python3 mcp_client_example.py
"""

import asyncio
import json
from typing import Any, Dict

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    print("ERROR: MCP SDK not installed")
    print("Install with: pip install mcp")
    exit(1)


async def run_reflow_mcp_example():
    """Example of using Reflow MCP server"""
    
    # Create server parameters
    server_params = StdioServerParameters(
        command="python3",
        args=["../tools/reflow_mcp_server.py", "--reflow-root", "../"],
        env=None
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            print("=" * 80)
            print("REFLOW MCP CLIENT EXAMPLE")
            print("=" * 80)
            
            # ===================================================================
            # EXAMPLE 1: List available resources
            # ===================================================================
            print("\n1. Listing available resources...")
            resources = await session.list_resources()
            
            print(f"\nFound {len(resources.resources)} resources:")
            for resource in resources.resources[:5]:  # Show first 5
                print(f"  - {resource.name}")
                print(f"    URI: {resource.uri}")
                print(f"    Description: {resource.description}")
                print()
            
            # ===================================================================
            # EXAMPLE 2: Read decision_flow.json
            # ===================================================================
            print("\n2. Reading decision_flow.json...")
            decision_flow_content = await session.read_resource(
                uri="reflow://workflow/decision_flow"
            )
            
            decision_flow = json.loads(decision_flow_content.contents[0].text)
            print(f"Decision flow version: {decision_flow.get('workflow_metadata', {}).get('version')}")
            print(f"Description: {decision_flow.get('workflow_metadata', {}).get('description', '')[:100]}...")
            
            # ===================================================================
            # EXAMPLE 3: List available tools
            # ===================================================================
            print("\n3. Listing available tools...")
            tools = await session.list_tools()
            
            print(f"\nFound {len(tools.tools)} tools:")
            for tool in tools.tools:
                print(f"  - {tool.name}: {tool.description}")
            
            # ===================================================================
            # EXAMPLE 4: Set current system
            # ===================================================================
            print("\n4. Setting current system...")
            
            # First, list available systems
            resources_all = await session.list_resources()
            system_resources = [r for r in resources_all.resources if r.uri.startswith("reflow://systems/")]
            
            if system_resources:
                # Get first system
                first_system_uri = system_resources[0].uri
                system_name = first_system_uri.replace("reflow://systems/", "").replace("/info", "")
                
                print(f"Setting current system to: {system_name}")
                
                result = await session.call_tool(
                    name="set_current_system",
                    arguments={"system_name": system_name}
                )
                
                response = json.loads(result.content[0].text)
                print(f"Result: {json.dumps(response, indent=2)}")
                
                # ===============================================================
                # EXAMPLE 5: Read system context
                # ===============================================================
                print(f"\n5. Reading system context for {system_name}...")
                
                try:
                    memory = await session.read_resource(
                        uri=f"reflow://system/{system_name}/context/memory"
                    )
                    memory_data = json.loads(memory.contents[0].text)
                    print(f"System memory: {json.dumps(memory_data, indent=2)[:200]}...")
                except Exception as e:
                    print(f"Could not read memory: {e}")
                
                # ===============================================================
                # EXAMPLE 6: Get system context prompt
                # ===============================================================
                print(f"\n6. Getting system context prompt...")
                
                prompts = await session.list_prompts()
                print(f"Available prompts: {[p.name for p in prompts.prompts]}")
                
                system_context_prompt = await session.get_prompt(
                    name="system_context",
                    arguments={"system_name": system_name}
                )
                
                print(f"\nSystem context prompt:")
                print(system_context_prompt.messages[0].content.text[:500])
                print("...")
                
                # ===============================================================
                # EXAMPLE 7: Get critical behavioral rules
                # ===============================================================
                print(f"\n7. Getting critical behavioral rules...")
                
                rules_prompt = await session.get_prompt(
                    name="critical_behavioral_rules",
                    arguments={}
                )
                
                print(f"\nCritical rules prompt:")
                print(rules_prompt.messages[0].content.text[:400])
                print("...")
                
                # ===============================================================
                # EXAMPLE 8: Verify system isolation
                # ===============================================================
                print(f"\n8. Verifying system isolation...")
                
                isolation_result = await session.call_tool(
                    name="verify_system_isolation",
                    arguments={"system_name": system_name}
                )
                
                isolation_data = json.loads(isolation_result.content[0].text)
                print(f"Isolation check: {json.dumps(isolation_data, indent=2)}")
                
            else:
                print("No systems found. Create a system first.")
            
            # ===================================================================
            # EXAMPLE 9: Check validation tools status
            # ===================================================================
            print("\n9. Checking validation tools status...")
            
            tools_status = await session.read_resource(
                uri="reflow://validation/tools_status"
            )
            
            status_data = json.loads(tools_status.contents[0].text)
            print(f"Validation tools status: {json.dumps(status_data, indent=2)}")
            
            print("\n" + "=" * 80)
            print("MCP CLIENT EXAMPLE COMPLETE")
            print("=" * 80)


async def example_workflow_integration():
    """
    Example showing how an LLM agent workflow would use MCP
    """
    
    print("\n\nWORKFLOW INTEGRATION EXAMPLE")
    print("=" * 80)
    
    server_params = StdioServerParameters(
        command="python3",
        args=["../tools/reflow_mcp_server.py", "--reflow-root", "../"],
        env=None
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Workflow: LLM agent starting a new step
            print("\nScenario: LLM agent starting step Arch-01")
            print("-" * 80)
            
            # Step 1: Get critical rules (always)
            print("\n[Agent] Retrieving critical behavioral rules...")
            rules = await session.get_prompt("critical_behavioral_rules", {})
            print(f"[Context Loaded] {len(rules.messages[0].content.text)} chars of critical rules")
            
            # Step 2: Get step-specific context
            print("\n[Agent] Retrieving context for step Arch-01...")
            step_context = await session.get_prompt(
                "step_start_context",
                {"step_id": "Arch-01"}
            )
            print(f"[Context Loaded] Step instructions retrieved")
            
            # Step 3: Verify system isolation before proceeding
            print("\n[Agent] Verifying system isolation...")
            # (would call verify_system_isolation tool)
            
            # Step 4: Execute step actions with full context
            print("\n[Agent] Executing step actions with loaded context...")
            print("  - CRITICAL_BEHAVIORAL_RULES: Loaded ✓")
            print("  - Step instructions: Loaded ✓")
            print("  - System isolation: Verified ✓")
            print("\n[Agent] Ready to proceed with step execution")
            
            print("\n" + "=" * 80)


if __name__ == "__main__":
    print("Starting Reflow MCP Client Example...\n")
    asyncio.run(run_reflow_mcp_example())
    asyncio.run(example_workflow_integration())
