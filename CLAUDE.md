# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the Trustworthy Google Agent Development Kit (ADK) Extensions project, providing plugins and support harness for designing, developing, and deploying trustworthy AI agents. The codebase supports security-focused research for building trustworthy autonomous systems.

## Available Skills

This project leverages two specialized Claude Code skills:

1. **google-adk**: Comprehensive support for implementing ADK agents, plugins, and components. Provides patterns for building sophisticated LLM-powered agent applications using Google's ADK framework.

2. **google-gen-ai-sdk**: Integration support for Google's generative AI models including Gemini Developer API and Vertex AI. Used for model inference, embeddings, and multimodal interactions.

## Development Commands

### Dependencies & Environment
```bash
# Install dependencies with uv
uv pip install -e .
uv pip install -e ".[dev]"

# Python 3.13+ required
```

### Testing
```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_plugin_soft_instruction_control.py

# Run with coverage
uv run pytest --cov=src/trustworthy
```

### Code Quality
```bash
# Format code with Black
uv run black src/ tests/ examples/

# Lint with Ruff
uv run ruff check src/ tests/ examples/

# Type checking with mypy
uv run mypy src/
```

# Always run ruff to lint and format Python code before commiting any changes.

```bash
# Format
uv run ruff format
# Lint
uv run ruff check
```

### Running Examples
```bash
# Payment agent example
uv run python -m examples.payment_agent.agent

# Email calendar assistant example  
uv run python -m examples.email_calendar_assistant.agent
```

## Architecture

### Core Components

**trustworthy.plugins**: Security-focused ADK plugins
- `soft_instruction_control.py`: Implements Soft Instruction De-escalation Defense against prompt injection attacks using iterative LLM-based sanitization

**examples/**: Demonstration agents showing plugin integration
- `payment_agent/`: Payment processing customer service agent demonstrating secure payment handling
- `email_calendar_assistant/`: Assistant for email and calendar management with prompt injection defense

### Plugin System

The codebase extends Google's ADK framework with security plugins that intercept and process messages before they reach agents. Plugins follow the `BasePlugin` interface from `google.adk` and implement hooks like `on_user_message()` for message interception.

### Key Design Patterns

1. **Iterative Sanitization**: The Soft Instruction Control plugin uses multiple sanitization rounds with an LLM to detect and neutralize injection attempts
2. **Lazy Initialization**: Resources like AI clients are initialized on first use
3. **Statistics Tracking**: Plugins maintain internal metrics for monitoring detection and sanitization rates
4. **Configurable Defense**: Plugins use dataclass configurations for tunable defense parameters

## Project Structure

```
trustworthy-adk/
├── src/trustworthy/           # Main package
│   ├── __init__.py
│   └── plugins/               # Security plugins
│       └── soft_instruction_control.py
├── examples/                  # Example agent implementations
│   ├── payment_agent/         # Payment processing agent
│   │   ├── agent.py
│   │   ├── scenarios.py
│   │   └── tools/            # Custom tools for payment processing
│   └── email_calendar_assistant/  # Email/calendar management agent
│       ├── agent.py
│       ├── scenarios.py
│       └── tools/            # Custom tools for email/calendar
├── tests/                     # Test suite
├── .claude/skills/            # Claude Code skill definitions
│   ├── adk/                  # ADK framework skill
│   └── gemini/               # Gemini AI SDK skill
├── pyproject.toml            # Project configuration
└── uv.lock                   # Dependency lock file
```

## Dependencies

- `google-adk>=1.19.0`: Base ADK framework
- `google-genai`: For Gemini model integration (if needed)
- Development tools: black, ruff, mypy, pytest, jupyterlab
- Python 3.13+

## Security Focus

This project emphasizes building trustworthy AI agents with robust defenses against:
- Prompt injection attacks
- Instruction hijacking
- Context manipulation
- Unauthorized tool usage

All plugins and examples are designed with security-first principles to demonstrate best practices for deploying AI agents in production environments.