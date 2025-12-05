"""
Trustworthy ADK Plugins

This module contains security-focused plugins for Google ADK agents.
These plugins implement defensive mechanisms to protect against various
attack vectors including prompt injection, unauthorized tool usage, and more.
"""

from .hitl_tool import HITLToolPlugin
from .soft_instruction_control import SoftInstructionDefensePlugin

__all__ = [
    "HITLToolPlugin",
    "SoftInstructionDefensePlugin",
]