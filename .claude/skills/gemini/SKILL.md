---
name: google-gen-ai-sdk
description: Google Gen AI Python SDK provides an interface for developers to integrate Google’s generative models into their Python applications. It supports the Gemini Developer API and Vertex AI APIs.
---

# Google Gen AI SDK

# Instructions

1. Always fetch and read the latest API docs on https://googleapis.github.io/python-genai/.

## Installation

```bash
pip install google-genai
# Or with uv
uv pip install google-genai
```

## Client Initialization

### Gemini Developer API
```python
import google.genai as genai

client = genai.Client(api_key='GEMINI_API_KEY')
```

### Vertex AI
```python
client = genai.Client(
    vertexai=True,
    project='your-project-id',
    location='us-central1'
)
```

## Main API Classes

- **Client**: Primary entry point for all API interactions
- **models**: Model inference and management
- **chats**: Multi-turn conversation sessions  
- **files**: File upload and management
- **batches**: Batch processing operations
- **tunings**: Model fine-tuning capabilities

## Key Features

- Gemini Developer API and Vertex AI support
- Generative content generation (text, image, video)
- Embedding content generation
- Function calling for tool integration
- Chat sessions with conversation history
- Token counting for cost estimation
- Safety settings and content filtering
- JSON and enum response schemas
- Multimodal interactions

## Common Usage Patterns

### Basic Content Generation
```python
response = client.models.generate_content(
    model='gemini-2.0-flash-exp',
    contents='Explain quantum computing in simple terms'
)
print(response.text)
```

### Chat Sessions
```python
chat = client.chats.create(
    model='gemini-2.0-flash-exp'
)
response = chat.send_message('Hello!')
print(response.text)
```

### Multimodal Input
```python
response = client.models.generate_content(
    model='gemini-2.0-flash-exp',
    contents=[
        'What is in this image?',
        {'mime_type': 'image/jpeg', 'data': image_bytes}
    ]
)
```

### Function Calling
```python
def get_weather(location: str) -> dict:
    # Implementation
    return {"temp": 72, "condition": "sunny"}

response = client.models.generate_content(
    model='gemini-2.0-flash-exp',
    contents='What is the weather in San Francisco?',
    tools=[get_weather]
)
```

### Embeddings
```python
response = client.models.embed_content(
    model='text-embedding-004',
    content='The quick brown fox jumps over the lazy dog'
)
embedding = response.embedding
```

## Configuration Options

- **API Versioning**: Specify API version for compatibility
- **Safety Settings**: Configure content filtering levels
- **Function Calling Modes**: AUTO, ANY, NONE
- **Custom Base URLs**: Override default API endpoints
- **Proxy Support**: Configure HTTP/HTTPS proxies
- **Authentication**: API keys, OAuth, service accounts

## Supported Models

### Text Generation
- gemini-2.0-flash-exp
- gemini-1.5-flash
- gemini-1.5-pro

### Embeddings
- text-embedding-004
- text-multilingual-embedding-002

### Image Generation
- imagen-3.0-generate
- imagen-3.0-fast-generate

## Best Practices

1. Use appropriate model for task complexity
2. Implement retry logic for transient errors
3. Monitor token usage for cost optimization
4. Apply safety settings based on use case
5. Cache embeddings when possible
6. Use batch processing for multiple requests
7. Implement proper error handling for API limits