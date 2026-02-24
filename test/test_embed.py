
from langchain_community.embeddings import JinaEmbeddings
import os
from dotenv import load_dotenv
load_dotenv()
print("Done Environment setup")

embeddings = JinaEmbeddings(
    jina_embedding_api_key=os.getenv("JINA_EMBEDDING_API_KEY"),
    jina_embedding_model=os.getenv("JINA_EMBEDDING_MODEL"),
)
print("Done Embedding initialization")

# testing the embeddings
if __name__ == "__main__":
    test_text = "Hello, world!"
    vector = embeddings.embed_query(test_text)
    print("Done Embedding call")
    print(f"Embedding vector for '{test_text}': {vector}")
    print("Done Output")