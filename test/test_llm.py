from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import os
load_dotenv()

llm = ChatOpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL"),
    model=os.getenv("LLM_MODEL_NAME"),
)

output = llm.invoke(input="Hello, how are you today?")

print(output.content)