# AI Travel Agent Service Toolkit

A comprehensive, production-ready AI travel agent service built with LangGraph, FastAPI, and Streamlit. This multi-agent system provides sophisticated travel planning capabilities including flight bookings, hotel reservations, car rentals, taxi services, and personalized trip recommendations with web search integration.

## Features

### Core Travel Agent System
- **Unified Travel Support Agent**: Primary travel assistant that coordinates all travel-related services
- **Flight Management**: Search, book, update, and cancel flights with user information tracking
- **Hotel Booking Services**: Complete hotel reservation system with search and management capabilities  
- **Car Rental Integration**: Full car rental booking and management workflow
- **Taxi Services**: On-demand taxi booking and search capabilities
- **Trip Recommendations**: AI-powered personalized travel suggestions with booking, updating, and cancellation
- **Web Search Integration**: TavilySearch integration for real-time travel information and research

### Advanced AI Capabilities
- **Multi-Agent Orchestration**: Sophisticated agent coordination with handoff capabilities
- **RAG Assistant**: Document retrieval and knowledge base assistance (available but not active by default)
- **Background Task Processing**: Async task handling for long-running operations
- **Conversational AI**: Natural language processing for complex travel queries
- **Memory Management**: Persistent conversation history and user preferences
- **Tool Error Handling**: Robust error handling and fallback mechanisms

### Production Architecture
- **FastAPI Backend**: High-performance REST API with async support and WebSocket streaming
- **Streamlit Frontend**: Interactive web interface with real-time agent communication
- **Multi-Database Support**: SQLite, PostgreSQL, and MongoDB backends
- **Client SDK**: Python client library for programmatic access
- **Docker Deployment**: Container-ready with Docker Compose orchestration
- **Comprehensive Testing**: Unit, integration, and end-to-end test coverage

## System Architecture

The toolkit implements a sophisticated multi-layered architecture with the following core components:

### Core Components

1. **Agent Service** ([`src/service/service.py`](src/service/service.py))
   - FastAPI-based REST API server with async support
   - WebSocket support for real-time streaming responses
   - Authentication and security middleware
   - Agent lifecycle management and routing
   - Service utilities for enhanced functionality ([`src/service/utils.py`](src/service/utils.py))

2. **Travel Agent System** ([`src/agents/`](src/agents/))
   - **Primary Travel Support Agent** ([`src/agents/travel_agent_support.py`](src/agents/travel_agent_support.py)): Main orchestrator for all travel-related interactions
   - **Multi-Agent Travel Planner** ([`src/agents/multi_agent_travel_planner.py`](src/agents/multi_agent_travel_planner.py)): Advanced multi-agent coordination system
   - **Travel Planner** ([`src/agents/travel_planner.py`](src/agents/travel_planner.py)): Specialized travel planning workflows
   - **Supervisor Travel** ([`src/agents/supervisor_travel.py`](src/agents/supervisor_travel.py)): Travel agent supervision and coordination
   - **RAG Assistant** ([`src/agents/rag_assistant.py`](src/agents/rag_assistant.py)): Document retrieval and knowledge base queries
   - **Background Task Agent** ([`src/agents/bg_task_agent/`](src/agents/bg_task_agent/)): Async task processing system
   - **Agent Utilities** ([`src/agents/utils.py`](src/agents/utils.py)): Shared agent functionality

3. **Travel Tools Suite** ([`src/agents/tools/`](src/agents/tools/))
   - **Flight Tools** ([`src/agents/tools/flight_tools.py`](src/agents/tools/flight_tools.py)): Flight search, booking, updates, and cancellations
   - **Hotel Tools** ([`src/agents/tools/hotel_tools.py`](src/agents/tools/hotel_tools.py)): Hotel search and booking management
   - **Car Rental Tools** ([`src/agents/tools/car_rental_tools.py`](src/agents/tools/car_rental_tools.py)): Car rental services
   - **Taxi Tools** ([`src/agents/tools/taxi_tools.py`](src/agents/tools/taxi_tools.py)): Taxi booking and search
   - **Trip Recommendations** ([`src/agents/tools/trip_recommendations.py`](src/agents/tools/trip_recommendations.py)): AI-powered travel suggestions
   - **Error Handling** ([`src/agents/tools/error_handling.py`](src/agents/tools/error_handling.py)): Robust tool error management

4. **Interactive Frontend** ([`src/streamlit_app.py`](src/streamlit_app.py))
   - Real-time chat interface with streaming responses
   - Agent selection and model configuration
   - Conversation history management  
   - Feedback collection system
   - Integration with agent service backend

5. **Client SDK** ([`src/client/client.py`](src/client/client.py))
   - Python SDK for programmatic access
   - Async and synchronous API support
   - Streaming response handling
   - Built-in error handling and retry logic

### Core Infrastructure

6. **LLM Integration** ([`src/core/`](src/core/))
   - **Model Management** ([`src/core/llm.py`](src/core/llm.py)): Multi-provider LLM integration
   - **Settings Configuration** ([`src/core/settings.py`](src/core/settings.py)): Centralized configuration management

7. **Memory & Storage** ([`src/memory/`](src/memory/))
   - **SQLite Backend** ([`src/memory/sqlite.py`](src/memory/sqlite.py)): Default file-based storage
   - **PostgreSQL Backend** ([`src/memory/postgres.py`](src/memory/postgres.py)): Production database support
   - **MongoDB Backend** ([`src/memory/mongodb.py`](src/memory/mongodb.py)): NoSQL document storage
   - Conversation state persistence and checkpointing

8. **Schema & Models** ([`src/schema/`](src/schema/))
   - **Data Models** ([`src/schema/models.py`](src/schema/models.py)): LLM provider configurations and model definitions
   - **API Schema** ([`src/schema/schema.py`](src/schema/schema.py)): Request/response models and validation
   - **Task Data** ([`src/schema/task_data.py`](src/schema/task_data.py)): Background task data structures

### Execution Scripts

9. **Runtime Components**
   - **Service Runner** ([`src/run_service.py`](src/run_service.py)): FastAPI service startup
   - **Agent Runner** ([`src/run_agent.py`](src/run_agent.py)): Direct agent execution
   - **Client Runner** ([`src/run_client.py`](src/run_client.py)): SDK demonstration and testing
   - **Database Setup** ([`src/download_db.py`](src/download_db.py)): Travel database initialization

### Data Layer
- **Travel Database**: SQLite database with comprehensive travel data (flights, hotels, car rentals)
- **Conversation Memory**: Multi-backend conversation state and history management
- **Agent Checkpointing**: LangGraph state persistence for complex workflows

## Quick Start

### Prerequisites

- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/) package manager

### 1. Set up the Environment

Create and activate a virtual environment using uv:

```bash
# Create virtual environment
uv venv

# Activate virtual environment
# On Unix/macOS:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate
```

### 2. Install Dependencies

Install all project dependencies:

```bash
uv sync --frozen
```


### 3. Download Database

Download the travel database for the travel planner agent:

```bash
python src/download_db.py
```

### 4. Configure Environment

Copy the example environment file and configure your API keys:

```bash
cp .env.example .env
```

Edit [`.env`](.env) and add your API keys:

```env
# Required for most agents
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here

# Optional: Other provider keys
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key
GROQ_API_KEY=your_groq_key

# For VertexAI (see docs/VertexAI.md for setup)
GOOGLE_APPLICATION_CREDENTIALS=path_to_service_account.json
```

### 5. Run the Application

#### Option A: Run Both Services Separately

**Terminal 1 - Start the Agent Service:**
```bash
python src/run_service.py
```

**Terminal 2 - Start the Streamlit App:**
```bash
streamlit run src/streamlit_app.py
```

#### Option B: Use Docker Compose

```bash
docker compose up --build
```

### 6. Access the Application

- **Streamlit App**: http://localhost:8501
- **Agent Service API**: http://localhost:8080
- **API Documentation**: http://localhost:8080/docs

## Available Agents

### Current Active Agent: Travel Agent Support
The system currently runs a unified **Travel Agent Support** agent (`travel-agent-support`) that provides:

- **Comprehensive Travel Services**: Flight, hotel, car rental, and taxi booking capabilities
- **Trip Planning**: Personalized recommendations and itinerary management  
- **Web Search Integration**: Real-time travel information via TavilySearch
- **Multi-Tool Coordination**: Seamless integration of all travel-related tools
- **Error Handling**: Robust fallback mechanisms for failed operations
- **Conversation Memory**: Persistent dialogue state and context management

### Additional Available Agents (Commented Out)
The system includes several other specialized agents that can be activated by uncommenting them in [`src/agents/agents.py`](src/agents/agents.py):

- **Multi-Agent Travel Planner**: Advanced multi-agent coordination system
- **Supervisor Travel**: Travel agent supervision and orchestration
- **RAG Assistant**: Document retrieval and knowledge base queries
- **Background Task Agent**: Async task processing capabilities

*Note: Only the Travel Agent Support agent is currently active by default. Other agents can be enabled by modifying the agents configuration.*

## Configuration

### Database Options

The toolkit supports multiple database backends via [`src/memory/`](src/memory/):

- **SQLite** ([`src/memory/sqlite.py`](src/memory/sqlite.py)): Default, file-based storage (set `DATABASE_TYPE=sqlite`)
- **PostgreSQL** ([`src/memory/postgres.py`](src/memory/postgres.py)): Production-ready relational database (set `DATABASE_TYPE=postgres`)
- **MongoDB** ([`src/memory/mongodb.py`](src/memory/mongodb.py)): NoSQL document database (requires additional setup)

### Model Providers

Supported LLM providers through [`src/schema/models.py`](src/schema/models.py):

- **OpenAI**: GPT-4, GPT-3.5, and other OpenAI models
- **Anthropic**: Claude family models  
- **Google**: Gemini and VertexAI models
- **Groq**: High-speed inference models
- **Azure OpenAI**: Enterprise OpenAI integration
- **Ollama**: Local model execution
- **AWS Bedrock**: Amazon's managed AI service
- **OpenAI-Compatible**: Custom API endpoints

## Development

### Project Structure

```
src/
├── agents/                    # LangGraph agent implementations
│   ├── __init__.py           # Agent registry and access functions
│   ├── agents.py             # Main agent definitions and configuration
│   ├── travel_agent_support.py # Primary travel support agent
│   ├── multi_agent_travel_planner.py # Multi-agent coordination system
│   ├── travel_planner.py     # Specialized travel planning workflows
│   ├── supervisor_travel.py  # Travel agent supervision
│   ├── rag_assistant.py      # RAG document retrieval assistant
│   ├── travel_agents.py      # Additional travel agent utilities
│   ├── utils.py              # Shared agent functionality
│   ├── bg_task_agent/        # Background task processing
│   │   ├── bg_task_agent.py  # Async task agent implementation
│   │   └── task.py           # Task data structures
│   ├── db/                   # Agent-specific databases
│   │   └── travel.sqlite     # Travel data storage
│   └── tools/                # Agent tool implementations
│       ├── __init__.py       # Tool registry
│       ├── flight_tools.py   # Flight booking and management
│       ├── hotel_tools.py    # Hotel reservation tools
│       ├── car_rental_tools.py # Car rental services
│       ├── taxi_tools.py     # Taxi booking tools
│       ├── trip_recommendations.py # AI trip suggestions
│       └── error_handling.py # Tool error management
├── client/                   # Python client SDK
│   ├── __init__.py          # Client exports
│   └── client.py            # Main client implementation
├── core/                    # Core system components
│   ├── __init__.py          # Core exports
│   ├── llm.py               # LLM provider integration
│   └── settings.py          # Configuration management
├── memory/                  # Database backends
│   ├── __init__.py          # Memory system exports
│   ├── sqlite.py            # SQLite backend
│   ├── postgres.py          # PostgreSQL backend
│   └── mongodb.py           # MongoDB backend
├── schema/                  # Data models and validation
│   ├── __init__.py          # Schema exports
│   ├── models.py            # LLM model definitions
│   ├── schema.py            # API request/response models
│   └── task_data.py         # Background task schemas
├── service/                 # FastAPI service implementation
│   ├── __init__.py          # Service exports
│   ├── service.py           # Main FastAPI application
│   └── utils.py             # Service utilities
├── streamlit_app.py         # Streamlit web interface
├── run_service.py           # Service startup script
├── run_agent.py             # Direct agent execution
├── run_client.py            # Client SDK demo
└── download_db.py           # Database setup script
```


## Environment Variables

Key configuration options in [`.env`](.env):

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `TAVILY_API_KEY` | Tavily search API key | Required for web search |
| `ANTHROPIC_API_KEY` | Anthropic Claude API key | Optional |
| `GOOGLE_API_KEY` | Google AI API key | Optional |
| `GROQ_API_KEY` | Groq API key | Optional |
| `HOST` | Service host | `0.0.0.0` |
| `PORT` | Service port | `8080` |
| `DATABASE_TYPE` | Database backend | `sqlite` |
| `AUTH_SECRET` | API authentication token | None |
| `LANGSMITH_API_KEY` | LangSmith tracing | Optional |
| `AGENT_URL` | Agent service URL for Streamlit | Auto-detected |

## Usage Examples

### Using the Client SDK

```python
import asyncio
from client import AgentClient

async def example_usage():
    client = AgentClient("http://localhost:8080")
    
    # Get agent information
    print("Available agents:", client.info)
    
    # Simple query
    response = await client.ainvoke(
        "Find me flights from New York to London", 
        model="gpt-4o"
    )
    response.pretty_print()
    
    # Streaming responses
    async for message in client.astream("Plan a 3-day trip to Paris"):
        if isinstance(message, str):
            print(message, end="", flush=True)

asyncio.run(example_usage())
```

### Direct Agent Execution

```python
import asyncio
from uuid import uuid4
from langchain_core.runnables import RunnableConfig
from agents import get_agent, DEFAULT_AGENT

async def run_agent_directly():
    agent = get_agent(DEFAULT_AGENT)
    
    inputs = {
        "messages": [("user", "Help me book a hotel in San Francisco")]
    }
    
    result = await agent.ainvoke(
        inputs,
        config=RunnableConfig(configurable={"thread_id": uuid4()})
    )
    
    result["messages"][-1].pretty_print()

asyncio.run(run_agent_directly())
```


## API Endpoints

When running the service, the following endpoints are available:

- `GET /` - Service health check and metadata
- `POST /invoke` - Synchronous agent invocation
- `POST /stream` - Streaming agent responses
- `POST /feedback` - Submit user feedback
- `GET /chat/history/{thread_id}` - Retrieve conversation history
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation


## Tool Capabilities

### Flight Management Tools
- **Search Flights**: Find available flights with flexible search criteria
- **Book Flight**: Complete flight reservation with passenger details
- **Update Flight**: Modify existing flight reservations
- **Cancel Flight**: Cancel bookings with proper confirmation
- **Fetch User Flight Information**: Retrieve user's current flight bookings

### Hotel Services
- **Search Hotels**: Find accommodations by location, dates, and preferences
- **Book Hotel**: Complete hotel reservations with room preferences
- **Update Hotel Booking**: Modify existing hotel reservations
- **Cancel Hotel Booking**: Cancel hotel reservations with confirmation

### Transportation Services
- **Car Rental Tools**: Search, book, update, and cancel car rentals
- **Taxi Services**: Book and search for taxi services in any location

### Trip Planning
- **Search Trip Recommendations**: Get AI-powered travel suggestions
- **Book Trip**: Reserve complete trip packages
- **Update Trip**: Modify existing trip reservations
- **Cancel Trip**: Cancel trip bookings with proper handling

### Web Search Integration
- **TavilySearch**: Real-time web search for travel information, current prices, and recommendations

## Error Handling & Reliability

The system includes comprehensive error handling:

- **Tool Fallbacks**: Automatic fallback mechanisms when tools fail
- **Error Recovery**: Graceful degradation and user notification
- **Retry Logic**: Automatic retry for transient failures
- **Validation**: Input validation and sanitization
- **Logging**: Comprehensive logging for debugging and monitoring

## Troubleshooting

### Common Issues

**Agent Not Responding**
```bash
# Check if the service is running
curl http://localhost:8080/

# Verify environment variables
python -c "from core import settings; print(settings.model_dump())"
```

**Database Connection Issues**
```bash
# Download the travel database
python src/download_db.py

# Check database connectivity
python -c "from memory.sqlite import get_connection; print('DB OK')"
```

**API Key Issues**
```bash
# Verify API keys are loaded
python -c "from core import settings; print('OpenAI:', bool(settings.OPENAI_API_KEY))"
```

**Streamlit Frontend Issues**
```bash
# Run Streamlit with debugging
streamlit run src/streamlit_app.py --logger.level=debug

# Check agent service connection
curl http://localhost:8080/
```

### Performance Optimization

- **Model Selection**: Choose appropriate models for your use case (faster models for simple queries)
- **Database Optimization**: Use PostgreSQL for production workloads
- **Caching**: Enable response caching for frequently asked queries
- **Async Operations**: Use async client methods for better performance

### Adding New Tools

To add new travel-related tools:

1. Create tool implementation in `src/agents/tools/`
2. Add tool imports to the main agent in `src/agents/travel_agent_support.py`
3. Update tool lists and routing logic
4. Add comprehensive tests
5. Update documentation

### Adding New Agents

To add new specialized agents:

1. Create agent implementation in `src/agents/`
2. Register agent in `src/agents/agents.py`
3. Add agent-specific tools and workflows
4. Update tests and documentation

## Support

For support and questions:

- **Documentation**: See the `docs/` folder for specialized setup guides
- **Examples**: Check the `notebooks/` folder for usage examples

## Acknowledgments

Built with:
- [LangGraph](https://github.com/langchain-ai/langgraph) - Multi-agent orchestration
- [FastAPI](https://fastapi.tiangolo.com/) - High-performance web framework
- [Streamlit](https://streamlit.io/) - Interactive web applications
- [LangChain](https://langchain.com/) - LLM application framework
- [Pydantic](https://pydantic.dev/) - Data validation and settings management
