from typing import TypedDict, Literal
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
import os

# Load environment variables
load_dotenv()

# Initialize LLM for supervisor
llm = ChatOpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASEURL"),
    model=os.getenv("LLM_NAME"),
)

# Define the state structure
class AgentState(TypedDict):
    user_input: str
    next_agent: str
    result: str

# Supervisor node - decides which agent to delegate to
def supervisor_node(state: AgentState) -> AgentState:
    """Supervisor that analyzes the request and routes to appropriate agent."""
    
    user_input = state["user_input"]
    
    # Ask LLM to determine which agent should handle this
    prompt = f"""You are a supervisor that routes requests to specialized agents.
    
Available agents:
- uppercase_agent: Converts text to UPPERCASE
- lowercase_agent: Converts text to lowercase

User request: {user_input}

Based on the user's request, determine which agent should handle it.
Respond with ONLY the agent name: either 'uppercase_agent' or 'lowercase_agent'.
If the request is about making text uppercase, capital letters, or all caps, choose 'uppercase_agent'.
If the request is about making text lowercase, small letters, or all lowercase, choose 'lowercase_agent'.
"""
    
    response = llm.invoke(prompt)
    next_agent = response.content.strip()
    
    # Validate the response
    if next_agent not in ["uppercase_agent", "lowercase_agent"]:
        # Default to uppercase if unclear
        next_agent = "uppercase_agent"
    
    print(f"Supervisor routing to: {next_agent}")
    
    return {
        "user_input": user_input,
        "next_agent": next_agent,
        "result": state.get("result", "")
    }

# Uppercase agent
def uppercase_agent_node(state: AgentState) -> AgentState:
    """Agent that converts text to uppercase."""
    
    user_input = state["user_input"]
    
    # Extract text to convert
    prompt = f"""Extract the text that needs to be converted to uppercase from this request: {user_input}
    
Respond with ONLY the extracted text, nothing else. If the entire message should be converted, return it."""
    
    response = llm.invoke(prompt)
    text_to_convert = response.content.strip()
    
    # Convert to uppercase
    result = text_to_convert.upper()
    
    print(f"Uppercase agent converted: '{text_to_convert}' -> '{result}'")
    
    return {
        "user_input": user_input,
        "next_agent": "end",
        "result": result
    }

# Lowercase agent
def lowercase_agent_node(state: AgentState) -> AgentState:
    """Agent that converts text to lowercase."""
    
    user_input = state["user_input"]
    
    # Extract text to convert
    prompt = f"""Extract the text that needs to be converted to lowercase from this request: {user_input}
    
Respond with ONLY the extracted text, nothing else. If the entire message should be converted, return it."""
    
    response = llm.invoke(prompt)
    text_to_convert = response.content.strip()
    
    # Convert to lowercase
    result = text_to_convert.lower()
    
    print(f"Lowercase agent converted: '{text_to_convert}' -> '{result}'")
    
    return {
        "user_input": user_input,
        "next_agent": "end",
        "result": result
    }

# Router function to decide next step
def route_to_agent(state: AgentState) -> Literal["uppercase_agent", "lowercase_agent"]:
    """Routes to the appropriate agent based on supervisor's decision."""
    return state["next_agent"]

# Create the workflow graph
workflow = StateGraph(AgentState)

# Add nodes to the workflow
workflow.add_node("supervisor", supervisor_node)
workflow.add_node("uppercase_agent", uppercase_agent_node)
workflow.add_node("lowercase_agent", lowercase_agent_node)

# Define the workflow flow
workflow.add_edge(START, "supervisor")

# Add conditional routing from supervisor to agents
workflow.add_conditional_edges(
    "supervisor",
    route_to_agent,
    {
        "uppercase_agent": "uppercase_agent",
        "lowercase_agent": "lowercase_agent"
    }
)

# Both agents end the workflow
workflow.add_edge("uppercase_agent", END)
workflow.add_edge("lowercase_agent", END)

# Compile the workflow
app = workflow.compile()

# Run the workflow
if __name__ == "__main__":
    # Test with uppercase request
    print("\n=== Test 1: Uppercase Request ===")
    result = app.invoke({"user_input": "Please convert 'Hello World' to uppercase", "next_agent": "", "result": ""})
    print(f"Final result: {result['result']}")
    
    print("\n=== Test 2: Lowercase Request ===")
    result = app.invoke({"user_input": "Make 'HELLO WORLD' lowercase please", "next_agent": "", "result": ""})
    print(f"Final result: {result['result']}")