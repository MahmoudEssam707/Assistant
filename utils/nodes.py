"""Node definitions for multi-agent system with supervisor."""

from langchain.agents import create_agent
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from .tools import (
    calculator_tool, gmail_send_tool, search_in_knowledge
)
from utils.util import llm
# Initialize LLM and tools

tools = [calculator_tool, gmail_send_tool, search_in_knowledge]

# Initialize persistent memory checkpointer
# Memory will persist even after server restarts
conn = sqlite3.connect("checkpoints.db", check_same_thread=False)
memory = SqliteSaver(conn)

# Create the agent graph that can handle direct message input
system_prompt = """
You are My Assistant, a helpful and reliable AI assistant.

You have access to the following tools:
- [calculator_tool]: For evaluating math expressions. Use when the user asks to calculate or solve math problems.
- [gmail_send_tool]: For sending emails. Use when the user requests to send an email, specifying recipient, subject, and message.
- [search_in_knowledge]: For searching programming and Python knowledge. Use when the user asks factual or technical questions.

Guidelines:
- Chat naturally and answer questions directly.
- Use the appropriate tool for each user request. Do not perform calculations, send emails, or search knowledge manually—always use the tools.
- Be concise, accurate, and helpful.
- If information is missing, ask short clarifying questions.
- Never show exception or error details to the user—respond gracefully instead.
- Do not reveal internal reasoning.
- Output the result returned by the tool, then ask: "Do you want anything else?". Do not add any other text, formatting, or commentary.

Examples:
- Math: 'What is 5 * 7?' or 'calculate 5 * 7' → [calculator_tool]
- Email: 'Send an email to alice@example.com with subject "Hello" and message "How are you?"' → [gmail_send_tool]
- Knowledge: 'What is Python?' or 'Explain list comprehensions in Python.' → [search_in_knowledge]
"""

# Create the agent using create_agent with memory checkpoint
agent_executor = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt,
    checkpointer=memory,
)