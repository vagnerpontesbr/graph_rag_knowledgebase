# graph_rag_knowledgebase

Sample legal RAG application built with Python + LangChain + MongoDB + Streamlit.

## Stack

- Streamlit UI
- LangChain
- MongoDB Atlas Vector Search (`langchain-mongodb`)
- Optional GraphRAG flow (`MongoDBGraphStore`, via `langchain-mongodb>=0.11.0`)

## Features

- Generates a synthetic legal dataset based on a legal ontology.
- Ingests legal documents into MongoDB Atlas Vector Search.
- Optionally ingests docs into MongoDB Graph Store for GraphRAG exploration.
- Answers legal questions using retrieved context.

## Directory Structure

```text
graph_rag_knowledgebase/
├── .env.example
├── .streamlit/
│   └── config.toml
├── app.py
├── requirements.txt
├── README.md
├── data/
│   ├── legal_docs.jsonl
│   ├── legal_relations.jsonl
│   └── legal_ontology.ttl
├── scripts/
│   ├── generate_dataset.py
│   ├── ingest_vector_store.py
│   ├── ingest_graph_store.py
│   └── run_streamlit.sh
└── rag_knowledgebase/
    ├── __init__.py
    ├── config.py
    ├── dataset.py
    ├── mongodb.py
    └── rag_pipeline.py
```

## Setup

Dependencies are managed with [uv](https://docs.astral.sh/uv/). Install it once if you haven't already:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then bootstrap the project:

```bash
cd /Users/vagnerpontes/Documents/Demos/graph_rag_knowledgebase
uv sync          # creates .venv and installs all dependencies
cp .env.example .env
```

### Python Version

- Required: `Python 3.14`.
- `pyproject.toml` pins `requires-python = "==3.14.*"` — `uv` enforces this automatically.
- The `scripts/*.py` scripts and `app.py` also validate this version at runtime.

### Minimum `.env` Variables

- `ATLAS_MODEL_API_KEY` (recommended, used by the Atlas Embedding API)
- `VOYAGE_API_KEY` (compatible fallback)
- `OPENAI_API_KEY` (used by the answer LLM and GraphRAG)
- `MONGODB_URI`

All other variables already have default values in `.env.example`.

When the app starts, it validates these variables. If any are missing, the app displays an error and stops.

## Running the App

1. Generate the synthetic legal dataset.
2. Ingest documents into Vector Search.
3. Start the Streamlit interface.

```bash
uv run python scripts/generate_dataset.py
uv run python scripts/ingest_vector_store.py
uv run streamlit run app.py
```

Alternative using the shell script (runs `uv sync` + starts Streamlit in one step):

```bash
bash scripts/run_streamlit.sh
```

If the `MONGODB_DB` database does not yet exist, the app automatically creates all database objects:
- Collections
- Standard indexes (B-Tree)
- Atlas Search index
- Atlas Vector Search index

If the database already exists, the initialization steps are skipped.

### Embedding Model

- Provider: Voyage AI via Atlas Embedding API (`https://ai.mongodb.com/v1/embeddings`)
- Default model: `voyage-4-large` (Voyage 4 family)
- Default dimensions: `1024`

## Optional GraphRAG Ingestion

```bash
uv run python scripts/ingest_graph_store.py
```

## Notes

- You need a MongoDB Atlas cluster with Vector Search support.
- `MongoDBGraphStore` is loaded from `langchain_mongodb.graphrag.graph`.
- `MongoDBGraphStore` requires LLM calls for entity/relation extraction.
- Streamlit app allows querying with vector retrieval and optional GraphRAG response.
- GraphRAG integration approach is aligned with MongoDB's LangChain GraphRAG notebook:
  `https://github.com/mongodb/docs-notebooks/blob/main/ai-integrations/langchain-graphrag.ipynb`
