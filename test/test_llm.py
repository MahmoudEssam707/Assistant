
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import os
load_dotenv()
print("Done Environment setup")


llm = ChatOpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL"),
    model=os.getenv("LLM_MODEL_NAME"),
)
print("Done LLM initialization")


output = llm.invoke(input="Hello, how are you today?")
print("Done LLM call")

print(output.content)
print("Done Output")