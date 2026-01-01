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
        logger.info(f"Received query: {request.message[:100]}...")
        logger.info(f"Thread ID: {request.thread_id}")
        
        # Create the input for the agent following the pattern you showed
        inputs = {"messages": [{"role": "user", "content": request.message}]}
        logger.info(f"Created inputs: {inputs}")
        
        # Stream the agent response and collect results
        stream_results = []
        logger.info("Starting graph stream...")
        logger.info(f"Using memory checkpoint: {request.thread_id}")
        
        # Configure with thread_id for memory persistence
        config = {"configurable": {"thread_id": request.thread_id}}
        
        try:
            for i, chunk in enumerate(graph.stream(inputs, config=config, stream_mode="updates")):
                logger.info(f"Chunk {i}: {chunk}")
                stream_results.append(chunk)
        except Exception as stream_error:
            logger.error(f"Error during graph streaming: {stream_error}")
            logger.error(f"Stream error type: {type(stream_error)}")
            raise
        
        logger.info(f"Total stream results: {len(stream_results)}")
        
        # Extract tool outputs and final AI message
        response_parts = []
        final_ai_message = ""
        
        # Process all chunks to collect tool outputs and final message
        for i, chunk in enumerate(stream_results):
            logger.info(f"Processing chunk {i}: {type(chunk)} - {chunk}")
            
            # Check for tool outputs
            if isinstance(chunk, dict) and 'tools' in chunk:
                messages = chunk['tools'].get('messages', [])
                for message in messages:
                    if hasattr(message, 'content') and message.content:
                        # Add tool output to response parts
                        response_parts.append(message.content)
                        logger.info(f"Found tool output: {message.content[:100]}...")
            
            # Check for AI messages
            if isinstance(chunk, dict) and 'model' in chunk:
                messages = chunk['model'].get('messages', [])
                for message in messages:
                    if hasattr(message, 'content') and message.content:
                        final_ai_message = message.content
                        logger.info(f"Found AI message: {final_ai_message[:100]}...")
        
        # Combine tool outputs with final AI message
        if response_parts:
            # Show tool outputs first, then AI message
            final_response = "\n\n".join(response_parts)
            if final_ai_message:
                final_response += f"\n\n{final_ai_message}"
        else:
            final_response = final_ai_message if final_ai_message else "No response generated"
        
        logger.info(f"Returning response: {final_response[:100]}...")
        return QueryResponse(response=final_response, thread_id=request.thread_id)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Agent"}
