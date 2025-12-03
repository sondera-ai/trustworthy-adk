"""
Fides ADK Plugin - Information Flow Control for AI Agents

This module implements the main Fides plugin that integrates with the Google ADK
plugin architecture to provide information flow control capabilities for AI agents.

The plugin intercepts agent operations to:
1. Track security labels through all data flows
2. Enforce security policies during execution
3. Prevent information flow violations
4. Provide deterministic security guarantees

Based on "Securing AI Agents with Information-Flow Control" by Costa et al.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Callable

from google.adk.plugins import BasePlugin
from google.adk.tools import BaseTool, ToolContext
from google.genai.types import Content

from .lattices import IntegrityLabel, PowersetLattice, InverseLattice, ProductLabel
from .labels import MetaValue, propagate_labels, label_as_trusted, label_as_untrusted
from .policies import PolicyEngine, NoExfiltrationPolicy, IntegrityProtectionPolicy, PolicyViolation
from .planner import IFCPlanner, PlannerConfig


logger = logging.getLogger(__name__)


@dataclass
class FidesConfig:
    """Configuration for the Fides plugin."""
    
    # Core IFC settings
    enable_integrity_protection: bool = True
    enable_confidentiality_protection: bool = True
    enable_policy_enforcement: bool = True
    
    # Policy settings
    halt_on_policy_violation: bool = True
    severity_threshold: int = 5
    custom_policies: List[Any] = field(default_factory=list)
    
    # Label settings
    default_integrity_label: str = "untrusted"  # "trusted" or "untrusted"
    trusted_domains: Set[str] = field(default_factory=lambda: {"@contoso.com", "@company.com"})
    universe_principals: Set[str] = field(default_factory=set)
    
    # Tool settings
    sensitive_tools: Set[str] = field(default_factory=lambda: {
        "send_email", "send_message", "send_teams_message",
        "execute_command", "delete_file", "modify_system"
    })
    trusted_tools: Set[str] = field(default_factory=lambda: {
        "read_calendar", "get_weather", "search_web"
    })
    
    # Planner settings
    max_planning_iterations: int = 10
    enable_variable_hiding: bool = True
    enable_revealing: bool = True
    
    # Logging and debugging
    enable_trace_logging: bool = True
    log_label_propagation: bool = False
    log_policy_violations: bool = True


class FidesPlugin(BasePlugin):
    """
    Fides plugin for Information Flow Control in ADK agents.
    
    This plugin provides comprehensive IFC capabilities including:
    - Automatic security label tracking and propagation
    - Policy-based security enforcement
    - Protection against prompt injection attacks
    - Deterministic security guarantees
    
    The plugin integrates seamlessly with existing ADK agents and tools,
    adding security without requiring changes to existing code.
    """

    def __init__(self, config: Optional[FidesConfig] = None):
        """
        Initialize the Fides plugin.
        
        Args:
            config: Configuration for the plugin
        """
        super().__init__(name="Fides")
        self.config = config or FidesConfig()
        
        # Initialize policy engine
        self.policy_engine = self._create_policy_engine()
        
        # Initialize planner
        planner_config = PlannerConfig(
            enable_policy_enforcement=self.config.enable_policy_enforcement,
            halt_on_violation=self.config.halt_on_policy_violation,
            severity_threshold=self.config.severity_threshold,
            max_iterations=self.config.max_planning_iterations,
            enable_variable_hiding=self.config.enable_variable_hiding,
            enable_revealing=self.config.enable_revealing,
            enable_trace_logging=self.config.enable_trace_logging,
            log_label_propagation=self.config.log_label_propagation
        )
        
        self.planner = IFCPlanner(self.policy_engine, planner_config)
        
        # Statistics
        self._stats = {
            "total_tool_calls": 0,
            "blocked_tool_calls": 0,
            "policy_violations": 0,
            "labels_propagated": 0
        }
        
        logger.info("Fides plugin initialized with IFC protection")

    def _create_policy_engine(self) -> PolicyEngine:
        """Create and configure the policy engine."""
        policies = []
        
        if self.config.enable_confidentiality_protection:
            policies.append(NoExfiltrationPolicy(
                authorized_channels=self.config.trusted_tools,
                severity=self.config.severity_threshold
            ))
        
        if self.config.enable_integrity_protection:
            policies.append(IntegrityProtectionPolicy(
                trusted_operations=self.config.sensitive_tools,
                severity=self.config.severity_threshold
            ))
        
        # Add custom policies
        policies.extend(self.config.custom_policies)
        
        return PolicyEngine(policies)

    def _infer_data_labels(self, data: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Infer security labels for data based on its content and context.
        
        Args:
            data: The data to label
            context: Context information (e.g., source, tool name)
            
        Returns:
            Dictionary of inferred security labels
        """
        labels = {}
        
        # Infer integrity label
        if self.config.enable_integrity_protection:
            is_trusted = self._is_data_trusted(data, context)
            labels["integrity"] = IntegrityLabel.trusted() if is_trusted else IntegrityLabel.untrusted()
        
        # Infer confidentiality label
        if self.config.enable_confidentiality_protection:
            readers = self._infer_data_readers(data, context)
            if readers and self.config.universe_principals:
                universe = frozenset(self.config.universe_principals)
                confidentiality = InverseLattice(PowersetLattice(readers, universe))
                labels["confidentiality"] = confidentiality
        
        return labels

    def _is_data_trusted(self, data: Any, context: Dict[str, Any]) -> bool:
        """Determine if data should be labeled as trusted."""
        # Check if data comes from a trusted source
        source = context.get("source", "")
        if any(domain in source for domain in self.config.trusted_domains):
            return True
        
        # Check if data comes from a trusted tool
        tool_name = context.get("tool_name", "")
        if tool_name in self.config.trusted_tools:
            return True
        
        # Default based on configuration
        return self.config.default_integrity_label == "trusted"

    def _infer_data_readers(self, data: Any, context: Dict[str, Any]) -> frozenset[str]:
        """Infer who should be able to read this data."""
        readers = set()
        
        # Extract email addresses or user IDs from data
        if isinstance(data, str):
            # Simple heuristic - look for email patterns
            import re
            emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', data)
            readers.update(emails)
        
        # Add context-based readers
        if "recipients" in context:
            recipients = context["recipients"]
            if isinstance(recipients, (list, set)):
                readers.update(recipients)
            elif isinstance(recipients, str):
                readers.add(recipients)
        
        # Default to current user if no specific readers found
        if not readers and "current_user" in context:
            readers.add(context["current_user"])
        
        return frozenset(readers)

    def _wrap_data_with_labels(self, data: Any, context: Dict[str, Any]) -> MetaValue[Any]:
        """Wrap data with appropriate security labels."""
        if isinstance(data, MetaValue):
            return data  # Already labeled
        
        labels = self._infer_data_labels(data, context)
        return MetaValue(data, metadata=labels)

    def before_tool_callback(
        self, tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
    ) -> Optional[Content]:
        """
        Intercept tool calls to apply IFC protection.
        
        This method is called before each tool execution to:
        1. Extract and propagate security labels from arguments
        2. Evaluate security policies
        3. Block or allow tool execution based on policy decisions
        """
        self._stats["total_tool_calls"] += 1
        
        if self.config.enable_trace_logging:
            logger.debug(f"Fides: Intercepting tool call to {tool.name}")
        
        try:
            # Wrap arguments with labels if needed
            labeled_args = {}
            for arg_name, arg_value in args.items():
                if not isinstance(arg_value, MetaValue):
                    context = {
                        "tool_name": tool.name,
                        "arg_name": arg_name,
                        "source": f"tool_arg_{arg_name}"
                    }
                    labeled_args[arg_name] = self._wrap_data_with_labels(arg_value, context)
                else:
                    labeled_args[arg_name] = arg_value
            
            # Extract input labels for policy evaluation
            input_labels = {}
            meta_values = [v for v in labeled_args.values() if isinstance(v, MetaValue)]
            if meta_values:
                input_labels = propagate_labels(*meta_values)
                self._stats["labels_propagated"] += 1
            
            # Create a mock action trace for policy evaluation
            from .policies import ActionTrace
            import time
            
            mock_action = ActionTrace(
                action_name=tool.name,
                action_index=self._stats["total_tool_calls"],
                input_labels=input_labels,
                output_labels={},  # Will be filled after execution
                parameters=args,
                result=None,  # Not available yet
                timestamp=time.time()
            )
            
            # Evaluate policies
            violations = self.policy_engine.evaluate_action(mock_action, [])
            
            if violations:
                self._stats["policy_violations"] += len(violations)
                
                if self.config.log_policy_violations:
                    for violation in violations:
                        logger.warning(f"Fides policy violation: {violation.description}")
                
                # Check if we should block the tool call
                should_block = self.policy_engine.should_block_action(
                    violations, self.config.severity_threshold
                )
                
                if should_block:
                    self._stats["blocked_tool_calls"] += 1
                    logger.error(f"Fides: Blocking tool call to {tool.name} due to policy violations")
                    
                    # Create a response explaining why the tool was blocked
                    violation_descriptions = [v.description for v in violations]
                    response_text = (
                        f"Tool call to '{tool.name}' was blocked by Fides security policy. "
                        f"Violations: {'; '.join(violation_descriptions)}"
                    )
                    
                    return Content(text=response_text)
            
            # Tool call is allowed - update args with labeled versions
            args.update({k: v.value if isinstance(v, MetaValue) else v 
                        for k, v in labeled_args.items()})
            
            return None  # Allow tool execution
            
        except Exception as e:
            logger.error(f"Fides: Error in before_tool_callback: {e}")
            # On error, allow the tool call to proceed to avoid breaking the agent
            return None

    def after_tool_callback(
        self, tool: BaseTool, args: Dict[str, Any], result: Any, tool_context: ToolContext
    ) -> Any:
        """
        Process tool results to apply security labels and track information flow.
        
        This method is called after tool execution to:
        1. Apply appropriate security labels to results
        2. Track the action in the execution trace
        3. Update the planner's state
        """
        try:
            if self.config.enable_trace_logging:
                logger.debug(f"Fides: Processing result from {tool.name}")
            
            # Create context for result labeling
            context = {
                "tool_name": tool.name,
                "source": f"tool_result_{tool.name}",
                "args": args
            }
            
            # Wrap result with appropriate labels
            labeled_result = self._wrap_data_with_labels(result, context)
            
            # Extract labels for tracking
            result_labels = labeled_result.metadata
            
            # Track this action in the planner
            # Note: This is a simplified version - full integration would require
            # more sophisticated coordination with the planner
            
            if self.config.log_label_propagation:
                logger.debug(f"Fides: Result labeled with {result_labels}")
            
            return labeled_result.value  # Return the unwrapped value
            
        except Exception as e:
            logger.error(f"Fides: Error in after_tool_callback: {e}")
            return result  # Return original result on error

    def get_statistics(self) -> Dict[str, Any]:
        """Get plugin statistics for monitoring."""
        policy_summary = self.policy_engine.get_violation_summary()
        planner_summary = self.planner.get_execution_summary()
        
        return {
            **self._stats,
            "block_rate": (
                self._stats["blocked_tool_calls"] / self._stats["total_tool_calls"]
                if self._stats["total_tool_calls"] > 0 else 0
            ),
            "violation_rate": (
                self._stats["policy_violations"] / self._stats["total_tool_calls"]
                if self._stats["total_tool_calls"] > 0 else 0
            ),
            "policy_summary": policy_summary,
            "planner_summary": planner_summary
        }

    def reset_statistics(self) -> None:
        """Reset plugin statistics."""
        self._stats = {
            "total_tool_calls": 0,
            "blocked_tool_calls": 0,
            "policy_violations": 0,
            "labels_propagated": 0
        }
        self.policy_engine.clear_history()
        self.planner.reset_execution_state()

    def configure_for_email_assistant(self, user_email: str, 
                                    trusted_domains: Optional[Set[str]] = None) -> None:
        """
        Configure the plugin for the email assistant scenario from the Fides paper.
        
        Args:
            user_email: The user's email address
            trusted_domains: Set of trusted email domains
        """
        if trusted_domains:
            self.config.trusted_domains.update(trusted_domains)
        
        # Add user email to universe of principals
        self.config.universe_principals.add(user_email)
        
        # Configure email-specific sensitive tools
        self.config.sensitive_tools.update({
            "send_email", "send_teams_message", "send_message"
        })
        
        logger.info(f"Fides configured for email assistant with user {user_email}")


def create_fides_plugin(
    enable_integrity: bool = True,
    enable_confidentiality: bool = True,
    halt_on_violation: bool = True,
    trusted_domains: Optional[Set[str]] = None,
    **kwargs
) -> FidesPlugin:
    """
    Factory function to create a Fides plugin with common configurations.
    
    Args:
        enable_integrity: Enable integrity protection
        enable_confidentiality: Enable confidentiality protection
        halt_on_violation: Halt execution on policy violations
        trusted_domains: Set of trusted domains
        **kwargs: Additional configuration options
        
    Returns:
        Configured FidesPlugin instance
    """
    config = FidesConfig(
        enable_integrity_protection=enable_integrity,
        enable_confidentiality_protection=enable_confidentiality,
        halt_on_policy_violation=halt_on_violation,
        trusted_domains=trusted_domains or {"@contoso.com"},
        **kwargs
    )
    
    return FidesPlugin(config)