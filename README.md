# graph_rag_knowledgebase

Aplicação de exemplo de RAG jurídico com Python + LangChain + MongoDB + Streamlit.

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

## Estrutura do diretório

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

1. Criar e ativar ambiente virtual.
2. Instalar dependências.
3. Configurar variáveis no `.env`.

```bash
cd /Users/vagnerpontes/Documents/Demos/graph_rag_knowledgebase
python3.14 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### Versão de Python

- Requerido: `Python 3.14.3`.
- O script `scripts/run_streamlit.sh` valida essa versão e aborta se estiver diferente.
- Os scripts `scripts/*.py` e o `app.py` também validam essa versão em runtime.

### Variáveis mínimas no `.env`

- `ATLAS_MODEL_API_KEY` (recomendado, usado na Atlas Embedding API)
- `VOYAGE_API_KEY` (fallback compatível)
- `OPENAI_API_KEY` (usada pelo LLM de resposta e GraphRAG)
- `MONGODB_URI`

As demais variáveis já possuem valores padrão no `.env.example`.

Ao iniciar o app, ele valida essas variáveis. Se faltar alguma, o app mostra erro e encerra a execução.

## Como executar o app

1. Gerar dataset jurídico sintético.
2. Ingerir documentos no Vector Search.
3. Subir interface Streamlit.

```bash
python3.14 scripts/generate_dataset.py
python3.14 scripts/ingest_vector_store.py
streamlit run app.py
```

Alternativa com script:

```bash
bash scripts/run_streamlit.sh
```

Se o banco `MONGODB_DB` ainda não existir, o app cria automaticamente os objetos de banco:
- collections
- índices padrão (B-Tree)
- Atlas Search index
- Atlas Vector Search index

Se o banco já existir, os scripts de inicialização são ignorados.

### Modelo de embedding

- Provider: Voyage AI via Atlas Embedding API (`https://ai.mongodb.com/v1/embeddings`)
- Modelo padrão: `voyage-4-large` (família Voyage 4)
- Dimensões padrão: `1024`

## Execução opcional de GraphRAG

```bash
python3.14 scripts/ingest_graph_store.py
```

## Notes

- You need a MongoDB Atlas cluster with Vector Search support.
- `MongoDBGraphStore` is loaded from `langchain_mongodb.graphrag.graph`.
- `MongoDBGraphStore` requires LLM calls for entity/relation extraction.
- Streamlit app allows querying with vector retrieval and optional GraphRAG response.
- GraphRAG integration approach is aligned with MongoDB's LangChain GraphRAG notebook:
  `https://github.com/mongodb/docs-notebooks/blob/main/ai-integrations/langchain-graphrag.ipynb`
