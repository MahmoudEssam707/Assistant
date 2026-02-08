"""Test LLM connectivity and basic functionality."""
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(
        api_key=os.getenv("LLM_API_KEY"),
        base_url=os.getenv("LLM_BASE_URL"),
        model=os.getenv("LLM_MODEL_NAME"),
    )

def test_llm_connection(llm):
    """Test that LLM can be initialized and respond to basic input."""
    output = llm.invoke(input="Hello, how are you today?")
    print(f"✅ LLM Response: {output.content}")

test_llm_connection(llm)