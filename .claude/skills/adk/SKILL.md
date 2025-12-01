```
name: google-adk
description: Implement Agent Development Kit (ADK) agents, plugins, and other classes. The Google Agent Development Kit (ADK) is a comprehensive Python framework for building sophisticated LLM-powered agent applications. It provides a modular, extensible architecture for creating intelligent agents that can use tools, maintain conversation memory, execute code, and interact with various Google services.
```

# Google Agent Development Kit (ADK)


# Instructions

1. Always fetch and read the latest ADK documentation on https://google.github.io/adk-docs/api-reference/python/.
2. When creating a Plugin always read and refer to https://google.github.io/adk-docs/plugins/ and refer to examples in https://github.com/google/adk-python/tree/main/src/google/adk/plugins.

## Architecture

### Core Components

```
google.adk/
├── agents/          # Agent implementations and configurations
├── tools/           # Built-in and custom tool framework
├── models/          # Data models and structures
├── memory/          # Conversation memory management
├── sessions/        # Session state management
├── runners.py       # Execution orchestration
├── apps/            # Application layer
├── code_executors/  # Code execution framework
├── auth/            # Authentication and credentials
├── plugins/         # Plugin system for extending behavior
├── flows/           # Conversation flow management
├── a2a/             # Agent-to-Agent communication
├── evaluation/      # Agent evaluation framework
└── cli/             # Command-line interface tools
```

## Agent System

### BaseAgent

The foundational class for all agents in the ADK framework.

```python
from google.adk.agents import BaseAgent
from google.adk.models import AgentRequest, AgentResponse

class BaseAgent:
    """Abstract base class for all agents"""
    
    def __init__(self, name: str, parent: Optional[BaseAgent] = None):
        self.name = name
        self.parent = parent
        self.children = []
        self.tools = []
        self.memory = None
    
    def process(self, request: AgentRequest) -> AgentResponse:
        """Process an agent request"""
        pass
    
    def add_tool(self, tool: Tool):
        """Register a tool with the agent"""
        pass
    
    def get_context(self) -> Dict:
        """Get current conversation context"""
        pass
```

### LlmAgent

The primary agent implementation that integrates with language models.

```python
from google.adk.agents import LlmAgent, LlmAgentConfig
from google.adk.models import LlmModel

# Configure an LLM agent
config = LlmAgentConfig(
    name="assistant",
    model=LlmModel.GEMINI_1_5_PRO,
    system_prompt="You are a helpful AI assistant",
    temperature=0.7,
    max_tokens=2048,
    tools_enabled=True,
    memory_enabled=True
)

# Create the agent
agent = LlmAgent(config)
```

### Agent Types

1. **SequentialAgent**: Executes tasks in sequence
2. **ParallelAgent**: Executes multiple tasks concurrently
3. **LoopAgent**: Iterative execution with conditions
4. **RemoteA2AAgent**: Agent-to-Agent communication

## Tools Framework

### Built-in Tools

The ADK provides extensive built-in tools:

```python
# Core Tools
from google.adk.tools import (
    AgentTool,           # Base tool class
    TransferToAgentTool, # Transfer control between agents
    GoogleSearchAgentTool # Web search capability
)

# Google Service Tools
from google.adk.tools import (
    BigQueryTool,        # BigQuery operations
    CloudStorageTool,    # GCS operations
    CloudSqlTool,        # Cloud SQL interactions
    DatastoreTool,       # Datastore operations
    FirestoreTool,       # Firestore operations
    PubSubTool,          # Pub/Sub messaging
    SpannerTool,         # Spanner database
    TaskQueueTool        # Task queue management
)

# Development Tools
from google.adk.tools import (
    CodeExecutorTool,    # Execute Python code
    GitTool,             # Git operations
    FileTool,            # File system operations
    ShellTool,           # Shell command execution
    HttpTool,            # HTTP requests
    JsonTool,            # JSON manipulation
    RegexTool            # Regular expression operations
)

# AI/ML Tools
from google.adk.tools import (
    VertexAITool,        # Vertex AI integration
    TextEmbeddingTool,   # Generate embeddings
    ImageGenerationTool, # Generate images
    AudioTranscriptionTool # Transcribe audio
)
```

### Custom Tool Development

```python
from google.adk.tools import AgentTool
from google.adk.models import ToolRequest, ToolResponse

class CustomTool(AgentTool):
    """Custom tool implementation"""
    
    def __init__(self):
        super().__init__(
            name="custom_tool",
            description="Performs custom operations",
            parameters={
                "input": {"type": "string", "required": True},
                "options": {"type": "object", "required": False}
            }
        )
    
    def execute(self, request: ToolRequest) -> ToolResponse:
        """Execute the tool logic"""
        input_data = request.parameters.get("input")
        result = self.process_input(input_data)
        
        return ToolResponse(
            success=True,
            output=result,
            metadata={"processed_at": datetime.now()}
        )
    
    def process_input(self, data: str) -> str:
        # Custom processing logic
        return f"Processed: {data}"

# Register with agent
agent.add_tool(CustomTool())
```

## Memory and Sessions

### Memory Management

```python
from google.adk.memory import (
    MemoryStore,
    ConversationMemory,
    SearchableMemory
)

# Create memory store
memory = ConversationMemory(
    max_messages=100,
    summarize_after=50,
    enable_search=True
)

# Add to agent
agent.set_memory(memory)

# Search memory
results = memory.search("previous discussion about API")
```

### Session Management

```python
from google.adk.sessions import SessionManager, SessionConfig

# Configure session
session_config = SessionConfig(
    session_id="user-123",
    persist=True,
    timeout_minutes=30,
    max_turns=50
)

# Create session manager
session = SessionManager(config=session_config)

# Load previous session
session.load()

# Save session state
session.save()
```

## Code Execution

### Code Executor Framework

```python
from google.adk.code_executors import (
    CodeExecutor,
    PythonExecutor,
    ExecutionConfig
)

# Configure executor
exec_config = ExecutionConfig(
    timeout_seconds=30,
    max_retries=3,
    sandbox_mode=True,
    allowed_imports=["math", "datetime", "json"]
)

# Create executor
executor = PythonExecutor(config=exec_config)

# Execute code
result = executor.execute("""
import math
radius = 5
area = math.pi * radius ** 2
print(f"Area: {area}")
""")

print(result.output)  # "Area: 78.53981633974483"
print(result.success)  # True
```

### Integration with Agents

```python
from google.adk.tools import CodeExecutorTool

# Add code execution capability to agent
agent.add_tool(CodeExecutorTool(
    executor=executor,
    auto_retry=True
))
```

## Authentication

### Credential Management

```python
from google.adk.auth import (
    Credentials,
    ServiceAccountCredentials,
    OAuth2Credentials,
    APIKeyCredentials
)

# Service Account
creds = ServiceAccountCredentials.from_file(
    "path/to/service-account.json"
)

# OAuth2
oauth_creds = OAuth2Credentials(
    client_id="your-client-id",
    client_secret="your-secret",
    refresh_token="refresh-token"
)

# API Key
api_creds = APIKeyCredentials(
    api_key="your-api-key"
)

# Apply to agent
agent.set_credentials(creds)
```

## Runners and Applications

### Runner Framework

```python
from google.adk.runners import (
    Runner,
    RunnerConfig,
    ExecutionMode
)

# Configure runner
runner_config = RunnerConfig(
    mode=ExecutionMode.INTERACTIVE,
    max_iterations=10,
    timeout_seconds=300,
    enable_logging=True,
    log_level="INFO"
)

# Create and run
runner = Runner(agent=agent, config=runner_config)
response = runner.run(user_input="Help me analyze this data")
```

### Application Layer

```python
from google.adk.apps import AgentApp, AppConfig

# Create application
app = AgentApp(
    name="DataAnalysisBot",
    agent=agent,
    config=AppConfig(
        port=8080,
        enable_ui=True,
        auth_required=True
    )
)

# Run application
app.run()
```

## Plugin System

### Creating Plugins

```python
from google.adk.plugins import Plugin, PluginContext

class LoggingPlugin(Plugin):
    """Plugin for enhanced logging"""
    
    def on_request(self, context: PluginContext):
        """Called before request processing"""
        print(f"Request: {context.request}")
    
    def on_response(self, context: PluginContext):
        """Called after response generation"""
        print(f"Response: {context.response}")
    
    def on_error(self, context: PluginContext, error: Exception):
        """Called on error"""
        print(f"Error: {error}")

# Register plugin
agent.register_plugin(LoggingPlugin())
```

### Built-in Plugins

```python
from google.adk.plugins import (
    BigQueryAnalyticsPlugin,  # Analytics tracking
    CachePlugin,              # Response caching
    RateLimitPlugin,          # Rate limiting
    SecurityPlugin,           # Security features
    MetricsPlugin            # Performance metrics
)
```

## Flow Management

### Conversation Flows

```python
from google.adk.flows import Flow, FlowStep, Condition

# Define flow
flow = Flow(name="customer_support")

# Add steps
flow.add_step(FlowStep(
    name="greeting",
    action=lambda ctx: "How can I help you today?",
    next_step="problem_identification"
))

flow.add_step(FlowStep(
    name="problem_identification",
    action=identify_problem,
    conditions=[
        Condition(
            check=lambda ctx: ctx.intent == "technical",
            next_step="technical_support"
        ),
        Condition(
            check=lambda ctx: ctx.intent == "billing",
            next_step="billing_support"
        )
    ]
))

# Apply to agent
agent.set_flow(flow)
```

## Multi-Modal Support

### Handling Different Content Types

```python
from google.adk.models import (
    TextContent,
    ImageContent,
    AudioContent,
    VideoContent
)

# Text
text = TextContent("Analyze this text")

# Image
image = ImageContent.from_file("path/to/image.jpg")

# Audio
audio = AudioContent.from_bytes(
    audio_bytes,
    format="mp3"
)

# Create multi-modal request
request = AgentRequest(
    contents=[text, image],
    context={"task": "image_analysis"}
)

response = agent.process(request)
```

## Agent-to-Agent Communication

### A2A Framework

```python
from google.adk.a2a import A2AClient, A2AServer
from google.adk.agents import RemoteA2AAgent

# Set up A2A server
server = A2AServer(
    agent=specialist_agent,
    port=9090
)
server.start()

# Create remote agent client
remote_agent = RemoteA2AAgent(
    name="remote_specialist",
    endpoint="http://localhost:9090"
)

# Use in main agent
main_agent.add_child(remote_agent)
```

## Evaluation Framework

### Agent Evaluation

```python
from google.adk.evaluation import (
    Evaluator,
    MetricSet,
    TestSuite
)

# Define metrics
metrics = MetricSet([
    "accuracy",
    "response_time",
    "token_usage",
    "user_satisfaction"
])

# Create test suite
test_suite = TestSuite.from_file("tests.json")

# Evaluate agent
evaluator = Evaluator(
    agent=agent,
    metrics=metrics,
    test_suite=test_suite
)

results = evaluator.run()
print(results.summary())
```

## Advanced Features

### Live Mode and Streaming

```python
from google.adk.agents import LlmAgent
from google.adk.models import StreamingConfig

# Configure streaming
streaming_config = StreamingConfig(
    enabled=True,
    chunk_size=20,
    buffer_size=100
)

agent = LlmAgent(
    config=config,
    streaming=streaming_config
)

# Stream responses
for chunk in agent.stream_process(request):
    print(chunk.text, end="", flush=True)
```

### Context Caching

```python
from google.adk.models import CacheConfig

# Configure caching
cache_config = CacheConfig(
    enabled=True,
    ttl_seconds=3600,
    max_entries=1000,
    cache_key_prefix="agent_cache_"
)

agent.set_cache_config(cache_config)
```

### Resumable Invocations

```python
from google.adk.models import ResumableConfig

# Enable resumability
resumable_config = ResumableConfig(
    enabled=True,
    checkpoint_interval=10,
    state_storage="firestore"
)

agent.set_resumable_config(resumable_config)

# Resume from checkpoint
agent.resume_from_checkpoint(checkpoint_id="ckpt-123")
```

## Complete Example

### Building a Data Analysis Agent

```python
from google.adk.agents import LlmAgent, LlmAgentConfig
from google.adk.models import LlmModel
from google.adk.tools import (
    BigQueryTool,
    CodeExecutorTool,
    GoogleSearchAgentTool,
    FileTool
)
from google.adk.memory import ConversationMemory
from google.adk.plugins import BigQueryAnalyticsPlugin
from google.adk.auth import ServiceAccountCredentials

# Configure agent
config = LlmAgentConfig(
    name="data_analyst",
    model=LlmModel.GEMINI_1_5_PRO,
    system_prompt="""You are an expert data analyst. 
    You can query databases, execute Python code for analysis,
    search for information, and work with files.""",
    temperature=0.3,
    tools_enabled=True,
    memory_enabled=True
)

# Create agent
agent = LlmAgent(config)

# Set up authentication
creds = ServiceAccountCredentials.from_file("credentials.json")
agent.set_credentials(creds)

# Add tools
agent.add_tool(BigQueryTool(project_id="my-project"))
agent.add_tool(CodeExecutorTool())
agent.add_tool(GoogleSearchAgentTool())
agent.add_tool(FileTool())

# Configure memory
memory = ConversationMemory(max_messages=100)
agent.set_memory(memory)

# Add analytics plugin
agent.register_plugin(BigQueryAnalyticsPlugin(
    dataset="analytics",
    table="agent_logs"
))

# Create runner
from google.adk.runners import Runner, RunnerConfig

runner = Runner(
    agent=agent,
    config=RunnerConfig(
        mode=ExecutionMode.INTERACTIVE,
        enable_logging=True
    )
)

# Example usage
response = runner.run("""
Analyze the sales data from the last quarter in BigQuery.
Create a visualization showing trends and identify top performers.
""")

print(response.text)
print(f"Tools used: {response.tool_calls}")
print(f"Execution time: {response.metrics.execution_time}")
```

## Best Practices

### 1. Agent Design
- Keep agents focused on specific domains
- Use parent-child hierarchies for complex workflows
- Implement proper error handling and fallbacks

### 2. Tool Selection
- Only enable tools that are necessary
- Implement tool validation and sanitization
- Use tool timeouts to prevent hanging

### 3. Memory Management
- Set appropriate memory limits
- Implement memory summarization for long conversations
- Use searchable memory for knowledge retrieval

### 4. Performance Optimization
- Enable caching for repeated queries
- Use streaming for real-time interactions
- Implement connection pooling for database tools

### 5. Security
- Always use proper authentication
- Implement rate limiting
- Sanitize user inputs
- Use sandbox mode for code execution

### 6. Monitoring
- Enable comprehensive logging
- Track metrics and performance
- Implement health checks
- Use the evaluation framework for quality assurance

## Troubleshooting

### Common Issues

1. **Import Errors**
```python
# Ensure ADK is properly installed
pip install google-adk
```

2. **Authentication Failures**
```python
# Verify credentials
from google.adk.auth import validate_credentials
is_valid = validate_credentials(creds)
```

3. **Tool Execution Errors**
```python
# Enable detailed tool logging
tool.set_log_level("DEBUG")
```

4. **Memory Issues**
```python
# Clear memory when needed
agent.memory.clear()
```

5. **Performance Problems**
```python
# Profile agent execution
from google.adk.utils import Profiler
with Profiler() as p:
    response = agent.process(request)
print(p.report())
```

## CLI Tools

The ADK provides command-line tools for agent management:

```bash
# Create new agent project
adk init my-agent

# Test agent
adk test --agent my-agent --input "test query"

# Deploy agent
adk deploy --agent my-agent --project my-project

# Monitor agent
adk monitor --agent my-agent --metrics

# Generate documentation
adk docs --agent my-agent --output docs/
```

## Resources

- **Repository**: Internal Google repository
- **Documentation**: Available in ADK module
- **Examples**: `.venv/lib/python3.13/site-packages/google/adk/examples/`
- **API Reference**: Generated from docstrings
- **Support**: Internal Google channels

## Version Information

Current installed version can be checked:

```python
from google.adk import version
print(version.__version__)
```

This documentation covers the core functionality of the Google Agent Development Kit. For specific use cases or advanced features, refer to the module's inline documentation and examples directory.