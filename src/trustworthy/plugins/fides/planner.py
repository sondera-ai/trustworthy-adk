"""
IFC-Instrumented Planning Loop for Secure Agent Execution

This module implements the planning loop with dynamic taint tracking as described
in the Fides paper. It extends the standard agent planning loop to track security
labels and enforce policies during execution.

Key Components:
- IFCPlanner: Main planner with information flow control
- ActionTracker: Tracks actions and their security labels
- Integration with ADK agent architecture
- Policy enforcement during planning
"""

import logging
import time
from typing import Any, Dict, List, Optional, Callable, AsyncGenerator, Tuple
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

from .lattices import Lattice, join_labels
from .labels import MetaValue, propagate_labels
from .policies import PolicyEngine, ActionTrace, PolicyViolation, PolicyViolationType


logger = logging.getLogger(__name__)


@dataclass
class PlannerConfig:
    """Configuration for the IFC planner."""
    
    # Policy enforcement settings
    enable_policy_enforcement: bool = True
    halt_on_violation: bool = True
    severity_threshold: int = 5
    
    # Label tracking settings
    track_all_labels: bool = True
    default_label_types: List[str] = field(default_factory=lambda: ["integrity", "confidentiality"])
    
    # Planning loop settings
    max_iterations: int = 10
    enable_variable_hiding: bool = True
    enable_revealing: bool = True
    
    # Logging and debugging
    enable_trace_logging: bool = True
    log_label_propagation: bool = False


class ActionTracker:
    """
    Tracks actions and their associated security labels during planning.
    
    This class maintains the action trace that is used for policy evaluation
    and provides utilities for label propagation and tracking.
    """

    def __init__(self, config: PlannerConfig):
        """Initialize the action tracker."""
        self.config = config
        self.action_trace: List[ActionTrace] = []
        self.variable_store: Dict[str, MetaValue[Any]] = {}
        self.hidden_variables: set[str] = set()

    def track_action(self, action_name: str, parameters: Dict[str, Any], 
                    input_labels: Dict[str, Lattice], result: Any,
                    output_labels: Dict[str, Lattice]) -> ActionTrace:
        """
        Track a new action in the trace.
        
        Args:
            action_name: Name of the action/tool being executed
            parameters: Parameters passed to the action
            input_labels: Security labels of the inputs
            result: Result of the action
            output_labels: Security labels of the outputs
            
        Returns:
            The created ActionTrace
        """
        action = ActionTrace(
            action_name=action_name,
            action_index=len(self.action_trace),
            input_labels=input_labels,
            output_labels=output_labels,
            parameters=parameters,
            result=result,
            timestamp=time.time()
        )
        
        self.action_trace.append(action)
        
        if self.config.enable_trace_logging:
            logger.info(f"Tracked action {action.action_index}: {action_name}")
            if self.config.log_label_propagation:
                logger.debug(f"Input labels: {input_labels}")
                logger.debug(f"Output labels: {output_labels}")
        
        return action

    def store_variable(self, var_name: str, value: MetaValue[Any], 
                      should_hide: bool = False) -> None:
        """
        Store a labeled variable in the variable store.
        
        Args:
            var_name: Name of the variable
            value: The labeled value to store
            should_hide: Whether to hide this variable from future tool calls
        """
        self.variable_store[var_name] = value
        
        if should_hide and self.config.enable_variable_hiding:
            self.hidden_variables.add(var_name)
            logger.debug(f"Variable {var_name} hidden from future tool calls")

    def get_variable(self, var_name: str) -> Optional[MetaValue[Any]]:
        """Get a variable from the store."""
        return self.variable_store.get(var_name)

    def is_variable_hidden(self, var_name: str) -> bool:
        """Check if a variable is hidden."""
        return var_name in self.hidden_variables

    def reveal_variable(self, var_name: str) -> bool:
        """
        Reveal a previously hidden variable.
        
        Args:
            var_name: Name of the variable to reveal
            
        Returns:
            True if variable was revealed, False if not found or not hidden
        """
        if var_name in self.hidden_variables:
            self.hidden_variables.remove(var_name)
            logger.debug(f"Variable {var_name} revealed")
            return True
        return False

    def get_trace_summary(self) -> Dict[str, Any]:
        """Get a summary of the action trace."""
        return {
            "total_actions": len(self.action_trace),
            "action_names": [a.action_name for a in self.action_trace],
            "variables_stored": len(self.variable_store),
            "hidden_variables": len(self.hidden_variables)
        }


class IFCPlanner:
    """
    Information Flow Control Planner with dynamic taint tracking.
    
    This planner extends the standard agent planning loop to:
    1. Track security labels through all operations
    2. Enforce security policies during execution
    3. Implement variable hiding and revealing mechanisms
    4. Provide deterministic security guarantees
    """

    def __init__(self, policy_engine: PolicyEngine, config: Optional[PlannerConfig] = None):
        """
        Initialize the IFC planner.
        
        Args:
            policy_engine: Policy engine for security enforcement
            config: Configuration for the planner
        """
        self.policy_engine = policy_engine
        self.config = config or PlannerConfig()
        self.action_tracker = ActionTracker(self.config)
        self.execution_halted = False
        self.halt_reason: Optional[str] = None

    def extract_input_labels(self, tool_args: Dict[str, Any]) -> Dict[str, Lattice]:
        """
        Extract and propagate security labels from tool arguments.
        
        Args:
            tool_args: Arguments passed to a tool
            
        Returns:
            Dictionary of propagated security labels
        """
        meta_values = []
        
        # Extract MetaValues from arguments
        for arg_name, arg_value in tool_args.items():
            if isinstance(arg_value, MetaValue):
                meta_values.append(arg_value)
            elif isinstance(arg_value, (list, tuple)):
                for item in arg_value:
                    if isinstance(item, MetaValue):
                        meta_values.append(item)
            elif isinstance(arg_value, dict):
                for item in arg_value.values():
                    if isinstance(item, MetaValue):
                        meta_values.append(item)
        
        # Also check variables referenced in arguments
        for arg_name, arg_value in tool_args.items():
            if isinstance(arg_value, str) and arg_value in self.action_tracker.variable_store:
                var_value = self.action_tracker.get_variable(arg_value)
                if var_value:
                    meta_values.append(var_value)
        
        # Propagate labels
        if meta_values:
            return propagate_labels(*meta_values, label_types=self.config.default_label_types)
        else:
            return {}

    def create_output_labels(self, input_labels: Dict[str, Lattice], 
                           tool_name: str, result: Any) -> Dict[str, Lattice]:
        """
        Create output labels for tool results based on input labels and tool semantics.
        
        Args:
            input_labels: Labels from the tool inputs
            tool_name: Name of the tool being executed
            result: Result of the tool execution
            
        Returns:
            Dictionary of output security labels
        """
        # Default: propagate input labels to output
        output_labels = input_labels.copy()
        
        # Tool-specific label transformations
        if tool_name.lower() in ["read_emails", "read_file", "fetch_data"]:
            # Reading operations might introduce new labels based on data source
            # This would be customized based on the specific tool semantics
            pass
        elif tool_name.lower() in ["send_email", "send_message", "write_file"]:
            # Output operations typically preserve input labels
            pass
        
        return output_labels

    def evaluate_action_policies(self, action: ActionTrace) -> List[PolicyViolation]:
        """
        Evaluate an action against all policies.
        
        Args:
            action: The action to evaluate
            
        Returns:
            List of policy violations detected
        """
        return self.policy_engine.evaluate_action(action, self.action_tracker.action_trace[:-1])

    def should_halt_execution(self, violations: List[PolicyViolation]) -> Tuple[bool, Optional[str]]:
        """
        Determine if execution should be halted based on policy violations.
        
        Args:
            violations: List of policy violations
            
        Returns:
            Tuple of (should_halt, reason)
        """
        if not self.config.halt_on_violation:
            return False, None
        
        critical_violations = [v for v in violations if v.severity >= self.config.severity_threshold]
        
        if critical_violations:
            reasons = [f"{v.violation_type.value}: {v.description}" for v in critical_violations]
            return True, "; ".join(reasons)
        
        return False, None

    async def execute_tool_with_ifc(self, tool_name: str, tool_callable: Callable, 
                                  tool_args: Dict[str, Any]) -> Tuple[Any, bool]:
        """
        Execute a tool with information flow control.
        
        Args:
            tool_name: Name of the tool
            tool_callable: The tool function to execute
            tool_args: Arguments for the tool
            
        Returns:
            Tuple of (result, execution_allowed)
        """
        if self.execution_halted:
            logger.warning(f"Execution halted, skipping tool {tool_name}")
            return None, False

        # Extract input labels
        input_labels = self.extract_input_labels(tool_args)
        
        # Execute the tool (this would be the actual tool execution)
        try:
            result = await tool_callable(**tool_args) if callable(tool_callable) else tool_callable
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            result = f"Error: {str(e)}"

        # Create output labels
        output_labels = self.create_output_labels(input_labels, tool_name, result)

        # Track the action
        action = self.action_tracker.track_action(
            action_name=tool_name,
            parameters=tool_args,
            input_labels=input_labels,
            result=result,
            output_labels=output_labels
        )

        # Evaluate policies
        violations = self.evaluate_action_policies(action)
        
        if violations:
            logger.warning(f"Policy violations detected for {tool_name}: {len(violations)} violations")
            for violation in violations:
                logger.warning(f"  - {violation.description}")

        # Check if execution should be halted
        should_halt, halt_reason = self.should_halt_execution(violations)
        
        if should_halt:
            self.execution_halted = True
            self.halt_reason = halt_reason
            logger.error(f"Execution halted: {halt_reason}")
            return None, False

        # Store result as a variable if it's a MetaValue or create one
        if isinstance(result, MetaValue):
            result_var = result
        else:
            result_var = MetaValue(result, metadata=output_labels)

        # Generate a variable name for the result
        var_name = f"result_{action.action_index}"
        
        # Determine if variable should be hidden based on policy
        should_hide = self._should_hide_variable(result_var, violations)
        
        self.action_tracker.store_variable(var_name, result_var, should_hide)

        return result, True

    def _should_hide_variable(self, variable: MetaValue[Any], 
                            violations: List[PolicyViolation]) -> bool:
        """
        Determine if a variable should be hidden based on its labels and violations.
        
        Args:
            variable: The variable to check
            violations: Any policy violations associated with this variable
            
        Returns:
            True if the variable should be hidden
        """
        if not self.config.enable_variable_hiding:
            return False

        # Hide if there were policy violations
        if violations:
            return True

        # Hide if the variable contains sensitive information
        # This would be customized based on specific label semantics
        integrity_label = variable.get_label("integrity")
        if integrity_label and hasattr(integrity_label, 'is_trusted') and not integrity_label.is_trusted:
            return True

        return False

    def get_execution_summary(self) -> Dict[str, Any]:
        """Get a summary of the execution state."""
        return {
            "execution_halted": self.execution_halted,
            "halt_reason": self.halt_reason,
            "trace_summary": self.action_tracker.get_trace_summary(),
            "policy_summary": self.policy_engine.get_violation_summary()
        }

    def reset_execution_state(self) -> None:
        """Reset the execution state for a new planning session."""
        self.execution_halted = False
        self.halt_reason = None
        self.action_tracker = ActionTracker(self.config)
        self.policy_engine.clear_history()


class IFCAgent:
    """
    Agent wrapper that integrates IFC planning with ADK agents.
    
    This class provides a bridge between the IFC planner and the ADK agent
    architecture, allowing existing agents to be enhanced with information
    flow control capabilities.
    """

    def __init__(self, base_agent: Any, planner: IFCPlanner):
        """
        Initialize the IFC agent.
        
        Args:
            base_agent: The base ADK agent to enhance
            planner: The IFC planner to use
        """
        self.base_agent = base_agent
        self.planner = planner

    async def run_with_ifc(self, *args, **kwargs) -> Any:
        """
        Run the agent with IFC protection.
        
        This method intercepts the agent's execution to add IFC capabilities.
        """
        # Reset planner state
        self.planner.reset_execution_state()
        
        # This would integrate with the actual ADK agent execution
        # For now, this is a placeholder that shows the integration pattern
        logger.info("Starting IFC-protected agent execution")
        
        try:
            # The actual integration would intercept tool calls and route them
            # through the IFC planner's execute_tool_with_ifc method
            result = await self.base_agent.run(*args, **kwargs)
            
            # Log execution summary
            summary = self.planner.get_execution_summary()
            logger.info(f"IFC execution completed: {summary}")
            
            return result
            
        except Exception as e:
            logger.error(f"IFC agent execution failed: {e}")
            raise