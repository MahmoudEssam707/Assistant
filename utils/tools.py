"""Tool definitions using @tool decorator for the agent."""

import os

from qdrant_client import QdrantClient
from .util import logger, send_email_smtp, embeddings
from langchain_core.tools import tool

# =========================
# Qdrant Client
# =========================
client = QdrantClient(
    url=os.getenv("QDRANT_BASE_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
)

# Tool to search in Qdrant collection
@tool
def search_in_knowledge(query: str, collection_name: str = "my_collection") -> str:
    """
    Search for the top similar vector in a Qdrant collection using a text query.

    Args:
        query: The user text query.
        collection_name: The name of the Qdrant collection to search (default: "my_collection").

    Returns:
        A string representation of the top search result.
    """
    logger.info(f"Qdrant search in collection={collection_name} with query='{query}'")

    try:
        # Generate embedding for the query
        query_vector = embeddings.embed_query(query)
        search_result = client.query_points(
            collection_name=collection_name,
            query=query_vector,
            limit=1,
        )

        if search_result:
            logger.info(f"Qdrant search result: {search_result}")
            top_result = search_result.points[0].payload["doc"]
            logger.info(f"Top Qdrant search result: {top_result}")
            return str(top_result)
        else:
            return "No results in my mind about it."

    except Exception as e:
        logger.exception("Qdrant search failed")
        return f"❌ Qdrant search failed: {e}"



@tool
def gmail_send_tool(to: str, subject: str, body: str) -> str:
    """
    Send an email using Gmail SMTP.
    """
    logger.info(f"Sending email via SMTP to={to}, subject={subject}")

    try:
        result = send_email_smtp(to=to, subject=subject, body=body)
        return f"✅ {result}"

    except ValueError as e:
        return f"❌ Configuration error: {e}"

    except Exception as e:
        logger.exception("Email send failed")
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