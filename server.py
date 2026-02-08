"""FastAPI server for the LangChain agent."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from utils.nodes import agent_executor as graph
from utils.util import logger

app = FastAPI(title="Agent API", version="2.0.0")

class QueryRequest(BaseModel):
    message: str
    thread_id: str = "Default"

class QueryResponse(BaseModel):
    response: str
    thread_id: str


def log_chunk(chunk):
    """Log stream chunk with messages."""
    if not isinstance(chunk, dict):
        return
    
    for node_name, node_data in chunk.items():
        logger.info(f"\n🔄 {node_name.upper()}")
        
        for msg in node_data.get('messages', []):
            msg_type = msg.__class__.__name__
            
            if msg_type == 'HumanMessage':
                logger.info(f"  👤 {msg.content[:200]}")
            elif msg_type == 'AIMessage':
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    logger.info(f"  🤖 Tools: {', '.join(tc['name'] for tc in msg.tool_calls)}")
                elif msg.content:
                    logger.info("  🤖 {}".format(msg.content.replace("\n", " ")[:200]))
            elif msg_type == 'ToolMessage':
                logger.info(f"  🔧 {getattr(msg, 'name', 'unknown')}: {msg.content[:100]}")
        
        logger.info("-" * 80)


def extract_final_response(stream_results):
    """Extract final AI response from stream."""
    for chunk in reversed(stream_results):
        if not isinstance(chunk, dict):
            continue
        
        for node_name, node_data in chunk.items():
            messages = node_data.get('messages', []) if isinstance(node_data, dict) else []
            
            for msg in reversed(messages):
                if (hasattr(msg, 'content') and msg.content and 
                    'AIMessage' in msg.__class__.__name__ and 
                    'Transferring back to supervisor' not in msg.content):
                    logger.info(f"📤 Final: {msg.content[:150]}...")
                    return msg.content
    
    return "No response generated"


def process_query(message, thread_id):
    """Process agent query and return response."""
    inputs = {"messages": [{"role": "user", "content": message}]}
    config = {"configurable": {"thread_id": thread_id}}
    
    logger.info("=" * 80)
    logger.info(f"📨 Thread: {thread_id} | Query: {message}")
    logger.info("🚀 Executing...")
    logger.info("-" * 80)
    
    stream_results = []
    for chunk in graph.stream(inputs, config=config, stream_mode="updates"):
        stream_results.append(chunk)
        log_chunk(chunk)
    
    logger.info(f"\n✅ Complete. Chunks: {len(stream_results)}")
    logger.info("=" * 80 + "\n")
    
    return extract_final_response(stream_results)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Agent API is running!"}


@app.post("/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest) -> QueryResponse:
    """Query the agent with a message."""
    try:
        response = process_query(request.message, request.thread_id)
        return QueryResponse(response=response, thread_id=request.thread_id)
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Agent"}

