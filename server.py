"""FastAPI server for the LangChain agent."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent.graph import graph
from utils.util import logger

app = FastAPI(title="Agent API", version="1.0.0")

class QueryRequest(BaseModel):
    message: str
    thread_id: str = "Default"  # Identifier for memory checkpointing

class QueryResponse(BaseModel):
    response: str
    thread_id: str

@app.get("/")
async def root():
    """Health check endpoint."""
    # setup google credentials on startup if needed
    return {"message": "Agent API is running!"}

@app.post("/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest) -> QueryResponse:
    """Query the agent with a message."""
    try:
        logger.info("=" * 80)
        logger.info(f"📨 NEW REQUEST | Thread: {request.thread_id}")
        logger.info(f"💬 User Query: {request.message}")
        logger.info("=" * 80)
        
        # Create the input for the agent following the pattern you showed
        inputs = {"messages": [{"role": "user", "content": request.message}]}
        
        # Stream the agent response and collect results
        stream_results = []
        
        # Configure with thread_id for memory persistence
        config = {"configurable": {"thread_id": request.thread_id}}
        
        logger.info("🚀 Starting agent execution...")
        logger.info("-" * 80)
        
        try:
            for i, chunk in enumerate(graph.stream(inputs, config=config, stream_mode="updates")):
                stream_results.append(chunk)
                
                # Log each chunk in a readable format
                if isinstance(chunk, dict):
                    for node_name, node_data in chunk.items():
                        logger.info(f"\n🔄 AGENT NODE: {node_name.upper()}")
                        
                        if isinstance(node_data, dict) and 'messages' in node_data:
                            messages = node_data['messages']
                            
                            # Log each message in the chunk
                            for msg in messages:
                                msg_type = msg.__class__.__name__
                                
                                if msg_type == 'HumanMessage':
                                    logger.info(f"  👤 Human: {msg.content[:200]}")
                                    
                                elif msg_type == 'AIMessage':
                                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                                        tool_names = [tc['name'] for tc in msg.tool_calls]
                                        logger.info(f"  🤖 AI calling tools: {', '.join(tool_names)}")
                                    elif msg.content:
                                        content_preview = msg.content.replace('\n', ' ')[:200]
                                        logger.info(f"  🤖 AI response: {content_preview}")
                                        
                                elif msg_type == 'ToolMessage':
                                    tool_name = msg.name if hasattr(msg, 'name') else 'unknown'
                                    content_preview = msg.content[:100]
                                    logger.info(f"  🔧 Tool '{tool_name}': {content_preview}")
                        
                        logger.info("-" * 80)
                        
        except Exception as stream_error:
            logger.error(f"❌ Error during graph streaming: {stream_error}")
            logger.error(f"Error type: {type(stream_error)}")
            raise
        
        logger.info(f"\n✅ Execution complete. Total chunks: {len(stream_results)}")
        logger.info("=" * 80)
        
        # Extract the final response from the last supervisor message
        final_response = "No response generated"
        
        # Process chunks to find the final AI response
        for i, chunk in enumerate(stream_results):
            if isinstance(chunk, dict):
                # Check for any agent node (supervisor, calculator, researcher, email_handler)
                for node_name, node_data in chunk.items():
                    if isinstance(node_data, dict) and 'messages' in node_data:
                        messages = node_data['messages']
                        # Find the last AI message with content
                        for message in reversed(messages):
                            if hasattr(message, 'content') and message.content:
                                # Skip tool/system messages, get actual AI responses
                                if hasattr(message, '__class__') and 'AIMessage' in message.__class__.__name__:
                                    # Skip handoff messages
                                    if 'Transferring back to supervisor' not in message.content:
                                        final_response = message.content
                                        logger.info(f"📤 Final Response from {node_name}: {final_response[:150]}...")
                                        break
        
        logger.info("=" * 80 + "\n")
        return QueryResponse(response=final_response, thread_id=request.thread_id)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Agent"}
