# Examples - LangGraph Learning Materials

This folder contains educational examples demonstrating various LangGraph concepts and patterns. These files are **not used in production** and serve purely as learning resources.

---

## 📚 Example Files

### `simple_workflow.py`
**Concept**: Basic LangGraph workflow  
**What it demonstrates**: 
- Creating a simple state graph
- Adding nodes and edges
- Basic uppercase transformation workflow

### `agent.py`
**Concept**: Simple agent with tools  
**What it demonstrates**:
- Creating an agent with a custom tool
- Using the Faker library to generate fake person data
- Tool integration with LangGraph

### `agent_workflow.py`
**Concept**: Agent workflow with state management  
**What it demonstrates**:
- Building an agent workflow
- State management in LangGraph
- Using the fake person generator tool

### `agentic_workflow.py`
**Concept**: Supervisor pattern (multi-agent)  
**What it demonstrates**:
- Supervisor agent that delegates tasks
- Multiple specialized agents (uppercase, lowercase)
- Agent coordination and task delegation
- This is a simplified version of the production supervisor pattern

### `memory.py`
**Concept**: Chat agent with persistent memory  
**What it demonstrates**:
- SQLite-based memory checkpointing
- Conversation history management
- Stateful chat interactions
- Thread-based conversation tracking

### `tools.py`
**Concept**: Custom tool definitions  
**What it demonstrates**:
- Using the `@tool` decorator
- Creating tools with the Faker library
- Tool function signature and documentation
- **Note**: This is different from production `utils/tools.py`

---

## 🏃 Running Examples

All examples can be run directly with Python:

```bash
# Make sure you're in the project root with .env configured
python examples/simple_workflow.py
python examples/agent.py
python examples/agent_workflow.py
python examples/agentic_workflow.py
python examples/memory.py
```

**Prerequisites**:
- Python environment with dependencies installed
- `.env` file configured with LLM credentials (LLM_API_KEY, LLM_BASE_URL, LLM_MODEL_NAME)

---

## 🔍 Key Differences from Production Code

| Aspect | Examples | Production (`utils/`) |
|--------|----------|----------------------|
| **Purpose** | Learning & demonstration | Production functionality |
| **Tools** | Faker (fake person generator) | Real tools (Qdrant search, calculator, email) |
| **Complexity** | Simplified patterns | Full supervisor with 3 specialized agents |
| **Dependencies** | Uses faker library | Uses Qdrant, SMTP, safe calculator |
| **Memory** | Some examples show basics | Production uses persistent SQLite checkpointing |

---

## 📖 Learning Path

Recommended order for understanding LangGraph concepts:

1. **Start**: `simple_workflow.py` - Understand basic graph structure
2. **Next**: `tools.py` - See how to define tools
3. **Then**: `agent.py` - Simple agent using a tool
4. **After**: `agent_workflow.py` - Agent workflow patterns
5. **Advanced**: `agentic_workflow.py` - Supervisor pattern (relates to production)
6. **Finally**: `memory.py` - Persistent state management

---

## 🎓 Related Production Code

To see how these concepts are used in production:

- **Supervisor Pattern**: See `utils/nodes.py` for the production supervisor implementation
- **Tools**: See `utils/tools.py` for real production tools (search, calculator, email)
- **Memory**: Production uses SQLite checkpoint in `utils/nodes.py`
- **API Integration**: See `server.py` for FastAPI wrapper around the agent

---

## 📝 Notes

- Examples use the **same LLM configuration** as production (from `.env`)
- The `faker` library used in examples is **not installed in production** (removed from requirements.txt)
- To run these examples, you may need to install faker: `pip install faker`
- These files demonstrate patterns but are intentionally simplified for clarity