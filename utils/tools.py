"""Tool definitions using @tool decorator for the agent."""

from .util import logger, get_gmail_service
from langchain_core.tools import tool
from langchain_google_community.gmail.send_message import GmailSendMessage


@tool
def gmail_send_tool(to: str, subject: str, body: str) -> str:
    """
    Send an email using Gmail.
    """
    logger.info(f"Sending Gmail to={to}, subject={subject}")

    try:
        service = get_gmail_service()

        send_mail_tool = GmailSendMessage.from_api_resource(
            api_resource=service
        )

        send_mail_tool.run(
            {
                "to": to,
                "subject": subject,
                "message": body,
            }
        )

        return "✅ Email sent successfully."

    except FileNotFoundError:
        return "❌ credentials.json not found. Gmail is not configured."

    except Exception as e:
        logger.exception("Gmail send failed")
        return f"❌ Failed to send email: {e}"


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