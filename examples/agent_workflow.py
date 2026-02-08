from typing import TypedDict
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
import os

# Load environment variables
load_dotenv()

# Initialize LLM
llm = ChatOpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL"),
    model=os.getenv("LLM_MODEL_NAME"),
)

# Define the state structure
class AgentState(TypedDict):
    message: str

# Define workflow nodes
def llm_call_node(state: AgentState) -> AgentState:
    """Node that calls the LLM with the input message."""
    
    output = llm.invoke(input=state["message"])
    
    return {
        "message": output,
    }


# Create the workflow graph
workflow = StateGraph(AgentState)

# Add nodes to the workflow
workflow.add_node("llm_call", llm_call_node)

# Define the workflow flow
workflow.add_edge(START, "llm_call")
workflow.add_edge("llm_call", END)

# Compile the workflow
app = workflow.compile()

# Run the workflow
if __name__ == "__main__":
    result = app.invoke({"message": "Hello, how are you today?"})
    print(f"Final result: {result['message'].content}")