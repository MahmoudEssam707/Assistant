# Multi-Agent Assistant

A multi-agent AI assistant with knowledge search, calculations, and email capabilities. Built with LangGraph, FastAPI, and Streamlit.

---

## Prerequisites

* Docker & Docker Compose
* Python 3.10+ (for data ingestion)

---

## Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/MahmoudEssam707/Assistant/
cd Assistant
cp .env.example .env
```

### 2. Configure `.env`

```env
# LLM and API Configuration 
LLM_API_KEY=
LLM_BASE_URL=
LLM_MODEL_NAME=

# embedding service configuration
JINA_EMBEDDING_API_KEY=
JINA_EMBEDDING_MODEL=

# ChromaDB service (vector database)
CHROMA_HOST=assistant-chromadb
CHROMA_PORT=8000
CHROMA_COLLECTION_NAME=my_collection

# SMTP Email Configuration (for Gmail)
# Generate app password: https://myaccount.google.com/apppasswords
SMTP_EMAIL=
SMTP_PASSWORD=

# API Configuration (for chat UI)
API_URL=http://assistant-api:2024

# Logging Configuration
LOG_LEVEL=INFO
```

### 3. Run with Docker

```bash
docker compose up -d --build
```

### 4. Add Knowledge Base

```bash
docker exec -it assistant-api bash -c "python utils/ingest_data.py && python test/test_chroma.py"
```

---

## Access

* **Chat UI**: [http://localhost:8501](http://localhost:8501)
* **API**: [http://localhost:2024](http://localhost:2024)
* **ChromaDB**: [http://localhost:8000](http://localhost:8000)

---

## Stop

```bash
docker compose down
```