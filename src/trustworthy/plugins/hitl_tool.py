from typing import Any, Dict, List, Optional

from google.adk.plugins import BasePlugin
from google.adk.tools import BaseTool, ToolContext
from google.adk.types import Content


class HITLToolPlugin(BasePlugin):
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
