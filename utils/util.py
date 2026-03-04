"""
Shared utilities, classes, and configurations for the agent.
"""

# =========================
# Imports
# =========================
import logging
from langchain_openai import ChatOpenAI
from langchain_community.embeddings import JinaEmbeddings
import os
import time
import chromadb
from dotenv import load_dotenv
from atlassian import Jira

# SMTP for Email
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# =========================
# Environment Setup
# =========================
load_dotenv()

# =========================
# Logging Configuration
# =========================
def _setup_logger():
    """Configure logger with stdout/stderr handlers for Docker compatibility."""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    
    # Use stdout for Docker compatibility instead of file
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Structured logging format
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    
    return logger

logger = _setup_logger()

# =========================
# SMTP Email Configuration
# =========================
def send_email_smtp(to: str, subject: str, body: str) -> str:
    """
    Send an email using SMTP (Gmail).
    Requires SMTP_EMAIL and SMTP_PASSWORD environment variables.
    """
    smtp_email = os.getenv("SMTP_EMAIL")
    smtp_password = os.getenv("SMTP_PASSWORD")
    
    if not smtp_email or not smtp_password:
        raise ValueError("SMTP_EMAIL and SMTP_PASSWORD must be set in environment")
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = smtp_email
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    # Send via Gmail SMTP
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(smtp_email, smtp_password)
        server.send_message(msg)
    
    return "Email sent successfully"

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
    jina_embedding_model=os.getenv("JINA_EMBEDDING_MODEL"),
)   

_chroma_client = None


def get_chroma_client():
    """Create (or reuse) a resilient ChromaDB HttpClient with retries."""
    global _chroma_client
    if _chroma_client is not None:
        return _chroma_client

    host = os.getenv("CHROMA_HOST", "localhost")
    port = int(os.getenv("CHROMA_PORT", "8000"))
    tenant = os.getenv("CHROMA_TENANT", "default_tenant")
    database = os.getenv("CHROMA_DATABASE", "default_database")
    attempts = int(os.getenv("CHROMA_CONNECT_RETRIES", "8"))
    delay_seconds = float(os.getenv("CHROMA_CONNECT_RETRY_DELAY", "1.5"))

    last_error = None
    for attempt in range(1, attempts + 1):
        try:
            _chroma_client = chromadb.HttpClient(
                host=host,
                port=port,
                tenant=tenant,
                database=database,
            )
            logger.info(
                "Connected to ChromaDB at %s:%s (tenant=%s, database=%s)",
                host,
                port,
                tenant,
                database,
            )
            return _chroma_client
        except Exception as exc:
            last_error = exc
            logger.warning(
                "ChromaDB connection attempt %s/%s failed: %s",
                attempt,
                attempts,
                exc,
            )
            if attempt < attempts:
                time.sleep(delay_seconds)

    raise RuntimeError(
        f"Unable to connect to ChromaDB at {host}:{port} after {attempts} attempts. "
        f"Last error: {last_error}"
    )


# Backward compatibility for existing imports.
client = get_chroma_client
# Default collection name (configurable via env var)
DEFAULT_COLLECTION = os.getenv("CHROMA_COLLECTION_NAME", "my_collection")

# ==========================
# Jira Init
# ==========================
def get_jira_client():
    """Get Jira client with username/password authentication."""
    jira_url = os.getenv("JIRA_INSTANCE_URL")
    jira_username = os.getenv("JIRA_USERNAME")
    jira_password = os.getenv("JIRA_PASSWORD")
    
    if not all([jira_url, jira_username, jira_password]):
        raise ValueError(
            "Missing Jira credentials. Please set JIRA_INSTANCE_URL, "
            "JIRA_USERNAME, and JIRA_PASSWORD environment variables."
        )
    
    return Jira(
        url=jira_url,
        username=jira_username,
        password=jira_password
    )