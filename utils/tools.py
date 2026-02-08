"""Tool definitions using @tool decorator for the agent."""

import os

import chromadb
from .util import logger, send_email_smtp, embeddings
from langchain_core.tools import tool

# =========================
# ChromaDB Client
# =========================
client = chromadb.HttpClient(
    host=os.getenv("CHROMA_HOST", "localhost"),
    port=int(os.getenv("CHROMA_PORT", "8000")),
)
# Default collection name (configurable via env var)
DEFAULT_COLLECTION = os.getenv("CHROMA_COLLECTION_NAME", "my_collection")

# Tool to search in ChromaDB collection
@tool
def search_in_knowledge(query: str, collection_name: str = None) -> str:
    """
    Search for the top similar vector in a ChromaDB collection using a text query.

    Args:
        query: The user text query.
        collection_name: The name of the ChromaDB collection to search. 
                        If not provided, uses CHROMA_COLLECTION_NAME env var (default: "my_collection").

    Returns:
        A string representation of the top search result.
    """
    if collection_name is None:
        collection_name = DEFAULT_COLLECTION
        
    logger.info(f"🔍 TOOL CALL: search_in_knowledge")
    logger.info(f"   Collection: {collection_name}")
    logger.info(f"   Query: '{query}'")

    try:
        # Get or create collection
        collection = client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        # Generate embedding for the query
        query_vector = embeddings.embed_query(query)
        
        # Query ChromaDB
        search_result = collection.query(
            query_embeddings=[query_vector],
            n_results=1,
        )

        if search_result and search_result['documents'] and search_result['documents'][0]:
            top_result = search_result['documents'][0][0]
            logger.info(f"   ✅ Result: {str(top_result)[:100]}...")
            return str(top_result)
        else:
            logger.info("   ℹ️ No results found")
            return "No results in my mind about it."

    except Exception as e:
        logger.exception("   ❌ ChromaDB search failed")
        return f"❌ ChromaDB search failed: {e}"


@tool
def gmail_send_tool(to: str, subject: str, body: str) -> str:
    """
    Send an email using Gmail SMTP.
    """
    logger.info(f"📧 TOOL CALL: gmail_send_tool")
    logger.info(f"   To: {to}")
    logger.info(f"   Subject: {subject}")

    try:
        result = send_email_smtp(to=to, subject=subject, body=body)
        logger.info(f"   ✅ Email sent successfully")
        return f"✅ {result}"

    except ValueError as e:
        logger.error(f"   ❌ Configuration error: {e}")
        return f"❌ Configuration error: {e}"

    except Exception as e:
        logger.exception("   ❌ Email send failed")
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
    logger.info(f"🧮 TOOL CALL: calculator_tool")
    logger.info(f"   Expression: {expression}")
    try:
        result = eval(expression)
        logger.info(f"   ✅ Result: {result}")
        return str(result)
    except Exception as e:
        logger.error(f"   ❌ Error: {e}")
        return "Invalid mathematical expression"