# =========================
# Imports
# =========================
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
from utils.util import embeddings
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct


# =========================
# Environment Setup
# =========================
load_dotenv()

COLLECTION_NAME = "my_collection"


# =========================
# Qdrant Client
# =========================
qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_BASE_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
)


# =========================
# Sample Documents
# =========================
python_docs = [
    "Python is an interpreted, high-level programming language.",
    "List comprehensions provide a concise way to create lists in Python.",
    "The 'def' keyword is used to define a function in Python.",
    "Dictionaries in Python are implemented as hash tables.",
    "Exception handling in Python is done with try and except blocks.",
    "Decorators allow you to modify the behavior of functions.",
    "Generators are a simple way of creating iterators in Python.",
    "Python supports multiple programming paradigms.",
    "Virtual environments help manage dependencies.",
    "Lambda functions are small anonymous functions.",
]


# =========================
# Generate Embeddings
# =========================
document_embeddings = embeddings.embed_documents(python_docs)

VECTOR_SIZE = len(document_embeddings[0])


# =========================
# Collection Setup
# =========================
if not qdrant_client.collection_exists(COLLECTION_NAME):
    qdrant_client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=VECTOR_SIZE,
            distance=Distance.COSINE,
        ),
    )


# =========================
# Insert Documents
# =========================
qdrant_client.upsert(
    collection_name=COLLECTION_NAME,
    points=[
        PointStruct(
            id=idx,
            vector=embedding,          
            payload={"doc": doc},      
        )
        for idx, (doc, embedding) in enumerate(
            zip(python_docs, document_embeddings)
        )
    ],
)

# search for a sample query
query = "What is a lambda function in Python?"
query_vector = embeddings.embed_query(query)
search_result = qdrant_client.query_points(
    collection_name=COLLECTION_NAME,
    query=query_vector,
    limit=1,
)

# =========================
# Verification
# =========================
print(qdrant_client.get_collections())
print(f"For query '{query}', top result: {search_result.points[0].payload['doc']}")