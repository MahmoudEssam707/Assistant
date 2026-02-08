"""Node definitions for multi-agent system with supervisor."""

from langchain.agents import create_agent
from tools import generate_fake_person

from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
# Initialize LLM and tools
load_dotenv()

llm = ChatOpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL"),
    model=os.getenv("LLM_MODEL_NAME"),
)

tools = [generate_fake_person]

# Create the agent graph that can handle direct message input
system_prompt = """
You are a helpful assistant that generates fake personal information.

When the user requests fake person data:
1. Use the generate_fake_person tool
2. Return ONLY the tool's output - nothing else
3. Do NOT include any reasoning, thinking, or explanations
4. Do NOT describe what you're doing or why

Output format: Simply return the name, age, and address provided by the tool - and you can say "Here is the fake person data you requested:" before the output.
"""
# Create the agent using create_agent with memory checkpoint
agent_executor = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt,
)

# Example invocation
def run_agent(input_text: str) -> str:
    """Run the agent with the given input text."""
    result = agent_executor.invoke({"input": input_text})
    
    # Get the final AI response
    messages = result.get("messages", [])
    for message in reversed(messages):
        if message.__class__.__name__ == 'AIMessage' and message.content:
            return message.content
    
    return "No response generated"

if __name__ == "__main__":
    # Example usage
    user_input = input("Enter your request: ")
    output = run_agent(user_input)
    print("\n" + output)