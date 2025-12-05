"""
Human-in-the-Loop (HITL) Tool Plugin for ADK

This plugin implements a Human-in-the-Loop pattern that requires human approval
before executing sensitive or high-risk tools. It helps prevent unauthorized
actions by pausing execution and requesting user confirmation.
"""

from typing import Any, Dict, List, Optional

from google.adk.plugins import BasePlugin
from google.adk.tools import BaseTool, ToolContext
from google.adk.types import Content


class HITLToolPlugin(BasePlugin):
    """
    Human-in-the-Loop Tool Plugin
    
    This plugin intercepts tool calls for specified sensitive tools and requires
    human approval before allowing execution. It provides an additional security
    layer for high-risk operations.
    
    Example:
        ```python
        # Create plugin that requires approval for sensitive tools
        hitl_plugin = HITLToolPlugin(
            sensitive_tools=["delete_user", "transfer_funds", "send_email"]
        )
        
        # Add to agent
        agent = LlmAgent(
            model="gemini-2.5-flash",
            tools=[delete_user, transfer_funds, send_email],
            plugins=[hitl_plugin]
        )
        ```
    """
    def __init__(self, sensitive_tools: List[str]):
        """
        Args:
            sensitive_tools: A list of tool names that require human approval.
        """
        self.sensitive_tools = sensitive_tools

    def before_tool_callback(
        self, tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
    ) -> Optional[Content]:
        # 1. Check if the tool is on the sensitive list
        if tool.name not in self.sensitive_tools:
            return None

        # 2. Check for existing confirmation
        confirmation = tool_context.tool_confirmation

        # 3. SCENARIO A: Request Confirmation (First Pass)
        if confirmation is None:
            # Dynamic hint generation based on the specific tool call
            # Example: "Allow tool 'delete_user' with arguments: {'user_id': '123'}?"
            dynamic_hint = f"Allow tool '{tool.name}' with arguments: {args}?"

            print(f"[HITLPlugin] Pausing for confirmation: {dynamic_hint}")

            # We provide the hint but omit a complex custom payload.
            # Passing a simple dict or None often defaults to a standard confirmation in client UIs.
            # Here we use a minimal indicator that we just need a boolean response.
            tool_context.request_confirmation(hint=dynamic_hint)
            return None

        # 4. SCENARIO B: Process Response (Second Pass)
        # We accept the confirmation if the payload is present or explicitly true
        if confirmation.confirmed:
            return None  # Allow tool execution
        else:
            return Content(text=f"User rejected the request to run {tool.name}.")
