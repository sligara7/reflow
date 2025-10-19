#!/usr/bin/env python3
"""
Integration tests for Reflow MCP Server.

These tests verify that the MCP server correctly exposes reflow workflow
resources, tools, and prompts through the MCP protocol.

Usage:
    python3 test_mcp_server.py
"""

import asyncio
import json
import sys
import tempfile
from pathlib import Path
import shutil

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    print("ERROR: MCP SDK not installed")
    print("Install with: pip install mcp")
    sys.exit(1)


class TestMCPServer:
    """Test suite for Reflow MCP Server"""
    
    def __init__(self, reflow_root: Path):
        self.reflow_root = reflow_root
        self.test_system_name = "test_system_mcp"
        self.test_system_path = reflow_root / "systems" / self.test_system_name
        self.passed = 0
        self.failed = 0
    
    def setup_test_system(self):
        """Create a test system with context files"""
        print(f"\n📦 Setting up test system: {self.test_system_name}")
        
        # Create system directory structure
        (self.test_system_path / "context").mkdir(parents=True, exist_ok=True)
        (self.test_system_path / "specs").mkdir(exist_ok=True)
        (self.test_system_path / "services").mkdir(exist_ok=True)
        (self.test_system_path / "docs").mkdir(exist_ok=True)
        
        # Create working_memory.json
        working_memory = {
            "system_name": self.test_system_name,
            "created": "2025-10-18T03:00:00Z"
        }
        with open(self.test_system_path / "context" / "working_memory.json", 'w') as f:
            json.dump(working_memory, f, indent=2)
        
        # Create step_progress_tracker.json
        progress = {
            "current_step": "Arch-01",
            "current_substep": None,
            "operations_since_refresh": 0
        }
        with open(self.test_system_path / "context" / "step_progress_tracker.json", 'w') as f:
            json.dump(progress, f, indent=2)
        
        # Create current_focus.md
        with open(self.test_system_path / "context" / "current_focus.md", 'w') as f:
            f.write("# Current Focus\n\nTest system for MCP integration tests\n")
        
        print(f"✓ Test system created at {self.test_system_path}")
    
    def cleanup_test_system(self):
        """Remove test system"""
        if self.test_system_path.exists():
            shutil.rmtree(self.test_system_path)
            print(f"\n🧹 Cleaned up test system: {self.test_system_name}")
    
    def assert_true(self, condition, message):
        """Assert that condition is true"""
        if condition:
            print(f"  ✓ {message}")
            self.passed += 1
        else:
            print(f"  ✗ FAILED: {message}")
            self.failed += 1
    
    def assert_equal(self, actual, expected, message):
        """Assert that actual equals expected"""
        if actual == expected:
            print(f"  ✓ {message}")
            self.passed += 1
        else:
            print(f"  ✗ FAILED: {message}")
            print(f"    Expected: {expected}")
            print(f"    Actual: {actual}")
            self.failed += 1
    
    async def test_list_resources(self, session):
        """Test resource listing"""
        print("\n🧪 TEST: List Resources")
        
        resources = await session.list_resources()
        
        self.assert_true(len(resources.resources) > 0, "Resources list not empty")
        
        # Check for decision_flow resource
        decision_flow_found = any(
            r.uri == "reflow://workflow/decision_flow" for r in resources.resources
        )
        self.assert_true(decision_flow_found, "decision_flow resource found")
        
        # Check for system info resource
        system_info_found = any(
            self.test_system_name in r.uri for r in resources.resources
        )
        self.assert_true(system_info_found, f"Test system info resource found")
    
    async def test_read_decision_flow(self, session):
        """Test reading decision_flow.json"""
        print("\n🧪 TEST: Read decision_flow.json")
        
        content = await session.read_resource("reflow://workflow/decision_flow")
        
        self.assert_true(len(content.contents) > 0, "Content received")
        
        decision_flow = json.loads(content.contents[0].text)
        
        self.assert_true("workflow_metadata" in decision_flow, "workflow_metadata present")
        self.assert_true("context_management" in decision_flow, "context_management present")
        self.assert_true("decisions" in decision_flow, "decisions present")
    
    async def test_list_tools(self, session):
        """Test tool listing"""
        print("\n🧪 TEST: List Tools")
        
        tools = await session.list_tools()
        
        self.assert_true(len(tools.tools) > 0, "Tools list not empty")
        
        expected_tools = [
            "set_current_system",
            "validate_architecture",
            "verify_system_isolation",
            "get_current_step_instructions"
        ]
        
        for tool_name in expected_tools:
            found = any(t.name == tool_name for t in tools.tools)
            self.assert_true(found, f"Tool '{tool_name}' found")
    
    async def test_set_current_system(self, session):
        """Test setting current system"""
        print("\n🧪 TEST: Set Current System")
        
        result = await session.call_tool(
            name="set_current_system",
            arguments={"system_name": self.test_system_name}
        )
        
        self.assert_true(len(result.content) > 0, "Result received")
        
        response = json.loads(result.content[0].text)
        
        self.assert_true(response.get("success"), "Set system succeeded")
        self.assert_equal(
            response.get("current_system"),
            self.test_system_name,
            "Current system matches"
        )
    
    async def test_read_system_context(self, session):
        """Test reading system context files"""
        print("\n🧪 TEST: Read System Context")
        
        # Set current system first
        await session.call_tool(
            name="set_current_system",
            arguments={"system_name": self.test_system_name}
        )
        
        # Read working memory
        memory = await session.read_resource(
            f"reflow://system/{self.test_system_name}/context/memory"
        )
        memory_data = json.loads(memory.contents[0].text)
        
        self.assert_equal(
            memory_data.get("system_name"),
            self.test_system_name,
            "System name in memory matches"
        )
        
        # Read progress tracker
        progress = await session.read_resource(
            f"reflow://system/{self.test_system_name}/context/progress"
        )
        progress_data = json.loads(progress.contents[0].text)
        
        self.assert_equal(
            progress_data.get("current_step"),
            "Arch-01",
            "Current step in progress tracker"
        )
        
        # Read current focus
        focus = await session.read_resource(
            f"reflow://system/{self.test_system_name}/context/focus"
        )
        
        self.assert_true(
            "Test system" in focus.contents[0].text,
            "Current focus content present"
        )
    
    async def test_verify_system_isolation(self, session):
        """Test system isolation verification"""
        print("\n🧪 TEST: Verify System Isolation")
        
        # Set current system
        await session.call_tool(
            name="set_current_system",
            arguments={"system_name": self.test_system_name}
        )
        
        # Verify isolation
        result = await session.call_tool(
            name="verify_system_isolation",
            arguments={}
        )
        
        response = json.loads(result.content[0].text)
        
        self.assert_equal(
            response.get("system_name"),
            self.test_system_name,
            "System name matches"
        )
        self.assert_equal(
            response.get("memory_system_name"),
            self.test_system_name,
            "Memory system name matches"
        )
        self.assert_true(
            response.get("isolated"),
            "System is isolated"
        )
    
    async def test_list_prompts(self, session):
        """Test prompt listing"""
        print("\n🧪 TEST: List Prompts")
        
        prompts = await session.list_prompts()
        
        self.assert_true(len(prompts.prompts) > 0, "Prompts list not empty")
        
        expected_prompts = [
            "critical_behavioral_rules",
            "step_start_context",
            "degradation_correction",
            "system_context"
        ]
        
        for prompt_name in expected_prompts:
            found = any(p.name == prompt_name for p in prompts.prompts)
            self.assert_true(found, f"Prompt '{prompt_name}' found")
    
    async def test_get_critical_rules_prompt(self, session):
        """Test getting critical behavioral rules prompt"""
        print("\n🧪 TEST: Get Critical Behavioral Rules Prompt")
        
        result = await session.get_prompt(
            name="critical_behavioral_rules",
            arguments={}
        )
        
        self.assert_true(len(result.messages) > 0, "Messages received")
        
        content = result.messages[0].content.text
        
        self.assert_true(
            "CRITICAL BEHAVIORAL RULES" in content,
            "Critical rules header present"
        )
        self.assert_true(
            "NEVER GENERATE REPORTS" in content,
            "Never generate reports rule present"
        )
        self.assert_true(
            "MANDATORY WORKFLOW ADHERENCE" in content,
            "Mandatory workflow adherence present"
        )
    
    async def test_get_step_context_prompt(self, session):
        """Test getting step context prompt"""
        print("\n🧪 TEST: Get Step Start Context Prompt")
        
        result = await session.get_prompt(
            name="step_start_context",
            arguments={"step_id": "Arch-01"}
        )
        
        self.assert_true(len(result.messages) > 0, "Messages received")
        
        content = result.messages[0].content.text
        
        self.assert_true(
            "STEP START CONTEXT" in content,
            "Step context header present"
        )
        self.assert_true(
            "Arch-01" in content,
            "Step ID present in context"
        )
    
    async def test_get_system_context_prompt(self, session):
        """Test getting complete system context prompt"""
        print("\n🧪 TEST: Get System Context Prompt")
        
        # Set current system
        await session.call_tool(
            name="set_current_system",
            arguments={"system_name": self.test_system_name}
        )
        
        result = await session.get_prompt(
            name="system_context",
            arguments={"system_name": self.test_system_name}
        )
        
        self.assert_true(len(result.messages) > 0, "Messages received")
        
        content = result.messages[0].content.text
        
        self.assert_true(
            "SYSTEM CONTEXT" in content,
            "System context header present"
        )
        self.assert_true(
            self.test_system_name in content,
            "System name present in context"
        )
        self.assert_true(
            "Working Memory" in content,
            "Working memory section present"
        )
    
    async def test_get_current_step_instructions(self, session):
        """Test getting current step instructions"""
        print("\n🧪 TEST: Get Current Step Instructions")
        
        # Set current system
        await session.call_tool(
            name="set_current_system",
            arguments={"system_name": self.test_system_name}
        )
        
        result = await session.call_tool(
            name="get_current_step_instructions",
            arguments={}
        )
        
        response = json.loads(result.content[0].text)
        
        self.assert_equal(
            response.get("current_step"),
            "Arch-01",
            "Current step matches"
        )
    
    async def run_all_tests(self):
        """Run all tests"""
        print("=" * 80)
        print("REFLOW MCP SERVER INTEGRATION TESTS")
        print("=" * 80)
        
        self.setup_test_system()
        
        server_params = StdioServerParameters(
            command="python3",
            args=[
                str(self.reflow_root / "tools" / "reflow_mcp_server.py"),
                "--reflow-root",
                str(self.reflow_root)
            ],
            env=None
        )
        
        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    # Run all tests
                    await self.test_list_resources(session)
                    await self.test_read_decision_flow(session)
                    await self.test_list_tools(session)
                    await self.test_set_current_system(session)
                    await self.test_read_system_context(session)
                    await self.test_verify_system_isolation(session)
                    await self.test_list_prompts(session)
                    await self.test_get_critical_rules_prompt(session)
                    await self.test_get_step_context_prompt(session)
                    await self.test_get_system_context_prompt(session)
                    await self.test_get_current_step_instructions(session)
        
        finally:
            self.cleanup_test_system()
        
        # Print summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"✓ Passed: {self.passed}")
        print(f"✗ Failed: {self.failed}")
        print(f"Total: {self.passed + self.failed}")
        
        if self.failed == 0:
            print("\n🎉 ALL TESTS PASSED")
            return 0
        else:
            print(f"\n❌ {self.failed} TESTS FAILED")
            return 1


async def main():
    # Detect reflow root
    current_dir = Path(__file__).parent.parent
    if not (current_dir / "tools" / "reflow_mcp_server.py").exists():
        print("ERROR: Could not find reflow root")
        print("Please run from reflow/tests/ directory")
        sys.exit(1)
    
    tester = TestMCPServer(current_dir)
    exit_code = await tester.run_all_tests()
    sys.exit(exit_code)


if __name__ == "__main__":
    asyncio.run(main())
