"""Node definitions for the agent."""

from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from .tools import calculator_tool, uppercase_tool, send_mail_tool

# Initialize LLM and tools
llm = ChatOllama(base_url="http://ollama:11434", model="llama3.1:8b")
tools = [calculator_tool, uppercase_tool, send_mail_tool]
# Create the agent graph that can handle direct message input
system_prompt = """You are a helpful assistant that can:
1. Perform mathematical calculations using the calculator_tool
2. Convert text to uppercase using the uppercase_tool
3. Send emails using the send_mail_tool

Use the appropriate tools when needed to help users with their requests."""

# Create the agent using create_agent - it takes user message input directly
agent_executor = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt,
)
