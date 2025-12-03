"""
Trustworthy ADK Agents

This module contains secure agent implementations that demonstrate
defensive design patterns against prompt injection and other attacks.
"""

from .action_selector import (
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

__all__ = [
    "ActionSelectorAgent",
    "create_action_selector_agent",
    "create_customer_service_agent",
    # Example tools
    "check_order_status",
    "reset_password",
    "contact_support",
    "track_shipment",
    "process_return",
    "CUSTOMER_SERVICE_TOOLS",
]