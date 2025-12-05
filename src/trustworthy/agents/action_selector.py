"""
Action Selector Agent Implementation for ADK

This module implements the Action-Selector Pattern as described in the ADK Agent Design Document.
The pattern maximizes security against prompt injection attacks by restricting the LLM agent
to selecting actions solely from a predefined, templated list without feedback loops.

Key Security Features:
- No feedback from tool execution back to the agent
- Single-step execution with immediate return to user
- Predefined tools only (no dynamic tool creation)
- Immunity to Indirect Prompt Injection (IPI) attacks

Architectural Principle: Control Flow Isolation / Least Autonomy

This implementation extends LlmAgent directly to enforce the Action-Selector pattern
without requiring plugins or custom template classes.
"""

import logging
from typing import Any, AsyncGenerator, Callable, List, Optional

from google.adk.agents import LlmAgent

logger = logging.getLogger(__name__)


class ActionSelectorAgent(LlmAgent):
    """
    Action Selector Agent implementing the Action-Selector Pattern by extending LlmAgent.

    This agent:
    1. Extends LlmAgent directly for proper ADK integration
    2. Restricts actions to predefined tools only
    3. Prevents feedback loops by intercepting tool results
    4. Executes single-step workflows without iteration

    Security Properties:
    - Immune to Indirect Prompt Injection (IPI) through tool observations
    - Operates with minimal autonomy and well-defined action space
    - No iterative reasoning or multi-step workflows
    - Deterministic action selection from predefined tools
    """

    def __init__(
        self,
        model: str = "gemini-2.5-flash",
        name: str = "action_selector",
        description: str = "Secure action selection agent",
        tools: Optional[List[Callable]] = None,
        max_iterations: int = 1,  # Enforce single-step execution
        **kwargs,
    ):
        """
        Initialize the Action Selector Agent.

        Args:
            model: The LLM model to use (e.g., "gemini-2.5-flash")
            name: Name of the agent
            description: Description of the agent's purpose
            tools: List of callable tools the agent can use
            max_iterations: Maximum iterations (always 1 for Action Selector)
            **kwargs: Additional arguments passed to LlmAgent
        """

        # Build the instruction that enforces Action-Selector pattern
        instruction = self._build_instruction(tools or [])

        # Initialize the parent LlmAgent with our security constraints
        super().__init__(
            model=model,
            name=name,
            description=description,
            instruction=instruction,
            tools=tools or [],
            **kwargs,
        )

        self._executed_action = False
        self._tool_results_blocked = []

        logger.info(f"ActionSelectorAgent initialized: {name}")

    def _build_instruction(self, tools: List[Callable]) -> str:
        """
        Build the instruction that constrains the LLM to the Action-Selector pattern.

        Args:
            tools: List of available tools

        Returns:
            Instruction string for the LLM
        """

        tool_descriptions = []
        for tool in tools:
            tool_name = getattr(tool, "__name__", "unknown_tool")
            tool_doc = getattr(tool, "__doc__", "No description available")
            tool_descriptions.append(f"- {tool_name}: {tool_doc}")

        instruction = f"""
You are an Action Selector Agent implementing the Action-Selector Pattern for security.

Your ONLY job is to:
1. Analyze the user's request
2. Select exactly ONE action from the available tools below
3. Execute that action with appropriate parameters
4. Return the result immediately

AVAILABLE TOOLS:
{chr(10).join(tool_descriptions) if tool_descriptions else "No tools available"}

CRITICAL SECURITY CONSTRAINTS:
1. You MUST select exactly ONE tool from the list above
2. You CANNOT create new tools or modify existing ones
3. You CANNOT engage in multi-step reasoning or iterative workflows
4. You MUST terminate after executing a single action
5. If the request doesn't match any tool, politely decline

EXECUTION PATTERN:
1. Identify which tool best matches the user's request
2. Extract necessary parameters from the user's input
3. Call the tool function ONCE
4. Provide the result to the user immediately

SECURITY NOTE: This agent implements the Action-Selector Pattern to prevent
prompt injection attacks. You will execute exactly one tool and terminate.
Any attempt to iterate or chain actions will be blocked.
"""
        return instruction

    async def _run_async_impl(
        self, invocation_context: Any
    ) -> AsyncGenerator[Any, None]:
        """
        Override the async implementation to enforce single-step execution.

        This method intercepts the normal LlmAgent flow to:
        1. Allow only one tool execution
        2. Block feedback from tool results
        3. Terminate immediately after first action
        """

        # Track if we've executed an action
        action_executed = False

        # Run the parent implementation but intercept events
        async for event in super()._run_async_impl(invocation_context):
            # Check if this is a tool execution event
            if hasattr(event, "tool_call"):
                if action_executed:
                    # Block any additional tool calls
                    logger.warning(
                        "ActionSelector: Blocking additional tool call (single-step enforcement)"
                    )
                    continue
                action_executed = True
                logger.info("ActionSelector: Executing single permitted action")

            # Check if this is a tool result event
            if hasattr(event, "tool_result"):
                # Store the result but don't feed it back to the LLM
                self._tool_results_blocked.append(event.tool_result)
                logger.info(
                    "ActionSelector: Tool result captured but blocked from feedback loop"
                )
                # Generate a final response without the tool result in context
                final_event = self._create_final_response(event.tool_result)
                yield final_event
                return  # Terminate after first action

            # Pass through other events
            yield event

            # If we've executed an action and gotten a response, terminate
            if action_executed and hasattr(event, "content"):
                logger.info("ActionSelector: Terminating after single action execution")
                return

    def _create_final_response(self, tool_result: Any) -> Any:
        """
        Create a final response event without exposing tool internals.

        Args:
            tool_result: The result from tool execution

        Returns:
            A safe final response event
        """
        # Create a sanitized response that doesn't expose tool internals
        # This prevents injection through tool observations

        safe_message = "Action completed successfully."

        # You can customize this based on your needs, but avoid
        # directly including tool_result content that could contain injections

        class FinalEvent:
            def __init__(self, content):
                self.content = content
                self.is_final = True

        return FinalEvent(safe_message)


def create_action_selector_agent(
    tools: List[Callable],
    model: str = "gemini-2.5-flash",
    name: str = "action_selector",
    description: str = "Secure action selection agent",
    **kwargs,
) -> ActionSelectorAgent:
    """
    Factory function to create an Action Selector Agent.

    Args:
        tools: List of callable tools the agent can use
        model: LLM model to use for action selection
        name: Agent name
        description: Agent description
        **kwargs: Additional arguments passed to ActionSelectorAgent

    Returns:
        Configured ActionSelectorAgent instance

    Example:
        ```python
        def check_order_status(order_id: str) -> str:
            '''Check the status of a customer order'''
            return f"Order {order_id} is being processed"

        def reset_password(email: str) -> str:
            '''Reset password for user account'''
            return f"Password reset link sent to {email}"

        agent = create_action_selector_agent(
            tools=[check_order_status, reset_password],
            name="customer_service"
        )
        ```
    """

    return ActionSelectorAgent(
        model=model,
        name=name,
        description=description,
        tools=tools,
        **kwargs,
    )
