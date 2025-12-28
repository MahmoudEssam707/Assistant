"""Tool definitions using @tool decorator for the agent."""

from .util import logger
from langchain_core.tools import tool
from langchain_google_community.gmail.send_message import GmailSendMessage
from langchain_google_community.gmail.utils import (
    build_gmail_service,
    get_google_credentials,
)
from googleapiclient.discovery import build

try:
    credentials = get_google_credentials(
        token_file="token.json",
        scopes=[
            "https://mail.google.com/",  # Gmail scope
            "https://www.googleapis.com/auth/spreadsheets"  # Sheets scope
        ],
        client_secrets_file="credentials.json",
    )
    api_resource = build_gmail_service(credentials=credentials)
    send_mail_tool = GmailSendMessage.from_api_resource(api_resource=api_resource)
    sheets_service = build('sheets', 'v4', credentials=credentials)
except:
    api_resource = None
    send_mail_tool = None
    sheets_service = None

@tool
def calculator_tool(expression: str) -> str:
    """
    Evaluate a mathematical expression.
    
    Args:
        expression: The mathematical expression to evaluate (e.g., "4*4", "10+5")
        
    Returns:
        The result of the calculation as a string
    """
    logger.info(f"Calculator tool executing: {expression}")
    try:
        result = eval(expression)
        logger.info(f"Calculator result: {result}")
        return str(result)
    except Exception as e:
        logger.error(f"Calculator error: {e}")
        return "Invalid mathematical expression"