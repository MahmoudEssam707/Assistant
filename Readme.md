# Assistant Agent - Technical Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Why LangChain vs Workflow Automation Tools](#why-langchain-vs-workflow-automation-tools)
3. [Architecture & Design Decisions](#architecture--design-decisions)
4. [Agent Implementation](#agent-implementation)
5. [Tools Integration](#tools-integration)
6. [Memory & State Management](#memory--state-management)
7. [Deployment Setup](#deployment-setup)
8. [API & UI Layer](#api--ui-layer)

---

## Project Overview

### What We Built
The Assistant is an intelligent AI agent system built with LangChain and LangGraph that combines:
- **Multi-tool capabilities**: Calculator, Gmail integration, and knowledge base search
- **Persistent memory**: Maintains conversation history across sessions using SQLite checkpoints
- **RESTful API**: FastAPI backend for agent communication
- **User-friendly interface**: Streamlit chat UI
- **Containerized deployment**: Docker Compose for easy deployment and scaling

### Project Structure
```
Assistant/
├── agent/
│   ├── __init__.py
│   └── graph.py              # Agent graph definition
├── utils/
│   ├── __init__.py
│   ├── nodes.py              # Agent executor with tools and memory
│   ├── tools.py              # Tool definitions (@tool decorators)
│   └── util.py               # Shared utilities (LLM, embeddings, logging)
├── test/
│   ├── __init__.py
│   ├── test_embed.py        # Testing your Embed Works
│   ├── test_llm.py          # Testing your LLM Works
│   └── test_qdrant.py       # Testing your Vector Works and set your data
├── server.py                # FastAPI backend server
├── chat_ui.py               # Streamlit frontend
├── requirements.txt         # Python dependencies
├── Dockerfile               # Container image definition
├── docker-compose.yml       # Multi-container orchestration
├── .env.example             # Environment variables 
├── checkpoints.db           # SQLite database for memory (auto-generated)
└── state_logs.log           # Application logs (auto-generated)
```

---

## Why LangChain vs Workflow Automation Tools

### The Decision: LangChain Over Zapier/N8N/Dify

We chose LangChain instead of workflow automation tools because our Assistant requires:

#### 1. **Dynamic Reasoning**
**Automation Tools (Zapier/N8N):**
- Execute fixed if-then workflows
- Cannot adapt to context
- Example: "IF email contains 'urgent' THEN send notification"

**Our LangChain Agent:**
- Analyzes user intent in natural language
- Decides which tool to use based on context
- Handles multi-step reasoning
- Example: User says "What's 5*7 and send the result to john@example.com" → Agent:
  1. Recognizes two tasks
  2. Uses calculator tool for math
  3. Composes professional email
  4. Uses Gmail tool to send

#### 2. **Natural Language Understanding**
- Users interact in plain English, not structured forms
- Agent interprets intent: "email my colleague about the meeting" vs "send email to user@example.com"
- Handles ambiguity and asks clarifying questions

#### 3. **Custom Tool Integration**
- **Qdrant Vector Database**: For semantic knowledge search
- **Jina Embeddings**: For document embeddings
- **Gmail SMTP**: Direct email sending
- **Custom Calculator**: Math evaluation

These integrations would require extensive custom development in automation tools, while LangChain provides native support through the `@tool` decorator.

#### 4. **Persistent, Contextual Memory**
- Remembers entire conversation history per user (thread-based)
- Uses SQLite checkpointer for persistence across restarts
- Automation tools typically have limited state management

#### 5. **Flexibility & Control**
- Full control over agent behavior and prompts
- Can modify reasoning patterns
- Can add/remove tools dynamically
- Open-source with no vendor lock-in

### When Automation Tools Would Be Better
- Simple trigger-based workflows (e.g., "When form submitted, save to spreadsheet")
- No-code requirement
- Pre-built integrations are sufficient
- No need for natural language understanding

### Our Use Case Fit
✅ **Perfect for LangChain:**
- Conversational AI assistant
- Multi-tool coordination
- Context-aware responses
- Knowledge retrieval with semantic search
- Email composition with intelligence

---

## Architecture & Design Decisions

### Agent Type: LangGraph with create_agent

We use **LangGraph's `create_agent`** function instead of traditional LangChain agents.

#### Why LangGraph?
1. **State Management**: Built-in state graphs for complex workflows
2. **Checkpointing**: Native persistent memory using `SqliteSaver`
3. **Streaming**: Real-time response streaming for better UX
4. **Message Format**: Direct message input without wrapper objects
5. **Production-Ready**: Designed for scalable, production deployments

#### Why Not ReAct or OpenAI Functions Agent?
- **ReAct Agent**: Limited memory capabilities, no built-in checkpointing
- **OpenAI Functions Agent**: Good for function calling but lacks LangGraph's state management
- **LangGraph Agent**: Combines benefits of both + persistent memory + streaming

### Agent Architecture Flow

```
User Input (Chat UI)
    ↓
FastAPI Endpoint (/query)
    ↓
LangGraph Agent (with memory checkpoint)
    ↓
System Prompt → LLM → Tool Selection
    ↓
Tool Execution (calculator/gmail/qdrant)
    ↓
Tool Results → LLM → Final Response
    ↓
Response Streamed Back
    ↓
Stored in SQLite Checkpoint
    ↓
Displayed in Chat UI
```

### Key Design Patterns Used

#### 1. **Thread-Based Memory**
Each user/conversation has a unique `thread_id` that maintains separate memory:
```python
config = {"configurable": {"thread_id": request.thread_id}}
graph.stream(inputs, config=config)
```

#### 2. **Streaming Updates**
Agent streams results in real-time for responsive UX:
```python
for chunk in graph.stream(inputs, config=config, stream_mode="updates"):
    # Process tool outputs and AI messages
```

#### 3. **Tool Decorator Pattern**
All tools use `@tool` decorator for clean, type-safe definitions:
```python
@tool
def calculator_tool(expression: str) -> str:
    """Evaluate a mathematical expression."""
```

#### 4. **Separation of Concerns**
- **server.py**: API layer (FastAPI)
- **chat_ui.py**: Presentation layer (Streamlit)
- **agent/graph.py**: Agent orchestration
- **utils/nodes.py**: Agent configuration and memory
- **utils/tools.py**: Tool implementations
- **utils/util.py**: Shared utilities

---

## Agent Implementation

### The Core Agent (utils/nodes.py)

#### Agent Executor Setup
Our implementation uses LangGraph's `create_agent` with SQLite checkpointing:

```python
agent_executor = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt,
    checkpointer=memory,
)
```

**Why This Approach:**
- `create_agent`: LangGraph's simplified agent creation
- `model`: Custom LLM configuration (supports any OpenAI-compatible API)
- `tools`: List of three available tools
- `system_prompt`: Defines agent personality and tool usage guidelines
- `checkpointer`: SQLite-based persistent memory

#### Memory Implementation
```python
conn = sqlite3.connect("checkpoints.db", check_same_thread=False)
memory = SqliteSaver(conn)
```

**How It Works:**
- Creates/opens `checkpoints.db` SQLite database
- `check_same_thread=False`: Allows multi-threaded FastAPI access
- `SqliteSaver`: LangGraph's checkpoint manager
- Automatically saves agent state after each interaction
- Loads previous state when `thread_id` is reused

#### System Prompt Design
Our system prompt (`utils/nodes.py`) defines:

1. **Agent Identity**: "You are My Assistant, a helpful and reliable AI assistant"
2. **Available Tools**: Lists each tool with usage guidelines
3. **Tool Selection Logic**: When to use which tool
4. **Behavioral Guidelines**:
   - Chat naturally
   - Always use tools (don't perform actions manually)
   - Be concise and accurate
   - Handle errors gracefully
   - Don't expose internal details
5. **Examples**: Demonstrates proper tool usage

**Key Principle**: The system prompt is the "brain" of the agent—it determines how the agent thinks and acts.

### LLM Configuration (utils/util.py)

```python
llm = ChatOpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL"),
    model=os.getenv("LLM_MODEL_NAME"),
)
```

**Flexibility:**
- Works with any OpenAI-compatible API (OpenAI, Azure, local models, etc.)
- Configurable via environment variables
- Easy to swap models without code changes

### Embeddings Configuration

```python
embeddings = JinaEmbeddings(
    jina_api_key=os.getenv("JINA_EMBEDDING_API_KEY"),
    model_name=os.getenv("JINA_EMBEDDING_MODEL"),
)
```

**Why Jina Embeddings:**
- High-quality multilingual embeddings
- API-based (no local model needed)
- Used for semantic search in Qdrant

---

## Tools Integration

We implemented three tools for the agent using the `@tool` decorator pattern.

### Tool 1: Calculator Tool

**Purpose**: Evaluate mathematical expressions

**Location**: `utils/tools.py`

**How It Works:**
1. Agent receives math question: "What is 5 * 7?"
2. Agent recognizes need for calculation
3. Calls `calculator_tool("5 * 7")`
4. Tool evaluates expression using Python's `eval()`
5. Returns "35"
6. Agent responds: "The result is 35"

**Implementation Detail:**
- Uses Python's `eval()` for simplicity
- Includes error handling for invalid expressions
- Returns string result for LLM consumption

**Safety Note**: In production, consider using `ast.literal_eval()` or a math parser library for security.

### Tool 2: Gmail Send Tool

**Purpose**: Send emails via Gmail SMTP

**Location**: `utils/tools.py`

**How It Works:**
1. User: "Send an email to john@example.com about the meeting tomorrow"
2. Agent extracts: recipient, subject (inferred), body (composed)
3. Agent makes professional email body
4. Calls `gmail_send_tool("john@example.com", "Meeting Tomorrow", "...")`
5. Tool calls `send_email_smtp()` helper function
6. Email sent via Gmail SMTP server
7. Returns success message

**Supporting Function** (`utils/util.py`):
The `send_email_smtp()` function handles:
- Loading Gmail credentials from environment
- Creating MIME message
- Connecting to Gmail SMTP server (SSL on port 465)
- Authentication and sending
- Error handling

**Configuration Requirements:**
- `SMTP_EMAIL`: Gmail address
- `SMTP_PASSWORD`: Gmail App Password (not regular password)
- Gmail account must have:
  - 2FA enabled
  - App Password generated from Google Account settings

### Tool 3: Knowledge Base Search (Agentic RAG)

**Purpose**: Search programming/Python knowledge using semantic similarity

**Location**: `utils/tools.py`

**How It Works:**
1. User asks: "What is a list comprehension in Python?"
2. Agent recognizes this is a knowledge question
3. Calls `search_in_knowledge("list comprehension Python")`
4. Tool:
   - Converts query to vector using Jina embeddings (`embeddings.embed_query()`)
   - Searches Qdrant vector database for similar documents
   - Returns most relevant document content (top 1 result)
5. Agent synthesizes answer from retrieved knowledge

**Qdrant Configuration:**
```python
client = QdrantClient(
    url=os.getenv("QDRANT_BASE_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
)
```

**Why Qdrant:**
- Vector database optimized for similarity search
- Fast retrieval with embeddings
- Cloud-hosted option available
- Simple API for query_points

**This is RAG (Retrieval-Augmented Generation):**
1. **Retrieval**: Search knowledge base for relevant info
2. **Augmentation**: Provide retrieved context to LLM
3. **Generation**: LLM generates answer based on context

**Agentic RAG Aspect:**
- Agent decides WHEN to search (only when needed)
- Agent formulates search query (not just using user input as-is)
- Agent can search multiple times if needed
- Agent reasons over retrieved information

---

## Memory & State Management

### Persistent Memory Architecture

#### SQLite Checkpointing
```python
conn = sqlite3.connect("checkpoints.db", check_same_thread=False)
memory = SqliteSaver(conn)
```

**What Gets Saved:**
- All user messages
- All agent responses
- Tool calls and results
- Intermediate reasoning steps

**How It Persists:**
- Stored in `checkpoints.db` file
- Survives server restarts
- Thread-specific: each `thread_id` has separate history

#### Thread-Based Sessions
```python
config = {"configurable": {"thread_id": request.thread_id}}
```

**Benefits:**
1. **Multi-User Support**: Different users have different `thread_id`
2. **Conversation Continuity**: "What did I ask you earlier?" works
3. **Context Awareness**: Agent remembers previous interactions
4. **Isolation**: User A's history doesn't affect User B

**Example:**
```
Thread: user_123
├─ Message 1: "My name is John"
├─ Response 1: "Nice to meet you, John!"
├─ Message 2: "What's my name?"
└─ Response 2: "Your name is John." (remembers from Message 1)
```

### Message Flow in Memory

1. **User sends message** → Stored in checkpoint
2. **Agent processes** → Stores reasoning steps
3. **Tool executed** → Stores tool call and result
4. **Agent responds** → Stores final response
5. **Next message** → Loads entire history for context

### State Structure (utils/util.py)

```python
class State(TypedDict):
    """State structure with message history."""
    messages: Annotated[list, add_messages]
```

**The `add_messages` Annotation:**
- LangGraph helper function
- Automatically appends new messages to list
- Maintains chronological order
- Handles message deduplication

---

## Deployment Setup

### Containerization Strategy

#### Why Docker?
1. **Consistency**: Same environment in dev and production
2. **Isolation**: Dependencies don't conflict with host system
3. **Scalability**: Easy to scale services independently
4. **Portability**: Run anywhere Docker is installed

### Dockerfile Explained

**Base Image:**
```dockerfile
FROM python:3.11-slim
```
- Uses Python 3.11 slim version (smaller image size)

**Working Directory & Environment:**
```dockerfile
WORKDIR /app
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
```
- Sets `/app` as working directory
- Configures Python path for imports
- Disables output buffering (for real-time logs)
- Prevents `.pyc` file creation (cleaner container)

**System Dependencies:**
```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*
```
- Installs compilers needed for Python packages
- `curl` for health checks
- Cleans up after to reduce image size

**Python Dependencies:**
```dockerfile
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
```
- Copies requirements first (Docker layer caching)
- Upgrades pip
- Installs all dependencies
- `--no-cache-dir`: Reduces image size

**Application Code:**
```dockerfile
COPY . .
```
- Copies entire application directory

**Security:**
```dockerfile
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app
```
- **Security best practice**: Don't run as root
- Creates non-privileged user `app`
- Changes ownership of files
- Runs application as `app` user

**Port Exposure:**
```dockerfile
EXPOSE 8501 2024
```
- Documents ports (8501 for Streamlit, 2024 for FastAPI)
- Doesn't actually publish (docker-compose does that)

### Docker Compose Architecture

We use a multi-service architecture with two containers:

#### Service 1: API (FastAPI Backend)

```yaml
api:
  build: .
  container_name: assistant-api
  ports:
    - "2024:2024"
  env_file:
    - .env
  command: ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "2024"]
  volumes:
    - .:/app
  restart: unless-stopped
```

**Key Points:**
- Builds from Dockerfile
- Maps port 2024 (host) → 2024 (container)
- Loads environment from `.env` file
- Runs uvicorn ASGI server on all interfaces
- Volume mount for live code updates during development
- Auto-restarts on failure

#### Service 2: UI (Streamlit Frontend)

```yaml
ui:
  build: .
  container_name: assistant-ui
  ports:
    - "8501:8501"
  env_file:
    - .env
  command: ["streamlit", "run", "chat_ui.py"]
  depends_on:
    - api
  restart: unless-stopped
```

**Key Points:**
- Same Dockerfile, different command
- Maps port 8501 for Streamlit
- `depends_on`: Ensures API starts first
- Communicates with API via Docker network

### Service Communication

```
Internet
    ↓
localhost:8501 (Streamlit UI) ← User accesses this
    ↓
Docker Network (internal)
    ↓
assistant-api:2024 (FastAPI) ← UI calls this
    ↓
External Services (OpenAI, Qdrant, Gmail)
```

**Container Networking:**
- Both services on same Docker network (auto-created)
- UI refers to API by container name: `assistant-api`
- Docker's DNS resolves `assistant-api` to API container's IP
- No localhost issues across containers

### Running the System

```bash
# Start both services in background
docker compose up -d

# View logs
docker compose logs -f

# View specific service logs
docker compose logs -f api
docker compose logs -f ui

# Stop services
docker compose down

# Rebuild after code changes
docker compose up -d --build

# Check status
docker compose ps
```

---

## API & UI Layer

### FastAPI Backend (server.py)

#### Endpoints

**1. Root Endpoint (`GET /`)**
```
GET http://localhost:2024/
```
- Health check
- Confirms service is running
- Returns: `{"message": "Agent API is running!"}`

**2. Health Endpoint (`GET /health`)**
```
GET http://localhost:2024/health
```
- Detailed health check
- Returns: `{"status": "healthy", "service": "Agent"}`

**3. Query Endpoint (`POST /query`)**
```
POST http://localhost:2024/query
Content-Type: application/json

{
  "message": "What is 5 * 7?",
  "thread_id": "user_123"
}
```

**Request Model (Pydantic):**
- `message` (str): User's message
- `thread_id` (str): Session identifier (default: "Default")

**Response Model:**
- `response` (str): Agent's response
- `thread_id` (str): Echo back thread_id

**Processing Logic:**

**Step 1: Receive & Prepare**
```python
inputs = {"messages": [{"role": "user", "content": request.message}]}
```
- Wraps user message in LangGraph message format

**Step 2: Configure Memory**
```python
config = {"configurable": {"thread_id": request.thread_id}}
```
- Links request to specific conversation thread

**Step 3: Stream Agent Response**
```python
for chunk in graph.stream(inputs, config=config, stream_mode="updates"):
    stream_results.append(chunk)
```
- Streams updates as agent processes
- `stream_mode="updates"`: Gets incremental updates (tool calls, messages)
- Collects all chunks for processing

**Step 4: Extract Results**
The streaming produces chunks with different types:
- `'tools'` key: Contains tool execution results
- `'model'` key: Contains AI-generated messages

We extract both:
```python
for chunk in stream_results:
    if 'tools' in chunk:
        # Extract tool outputs
    if 'model' in chunk:
        # Extract AI response
```

**Step 5: Combine & Return**
- Tool outputs shown first (transparency)
- Final AI message is the complete answer
- Combined for full response

**Error Handling:**
```python
try:
    # ... processing ...
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
```
- Catches all errors gracefully
- Returns HTTP 500 with error details

#### Logging Strategy

**Location**: `state_logs.log` (auto-created)

**What We Log:**
- Incoming requests with truncated message preview
- Thread IDs (for debugging memory issues)
- Input format sent to graph
- Each streaming chunk
- Tool outputs and AI messages
- Errors with full context

**Example Log Flow:**
```
INFO: Received query: What is 5 * 7?...
INFO: Thread ID: user_123
INFO: Created inputs: {'messages': [{'role': 'user', 'content': 'What is 5 * 7?'}]}
INFO: Starting graph stream...
INFO: Chunk 0: {'tools': ...}
INFO: Found tool output: 35...
INFO: Found AI message: The result is 35...
INFO: Returning response: 35...
```

### Streamlit Chat UI (chat_ui.py)

#### Page Configuration
```python
st.set_page_config(page_title="Assistant", page_icon="🤖")
```
- Sets browser tab title and icon

#### Custom CSS
```python
st.markdown("""<style>
.e1o8oa9v2.st-emotion-cache-14vh5up.stAppToolbar {
    display: none !important;
}
</style>""", unsafe_allow_html=True)
```
- Hides Streamlit toolbar for cleaner look

#### SimpleChat Class

**API Connection:**
```python
self.api_url = "http://assistant-api:2024"
```
- Points to API container using Docker network name
- Not localhost (doesn't work across containers)
- Port 2024 (FastAPI server)

**Send Message Method:**
```python
def send_message(self, message: str) -> Optional[str]:
    payload = {"message": message, "thread_id": "simple_chat"}
    response = requests.post(f"{self.api_url}/query", json=payload)
    return response.json()["response"]
```

**Current Limitation:**
- Uses fixed `"simple_chat"` thread_id for all users
- In production: implement user authentication and user-specific thread IDs

#### Chat Interface Logic

**1. Session State Initialization**
```python
if "messages" not in st.session_state:
    st.session_state.messages = []
```
- Stores chat history in Streamlit session
- Separate from agent memory (just for display)
- Persists across Streamlit reruns

**2. Display Chat History**
```python
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
```
- Shows previous messages on page load
- Maintains chat appearance
- Uses Streamlit's native chat message component

**3. Handle User Input**
```python
prompt = st.chat_input("Message")
if prompt:
    # 1. Add to session state
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 2. Display user message
    with st.chat_message("user"):
        st.write(prompt)
    
    # 3. Get agent response with loading spinner
    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            response = self.send_message(prompt)
        st.write(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
```

**UI Flow:**
1. User types message in input box
2. Message added to session state immediately
3. Message displayed in chat
4. Spinner shows while waiting for agent
5. Agent response displayed
6. Response added to session state

**Why Session State:**
- Streamlit reruns script on each interaction
- Session state persists data across reruns
- Without it, chat history would disappear

### Complete Request Flow Example

**User Action**: Types "What is 5*7?" in UI and presses Enter

**Step 1: UI Captures**
```
Streamlit chat_input receives: "What is 5*7?"
```

**Step 2: UI Sends to API**
```
POST http://assistant-api:2024/query
Body: {
  "message": "What is 5*7?",
  "thread_id": "simple_chat"
}
```

**Step 3: API Processes**
```
server.py receives request
↓
Loads memory for thread "simple_chat"
↓
Sends to LangGraph agent
↓
Agent analyzes: "This is a math question"
↓
Agent calls: calculator_tool("5*7")
↓
Tool returns: "35"
↓
Agent generates: "The result is 35"
```

**Step 4: API Returns**
```
Response: {
  "response": "35",
  "thread_id": "simple_chat"
}
```

**Step 5: UI Displays**
```
Streamlit shows: "35" in assistant message box
```

**Step 6: Memory Saved**
```
checkpoints.db updated with:
- User message: "What is 5*7?"
- Tool call: calculator_tool("5*7")
- Tool result: "35"
- Agent response: "The result is 35"
```

---

## Summary: What Makes This Implementation Special

### 1. **Agent Intelligence**
- Not just executing scripts—reasoning about what to do
- Natural language understanding
- Multi-tool coordination
- Context-aware responses

### 2. **Persistent Memory**
- SQLite-backed checkpoints survive restarts
- Thread-based isolation for multi-user support
- Full conversation history maintained

### 3. **Modular Architecture**
- Clean separation: API, UI, Agent, Tools, Utils
- Easy to add new tools
- Easy to swap LLM providers

### 4. **Production-Ready Deployment**
- Containerized with Docker
- Multi-service orchestration
- Health checks and auto-restart
- Environment-based configuration

### 5. **RAG Capabilities (Agentic RAG)**
- Vector database integration (Qdrant)
- Semantic search with Jina embeddings
- Agent decides when to search knowledge base
- Intelligent query formulation

### 6. **Email Intelligence**
- Composes professional emails
- Understands intent from natural language
- SMTP integration with error handling

### 7. **Developer Experience**
- Comprehensive logging
- Streaming responses for real-time feedback
- Easy local development with volume mounts
- Type-safe with Pydantic models

---

## Environment Variables Reference

Create a `.env` file in the project root:

```bash
# LLM Configuration
LLM_API_KEY=your_openai_api_key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL_NAME=gpt-4

# Jina Embeddings
JINA_EMBEDDING_API_KEY=your_jina_api_key
JINA_EMBEDDING_MODEL=jina-embeddings-v2-base-en

# Qdrant Vector Database
QDRANT_BASE_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key

# Gmail SMTP
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_gmail_app_password
```

---

## Potential Enhancements

### 1. Multi-User Support
- Implement user authentication
- User-specific thread IDs
- User management dashboard

### 2. Additional Tools
- Web search integration (DuckDuckGo, SerpAPI)
- File operations (read, write, upload)
- Database queries
- Calendar management
- Weather API

### 3. Better RAG
- Multiple Qdrant collections for different knowledge domains
- Reranking for better results
- Source citation in responses
- Document upload interface

### 4. Monitoring & Analytics
- Usage metrics dashboard
- Token consumption tracking
- Error rate monitoring
- User feedback collection

### 5. Performance
- Response caching for common queries
- LLM response streaming to UI
- Load balancing for multiple users
- Rate limiting

### 6. Security
- API key authentication
- Rate limiting
- Input sanitization
- Audit logging

---

## Key Technologies Used

- **LangChain**: Agent orchestration framework
- **LangGraph**: State graph and checkpointing
- **FastAPI**: Modern async API framework
- **Streamlit**: Rapid UI development
- **Qdrant**: Vector database for RAG
- **Jina Embeddings**: Embedding model API
- **Docker & Docker Compose**: Containerization
- **SQLite**: Persistent memory storage (via SqliteSaver)
- **Gmail SMTP**: Email sending

---

## Troubleshooting

### Issue: Agent not remembering conversations
**Solution**: Check `thread_id` is consistent across requests

### Issue: Email not sending
**Solution**: 
1. Verify Gmail App Password (not regular password)
2. Check 2FA is enabled
3. Verify environment variables loaded

### Issue: Qdrant search failing
**Solution**:
1. Verify Qdrant URL and API key
2. Check collection exists and has data
3. Verify Jina embeddings API key

### Issue: Container can't connect to API
**Solution**: Use container name `assistant-api`, not `localhost`

---

**Built with intelligence, deployed with confidence. 🚀**
