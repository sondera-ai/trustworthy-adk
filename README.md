# Trustworthy Agent Development Kit (ADK) Extensions

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

A comprehensive toolkit for building secure, trustworthy AI agents using Google's Agent Development Kit (ADK). This package provides security-focused plugins, defensive mechanisms, and analysis tools to help developers create robust autonomous systems that resist prompt injection attacks and other security threats.

## 🎯 Overview

This material supports the talk first presented at [2025 BSides Philadelphia](https://bsidesphilly.org/):
**"Your AI Agent Just Got Pwned: A Security Engineer's Guide to Building Trustworthy Autonomous Systems"**. The slides are available [here](docs/2025-12%20-%20Your%20AI%20Agent%20Just%20Got%20Pwned.pdf).

The toolkit implements proven security patterns and defensive mechanisms to protect AI agents from:
- Prompt injection attacks
- Unauthorized tool execution
- Data exfiltration attempts
- Social engineering attacks
- Indirect prompt injection (IPI)

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/trustworthy-adk.git
cd trustworthy-adk

# Install uv if you haven't already
pip install uv

# Install the package in editable mode
uv pip install -e .
```

### Basic Usage

```python
from trustworthy import ActionSelectorAgent, HITLToolPlugin

# Create a secure action selector agent
def check_order_status(order_id: str) -> str:
    """Check the status of a customer order"""
    return f"Order {order_id} is being processed"

def delete_user(user_id: str) -> str:
    """Delete a user account - SENSITIVE OPERATION"""
    return f"User {user_id} deleted"

# Create agent with security plugins
agent = ActionSelectorAgent(
    model="gemini-2.5-flash",
    tools=[check_order_status, delete_user],
    plugins=[
        HITLToolPlugin(sensitive_tools=["delete_user"])
    ]
)
```

## 📁 Repository Structure

```
trustworthy-adk/
├── src/trustworthy/                    # Main package source
│   ├── agents/                         # Secure agent implementations
│   │   ├── __init__.py
│   │   └── action_selector.py          # Action-Selector Pattern agent
│   ├── plugins/                        # Security plugins
│   │   ├── __init__.py
│   │   ├── hitl_tool.py                # Human-in-the-Loop plugin
│   │   └── soft_instruction_control.py # Soft Instruction Defense
│   ├── analysis/                       # Analysis and profiling tools
│   │   ├── __init__.py
│   │   └── agentic_profiler/           # Agent behavior analysis
│   │       ├── __init__.py
│   │       ├── __main__.py
│   │       ├── radar_chart_tool.py
│   │       └── rubric.py
│   └── __init__.py                     # Package initialization
├── examples/                           # Example implementations
│   └── workspace/                      # Workspace agent example
│       ├── tools/                      # Example tools
│       │   ├── calendar_tool.py
│       │   ├── email_tool.py
│       │   ├── mock.py                 # Mock data for testing
│       │   └── user.py                 # User simulation
│       ├── agent.py                    # Example agent setup
│       ├── eval_config.json            # Evaluation configuration
│       ├── conversation_scenarios.json # Test scenarios
│       └── IMPROVEMENT_PLAN.md         # Modernization roadmap
├── tests/                              # Test suite
│   ├── __init__.py
│   ├── conftest.py                     # Test configuration
│   ├── test_action_selector_agent.py   # Agent tests
│   ├── test_package.py                 # Package tests
│   └── test_plugin_soft_instruction_control.py
├── pyproject.toml                      # Project configuration
├── README.md                           # This file
├── LICENSE                             # MIT License
└── .gitignore                          # Git ignore rules
```

## 🛡️ Security Components

### Action Selector Agent

Implements the **Action-Selector Pattern** for maximum security against prompt injection:

- **Single-step execution**: No feedback loops that can be exploited
- **Predefined tools only**: Cannot create or modify tools dynamically  
- **Immunity to IPI**: Tool results don't feed back to the LLM
- **Minimal autonomy**: Restricted to selecting from approved actions

```python
from trustworthy import create_action_selector_agent

agent = create_action_selector_agent(
    tools=[check_order_status, reset_password],
    name="customer_service"
)
```

### Human-in-the-Loop (HITL) Plugin

Requires human approval for sensitive operations:

```python
from trustworthy import HITLToolPlugin

hitl_plugin = HITLToolPlugin(
    sensitive_tools=["delete_user", "transfer_funds", "send_email"]
)
```

### Soft Instruction Defense Plugin

Implements iterative prompt sanitization based on the research paper ["Soft Instruction De-escalation Defense"](https://arxiv.org/pdf/2510.21057):

```python
from trustworthy import SoftInstructionDefensePlugin

defense_plugin = SoftInstructionDefensePlugin(
    max_iterations=5,
    halt_on_detection=True
)
```

## 🧪 Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_action_selector_agent.py

# Run with verbose output and coverage
uv run pytest -v --cov=src/trustworthy
```

## 📊 Agent Development Lifecycle

### Design Patterns

- **Action-Selector Pattern**: Minimal autonomy with predefined actions
- **Human-in-the-Loop**: Human oversight for critical decisions
- **Defense in Depth**: Multiple security layers working together
- **Least Privilege**: Minimal permissions and capabilities

### Development Patterns

- **Security by Design**: Security considerations from the start
- **Iterative Hardening**: Continuous security improvements
- **Threat Modeling**: Systematic analysis of attack vectors
- **Defensive Programming**: Robust error handling and validation

### Deployment Patterns

- **Staged Rollout**: Gradual deployment with monitoring
- **Continuous Monitoring**: Real-time security and behavior analysis
- **Incident Response**: Prepared response to security events
- **Regular Audits**: Periodic security assessments

## 🔬 Analysis Tools

The package includes tools for analyzing agent behavior and security posture:

- **Agentic Profiler**: Visualize agent capabilities and risks
- **Security Metrics**: Quantify trustworthiness measures
- **Behavior Analysis**: Understand agent decision patterns

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone and install in development mode
git clone https://github.com/yourusername/trustworthy-adk.git
cd trustworthy-adk
uv pip install -e ".[dev]"

# Run tests
uv run pytest

# Format code
uv run black src/ tests/
uv run ruff check src/ tests/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google ADK team for the foundational framework
- BSides Philadelphia for hosting the original presentation
- Security research community for defensive techniques
- Contributors and early adopters

---

**⚠️ Security Notice**: This toolkit is designed for educational and research purposes. Always conduct thorough security testing before deploying AI agents in production environments.
