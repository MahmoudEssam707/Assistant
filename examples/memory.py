"""Simple graph-based chat agent with memory."""

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize the LLM
llm = ChatOpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL"),
    model=os.getenv("LLM_MODEL_NAME"),
)

# System message
system_message = "You are a friend, chat with the user naturally"

# Create agent with memory
memory = MemorySaver()
agent_graph = create_agent(
    llm, 
    system_prompt=system_message,
    checkpointer=memory
)

# Run function
def run_agent(input_text: str, thread_id: str = "default") -> str:
    config = {"configurable": {"thread_id": thread_id}}
    messages = [HumanMessage(content=input_text)]
    
    result = agent_graph.invoke({"messages": messages}, config)
    
    # Get last AI message
    for msg in reversed(result["messages"]):
        if hasattr(msg, 'content') and msg.__class__.__name__ == 'AIMessage':
            return msg.content
    
    return "No response"

if __name__ == "__main__":
    # Example usage with persistent conversation
    #     
    print("Chat with the agent (type 'quit' to exit):")
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ['quit', 'exit', 'q']:
            break
        
        output = run_agent(user_input)
        print("Agent:", output)