# Fides Plugin: Information Flow Control for AI Agents

The Fides plugin implements Information Flow Control (IFC) for AI agents based on the paper "Securing AI Agents with Information-Flow Control" by Costa et al. It provides deterministic security guarantees against prompt injection attacks and information exfiltration.

## Overview

Fides uses lattice-based security labels to track information flow through agent operations and enforces security policies to prevent violations. The system provides:

- **Dynamic Taint Tracking**: Automatically tracks security labels through all data flows
- **Policy Enforcement**: Blocks operations that would violate security policies
- **Prompt Injection Protection**: Prevents indirect prompt injection attacks
- **Deterministic Guarantees**: Provides formal security guarantees based on information flow control theory

## Architecture

### Core Components

1. **Lattice System** (`lattices.py`): Mathematical lattice structures for security labels
   - `IntegrityLabel`: Two-point lattice for trusted/untrusted classification
   - `PowersetLattice`: Confidentiality labels based on sets of authorized readers
   - `ProductLabel`: Combines multiple lattice dimensions
   - `InverseLattice`: Dual lattice structures

2. **Label Propagation** (`labels.py`): Automatic label tracking and propagation
   - `MetaValue`: Generic wrapper for attaching security labels to data
   - Pydantic integration for seamless schema validation
   - Automatic label propagation through operations

3. **Policy Engine** (`policies.py`): Security policy evaluation and enforcement
   - `NoExfiltrationPolicy`: Prevents confidential information leakage
   - `IntegrityProtectionPolicy`: Prevents untrusted data from influencing trusted operations
   - Extensible policy framework for custom security requirements

4. **IFC Planner** (`planner.py`): Planning loop with information flow control
   - Dynamic taint tracking through agent operations
   - Action trace monitoring and policy evaluation
   - Variable hiding and revealing mechanisms

5. **ADK Plugin** (`plugin.py`): Integration with Google ADK plugin architecture
   - Tool call interception and protection
   - Automatic security label inference
   - Configuration and statistics management

## Usage

### Basic Setup

```python
from trustworthy.plugins.fides import FidesPlugin, FidesConfig

# Create configuration
config = FidesConfig(
    enable_integrity_protection=True,
    enable_confidentiality_protection=True,
    halt_on_policy_violation=True,
    trusted_domains={"@company.com"},
    severity_threshold=5
)

# Create and configure plugin
fides_plugin = FidesPlugin(config)

# Use with ADK agent
agent = YourADKAgent(plugins=[fides_plugin])
```

### Email Assistant Example

The plugin includes a complete example demonstrating protection against the email assistant attack from the Fides paper:

```python
from trustworthy.plugins.fides import create_fides_plugin

# Configure for email assistant scenario
plugin = create_fides_plugin(
    enable_integrity=True,
    enable_confidentiality=True,
    trusted_domains={"@contoso.com"}
)

# Configure for specific user
plugin.configure_for_email_assistant(
    user_email="bob.sheffield@contoso.com",
    trusted_domains={"@contoso.com"}
)
```

### Manual Label Management

```python
from trustworthy.plugins.fides.labels import (
    label_as_trusted, label_as_untrusted, label_with_readers
)

# Create labeled data
trusted_data = label_as_trusted("System configuration")
untrusted_data = label_as_untrusted("User input from email")

# Confidentiality labels
universe = frozenset(["alice@company.com", "bob@company.com"])
confidential_data = label_with_readers(
    "Salary information",
    readers=frozenset(["alice@company.com"]),
    universe=universe
)
```

### Custom Policies

```python
from trustworthy.plugins.fides.policies import Policy, PolicyViolation

class CustomSecurityPolicy(Policy):
    def evaluate_action(self, action, trace_history):
        violations = []
        
        # Custom policy logic
        if self._is_suspicious_action(action):
            violations.append(PolicyViolation(
                violation_type=PolicyViolationType.CUSTOM_VIOLATION,
                description="Custom security rule violated",
                action_index=action.action_index,
                labels_involved=action.input_labels,
                severity=7
            ))
        
        return violations

# Add to configuration
config.custom_policies.append(CustomSecurityPolicy())
```

## Configuration Options

### FidesConfig Parameters

- **Core IFC Settings**:
  - `enable_integrity_protection`: Enable integrity label tracking
  - `enable_confidentiality_protection`: Enable confidentiality label tracking
  - `enable_policy_enforcement`: Enable policy evaluation and enforcement

- **Policy Settings**:
  - `halt_on_policy_violation`: Stop execution on policy violations
  - `severity_threshold`: Minimum severity level to block actions
  - `custom_policies`: List of custom policy instances

- **Label Settings**:
  - `default_integrity_label`: Default integrity level ("trusted" or "untrusted")
  - `trusted_domains`: Set of trusted email domains
  - `universe_principals`: Set of all possible principals for confidentiality

- **Tool Settings**:
  - `sensitive_tools`: Tools that require trusted inputs
  - `trusted_tools`: Tools that produce trusted outputs

- **Logging and Debugging**:
  - `enable_trace_logging`: Enable detailed execution logging
  - `log_label_propagation`: Log label propagation details
  - `log_policy_violations`: Log policy violation details

## Security Guarantees

The Fides plugin provides the following security guarantees:

1. **Information Flow Control**: All data flows are tracked and controlled according to security labels
2. **Policy Enforcement**: Security policies are deterministically enforced
3. **Prompt Injection Protection**: Indirect prompt injection attacks are prevented by label tracking
4. **Confidentiality**: Confidential information cannot flow to unauthorized recipients
5. **Integrity**: Untrusted data cannot influence trusted operations

## Example: Email Assistant Attack Prevention

The plugin demonstrates protection against the email assistant attack from the Fides paper:

1. **Attack Scenario**: Malicious email contains prompt injection attempting to exfiltrate sender information
2. **Without Fides**: Agent executes malicious instructions and sends sensitive data
3. **With Fides**: 
   - Email content is labeled as untrusted
   - Policy engine detects exfiltration attempt
   - Malicious Teams message is blocked
   - User is protected from attack

## Performance Considerations

- **Label Overhead**: MetaValue wrappers add minimal memory overhead
- **Policy Evaluation**: Policies are evaluated efficiently with early termination
- **Trace Storage**: Action traces are stored in memory; consider cleanup for long-running agents
- **Configuration**: Disable unused features (integrity/confidentiality) to reduce overhead

## Limitations

- **Static Analysis**: Some security properties require runtime enforcement
- **Label Inference**: Automatic label inference may not capture all security requirements
- **Policy Completeness**: Custom policies may be needed for specific security requirements
- **Performance**: Comprehensive tracking adds computational overhead

## Testing

The plugin includes comprehensive tests:

```bash
# Run lattice system tests
python -m pytest tests/test_fides_lattices.py

# Run policy engine tests
python -m pytest tests/test_fides_policies.py

# Run email assistant demo
python -m examples.fides_email_assistant.demo
```

## Integration with ADK

The Fides plugin integrates seamlessly with the Google ADK plugin architecture:

- **Tool Interception**: Automatically intercepts all tool calls
- **Label Propagation**: Tracks labels through Pydantic schemas
- **Policy Enforcement**: Blocks dangerous operations before execution
- **Statistics**: Provides monitoring and debugging information

## Research Background

This implementation is based on:

- **Paper**: "Securing AI Agents with Information-Flow Control" by Costa et al.
- **Tutorial**: Microsoft Fides tutorial demonstrating email assistant vulnerability
- **Theory**: Information Flow Control and lattice-based security models

The plugin provides a practical implementation of the theoretical IFC framework for real-world AI agent security.