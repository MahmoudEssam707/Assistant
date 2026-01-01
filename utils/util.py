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
    model_name=os.getenv("JINA_EMBEDDING_MODEL"),
)   