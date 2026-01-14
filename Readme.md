# How to Run the Assistant Project

This guide explains how to run the Assistant project locally using **Docker Compose**.

---

## Prerequisites

Make sure you have the following installed:

* Docker
* Docker Compose

Verify installation:

```bash
docker --version
docker compose version
```

---

## Clone the Repository

```bash
git clone <your-repo-url>
cd Assistant
```

---

## Environment Setup

Create a `.env` file in the project root:

```bash
touch .env
```

Add the following environment variables:

```env
# LLM Configuration
LLM_API_KEY=your_openai_api_key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL_NAME=gpt-4

# Jina Embeddings
JINA_EMBEDDING_API_KEY=your_jina_api_key
JINA_EMBEDDING_MODEL=jina-embeddings-v2-base-en

# Qdrant Vector Database
QDRANT_BASE_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key

# Gmail SMTP
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_gmail_app_password
```

---

## Build and Run the Application

From the project root directory:

```bash
docker compose up -d --build
```

This will start:

* FastAPI Backend
* Streamlit UI

---

## Access the Application

* Streamlit UI:
  [http://localhost:8501](http://localhost:8501)

* FastAPI Health Check:
  [http://localhost:2024/health](http://localhost:2024/health)

---

## View Logs (Optional)

```bash
docker compose logs -f
```

Or per service:

```bash
docker compose logs -f api
docker compose logs -f ui
```

---

## Stop the Application

```bash
docker compose down
```

---

## Rebuild After Code Changes

```bash
docker compose up -d --build
```
