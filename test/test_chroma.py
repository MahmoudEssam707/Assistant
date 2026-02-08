import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
from utils.util import embeddings
import chromadb

load_dotenv()

# Initialize ChromaDB client
chroma_client = chromadb.HttpClient(
    host="localhost",
    port=int(os.getenv("CHROMA_PORT", "8000")),
)

# Test query
query = "What is a \"def\"?"
collection_name = os.getenv("CHROMA_COLLECTION_NAME", "my_collection")

try:
    # Get collection
    collection = chroma_client.get_collection(name=collection_name)
    
    # Perform search
    query_vector = embeddings.embed_query(query)
    result = collection.query(query_embeddings=[query_vector], n_results=1)
    
    # Display results
    print(f"\n✅ ChromaDB Connection: OK")
    print(f"Collections: {[col.name for col in chroma_client.list_collections()]}")
    print(f"\nQuery: '{query}'")
    
    if result['documents'] and result['documents'][0]:
        print(f"Top result: {result['documents'][0][0]}")
    else:
        print("No results found")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nRun 'python utils/ingest_data.py' to populate the database first.")
