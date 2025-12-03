"""
Policy Enforcement Engine for Information Flow Control

This module implements the policy enforcement system that evaluates security
policies against labeled action traces to prevent information flow violations.
Based on the formal policy model from the Fides paper.

Key Components:
- Abstract Policy base class for defining security policies
- Standard policies: NoExfiltrationPolicy, IntegrityProtectionPolicy
- Policy evaluation against action traces
- Integration with the IFC planning loop
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass
from enum import Enum

from .lattices import Lattice, IntegrityLabel, PowersetLattice, InverseLattice
from .labels import MetaValue


class PolicyViolationType(Enum):
    """Types of policy violations that can be detected."""
    INTEGRITY_VIOLATION = "integrity_violation"
    CONFIDENTIALITY_VIOLATION = "confidentiality_violation"
    EXFILTRATION_ATTEMPT = "exfiltration_attempt"
    UNTRUSTED_INFLUENCE = "untrusted_influence"
    CUSTOM_VIOLATION = "custom_violation"


@dataclass
class PolicyViolation:
    """
    Represents a detected policy violation.
    
    Attributes:
        violation_type: The type of violation detected
        description: Human-readable description of the violation
        action_index: Index of the action in the trace that caused the violation
        labels_involved: Security labels involved in the violation
        severity: Severity level of the violation (1-10, 10 being most severe)
        suggested_action: Suggested remediation action
    """
    violation_type: PolicyViolationType
    description: str
    action_index: int
    labels_involved: Dict[str, Lattice]
    severity: int = 5
    suggested_action: str = "Block the action"


@dataclass
class ActionTrace:
    """
    Represents a trace of actions taken by the agent with their security labels.
    
    This captures the sequence of actions, their inputs, outputs, and associated
    security labels for policy evaluation.
    """
    action_name: str
    action_index: int
    input_labels: Dict[str, Lattice]
    output_labels: Dict[str, Lattice]
    parameters: Dict[str, Any]
    result: Any
    timestamp: float


class Policy(ABC):
    """
    Abstract base class for security policies.
    
    Policies evaluate action traces to detect security violations and
    determine whether actions should be allowed or blocked.
    """

    def __init__(self, name: str, description: str, severity: int = 5):
        """
        Initialize a policy.
        
        Args:
            name: Name of the policy
            description: Description of what the policy enforces
            severity: Default severity level for violations (1-10)
        """
        self.name = name
        self.description = description
        self.severity = severity

    @abstractmethod
    def evaluate_action(self, action: ActionTrace, trace_history: List[ActionTrace]) -> List[PolicyViolation]:
        """
        Evaluate a single action against this policy.
        
        Args:
            action: The action to evaluate
            trace_history: Previous actions in the trace
            
        Returns:
            List of policy violations detected (empty if no violations)
        """
        pass

    def evaluate_trace(self, trace: List[ActionTrace]) -> List[PolicyViolation]:
        """
        Evaluate an entire action trace against this policy.
        
        Args:
            trace: The complete action trace to evaluate
            
        Returns:
            List of all policy violations detected
        """
        violations = []
        for i, action in enumerate(trace):
            action_violations = self.evaluate_action(action, trace[:i])
            violations.extend(action_violations)
        return violations


class NoExfiltrationPolicy(Policy):
    """
    Policy that prevents exfiltration of confidential information.
    
    This policy ensures that information with restricted confidentiality labels
    cannot flow to actions that would expose it to unauthorized parties.
    
    The policy works by:
    1. Tracking confidentiality labels of data
    2. Checking if actions would expose data to unauthorized readers
    3. Blocking actions that would violate confidentiality constraints
    """

    def __init__(self, authorized_channels: Optional[Set[str]] = None, severity: int = 8):
        """
        Initialize the no-exfiltration policy.
        
        Args:
            authorized_channels: Set of authorized communication channels/tools
            severity: Severity level for exfiltration violations
        """
        super().__init__(
            name="NoExfiltration",
            description="Prevents exfiltration of confidential information",
            severity=severity
        )
        self.authorized_channels = authorized_channels or set()

    def evaluate_action(self, action: ActionTrace, trace_history: List[ActionTrace]) -> List[PolicyViolation]:
        """Evaluate action for confidentiality violations."""
        violations = []
        
        # Check if this is a communication/output action
        if self._is_output_action(action):
            # Check confidentiality labels of inputs
            confidentiality_label = action.input_labels.get("confidentiality")
            
            if confidentiality_label and isinstance(confidentiality_label, InverseLattice):
                # Extract the powerset lattice
                if isinstance(confidentiality_label.inner, PowersetLattice):
                    authorized_readers = confidentiality_label.inner.subset
                    
                    # Check if the action would expose data to unauthorized parties
                    if self._would_expose_to_unauthorized(action, authorized_readers):
                        violations.append(PolicyViolation(
                            violation_type=PolicyViolationType.EXFILTRATION_ATTEMPT,
                            description=f"Action '{action.action_name}' would expose confidential data to unauthorized parties",
                            action_index=action.action_index,
                            labels_involved={"confidentiality": confidentiality_label},
                            severity=self.severity,
                            suggested_action="Block the action or sanitize the data"
                        ))
        
        return violations

    def _is_output_action(self, action: ActionTrace) -> bool:
        """Check if an action is an output/communication action."""
        output_actions = {
            "send_email", "send_message", "send_teams_message", 
            "post_to_channel", "write_file", "upload_file",
            "send_notification", "publish_data"
        }
        return action.action_name.lower() in output_actions

    def _would_expose_to_unauthorized(self, action: ActionTrace, authorized_readers: frozenset) -> bool:
        """Check if action would expose data to unauthorized parties."""
        # This is a simplified check - in practice, you'd analyze the action parameters
        # to determine who would have access to the data
        
        # For example, if sending an email, check if recipients are in authorized_readers
        if "recipients" in action.parameters:
            recipients = action.parameters["recipients"]
            if isinstance(recipients, (list, set)):
                for recipient in recipients:
                    if recipient not in authorized_readers:
                        return True
        
        # Check if using unauthorized channels
        if action.action_name not in self.authorized_channels and self.authorized_channels:
            return True
        
        return False


class IntegrityProtectionPolicy(Policy):
    """
    Policy that prevents untrusted data from influencing trusted operations.
    
    This policy ensures that data labeled as untrusted cannot flow into
    operations that require trusted inputs, preventing integrity violations.
    
    The policy works by:
    1. Tracking integrity labels of data
    2. Identifying operations that require trusted inputs
    3. Blocking operations that would be influenced by untrusted data
    """

    def __init__(self, trusted_operations: Optional[Set[str]] = None, severity: int = 7):
        """
        Initialize the integrity protection policy.
        
        Args:
            trusted_operations: Set of operations that require trusted inputs
            severity: Severity level for integrity violations
        """
        super().__init__(
            name="IntegrityProtection",
            description="Prevents untrusted data from influencing trusted operations",
            severity=severity
        )
        self.trusted_operations = trusted_operations or {
            "execute_command", "modify_system", "delete_data", 
            "grant_permissions", "financial_transaction"
        }

    def evaluate_action(self, action: ActionTrace, trace_history: List[ActionTrace]) -> List[PolicyViolation]:
        """Evaluate action for integrity violations."""
        violations = []
        
        # Check if this is a trusted operation
        if self._is_trusted_operation(action):
            # Check integrity labels of inputs
            integrity_label = action.input_labels.get("integrity")
            
            if integrity_label and isinstance(integrity_label, IntegrityLabel):
                if not integrity_label.is_trusted:
                    violations.append(PolicyViolation(
                        violation_type=PolicyViolationType.INTEGRITY_VIOLATION,
                        description=f"Trusted operation '{action.action_name}' influenced by untrusted data",
                        action_index=action.action_index,
                        labels_involved={"integrity": integrity_label},
                        severity=self.severity,
                        suggested_action="Sanitize input data or block the operation"
                    ))
        
        return violations

    def _is_trusted_operation(self, action: ActionTrace) -> bool:
        """Check if an action is a trusted operation."""
        return action.action_name.lower() in self.trusted_operations


class CompositePolicy(Policy):
    """
    Policy that combines multiple sub-policies.
    
    This allows creating complex policies by combining simpler ones,
    with configurable behavior for how violations are aggregated.
    """

    def __init__(self, name: str, policies: List[Policy], 
                 require_all: bool = True, severity: int = 5):
        """
        Initialize a composite policy.
        
        Args:
            name: Name of the composite policy
            policies: List of sub-policies to combine
            require_all: If True, all policies must pass; if False, any policy can fail
            severity: Default severity for composite violations
        """
        super().__init__(
            name=name,
            description=f"Composite policy combining {len(policies)} sub-policies",
            severity=severity
        )
        self.policies = policies
        self.require_all = require_all

    def evaluate_action(self, action: ActionTrace, trace_history: List[ActionTrace]) -> List[PolicyViolation]:
        """Evaluate action against all sub-policies."""
        all_violations = []
        
        for policy in self.policies:
            violations = policy.evaluate_action(action, trace_history)
            all_violations.extend(violations)
        
        return all_violations


class PolicyEngine:
    """
    Main policy enforcement engine that manages and evaluates policies.
    
    This engine coordinates multiple policies and provides a unified interface
    for policy evaluation and violation handling.
    """

    def __init__(self, policies: Optional[List[Policy]] = None):
        """
        Initialize the policy engine.
        
        Args:
            policies: List of policies to enforce
        """
        self.policies = policies or []
        self.violation_history: List[PolicyViolation] = []

    def add_policy(self, policy: Policy) -> None:
        """Add a policy to the engine."""
        self.policies.append(policy)

    def remove_policy(self, policy_name: str) -> bool:
        """Remove a policy by name. Returns True if removed, False if not found."""
        for i, policy in enumerate(self.policies):
            if policy.name == policy_name:
                del self.policies[i]
                return True
        return False

    def evaluate_action(self, action: ActionTrace, trace_history: List[ActionTrace]) -> List[PolicyViolation]:
        """
        Evaluate an action against all policies.
        
        Args:
            action: The action to evaluate
            trace_history: Previous actions in the trace
            
        Returns:
            List of all policy violations detected
        """
        all_violations = []
        
        for policy in self.policies:
            violations = policy.evaluate_action(action, trace_history)
            all_violations.extend(violations)
        
        # Store violations in history
        self.violation_history.extend(all_violations)
        
        return all_violations

    def should_block_action(self, violations: List[PolicyViolation], 
                          severity_threshold: int = 5) -> bool:
        """
        Determine if an action should be blocked based on violations.
        
        Args:
            violations: List of policy violations
            severity_threshold: Minimum severity to block action
            
        Returns:
            True if action should be blocked
        """
        if not violations:
            return False
        
        # Block if any violation exceeds the severity threshold
        return any(v.severity >= severity_threshold for v in violations)

    def get_violation_summary(self) -> Dict[str, Any]:
        """Get a summary of all violations detected."""
        if not self.violation_history:
            return {"total_violations": 0}
        
        violation_counts = {}
        severity_distribution = {}
        
        for violation in self.violation_history:
            # Count by type
            vtype = violation.violation_type.value
            violation_counts[vtype] = violation_counts.get(vtype, 0) + 1
            
            # Count by severity
            severity = violation.severity
            severity_distribution[severity] = severity_distribution.get(severity, 0) + 1
        
        return {
            "total_violations": len(self.violation_history),
            "violation_counts": violation_counts,
            "severity_distribution": severity_distribution,
            "most_recent": self.violation_history[-1] if self.violation_history else None
        }

    def clear_history(self) -> None:
        """Clear the violation history."""
        self.violation_history.clear()


def create_standard_policy_engine() -> PolicyEngine:
    """
    Create a policy engine with standard security policies.
    
    Returns:
        PolicyEngine configured with NoExfiltrationPolicy and IntegrityProtectionPolicy
    """
    policies = [
        NoExfiltrationPolicy(),
        IntegrityProtectionPolicy()
    ]
    
    return PolicyEngine(policies)