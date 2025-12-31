"""Node definitions for multi-agent system with supervisor."""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from .tools import (
    calculator_tool, gmail_send_tool
)
load_dotenv()
# Initialize LLM and tools

llm = ChatOpenAI(
    api_key=os.getenv("API"),
    base_url=os.getenv("BASE_URL"),
    model=os.getenv("MODEL_NAME"),
)
tools = [calculator_tool, gmail_send_tool]

# Initialize persistent memory checkpointer
# Memory will persist even after server restarts
conn = sqlite3.connect("checkpoints.db", check_same_thread=False)
memory = SqliteSaver(conn)

# Create the agent graph that can handle direct message input
system_prompt = """
You are My Assistant, a helpful and reliable AI assistant.

- Chat naturally and answer questions directly.
- If the user wants to calculate something, they can simply type the math expression or say 'calculate ...'.
- If the user wants to send an email, they can say 'send an email to [recipient] with subject [subject] and message [message]'.
- Be concise, accurate, and helpful.
- If information is missing, ask short clarifying questions.
- Do not reveal internal reasoning.
- Never show exception or error details to the user—respond gracefully instead.
- Only use [calculator_tool] for math and [gmail_send_tool] for sending emails.

Examples:
- To calculate: 'What is 5 * 7?' or 'calculate 5 * 7'
- To send email: 'Send an email to alice@example.com with subject "Hello" and message "How are you?"'
"""

# Create the agent using create_agent with memory checkpoint
agent_executor = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt,
    checkpointer=memory,
)