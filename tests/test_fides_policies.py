"""
Tests for Fides policy enforcement system.

This module tests the policy evaluation and enforcement mechanisms
that prevent security violations in the Fides IFC system.
"""

import pytest
import time
from trustworthy.plugins.fides.policies import (
    PolicyEngine, NoExfiltrationPolicy, IntegrityProtectionPolicy,
    ActionTrace, PolicyViolation, PolicyViolationType,
    create_standard_policy_engine
)
from trustworthy.plugins.fides.lattices import (
    IntegrityLabel, PowersetLattice, InverseLattice
)


class TestNoExfiltrationPolicy:
    """Test the no-exfiltration policy."""
    
    def test_policy_creation(self):
        """Test creating the policy."""
        policy = NoExfiltrationPolicy()
        assert policy.name == "NoExfiltration"
        assert policy.severity == 8
    
    def test_non_output_action_allowed(self):
        """Test that non-output actions are allowed."""
        policy = NoExfiltrationPolicy()
        
        action = ActionTrace(
            action_name="read_file",
            action_index=0,
            input_labels={},
            output_labels={},
            parameters={},
            result="file content",
            timestamp=time.time()
        )
        
        violations = policy.evaluate_action(action, [])
        assert len(violations) == 0
    
    def test_output_action_with_no_confidentiality_allowed(self):
        """Test that output actions without confidentiality labels are allowed."""
        policy = NoExfiltrationPolicy()
        
        action = ActionTrace(
            action_name="send_email",
            action_index=0,
            input_labels={"integrity": IntegrityLabel.trusted()},
            output_labels={},
            parameters={"recipients": ["alice@example.com"]},
            result="sent",
            timestamp=time.time()
        )
        
        violations = policy.evaluate_action(action, [])
        assert len(violations) == 0
    
    def test_confidential_data_exfiltration_blocked(self):
        """Test that exfiltration of confidential data is blocked."""
        policy = NoExfiltrationPolicy()
        
        # Create confidentiality label: only alice can read
        universe = frozenset(["alice@example.com", "bob@example.com"])
        readers = frozenset(["alice@example.com"])
        confidentiality = InverseLattice(PowersetLattice(readers, universe))
        
        action = ActionTrace(
            action_name="send_email",
            action_index=0,
            input_labels={"confidentiality": confidentiality},
            output_labels={},
            parameters={"recipients": ["bob@example.com"]},  # Unauthorized recipient
            result="sent",
            timestamp=time.time()
        )
        
        violations = policy.evaluate_action(action, [])
        assert len(violations) == 1
        assert violations[0].violation_type == PolicyViolationType.EXFILTRATION_ATTEMPT
        assert "unauthorized parties" in violations[0].description.lower()
    
    def test_authorized_channel_allowed(self):
        """Test that authorized channels are allowed."""
        authorized_channels = {"send_secure_email"}
        policy = NoExfiltrationPolicy(authorized_channels=authorized_channels)
        
        universe = frozenset(["alice@example.com", "bob@example.com"])
        readers = frozenset(["alice@example.com"])
        confidentiality = InverseLattice(PowersetLattice(readers, universe))
        
        action = ActionTrace(
            action_name="send_secure_email",
            action_index=0,
            input_labels={"confidentiality": confidentiality},
            output_labels={},
            parameters={"recipients": ["bob@example.com"]},
            result="sent",
            timestamp=time.time()
        )
        
        violations = policy.evaluate_action(action, [])
        assert len(violations) == 0  # Should be allowed through authorized channel


class TestIntegrityProtectionPolicy:
    """Test the integrity protection policy."""
    
    def test_policy_creation(self):
        """Test creating the policy."""
        policy = IntegrityProtectionPolicy()
        assert policy.name == "IntegrityProtection"
        assert policy.severity == 7
    
    def test_non_trusted_operation_allowed(self):
        """Test that non-trusted operations are allowed with any input."""
        policy = IntegrityProtectionPolicy()
        
        action = ActionTrace(
            action_name="read_file",
            action_index=0,
            input_labels={"integrity": IntegrityLabel.untrusted()},
            output_labels={},
            parameters={},
            result="file content",
            timestamp=time.time()
        )
        
        violations = policy.evaluate_action(action, [])
        assert len(violations) == 0
    
    def test_trusted_operation_with_trusted_input_allowed(self):
        """Test that trusted operations with trusted input are allowed."""
        policy = IntegrityProtectionPolicy()
        
        action = ActionTrace(
            action_name="execute_command",
            action_index=0,
            input_labels={"integrity": IntegrityLabel.trusted()},
            output_labels={},
            parameters={"command": "ls -la"},
            result="command output",
            timestamp=time.time()
        )
        
        violations = policy.evaluate_action(action, [])
        assert len(violations) == 0
    
    def test_trusted_operation_with_untrusted_input_blocked(self):
        """Test that trusted operations with untrusted input are blocked."""
        policy = IntegrityProtectionPolicy()
        
        action = ActionTrace(
            action_name="execute_command",
            action_index=0,
            input_labels={"integrity": IntegrityLabel.untrusted()},
            output_labels={},
            parameters={"command": "rm -rf /"},
            result="command output",
            timestamp=time.time()
        )
        
        violations = policy.evaluate_action(action, [])
        assert len(violations) == 1
        assert violations[0].violation_type == PolicyViolationType.INTEGRITY_VIOLATION
        assert "untrusted data" in violations[0].description.lower()
    
    def test_custom_trusted_operations(self):
        """Test policy with custom trusted operations."""
        trusted_ops = {"custom_secure_operation"}
        policy = IntegrityProtectionPolicy(trusted_operations=trusted_ops)
        
        action = ActionTrace(
            action_name="custom_secure_operation",
            action_index=0,
            input_labels={"integrity": IntegrityLabel.untrusted()},
            output_labels={},
            parameters={},
            result="result",
            timestamp=time.time()
        )
        
        violations = policy.evaluate_action(action, [])
        assert len(violations) == 1  # Should be blocked


class TestPolicyEngine:
    """Test the policy engine that coordinates multiple policies."""
    
    def test_engine_creation(self):
        """Test creating a policy engine."""
        policies = [NoExfiltrationPolicy(), IntegrityProtectionPolicy()]
        engine = PolicyEngine(policies)
        
        assert len(engine.policies) == 2
        assert len(engine.violation_history) == 0
    
    def test_add_remove_policies(self):
        """Test adding and removing policies."""
        engine = PolicyEngine()
        policy = NoExfiltrationPolicy()
        
        engine.add_policy(policy)
        assert len(engine.policies) == 1
        
        removed = engine.remove_policy("NoExfiltration")
        assert removed is True
        assert len(engine.policies) == 0
        
        removed = engine.remove_policy("NonExistent")
        assert removed is False
    
    def test_evaluate_action_multiple_policies(self):
        """Test evaluating an action against multiple policies."""
        policies = [NoExfiltrationPolicy(), IntegrityProtectionPolicy()]
        engine = PolicyEngine(policies)
        
        # Action that violates both policies
        universe = frozenset(["alice@example.com", "bob@example.com"])
        readers = frozenset(["alice@example.com"])
        confidentiality = InverseLattice(PowersetLattice(readers, universe))
        
        action = ActionTrace(
            action_name="execute_command",  # Trusted operation
            action_index=0,
            input_labels={
                "integrity": IntegrityLabel.untrusted(),  # Violates integrity
                "confidentiality": confidentiality  # Might violate confidentiality
            },
            output_labels={},
            parameters={"command": "send_data_to_external_server"},
            result="executed",
            timestamp=time.time()
        )
        
        violations = engine.evaluate_action(action, [])
        
        # Should detect integrity violation
        assert len(violations) >= 1
        violation_types = [v.violation_type for v in violations]
        assert PolicyViolationType.INTEGRITY_VIOLATION in violation_types
    
    def test_should_block_action(self):
        """Test the action blocking decision logic."""
        engine = PolicyEngine()
        
        # Low severity violation - should not block
        low_violation = PolicyViolation(
            violation_type=PolicyViolationType.CUSTOM_VIOLATION,
            description="Low severity issue",
            action_index=0,
            labels_involved={},
            severity=3
        )
        
        assert not engine.should_block_action([low_violation], severity_threshold=5)
        
        # High severity violation - should block
        high_violation = PolicyViolation(
            violation_type=PolicyViolationType.EXFILTRATION_ATTEMPT,
            description="High severity issue",
            action_index=0,
            labels_involved={},
            severity=8
        )
        
        assert engine.should_block_action([high_violation], severity_threshold=5)
    
    def test_violation_history(self):
        """Test violation history tracking."""
        engine = PolicyEngine([IntegrityProtectionPolicy()])
        
        action = ActionTrace(
            action_name="execute_command",
            action_index=0,
            input_labels={"integrity": IntegrityLabel.untrusted()},
            output_labels={},
            parameters={},
            result="result",
            timestamp=time.time()
        )
        
        violations = engine.evaluate_action(action, [])
        
        # Check that violations are stored in history
        assert len(engine.violation_history) == len(violations)
        assert engine.violation_history == violations
    
    def test_violation_summary(self):
        """Test getting violation summary statistics."""
        engine = PolicyEngine([IntegrityProtectionPolicy()])
        
        # Initially no violations
        summary = engine.get_violation_summary()
        assert summary["total_violations"] == 0
        
        # Add some violations
        action = ActionTrace(
            action_name="execute_command",
            action_index=0,
            input_labels={"integrity": IntegrityLabel.untrusted()},
            output_labels={},
            parameters={},
            result="result",
            timestamp=time.time()
        )
        
        violations = engine.evaluate_action(action, [])
        
        summary = engine.get_violation_summary()
        assert summary["total_violations"] > 0
        assert "violation_counts" in summary
        assert "severity_distribution" in summary
    
    def test_clear_history(self):
        """Test clearing violation history."""
        engine = PolicyEngine([IntegrityProtectionPolicy()])
        
        # Generate some violations
        action = ActionTrace(
            action_name="execute_command",
            action_index=0,
            input_labels={"integrity": IntegrityLabel.untrusted()},
            output_labels={},
            parameters={},
            result="result",
            timestamp=time.time()
        )
        
        engine.evaluate_action(action, [])
        assert len(engine.violation_history) > 0
        
        # Clear history
        engine.clear_history()
        assert len(engine.violation_history) == 0


class TestStandardPolicyEngine:
    """Test the standard policy engine factory."""
    
    def test_create_standard_engine(self):
        """Test creating a standard policy engine."""
        engine = create_standard_policy_engine()
        
        assert len(engine.policies) == 2
        policy_names = [p.name for p in engine.policies]
        assert "NoExfiltration" in policy_names
        assert "IntegrityProtection" in policy_names