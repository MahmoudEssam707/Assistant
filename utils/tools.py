"""Tool definitions using @tool decorator for the agent."""

from venv import logger
from langchain_core.tools import tool
from langchain_google_community.gmail.send_message import GmailSendMessage
from langchain_google_community.gmail.utils import (
    build_gmail_service,
    get_google_credentials,
)

try:
    credentials = get_google_credentials(
        token_file="token.json",
        scopes=["https://mail.google.com/"],
        client_secrets_file="credentials.json",
    )
    api_resource = build_gmail_service(credentials=credentials)
    send_mail_tool = GmailSendMessage.from_api_resource(api_resource=api_resource)
except:
    api_resource = None
    send_mail_tool = None

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


@tool
def uppercase_tool(text: str) -> str:
    """
    Convert text to uppercase.
    
    Args:
        text: The text to convert to uppercase
        
    Returns:
        The text converted to uppercase
    """
    logger.info(f"Uppercase tool executing: {text}")
    result = text.upper()
    logger.info(f"Uppercase result: {result}")
    return result