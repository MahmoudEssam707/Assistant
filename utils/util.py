"""Shared utilities, classes and configurations for the agent."""

from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
import logging

# Configure logger
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler("state_logs.log")
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)

# Define the state structure with message history
class State(TypedDict):
    messages: Annotated[list, add_messages]