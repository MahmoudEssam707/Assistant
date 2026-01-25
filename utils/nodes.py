"""Node definitions for multi-agent system with supervisor."""

from langchain.agents import create_agent
from langgraph_supervisor import create_supervisor
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from .tools import (
    calculator_tool, gmail_send_tool, search_in_knowledge
)
from utils.util import llm

# Initialize persistent memory checkpointer
# Memory will persist even after server restarts
conn = sqlite3.connect("checkpoints.db", check_same_thread=False)
memory = SqliteSaver(conn)

# =========================
# Worker Agents
# =========================

# Research agent - handles knowledge searches and factual queries
research_agent = create_agent(
    llm,
    tools=[search_in_knowledge], 
    system_prompt=(
        "You are a research agent specialized in finding information.\n\n"
        "INSTRUCTIONS:\n"
        "- Assist ONLY with research-related tasks, including looking up factual information, "
        "programming concepts, and technical knowledge.\n"
        "- Use the search_in_knowledge tool to find relevant information.\n"
        "- After you're done with your tasks, respond to the supervisor directly with your findings.\n"
        "- Respond ONLY with the results of your work, do NOT include ANY other text.\n"
        "- Do NOT perform calculations or send emails - those are handled by other agents."
    ),
    name="researcher"
)

# Email handler agent - handles email sending
email_handler_agent = create_agent(
    llm,
    tools=[gmail_send_tool],
    system_prompt=(
        "You are an email handler agent specialized in sending emails.\n\n"
        "INSTRUCTIONS:\n"
        "- Assist ONLY with email-related tasks.\n"
        "- Use the gmail_send_tool to send emails with proper formatting.\n"
        "- Make emails professional and concise.\n"
        "- After you're done with your tasks, respond to the supervisor directly.\n"
        "- Respond ONLY with the results of your work, do NOT include ANY other text.\n"
        "- Do NOT perform calculations or search for information - those are handled by other agents."
    ),
    name="email_handler"
)

# Calculator agent - handles mathematical calculations
calculator_agent = create_agent(
    llm,
    tools=[calculator_tool],
    system_prompt=(
        "You are a calculator agent specialized in mathematical computations.\n\n"
        "INSTRUCTIONS:\n"
        "- Assist ONLY with mathematical calculations and problem-solving.\n"
        "- Use the calculator_tool to evaluate mathematical expressions.\n"
        "- After you're done with your tasks, respond to the supervisor directly.\n"
        "- Respond ONLY with the results of your work, do NOT include ANY other text.\n"
        "- Do NOT send emails or search for information - those are handled by other agents."
    ),
    name="calculator"
)

# =========================
# Supervisor Agent
# =========================

# Create supervisor multi-agent that delegates tasks to worker agents
agent_executor = create_supervisor(
    model=llm,
    agents=[research_agent, email_handler_agent, calculator_agent],
    prompt=(
        "You are a supervisor managing three specialized agents:\n"
        "- researcher: Assign knowledge search and factual/technical queries to this agent.\n"
        "- email_handler: Assign email sending tasks to this agent.\n"
        "- calculator: Assign mathematical calculations and computations to this agent.\n\n"
        "INSTRUCTIONS:\n"
        "- Analyze user requests and delegate to the appropriate agent.\n"
        "- Assign work to one agent at a time, do not call agents in parallel.\n"
        "- Do not do any work yourself - always delegate to the appropriate specialist.\n"
        "- If the user's request is unclear, ask for clarification.\n"
        "- Be helpful, concise, and professional in your responses."
    ),
    add_handoff_back_messages=True,
    output_mode="full_history",
).compile(checkpointer=memory)