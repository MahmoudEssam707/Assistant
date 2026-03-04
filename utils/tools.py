"""Tool definitions using @tool decorator for the agent."""

import os
import json
from .util import logger, send_email_smtp, embeddings, get_jira_client, get_chroma_client, DEFAULT_COLLECTION
from langchain_core.tools import tool

# =========================
# Calculator
# =========================

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
    
# =========================
# Send Mail to Someone
# =========================

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

# =========================
# Searching in Knowledge Base
# =========================

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
        chroma_client = get_chroma_client()
        # Get or create collection
        collection = chroma_client.get_or_create_collection(
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
    
# =========================
# Jira Tools - List all Projects
# =========================
@tool
def jira_get_projects() -> str:
    """
    Fetch all Jira projects the user has access to.
    
    Returns:
        A formatted string with project keys, names, and descriptions.
    """
    logger.info(f"🎫 TOOL CALL: jira_get_projects")
    
    try:
        jira = get_jira_client()
        projects = jira.projects()
        
        if not projects:
            logger.info("   ℹ️ No projects found")
            return "No projects found."
        
        formatted_results = f"Found {len(projects)} project(s):\n\n"
        
        for project in projects:
            key = project.get('key', 'N/A')
            name = project.get('name', 'N/A')
            project_type = project.get('projectTypeKey', 'N/A')
            
            formatted_results += f"• [{key}] {name}\n"
            formatted_results += f"  Type: {project_type}\n\n"
        
        logger.info(f"   ✅ Found {len(projects)} project(s)")
        return formatted_results.strip()
        
    except Exception as e:
        logger.exception("   ❌ Jira get projects failed")
        return f"❌ Failed to fetch projects: {str(e)}"

# =========================
# Jira Tools - Create Issue
# =========================

@tool
def jira_create_issue(issue_dict: str) -> str:
    """
    Create a new Jira issue.
    
    Args:
        issue_dict: A JSON string representing the issue fields. Must include 'project', 'summary', and 'issuetype'.
                   Example: '{"project": {"key": "TEST"}, "summary": "Bug in login", 
                            "description": "Users cannot log in", "issuetype": {"name": "Bug"}, 
                            "priority": {"name": "High"}}'
    
    Returns:
        The created issue key and URL.
    """
    logger.info(f"🎫 TOOL CALL: jira_create_issue")
    logger.info(f"   Issue data: {issue_dict}")
    
    try:
        jira = get_jira_client()
        
        # Parse the JSON string
        try:
            fields = json.loads(issue_dict)
        except json.JSONDecodeError:
            return "❌ Invalid JSON format. Please provide a valid JSON string."
        
        # Create the issue
        new_issue = jira.create_issue(fields=fields)
        issue_key = new_issue.get('key', 'N/A')
        issue_url = f"{os.getenv('JIRA_INSTANCE_URL')}/browse/{issue_key}"
        
        logger.info(f"   ✅ Created issue: {issue_key}")
        return f"✅ Successfully created issue [{issue_key}]\nURL: {issue_url}"
        
    except Exception as e:
        logger.exception("   ❌ Jira create issue failed")
        return f"❌ Failed to create issue: {str(e)}"

# =========================
# Jira Tools - Add Comment
# ========================= 
@tool
def jira_add_comment(issue_key: str, comment: str) -> str:
    """
    Add a comment to a Jira issue.
    
    Args:
        issue_key: The issue key (e.g., "TEST-123")
        comment: The comment text to add
    
    Returns:
        Confirmation message.
    """
    logger.info(f"🎫 TOOL CALL: jira_add_comment")
    logger.info(f"   Issue: {issue_key}")
    logger.info(f"   Comment: {comment[:100]}...")
    
    try:
        jira = get_jira_client()
        jira.issue_add_comment(issue_key, comment)
        
        logger.info(f"   ✅ Added comment to: {issue_key}")
        return f"✅ Successfully added comment to issue [{issue_key}]"
        
    except Exception as e:
        logger.exception("   ❌ Jira add comment failed")
        return f"❌ Failed to add comment: {str(e)}"
