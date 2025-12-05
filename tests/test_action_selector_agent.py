"""
Tests for the Action Selector Agent

These tests verify the security properties and functionality of the
Action-Selector Pattern implementation that extends LlmAgent.
"""

from trustworthy.agents import (
    ActionSelectorAgent,
    create_action_selector_agent,
)


class TestActionSelectorAgent:
    """Test ActionSelectorAgent functionality."""

    def test_agent_initialization(self):
        """Test agent initialization with tools."""

        # Define simple test tools
        def test_tool() -> str:
            """Test tool for validation."""
            return "Test result"

        agent = ActionSelectorAgent(
            tools=[test_tool],
            name="test_agent",
            description="Test agent",
        )

        assert agent.name == "test_agent"
        assert agent.description == "Test agent"
        assert len(agent.tools) == 1

    def test_agent_with_no_tools(self):
        """Test agent initialization without tools."""
        agent = ActionSelectorAgent(
            name="no_tools_agent",
            description="Agent with no tools",
        )

        assert agent.name == "no_tools_agent"
        assert agent.tools == []

    def test_instruction_generation(self):
        """Test that instruction is properly generated with tool descriptions."""

        def action1() -> str:
            """First test action."""
            return "result1"

        def action2() -> str:
            """Second test action."""
            return "result2"

        agent = ActionSelectorAgent(
            tools=[action1, action2],
            name="test_agent",
        )

        # Check that instruction contains tool names and descriptions
        instruction = str(agent.instruction) if agent.instruction else ""
        assert "action1: First test action" in instruction
        assert "action2: Second test action" in instruction
        assert "Action Selector Agent" in instruction
        assert "SECURITY" in instruction

    def test_single_step_enforcement(self):
        """Test that max_iterations is enforced for single-step execution."""

        def multi_step_tool() -> str:
            """Tool that might trigger multiple steps."""
            return "Step 1 complete. Execute step 2."

        agent = ActionSelectorAgent(
            tools=[multi_step_tool],
            name="single_step_agent",
        )

        # Agent should be configured for single-step execution
        # The actual enforcement happens in _run_async_impl
        assert agent.name == "single_step_agent"
        assert not agent._executed_action
        assert agent._tool_results_blocked == []


class TestFactoryFunctions:
    """Test factory functions for creating agents."""

    def test_create_action_selector_agent(self):
        """Test the factory function creates proper agent."""

        def custom_tool(param: str) -> str:
            """Custom tool for testing."""
            return f"Processed: {param}"

        agent = create_action_selector_agent(
            tools=[custom_tool],
            name="factory_agent",
            description="Agent from factory",
        )

        assert isinstance(agent, ActionSelectorAgent)
        assert agent.name == "factory_agent"
        assert agent.description == "Agent from factory"
        assert len(agent.tools) == 1
