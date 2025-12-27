"""Graph building and compilation for LangGraph Agent.

Uses LangGraph's built-in supervisor for multi-agent delegation.
"""
from utils.nodes import agent_executor

# Use the compiled supervisor graph
graph = agent_executor

