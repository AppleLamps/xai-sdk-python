# xAI Python SDK

The official Python SDK for xAI's APIs, providing both synchronous and asynchronous clients for interacting with xAI's powerful AI models. Built for Python 3.10 and above, the SDK offers a comprehensive set of features for text generation, image understanding, function calling, and more.

## Features

- **Dual Client Support**: Both synchronous (`Client`) and asynchronous (`AsyncClient`) clients
- **Multi-Turn Chat**: Intuitive conversation management with message history
- **Streaming Responses**: Real-time processing for interactive applications
- **Image Understanding**: Analyze and process images alongside text
- **Function Calling**: Define and execute tools with model-generated inputs
- **Structured Outputs**: Get responses as Pydantic models for type safety
- **Reasoning Models**: Leverage models with configurable reasoning effort
- **Server-Side Tools**: Web search, X search, code execution, and more
- **Collections API**: Manage and search document collections
- **Files API**: Upload and manage files for use in conversations
- **OpenTelemetry Integration**: Built-in observability and tracing
- **Batch Processing**: Handle multiple requests efficiently
- **Tokenization**: Access tokenizer functionality
- **Model Management**: Retrieve information about available models

## Quick Start

### Installation

Install from PyPI:

```bash
pip install xai-sdk
```

Or using [uv](https://docs.astral.sh/uv/):

```bash
uv add xai-sdk
```

### Basic Usage

```python
from xai_sdk import Client
from xai_sdk.chat import system, user

# Initialize client (uses XAI_API_KEY environment variable)
client = Client()

# Create a chat conversation
chat = client.chat.create(
    model="grok-4-1-fast-non-reasoning",
    messages=[system("You are a helpful assistant.")],
)

# Multi-turn conversation
chat.append(user("Hello, how are you?"))
response = chat.sample()
print(f"Grok: {response.content}")
```

### Asynchronous Usage

```python
import asyncio
from xai_sdk import AsyncClient
from xai_sdk.chat import system, user

async def main():
    client = AsyncClient()
    chat = client.chat.create(
        model="grok-4-1-fast-non-reasoning",
        messages=[system("You are a helpful assistant.")],
    )
    
    chat.append(user("What's the weather like today?"))
    response = await chat.sample()
    print(f"Grok: {response.content}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Streaming Responses

```python
from xai_sdk import Client
from xai_sdk.chat import user

client = Client()
chat = client.chat.create(model="grok-4-1-fast-non-reasoning")

chat.append(user("Tell me a story about pirates."))
print("Grok: ", end="", flush=True)
for response, chunk in chat.stream():
    print(chunk.content, end="", flush=True)
print()
```

### Image Understanding

```python
from xai_sdk import Client
from xai_sdk.chat import image, user

client = Client()
chat = client.chat.create(model="grok-4-1-fast-non-reasoning")

chat.append(
    user(
        "Which animal looks happier in these images?",
        image("https://images.unsplash.com/photo-1561037404-61cd46aa615b"),   # Puppy
        image("https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba") # Kitten
    )
)
response = chat.sample()
print(f"Grok: {response.content}")
```

### Function Calling

```python
from xai_sdk import Client
from xai_sdk.chat import system, tool
from pydantic import BaseModel, Field

class GetWeatherRequest(BaseModel):
    city: str = Field(description="The name of the city to get the weather for.")
    units: Literal["C", "F"] = Field(description="The units to use for the temperature.")

client = Client()

weather_tool = tool(
    name="get_weather",
    description="Get the weather for a given city.",
    parameters=GetWeatherRequest.model_json_schema()
)

chat = client.chat.create(
    model="grok-4-1-fast-non-reasoning",
    messages=[system("You are a helpful assistant.")],
    tools=[weather_tool]
)

chat.append(user("What's the weather like in San Francisco?"))
response = chat.sample()

# Handle tool calls
if response.tool_calls:
    for tool_call in response.tool_calls:
        args = json.loads(tool_call.function.arguments)
        # Execute your function here
        result = get_weather(args["city"], args["units"])
        chat.append(tool_result(result, tool_call_id=tool_call.id))
        response = chat.sample()
```

## Advanced Features

### Structured Outputs

```python
from xai_sdk import Client
from pydantic import BaseModel

class WeatherResponse(BaseModel):
    temperature: float
    condition: str
    humidity: int

client = Client()
chat = client.chat.create(
    model="grok-4-1-fast-non-reasoning",
    response_format=WeatherResponse
)

chat.append(user("Tell me about the weather in New York."))
response = chat.sample()
print(f"Weather: {response.temperature}°C, {response.condition}")
```

### Server-Side Tools

```python
from xai_sdk import Client
from xai_sdk.tools import web_search

client = Client()
chat = client.chat.create(
    model="grok-4-1-fast-non-reasoning",
    search_parameters=web_search(
        query="What was Arsenal's most recent game result?",
        sources=["web", "news"]
    )
)
response = chat.sample()
print(f"Grok: {response.content}")
```

### Collections API

```python
from xai_sdk import Client

client = Client()

# Create a collection
collection = client.collections.create(
    collection_name="my_documents",
    field_definitions={
        "title": {"type": "string", "required": True},
        "author": {"type": "string"}
    }
)

# Upload documents
with open("document.pdf", "rb") as f:
    client.collections.upload_document(
        collection_name="my_documents",
        file=f,
        metadata={"title": "My Document", "author": "Me"}
    )

# Search within collection
results = client.collections.search(
    collection_name="my_documents",
    query="search terms"
)
```

### OpenTelemetry Integration

```python
from xai_sdk.telemetry import Telemetry

# Setup console exporter (development)
telemetry = Telemetry()
telemetry.setup_console_exporter()

# Setup OTLP exporter (production)
telemetry.setup_otlp_exporter(
    endpoint="https://your-observability-platform.com/traces",
    headers={"Authorization": "Bearer your-token"}
)

client = Client()
# All API calls will now generate traces
```

## Configuration

### Environment Variables

- `XAI_API_KEY`: Your xAI API key (required)
- `XAI_MANAGEMENT_KEY`: Management API key for collections operations
- `XAI_SDK_DISABLE_TRACING`: Disable SDK tracing (1 or true)
- `XAI_SDK_DISABLE_SENSITIVE_TELEMETRY_ATTRIBUTES`: Exclude sensitive data from traces
- `OTEL_EXPORTER_OTLP_PROTOCOL`: OTLP protocol (grpc or http/protobuf)
- `OTEL_EXPORTER_OTLP_ENDPOINT`: OTLP endpoint URL
- `OTEL_EXPORTER_OTLP_HEADERS`: OTLP authentication headers

### Client Options

```python
from xai_sdk import Client

# Custom timeout
client = Client(timeout=300)  # 5 minutes

# Custom API hosts
client = Client(
    api_host="api.x.ai",
    management_api_host="management-api.x.ai"
)

# Custom metadata
client = Client(metadata=(
    ("custom-header", "value"),
))

# Disable retries
client = Client(channel_options=[("grpc.enable_retries", 0)])

# Use insecure channel (development)
client = Client(use_insecure_channel=True)
```

## Error Handling

```python
try:
    response = chat.sample()
except grpc.RpcError as e:
    status_code = e.code()
    if status_code == grpc.StatusCode.UNAUTHENTICATED:
        print("Invalid API key")
    elif status_code == grpc.StatusCode.DEADLINE_EXCEEDED:
        print("Request timed out")
    else:
        print(f"Error: {e}")
```

## Testing

The SDK includes a comprehensive test suite. To run tests:

```bash
uv run pytest -n auto -v
```

## Contributing

We welcome contributions! Please see our [contributing guidelines](CONTRIBUTING.md) for details on how to contribute.

## License

This project is licensed under the Apache-2.0 License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions, please visit our [documentation](https://docs.x.ai) or contact us at <support@x.ai>.

## Changelog

See the [changelog](CHANGELOG.md) for a complete list of changes across versions.
