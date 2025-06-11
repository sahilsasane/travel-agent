# AI Travel Agent Service Toolkit

A comprehensive, production-ready AI travel agent service built with LangGraph, FastAPI, and Streamlit. This advanced multi-agent system provides sophisticated travel planning capabilities including flight bookings, hotel reservations, car rentals, and personalized trip recommendations.

## Features

### Multi-Agent Travel Planning System
- **Intelligent Flight Management**: Search, book, update, and cancel flights with real-time availability
- **Hotel Booking Services**: Complete hotel reservation system with search and management capabilities
- **Car Rental Integration**: Full car rental booking and management workflow
- **Taxi Booking**: On-demand taxi booking with location-based services
- **Trip Recommendations**: AI-powered personalized travel suggestions and itinerary planning
- **Multi-Step Workflows**: Complex travel planning with agent handoffs and state management

### Advanced AI Capabilities  
- **RAG (Retrieval-Augmented Generation)**: Document search and company policy assistance
- **Research Assistant**: Web search with DuckDuckGo integration and calculator tools
- **Conversational AI**: Natural language processing for travel queries
- **Memory Management**: Persistent conversation history and user preferences
- **Safety Controls**: LlamaGuard integration for content filtering

### Production Architecture
- **FastAPI Backend**: High-performance REST API with async support
- **Streamlit Frontend**: Interactive web interface with real-time streaming
- **Multi-Database Support**: SQLite, PostgreSQL, and MongoDB backends
- **Docker Deployment**: Container-ready with Docker Compose orchestration
- **Comprehensive Testing**: Unit, integration, and end-to-end test coverage

## System Architecture

The toolkit implements a sophisticated multi-layered architecture:

### Core Components
1. **Agent Service** ([`src/service/service.py`](src/service/service.py))
   - FastAPI-based REST API server
   - WebSocket support for real-time streaming
   - Authentication and security middleware
   - Agent lifecycle management

2. **Multi-Agent Framework** ([`src/agents/`](src/agents/))
   - **Primary Assistant**: Central orchestrator for user interactions
   - **Flight Booking Agent**: Specialized flight search and booking capabilities
   - **Hotel Booking Agent**: Complete hotel reservation management
   - **Car Rental Agent**: Car rental search and booking services
   - **Taxi Booking Agent**: Local transportation coordination
   - **Trip Planning Agent**: Personalized itinerary recommendations
   - **RAG Assistant**: Document retrieval and policy questions
   - **Research Assistant**: Web search and computational tools

3. **Interactive Frontend** ([`src/streamlit_app.py`](src/streamlit_app.py))
   - Real-time chat interface with streaming responses
   - Agent selection and model configuration
   - Conversation history management
   - Feedback collection system

4. **Client SDK** ([`src/client/`](src/client/))
   - Python SDK for programmatic access
   - Async/sync API support
   - Streaming response handling
   - Error handling and retry logic

### Data Layer
- **Persistent Storage**: Multi-database backend support
- **Travel Database**: SQLite database with comprehensive travel data
- **Memory Management**: Conversation state and checkpointing
- **Document Store**: RAG system for knowledge retrieval

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

### Travel Planner
- Search and book flights
- Manage reservations
- Interactive booking process

### RAG Assistant
- Document retrieval from company handbook
- HR policy questions
- Benefits and company information

## Configuration

### Database Options

The toolkit supports multiple database backends via [`src/memory/__init__.py`](src/memory/__init__.py):

- **SQLite**: Default, file-based (set `DATABASE_TYPE=sqlite`)
- **PostgreSQL**: Production-ready (set `DATABASE_TYPE=postgres`)
- **MongoDB**: NoSQL option (requires additional setup)

### Model Providers

Supported LLM providers through [`src/schema/models.py`](src/schema/models.py):

- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Google (Gemini, VertexAI)
- Groq
- Azure OpenAI
- Ollama (local models)

## Development

### Project Structure

```
src/
├── agents/          # LangGraph agent implementations
├── client/          # Python client library
├── core/           # Core settings and configuration
├── memory/         # Database and storage backends
├── schema/         # Pydantic models and schemas
├── service/        # FastAPI service implementation
├── streamlit_app.py # Streamlit web interface
├── run_service.py  # Service entry point
└── download_db.py  # Database setup script
```


## Environment Variables

Key configuration options in [`.env`](.env):

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `HOST` | Service host | `0.0.0.0` |
| `PORT` | Service port | `8080` |
| `DATABASE_TYPE` | Database backend | `sqlite` |
| `AUTH_SECRET` | API authentication token | None |
| `LANGSMITH_API_KEY` | LangSmith tracing | Optional |
| `AGENT_URL` | Agent service URL for Streamlit | Auto-detected |
