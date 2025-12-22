"""Graph building and compilation for LangGraph Agent.

This module focuses on building and compiling the graph structure.
Node definitions and LLM initialization are in nodes.py.
"""
from utils.nodes import agent_executor
# The agent_executor is already a compiled graph, so we can use it directly
graph = agent_executor

