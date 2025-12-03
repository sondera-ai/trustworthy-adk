# Trustworthy ADK: Fides Information Flow Control Plugin

This repository implements **Fides**, an Information Flow Control (IFC) system for AI agents, as a plugin for Google's Agent Development Kit (ADK). Fides provides deterministic security guarantees against prompt injection attacks and information exfiltration by tracking information flow through lattice-based security labels.

## Overview

Based on the paper ["Securing AI Agents with Information-Flow Control"](https://arxiv.org/pdf/2505.23643) by Costa et al., this implementation demonstrates how to protect AI agents from security vulnerabilities using formal information flow control techniques.

### Key Features

- **🔒 Deterministic Security**: Formal guarantees against prompt injection and data exfiltration
- **📊 Lattice-Based Labels**: Mathematical framework for tracking confidentiality and integrity
- **🔄 Dynamic Taint Tracking**: Automatic propagation of security labels through agent operations
- **🛡️ Policy Enforcement**: Configurable security policies with violation detection
- **🔌 ADK Integration**: Seamless integration with Google's Agent Development Kit
- **📧 Real-World Example**: Email assistant protection against the attack from the Fides paper

## Quick Start

### Installation

```bash
git clone https://github.com/sondera-ai/trustworthy-adk.git
cd trustworthy-adk
pip install -e .
```

### Basic Usage

```python
from trustworthy.plugins.fides import FidesPlugin, FidesConfig

# Configure Fides protection
config = FidesConfig(
    enable_integrity_protection=True,
    enable_confidentiality_protection=True,
    halt_on_policy_violation=True,
    trusted_domains={"@company.com"}
)

# Create plugin
fides_plugin = FidesPlugin(config)

# Use with your ADK agent
agent = YourADKAgent(plugins=[fides_plugin])
```

### Run the Demo

See Fides protection in action with the email assistant example:

```bash
python -m examples.fides_email_assistant.demo
```

This demonstrates protection against the indirect prompt injection attack described in the Fides paper.

## Architecture

### Core Components

1. **Lattice System** (`src/trustworthy/plugins/fides/lattices.py`)
   - Mathematical lattice structures for security labels
   - `IntegrityLabel`: Two-point lattice (trusted/untrusted)
   - `PowersetLattice`: Confidentiality based on authorized readers
   - `ProductLabel`: Combines multiple lattice dimensions
   - `InverseLattice`: Dual lattice structures

2. **Label Propagation** (`src/trustworthy/plugins/fides/labels.py`)
   - `MetaValue`: Generic wrapper for attaching security labels
   - Automatic label propagation through Pydantic schemas
   - Helper functions for common labeling patterns

3. **Policy Engine** (`src/trustworthy/plugins/fides/policies.py`)
   - `NoExfiltrationPolicy`: Prevents confidential information leakage
   - `IntegrityProtectionPolicy`: Prevents untrusted data influence
   - Extensible framework for custom security policies

4. **IFC Planner** (`src/trustworthy/plugins/fides/planner.py`)
   - Dynamic taint tracking through agent planning loops
   - Action trace monitoring and policy evaluation
   - Variable hiding and revealing mechanisms

5. **ADK Plugin** (`src/trustworthy/plugins/fides/plugin.py`)
   - Integration with Google ADK plugin architecture
   - Tool call interception and protection
   - Configuration and statistics management

## Security Guarantees

Fides provides the following security guarantees:

- **Information Flow Control**: All data flows are tracked and controlled
- **Policy Enforcement**: Security policies are deterministically enforced
- **Prompt Injection Protection**: Indirect prompt injection attacks are prevented
- **Confidentiality**: Confidential information cannot flow to unauthorized recipients
- **Integrity**: Untrusted data cannot influence trusted operations

## Example: Email Assistant Attack Prevention

The plugin includes a complete demonstration of the email assistant attack from the Fides paper:

1. **Attack Scenario**: Malicious email contains prompt injection attempting to exfiltrate sender information
2. **Without Fides**: Agent executes malicious instructions and sends sensitive data
3. **With Fides**: 
   - Email content is labeled as untrusted
   - Policy engine detects exfiltration attempt
   - Malicious Teams message is blocked
   - User is protected from attack

## Testing

Run the comprehensive test suite:

```bash
# Install test dependencies
pip install pytest

# Run lattice system tests
python -m pytest tests/test_fides_lattices.py -v

# Run policy engine tests
python -m pytest tests/test_fides_policies.py -v

# Run all tests
python -m pytest tests/ -v
```

## Configuration

### FidesConfig Options

```python
config = FidesConfig(
    # Core IFC settings
    enable_integrity_protection=True,
    enable_confidentiality_protection=True,
    enable_policy_enforcement=True,
    
    # Policy settings
    halt_on_policy_violation=True,
    severity_threshold=5,
    
    # Label settings
    default_integrity_label="trusted",
    trusted_domains={"@company.com"},
    universe_principals={"alice@company.com", "bob@company.com"},
    
    # Tool settings
    sensitive_tools={"send_email", "send_teams_message"},
    trusted_tools={"read_calendar", "get_weather"},
    
    # Logging
    enable_trace_logging=True,
    log_policy_violations=True
)
```

## Documentation

- [Fides Plugin Documentation](docs/fides_plugin.md) - Comprehensive usage guide
- [API Reference](src/trustworthy/plugins/fides/) - Source code documentation
- [Examples](examples/) - Working examples and demonstrations

## Research Background

This implementation is based on:

- **Paper**: ["Securing AI Agents with Information-Flow Control"](https://arxiv.org/pdf/2505.23643) by Costa et al.
- **Tutorial**: [Microsoft Fides Tutorial](https://raw.githubusercontent.com/microsoft/fides/refs/heads/main/Tutorial.ipynb)
- **Theory**: Information Flow Control and lattice-based security models

## Contributing

We welcome contributions! Please see our contributing guidelines and feel free to submit issues and pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Microsoft Research for the original Fides paper and tutorial
- Google for the Agent Development Kit framework
- The information flow control research community
