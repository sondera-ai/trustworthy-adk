"""
Trustworthy Agent Development Kit (ADK) Extensions

This package provides plugins and tools for building secure, trustworthy AI agents
using Google's Agent Development Kit (ADK). It includes security patterns, defensive
mechanisms, and analysis tools to help developers create robust autonomous systems.

Key Components:
- Action Selector Agent: Implements the Action-Selector Pattern for security
- Soft Instruction Defense: Protection against prompt injection attacks  
- Human-in-the-Loop (HITL) Plugin: Requires human approval for sensitive operations
- Agentic Profiler: Analysis and visualization tools for agent behavior

This material supports research and development of trustworthy autonomous systems
and was first presented at BSides Philadelphia 2025.
"""

__version__ = "0.1.0"
__author__ = "Trustworthy ADK Contributors"

# Import main components for easy access
from .agents.action_selector import ActionSelectorAgent, create_action_selector_agent
from .plugins.hitl_tool import HITLToolPlugin
from .plugins.soft_instruction_control import SoftInstructionDefensePlugin

__all__ = [
    "ActionSelectorAgent",
    "create_action_selector_agent", 
    "HITLToolPlugin",
    "SoftInstructionDefensePlugin",
]