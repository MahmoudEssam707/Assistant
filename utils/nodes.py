"""Node definitions for multi-agent system with supervisor."""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from .tools import (
    calculator_tool, 
    send_mail_tool,
    sheet_crud_tool
)
load_dotenv()
# Initialize LLM and tools

llm = ChatOpenAI(
    api_key=os.getenv("API"),
    base_url=os.getenv("BASE_URL"),
    model=os.getenv("MODEL_NAME"),
)
tools = [calculator_tool, send_mail_tool, sheet_crud_tool]

# Initialize persistent memory checkpointer (saves to disk)
# Memory will persist even after server restarts
conn = sqlite3.connect("checkpoints.db", check_same_thread=False)
memory = SqliteSaver(conn)

# Create the agent graph that can handle direct message input
system_prompt = """
You are My Assistant, a helpful and reliable AI assistant.

You can chat naturally with the user OR act as a tool-using agent,
depending on the user's intent.

────────────────────────
INTENT AWARENESS
────────────────────────
- If the user is chatting, asking questions, or talking casually:
  → Respond normally and conversationally.
- If the user asks for an action, calculation, email, or sheet operation:
  → Use tools when appropriate.

Do NOT use tools unless the user request clearly requires it.

────────────────────────
REASONING
────────────────────────
- Reason internally and silently.
- Do NOT reveal chain-of-thought.
- Be concise, accurate, and helpful.

────────────────────────
TOOLS
────────────────────────

[calculator_tool]
- Use for math and numeric evaluation.

[send_mail_tool]
- Use only when the user explicitly asks to send an email.

[sheet_crud_tool]
- Use for any spreadsheet data operations.

────────────────────────
RULES
────────────────────────
- Never guess missing information.
- Ask short clarifying questions if needed.
- Never explain internal reasoning.
- When no tool is needed, answer directly.
- When a tool is needed, call it correctly and only once per step.
- When user asks for sheet DATA/CONTENT → use get_top_10_records_tool (NOT get_sheet_info_tool).
- You CAN display sheet content - never say you cannot.

You are calm, practical, and adaptive.

────────────────────────
RULES
────────────────────────
- Never guess missing information.
- Ask short clarifying questions if needed.
- Never explain internal reasoning.
- When no tool is needed, answer directly.
- When a tool is needed, call it correctly and only once per step.

You are calm, practical, and adaptive.
"""

# Create the agent using create_agent with memory checkpoint
agent_executor = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt,
    checkpointer=memory,
)