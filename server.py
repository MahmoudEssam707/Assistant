"""FastAPI server for the LangChain agent."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent.graph import graph
from utils.util import logger

app = FastAPI(title="Agent API", version="1.0.0")

class QueryRequest(BaseModel):
    message: str
    thread_id: str = "default"

class QueryResponse(BaseModel):
    response: str
    thread_id: str

@app.get("/")
async def root():
    """Health check endpoint."""
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
        
        try:
            for i, chunk in enumerate(graph.stream(inputs, stream_mode="updates")):
                logger.info(f"Chunk {i}: {chunk}")
                stream_results.append(chunk)
        except Exception as stream_error:
            logger.error(f"Error during graph streaming: {stream_error}")
            logger.error(f"Stream error type: {type(stream_error)}")
            raise
        
        logger.info(f"Total stream results: {len(stream_results)}")
        
        # Extract the last AI message from the stream results
        final_response = "No response generated"
        
        # Look through stream results from the end to find the last AI message
        for i, chunk in enumerate(reversed(stream_results)):
            logger.info(f"Processing chunk {i}: {type(chunk)} - {chunk}")
            if isinstance(chunk, dict) and 'model' in chunk:
                messages = chunk['model'].get('messages', [])
                for message in messages:
                    if hasattr(message, 'content') and message.content:
                        final_response = message.content
                        logger.info(f"Found final response: {final_response[:100]}...")
                        break
                if final_response != "No response generated":
                    break
        
        logger.info(f"Returning response: {final_response[:100]}...")
        return QueryResponse(response=final_response, thread_id=request.thread_id)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Agent"}
