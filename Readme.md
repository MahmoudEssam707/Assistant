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
# Required to change the following
LLM_API_KEY=your_openai_api_key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL_NAME=gpt-4
JINA_EMBEDDING_API_KEY=your_jina_api_key
JINA_EMBEDDING_MODEL=jina-embeddings-v2-base-en

# Optional (for email)
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_gmail_app_password
```

### 3. Run with Docker

```bash
docker compose up -d --build
```

### 4. Add Knowledge Base (Optional)

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python utils/ingest_data.py
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