"""
Shared utilities, classes, and configurations for the agent.
"""

# =========================
# Imports
# =========================
import logging
from langchain_openai import ChatOpenAI
from typing_extensions import TypedDict
from typing import Annotated
from langchain_community.embeddings import JinaEmbeddings
import os
from dotenv import load_dotenv

# LangChain & LLMs
from langgraph.graph.message import add_messages

# Gmail API
from langchain_google_community.gmail.utils import (
    get_google_credentials, build_gmail_service
)

# =========================
# Environment Setup
# =========================
load_dotenv()

# =========================
# Logging Configuration
# =========================
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler("state_logs.log")
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)

# =========================
# State Structure
# =========================
class State(TypedDict):
    """State structure with message history."""
    messages: Annotated[list, add_messages]

# =========================
# Gmail API Integration Utilities
# =========================
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
    

# =========================
# LLM and Embeddings Initialization
# =========================
llm = ChatOpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL"),
    model=os.getenv("LLM_MODEL_NAME"),
)

embeddings = JinaEmbeddings(
    jina_api_key=os.getenv("JINA_EMBEDDING_API_KEY"),
    model_name=os.getenv("JINA_EMBEDDING_MODEL"),
)   