from langchain_community.embeddings import JinaEmbeddings
import os
from dotenv import load_dotenv
load_dotenv()


embeddings = JinaEmbeddings(
    jina_api_key=os.getenv("EMBEDDING_API_KEY"),
    model_name=os.getenv("EMBEDDING_MODEL"),
)

# testing the embeddings
if __name__ == "__main__":
    test_text = "Hello, world!"
    vector = embeddings.embed_query(test_text)
    print(f"Embedding vector for '{test_text}': {vector}")