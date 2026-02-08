"""Ingest documents into ChromaDB vector database with text chunking."""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
from utils.util import embeddings
import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

# Sample knowledge base - replace with your own documents
TEST_DOCUMENT = """Once upon a time, in a land of computers, there was a young programmer named Alex who loved 
Python, an interpreted, high-level programming language known for its simplicity and power. 
Alex enjoyed exploring Python’s many features, starting with lists. He discovered that list 
comprehensions provided a concise and elegant way to create lists without writing long loops, 
which made coding much faster and more enjoyable. 
Eager to organize his code, Alex learned about functions. He realized that the `def` keyword 
allowed him to define reusable functions, keeping his programs neat and modular. As his projects 
grew, he encountered complex data, and dictionaries became his best friends. Implemented as hash 
tables, dictionaries allowed him to store and retrieve data efficiently using key-value pairs. 
One day, Alex’s code crashed unexpectedly. Frustrated but determined, he learned about exception 
handling in Python, using `try` and `except` blocks to gracefully handle errors and prevent his 
programs from failing completely. To make his code even more flexible, he explored decorators, 
a magical tool that could modify the behavior of functions without changing their core code. 
As Alex’s programs became larger, he discovered generators, a simple yet powerful way to create 
iterators that didn’t require storing all data in memory. He also realized that Python was versatile, 
supporting multiple programming paradigms, from object-oriented to functional programming. 
Managing multiple projects became tricky, so Alex embraced virtual environments to keep dependencies 
organized and avoid conflicts. Finally, he learned the art of lambda functions, small anonymous functions 
that could be written in a single line, perfect for simple operations. 
With these tools and techniques, Alex’s journey into Python programming became an exciting adventure, 
filled with discovery, efficiency, and endless possibilities."""


def ingest_documents(
    documents: str | list[str], 
    collection_name: str = None,
    chunk_size: int = 250,
    chunk_overlap: int = 50
):
    """
    Ingest documents into ChromaDB collection with automatic text chunking.
    
    Args:
        documents: Single document (string) or list of documents to ingest
        collection_name: Name of the collection (uses env var if not provided)
        chunk_size: Maximum size of each text chunk (default: 500 characters)
        chunk_overlap: Number of characters to overlap between chunks (default: 50)
    """
    if collection_name is None:
        collection_name = os.getenv("CHROMA_COLLECTION_NAME", "my_collection")
    
    # Convert single string to list for uniform processing
    if isinstance(documents, str):
        documents = [documents]
    
    print(f"🚀 Starting data ingestion to collection '{collection_name}'...")
    print(f"📄 Processing {len(documents)} document(s)")
    print(f"✂️  Chunk settings: size={chunk_size}, overlap={chunk_overlap}")
    
    # Initialize ChromaDB client
    client = chromadb.HttpClient(
        host=os.getenv("CHROMA_HOST", "localhost"),
        port=int(os.getenv("CHROMA_PORT", "8000")),
        settings=chromadb.config.Settings(anonymized_telemetry=False)
    )
    
    # Get or create collection
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )
    print(f"✅ Collection ready")
    
    # Initialize text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    # Chunk all documents
    all_chunks = []
    all_metadata = []
    
    for doc_idx, doc in enumerate(documents):
        chunks = text_splitter.split_text(doc)
        all_chunks.extend(chunks)
        
        # Track metadata for each chunk
        for chunk_idx, chunk in enumerate(chunks):
            all_metadata.append({
                "source": "ingestion",
                "doc_index": doc_idx,
                "chunk_index": chunk_idx,
                "total_chunks": len(chunks),
                "doc": chunk
            })

    print(f"✂️  Split into {len(all_chunks)} chunks")
    print(f"Sample Chunk {all_chunks[0]}")    
    # Generate embeddings
    print(f"🔄 Generating embeddings...")
    chunk_embeddings = embeddings.embed_documents(all_chunks)
    print(f"✅ Embeddings generated (dimension: {len(chunk_embeddings[0])})")
    
    # Insert chunks into ChromaDB
    print(f"💾 Inserting chunks into ChromaDB...")
    collection.add(
        ids=[str(idx) for idx in range(len(all_chunks))],
        embeddings=chunk_embeddings,
        documents=all_chunks,
        metadatas=all_metadata
    )
    
    print(f"✅ Successfully ingested {len(all_chunks)} chunks from {len(documents)} document(s)!")
    print(f"\n📊 Collections in database: {[col.name for col in client.list_collections()]}")
    
    return len(all_chunks)


if __name__ == "__main__":
    print("=" * 60)
    print("ChromaDB Data Ingestion Script with Text Chunking")
    print("=" * 60)
    
    # Ingest sample document (will be automatically chunked)
    total_chunks = ingest_documents(
        documents=TEST_DOCUMENT,
        chunk_size=250,  # Adjust based on your needs
        chunk_overlap=50
    )
    
    print("\n" + "=" * 60)
    print(f"✅ Ingestion complete! {total_chunks} chunks stored.")
    print("💡 Test with: python test/test_chroma.py")
    print("=" * 60)
