"""Tool definitions using @tool decorator for the agent."""

from .util import logger
from langchain_core.tools import tool
from langchain_google_community.gmail.send_message import GmailSendMessage
from langchain_google_community.gmail.utils import (
    build_gmail_service,
    get_google_credentials,
)

@tool
def gmail_send_tool(to: str, subject: str, body: str) -> str:
    """
    Send an email using Gmail.

    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body text

    Returns:
        Success or failure message
    """
    logger.info(f"Sending Gmail to={to}, subject={subject}")

    try:
        credentials = get_google_credentials(
            token_file="token.json",
            scopes=["https://mail.google.com/"],
            client_secrets_file="credentials.json",
        )

        api_resource = build_gmail_service(credentials=credentials)
        send_mail_tool = GmailSendMessage.from_api_resource(
            api_resource=api_resource
        )

        send_mail_tool.run(
            {
                "to": to,
                "subject": subject,
                "body": body,
            }
        )

        logger.info("Gmail sent successfully")
        return "Email sent successfully."

    except Exception as e:
        logger.error(f"Gmail send error: {e}")
        return f"Failed to send email: {e}"


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