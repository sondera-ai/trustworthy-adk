# Workspace Agent - ADK Modernization Plan

## Overview
This document outlines the plan to modernize the workspace example based on the latest Google ADK documentation and best practices.

## Current State Analysis
- Uses basic `Agent` instantiation with function-based tools
- Employs `gemini-2.5-flash` model
- Integrates `SonderaHarnessPlugin` for policy enforcement
- Creates new runner/session for each scenario
- Limited error handling and validation

## Improvement Areas

### 1. Architecture Improvements

#### 1.1 Upgrade to Modern Agent Framework
- **Current**: Direct `Agent` instantiation (`agent.py:61-74`)
- **Target**: Migrate to `LlmAgent` and `BaseAgent` patterns
- **Benefits**: Better lifecycle management, structured configuration
- **Implementation**: 
  - Replace `Agent()` with `LlmAgent()` 
  - Add `before_agent_callback` and `after_agent_callback`
  - Use `config_type` for flexible configuration

#### 1.2 Enhanced Tool Implementation
- **Current**: Function-based tools (`tools/email_tool.py`, `tools/calendar_tool.py`)
- **Target**: `BaseTool` classes with `run_async()` methods
- **Benefits**: Better error handling, validation, credential management
- **Implementation**:
  - Convert functions to `BaseTool` subclasses
  - Add `ToolContext` support
  - Implement proper async operations
  - Consider `GoogleApiToolset` for native integrations

### 2. Session Management Improvements

#### 2.1 Session Lifecycle Management
- **Current**: New runner/session per scenario (`agent.py:94-102`)
- **Target**: Proper session reuse with `InMemorySessionService`
- **Benefits**: Better performance, stateful conversations
- **Implementation**:
  - Implement session reuse pattern
  - Add `ResumabilityConfig` for state management
  - Optimize session creation/cleanup

### 3. Plugin Integration Updates

#### 3.1 Modern Plugin Patterns
- **Current**: Basic `SonderaHarnessPlugin` integration (`agent.py:91-98`)
- **Target**: Enhanced `BasePlugin` with comprehensive callbacks
- **Benefits**: Better monitoring, error recovery, telemetry
- **Implementation**:
  - Add callback methods: `before_run_callback`, `after_run_callback`, `on_tool_error_callback`
  - Implement `ReflectAndRetryToolPlugin` for error recovery
  - Add telemetry tracking

### 4. Model Configuration Enhancements

#### 4.1 Model Upgrade and Configuration
- **Current**: `gemini-2.5-flash` with basic configuration (`agent.py:62`)
- **Target**: Latest Gemini model with advanced configuration
- **Benefits**: Better performance, reliability, retry handling
- **Implementation**:
  - Upgrade to latest available Gemini model
  - Add retry options and speech configurations
  - Implement `LLMRegistry` for dynamic model management

### 5. Security Enhancements

#### 5.1 Authentication and Credentials
- **Current**: Basic validation in tools
- **Target**: `AuthenticatedFunctionTool` with credential management
- **Benefits**: Enhanced security, proper credential handling
- **Implementation**:
  - Implement `AuthenticatedFunctionTool` patterns
  - Add credential management via `ToolContext.request_credential()`
  - Enhance input validation and sanitization

### 6. Error Handling and Reliability

#### 6.1 Comprehensive Error Handling
- **Current**: Basic error returns in tools
- **Target**: Structured error handling with callbacks
- **Benefits**: Better reliability, debugging, monitoring
- **Implementation**:
  - Add `on_model_error_callback` and `on_tool_error_callback`
  - Implement proper exception handling
  - Add telemetry with `trace_call_llm()` and `trace_tool_call()`

## Implementation Priority

### Phase 1: Core Architecture (High Priority)
1. Upgrade to `LlmAgent` pattern
2. Convert tools to `BaseTool` classes
3. Implement proper session management
4. Update model configuration

### Phase 2: Enhanced Features (Medium Priority)
1. Add comprehensive error handling
2. Implement advanced plugin callbacks
3. Add credential management
4. Integrate telemetry tracking

### Phase 3: Advanced Integrations (Low Priority)
1. Consider `GoogleApiToolset` for native integrations
2. Implement advanced retry mechanisms
3. Add performance optimizations
4. Enhanced security features

## File-Specific Changes Required

### `agent.py`
- Line 61-74: Replace `Agent` with `LlmAgent`
- Line 62: Upgrade model to latest Gemini
- Line 91-98: Enhance plugin integration
- Line 94-102: Implement proper session reuse

### `tools/email_tool.py`
- Convert functions to `BaseTool` classes
- Add `ToolContext` support
- Implement async operations
- Enhance validation and error handling

### `tools/calendar_tool.py`
- Convert functions to `BaseTool` classes
- Add proper datetime validation
- Implement credential management
- Add comprehensive error handling

### `scenarios.py`
- Update test scenarios for new architecture
- Add error handling test cases
- Include telemetry validation

## Success Metrics
- Reduced error rates in tool execution
- Improved session management efficiency
- Enhanced security posture
- Better monitoring and observability
- Maintained backward compatibility with existing scenarios

## Next Steps
1. Review and approve this plan
2. Begin Phase 1 implementation
3. Test each phase incrementally
4. Update documentation and examples
5. Validate against existing scenarios