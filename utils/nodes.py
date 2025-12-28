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
- Use tools only when the user clearly requests an action (e.g., calculation or sending email).
- Be concise, accurate, and helpful.
- Never guess missing information; ask short clarifying questions if needed.
- Do not reveal internal reasoning.
- Never show exception or error details to the user—respond gracefully instead.
- Only use [calculator_tool] for math and [send_mail_tool] for sending emails.
"""

# Create the agent using create_agent with memory checkpoint
agent_executor = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt,
    checkpointer=memory,
)