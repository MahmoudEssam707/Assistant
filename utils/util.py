"""Shared utilities, classes and configurations for the agent."""

from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
import logging
from langchain_google_community.gmail.utils import (
    get_google_credentials, build_gmail_service
)
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



def get_gmail_service():
    """
    Load/create OAuth credentials and return a Gmail API service.
    """
    credentials = get_google_credentials(
        token_file="token.json",
        scopes=["https://mail.google.com/"],
        client_secrets_file="credentials.json",
    )
    return build_gmail_service(credentials=credentials)

def gmail_init_oauth():
    """
    Run once manually to generate token.json.
    """
    try:
        get_gmail_service()
        logger.info("Gmail OAuth completed. token.json created.")
    except Exception as e:
        logger.exception("Gmail OAuth failed")
        raise RuntimeError(f"Gmail OAuth initialization failed: {e}") from e
