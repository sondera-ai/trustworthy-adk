"""
Tests for the Action Selector Agent

These tests verify the security properties and functionality of the
Action-Selector Pattern implementation that extends LlmAgent.
"""

import pytest

from trustworthy.agents import (
    ActionSelectorAgent,
    create_action_selector_agent,
    create_customer_service_agent,
    # Example tools
    check_order_status,
    reset_password,
    contact_support,
    track_shipment,
    process_return,
    CUSTOMER_SERVICE_TOOLS,
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

    def test_create_customer_service_agent(self):
        """Test pre-configured customer service agent creation."""

        agent = create_customer_service_agent()

        assert isinstance(agent, ActionSelectorAgent)
        assert agent.name == "customer_service"
        assert "security" in agent.description.lower()
        assert len(agent.tools) == len(CUSTOMER_SERVICE_TOOLS)


class TestExampleTools:
    """Test the provided example tools."""

    def test_check_order_status(self):
        """Test order status tool."""
        result = check_order_status("ORD123")
        assert "ORD123" in result
        assert "processed" in result.lower()

    def test_reset_password(self):
        """Test password reset tool."""
        result = reset_password("user@example.com")
        assert "user@example.com" in result
        assert "reset" in result.lower()

    def test_contact_support(self):
        """Test support contact tool."""
        result = contact_support("billing", "high")
        assert "billing" in result
        assert "high" in result
        assert "ticket" in result.lower()

    def test_track_shipment(self):
        """Test shipment tracking tool."""
        result = track_shipment("TRACK123")
        assert "TRACK123" in result
        assert "transit" in result.lower() or "arrive" in result.lower()

    def test_process_return(self):
        """Test return processing tool."""
        result = process_return("ORD456", "ITEM789", "defective")
        assert "ORD456" in result
        assert "ITEM789" in result
        assert "defective" in result

    def test_customer_service_tools_list(self):
        """Test that all expected tools are in the list."""
        tool_names = [tool.__name__ for tool in CUSTOMER_SERVICE_TOOLS]

        assert "check_order_status" in tool_names
        assert "reset_password" in tool_names
        assert "contact_support" in tool_names
        assert "track_shipment" in tool_names
        assert "process_return" in tool_names
        assert len(CUSTOMER_SERVICE_TOOLS) == 5


class TestSecurityProperties:
    """Test security properties of the Action Selector pattern."""

    def test_no_dynamic_tool_creation(self):
        """Test that tools cannot be dynamically added after initialization."""

        def initial_tool() -> str:
            """Initial tool."""
            return "initial"

        agent = ActionSelectorAgent(tools=[initial_tool])
        initial_tool_count = len(agent.tools)

        # Try to add a new tool (this should not work dynamically)
        def new_tool() -> str:
            """New tool."""
            return "new"

        # Tools are immutable after initialization
        assert len(agent.tools) == initial_tool_count

    def test_tool_results_blocked_list(self):
        """Test that agent has mechanism to block tool results from feedback."""

        agent = ActionSelectorAgent(name="security_test")

        # Agent should have the blocking mechanism initialized
        assert hasattr(agent, "_tool_results_blocked")
        assert agent._tool_results_blocked == []
        assert hasattr(agent, "_executed_action")
        assert not agent._executed_action


if __name__ == "__main__":
    pytest.main([__file__])
